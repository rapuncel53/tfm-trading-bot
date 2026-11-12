"""Entrenamiento del modelo LLMReturnRegressor Multi-Horizonte (1d, 5d, 20d).

Aprende a predecir simultáneamente el vector forward de retornos r̂ = [r_1d, r_5d, r_20d]
utilizando Qwen3.5-9B cuantizado a 4-bit (QLoRA) y Masked Mean Pooling (Eq. 5 EMNLP 2024).
"""
import os
import sys
import time
import math
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import AutoTokenizer, get_linear_schedule_with_warmup
from tqdm.auto import tqdm
from scipy.stats import spearmanr

sys.path.insert(0, os.path.abspath('.'))
from src.config import ModelConfig, DataConfig, TrainingConfig
from src.dataset import StockReturnNewsDataset
from src.model import LLMReturnRegressor, get_peft_model
from src.train import make_collate_fn, set_windows_keep_awake, get_trainable_state_dict

def main():
    set_windows_keep_awake(True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n=======================================================")
    print(f"  ENTRENAMIENTO MULTI-HORIZONTE LLM (1d, 5d, 20d)")
    print(f"  Dispositivo: {device} | GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    print(f"=======================================================\n")

    model_cfg = ModelConfig(num_horizons=3)
    data_cfg = DataConfig(
        train_path="data/splits/train/daily_aligned.parquet",
        val_path="data/splits/val/daily_aligned.parquet",
        test_path="data/splits/test/daily_aligned.parquet",
        target_returns=["ret_1d", "ret_5d", "ret_20d"],
        max_token_length=2048,
        filter_news_only=True
    )
    
    output_dir = "checkpoints/llm_return_regressor"
    os.makedirs(output_dir, exist_ok=True)
    best_ckpt_path = os.path.join(output_dir, "best_model_multihorizon.pt")
    history_file = os.path.join(output_dir, "multihorizon_training_history.csv")

    # 1. Cargar Tokenizer
    print("[1/5] Cargando Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_cfg.model_name_or_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    pad_id = tokenizer.pad_token_id

    # 2. Inicializar Modelo con Cabezal Triple
    print("\n[2/5] Inicializando LLMReturnRegressor con Cabezal Multi-Horizonte (3 targets)...")
    model = LLMReturnRegressor(model_cfg)
    
    # Warm-start desde checkpoint previo (conservando los 718 parámetros LoRA adaptados a noticias financieras)
    prev_ckpt = os.path.join(output_dir, "best_model.pt")
    if os.path.exists(prev_ckpt):
        print(f"  -> Cargando pesos LoRA previos desde {prev_ckpt} (warm-start)...")
        ckpt = torch.load(prev_ckpt, map_location='cpu', weights_only=False)
        sd = ckpt['model_state_dict'] if isinstance(ckpt, dict) and 'model_state_dict' in ckpt else ckpt
        sd_filtered = {k: v for k, v in sd.items() if not k.startswith('forecasting_head.linear')}
        model.load_state_dict(sd_filtered, strict=False)
        print(f"  -> {len(sd_filtered)} tensores LoRA cargados con éxito. Cabezal triple inicializado.")
        del ckpt, sd, sd_filtered
        torch.cuda.empty_cache()

    # 3. Datasets y DataLoaders
    print("\n[3/5] Preparando DataLoaders...")
    train_ds = StockReturnNewsDataset(
        data_cfg.train_path, tokenizer=tokenizer, max_length=data_cfg.max_token_length,
        target_col=data_cfg.target_returns, filter_news_only=True
    )
    val_ds = StockReturnNewsDataset(
        data_cfg.val_path, tokenizer=tokenizer, max_length=data_cfg.max_token_length,
        target_col=data_cfg.target_returns, filter_news_only=True
    )
    
    collate = make_collate_fn(pad_id)
    batch_size = 2
    grad_accum_steps = 8  # Lote efectivo = 16
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, collate_fn=collate)

    # 4. Optimizador y Scheduler
    max_steps = 150
    eval_steps = 25
    eval_limit = 120  # Muestras para validación rápida
    lr = 8e-5

    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = AdamW(trainable_params, lr=lr, weight_decay=0.01)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=15, num_training_steps=max_steps)

    def evaluate_model(step_num):
        model.eval()
        all_preds = []
        all_targs = []
        val_loss = 0.0
        n_samples = 0
        with torch.no_grad():
            for b_idx, batch in enumerate(val_loader):
                if n_samples >= eval_limit:
                    break
                ids = batch['input_ids'].to(device)
                mask = batch['attention_mask'].to(device)
                targs = batch['targets'].to(device)
                
                out = model(ids, mask, targets=targs)
                val_loss += out['loss'].item() * len(targs)
                all_preds.append(out['preds'].cpu().numpy())
                all_targs.append(targs.cpu().numpy())
                n_samples += len(targs)
                del ids, mask, targs, out
                
        torch.cuda.empty_cache()
        model.train()
        
        preds_mat = np.concatenate(all_preds, axis=0)  # [N, 3]
        targs_mat = np.concatenate(all_targs, axis=0)  # [N, 3]
        
        metrics = {'val_loss': val_loss / n_samples}
        horizons = ['1d', '5d', '20d']
        for i, h in enumerate(horizons):
            diff = preds_mat[:, i] - targs_mat[:, i]
            rmse = float(np.sqrt(np.mean(diff ** 2)))
            ric, _ = spearmanr(preds_mat[:, i], targs_mat[:, i])
            hit = float(np.mean(np.sign(preds_mat[:, i]) == np.sign(targs_mat[:, i])) * 100.0)
            metrics[f'rmse_{h}'] = rmse
            metrics[f'rank_ic_{h}'] = 0.0 if np.isnan(ric) else float(ric)
            metrics[f'hit_{h}'] = hit
            
        # Ponderación compuesta
        composite_score = (metrics['rmse_1d']/0.0225 + metrics['rmse_5d']/0.0433 + metrics['rmse_20d']/0.0789) / 3.0
        metrics['composite_score'] = composite_score
        return metrics

    # 5. Bucle de Entrenamiento
    print(f"\n[4/5] Iniciando entrenamiento multi-horizonte ({max_steps} pasos, grad_accum={grad_accum_steps})...")
    model.train()
    optimizer.zero_grad()
    
    step = 0
    accum_loss = 0.0
    best_composite = float('inf')
    t_start = time.time()
    
    pbar = tqdm(total=max_steps, desc="Entrenamiento Multi-Horizonte", dynamic_ncols=True)
    
    for epoch in range(10):
        if step >= max_steps:
            break
        for b_idx, batch in enumerate(train_loader):
            if step >= max_steps:
                break
                
            ids = batch['input_ids'].to(device)
            mask = batch['attention_mask'].to(device)
            targs = batch['targets'].to(device)
            
            outputs = model(ids, mask, targets=targs)
            loss = outputs['loss'] / grad_accum_steps
            loss.backward()
            accum_loss += loss.item() * grad_accum_steps
            
            del ids, mask, targs, outputs
            
            if (b_idx + 1) % grad_accum_steps == 0:
                torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                
                step += 1
                cur_loss = accum_loss / grad_accum_steps
                accum_loss = 0.0
                pbar.update(1)
                pbar.set_postfix({'loss': f"{cur_loss:.4f}", 'lr': f"{scheduler.get_last_lr()[0]:.2e}"})
                
                # Evaluación periódica
                if step % eval_steps == 0 or step == max_steps:
                    val_res = evaluate_model(step)
                    pbar.write(f"\n[Paso {step:3d}/{max_steps}] Train Loss: {cur_loss:.4f} | Comp Score: {val_res['composite_score']:.4f}")
                    pbar.write(f"  -> 1d:  Hit={val_res['hit_1d']:5.1f}% | Rank IC={val_res['rank_ic_1d']:+.4f} | RMSE={val_res['rmse_1d']:.4f}")
                    pbar.write(f"  -> 5d:  Hit={val_res['hit_5d']:5.1f}% | Rank IC={val_res['rank_ic_5d']:+.4f} | RMSE={val_res['rmse_5d']:.4f}")
                    pbar.write(f"  -> 20d: Hit={val_res['hit_20d']:5.1f}% | Rank IC={val_res['rank_ic_20d']:+.4f} | RMSE={val_res['rmse_20d']:.4f}")
                    sys.stdout.flush()
                    
                    # Guardar en CSV
                    entry = {
                        'step': step, 'train_loss': cur_loss,
                        'val_composite': val_res['composite_score'],
                        'hit_1d': val_res['hit_1d'], 'rank_ic_1d': val_res['rank_ic_1d'], 'rmse_1d': val_res['rmse_1d'],
                        'hit_5d': val_res['hit_5d'], 'rank_ic_5d': val_res['rank_ic_5d'], 'rmse_5d': val_res['rmse_5d'],
                        'hit_20d': val_res['hit_20d'], 'rank_ic_20d': val_res['rank_ic_20d'], 'rmse_20d': val_res['rmse_20d']
                    }
                    pd.DataFrame([entry]).to_csv(history_file, mode='a', header=not os.path.exists(history_file), index=False)
                    
                    if val_res['composite_score'] < best_composite:
                        best_composite = val_res['composite_score']
                        cpu_sd = get_trainable_state_dict(model)
                        torch.save({
                            'step': step,
                            'model_state_dict': cpu_sd,
                            'val_metrics': val_res,
                            'model_cfg': model_cfg
                        }, best_ckpt_path)
                        del cpu_sd
                        pbar.write(f"  *** ¡Mejor modelo multi-horizonte guardado en {best_ckpt_path}! ***")
                        sys.stdout.flush()

    pbar.close()
    dt = time.time() - t_start
    print(f"\n[5/5] Entrenamiento finalizado con éxito en {dt/60:.1f} minutos.")
    print(f"Mejor Checkpoint: {best_ckpt_path} (Composite Score: {best_composite:.4f})")
    set_windows_keep_awake(False)

if __name__ == '__main__':
    main()
