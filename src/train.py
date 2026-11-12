"""Módulo de Entrenamiento y Validación para LLMReturnRegressor.

Implementa el bucle de optimización con LoRA + Gradient Accumulation + Early Stopping.
"""

import os
import sys
import time
import math
from typing import Optional, Dict, Any, Tuple

try:
    import torch
    from torch.utils.data import DataLoader
    from torch.optim import AdamW
    from transformers import AutoTokenizer, get_linear_schedule_with_warmup
    from tqdm.auto import tqdm
except ImportError:
    pass

import pandas as pd
import numpy as np

from src.config import ModelConfig, DataConfig, TrainingConfig
from src.dataset import StockReturnNewsDataset
from src.model import LLMReturnRegressor
from src.metrics import PortfolioEvaluator


import ctypes

def set_windows_keep_awake(enable: bool = True):
    """Evita que Windows entre en modo de suspensión durante entrenamientos largos en portátiles."""
    if sys.platform != 'win32':
        return
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_AWAYMODE_REQUIRED = 0x00000040
    try:
        if enable:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED)
            print("[Power] Prevención de suspensión de Windows activada durante el entrenamiento.", flush=True)
        else:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            print("[Power] Plan de energía estándar de Windows restaurado.", flush=True)
    except Exception:
        pass


def make_collate_fn(pad_token_id: int = 0):
    def collate_fn(batch):
        """Agrupa muestras del dataset en tensores de PyTorch con padding dinámico alineado a 16 tokens."""
        input_ids_list = [item['input_ids'] for item in batch]
        attention_mask_list = [item['attention_mask'] for item in batch]
        
        # Longitud máxima alineada a múltiplo de 16 (estabilidad CUBLAS y Tensor Cores en Ada/Blackwell)
        max_len = max(len(ids) for ids in input_ids_list)
        aligned_len = ((max_len + 15) // 16) * 16
        
        padded_input_ids = []
        padded_attention_mask = []
        for ids, mask in zip(input_ids_list, attention_mask_list):
            pad_len = aligned_len - len(ids)
            if pad_len > 0:
                padded_input_ids.append(torch.cat([ids, torch.full((pad_len,), pad_token_id, dtype=ids.dtype)]))
                padded_attention_mask.append(torch.cat([mask, torch.zeros(pad_len, dtype=mask.dtype)]))
            else:
                padded_input_ids.append(ids)
                padded_attention_mask.append(mask)
            
        input_ids = torch.stack(padded_input_ids, dim=0)
        attention_mask = torch.stack(padded_attention_mask, dim=0)
        
        targets = torch.tensor([item['target'] for item in batch], dtype=torch.float32)
        tickers = [item['ticker'] for item in batch]
        dates = [item['date'] for item in batch]
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'targets': targets,
            'tickers': tickers,
            'dates': dates
        }
    return collate_fn


def get_trainable_state_dict(model: torch.nn.Module) -> Dict[str, torch.Tensor]:
    """Extrae de forma limpia y ultra-rápida únicamente los parámetros entrenables (LoRA y forecasting_head) en CPU.
    Itera sobre model.named_parameters() filtrando p.requires_grad, garantizando que:
    1. Nunca se toque ni copie tensores 4-bit congelados (Params4bit) de bitsandbytes.
    2. Se eliminen de raíz los accesos indebidos de memoria en c10.dll (error APPCRASH 0xc0000005).
    3. El guardado tarde < 0.2 segundos (vs 20s de antes) y ocupe ~205 MB (vs 8.44 GB de antes).
    """
    return {name: param.detach().cpu().clone() for name, param in model.named_parameters() if param.requires_grad}


class StockReturnTrainer:
    """Entrenador del modelo de predicción de retornos."""

    def __init__(self, model_cfg: ModelConfig, data_cfg: DataConfig, train_cfg: TrainingConfig):
        self.model_cfg = model_cfg
        self.data_cfg = data_cfg
        self.train_cfg = train_cfg
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[Trainer] Dispositivo seleccionado: {self.device}")

        # 1. Cargar Tokenizer
        print(f"[Trainer] Cargando tokenizer para {model_cfg.model_name_or_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_cfg.model_name_or_path,
            trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # 2. Instanciar Modelo
        self.model = LLMReturnRegressor(model_cfg)
        self.evaluator = PortfolioEvaluator()

    def get_dataloaders(self) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """Crea DataLoaders para Train, Validation y Test."""
        tgt = self.data_cfg.target_returns if getattr(self.model_cfg, 'num_horizons', 1) > 1 else self.data_cfg.target_return
        train_ds = StockReturnNewsDataset(
            self.data_cfg.train_path,
            tokenizer=self.tokenizer,
            max_length=self.data_cfg.max_token_length,
            target_col=tgt,
            filter_news_only=self.data_cfg.filter_news_only
        )
        val_ds = StockReturnNewsDataset(
            self.data_cfg.val_path,
            tokenizer=self.tokenizer,
            max_length=self.data_cfg.max_token_length,
            target_col=tgt,
            filter_news_only=self.data_cfg.filter_news_only
        )
        test_ds = StockReturnNewsDataset(
            self.data_cfg.test_path,
            tokenizer=self.tokenizer,
            max_length=self.data_cfg.max_token_length,
            target_col=tgt,
            filter_news_only=self.data_cfg.filter_news_only
        )

        pad_id = self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else 0
        collate = make_collate_fn(pad_id)

        train_loader = DataLoader(train_ds, batch_size=self.train_cfg.batch_size, shuffle=True, collate_fn=collate)
        val_loader = DataLoader(val_ds, batch_size=self.train_cfg.batch_size, shuffle=False, collate_fn=collate)
        test_loader = DataLoader(test_ds, batch_size=self.train_cfg.batch_size, shuffle=False, collate_fn=collate)
        return train_loader, val_loader, test_loader

    def evaluate(self, dataloader: DataLoader, desc: str = "Validación", max_samples: Optional[int] = None) -> Dict[str, Any]:
        """Evalúa el modelo sobre un DataLoader calculando RMSE, Rank IC y métricas de cartera."""
        if max_samples is None:
            max_samples = self.train_cfg.eval_limit

        self.model.eval()
        records = []
        total_loss = 0.0

        max_batches = math.ceil(max_samples / self.train_cfg.batch_size) if max_samples else len(dataloader)
        eval_total = min(len(dataloader), max_batches)
        pbar = tqdm(total=eval_total, desc=f"  [Eval {desc}]", leave=False, dynamic_ncols=True)

        with torch.no_grad():
            for i, batch in enumerate(dataloader):
                if max_batches and i >= max_batches:
                    break

                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                targets = batch['targets'].to(self.device)

                outputs = self.model(input_ids, attention_mask, targets=targets)
                preds = outputs['preds'].cpu().numpy()
                targs = targets.cpu().numpy()
                total_loss += outputs['loss'].item() * len(targets)

                is_multi = preds.ndim > 1 and preds.shape[1] > 1
                if is_multi:
                    for t, d, p, y in zip(batch['tickers'], batch['dates'], preds, targs):
                        records.append({
                            'ticker': t, 'date': d,
                            'pred_1d': float(p[0]), 'target_1d': float(y[0]),
                            'pred_5d': float(p[1]), 'target_5d': float(y[1]),
                            'pred_20d': float(p[2]), 'target_20d': float(y[2]),
                            'pred': float(p[2]), 'target': float(y[2])
                        })
                else:
                    for t, d, p, y in zip(batch['tickers'], batch['dates'], preds, targs):
                        records.append({'ticker': t, 'date': d, 'pred': float(p), 'target': float(y)})

                del outputs, preds, targs, input_ids, attention_mask, targets
                pbar.update(1)
                if max_samples and len(records) >= max_samples:
                    break

        pbar.close()
        torch.cuda.empty_cache()
        df_eval = pd.DataFrame(records)
        metrics = self.evaluator.evaluate_deciles(df_eval)
        metrics['mse'] = total_loss / len(df_eval) if len(df_eval) > 0 else 0.0
        metrics['rmse'] = math.sqrt(metrics['mse'])

        if 'pred_1d' in df_eval.columns:
            from scipy.stats import spearmanr
            for h in ['1d', '5d', '20d']:
                p_col, t_col = f'pred_{h}', f'target_{h}'
                diff = df_eval[p_col] - df_eval[t_col]
                metrics[f'rmse_{h}'] = float(np.sqrt(np.mean(diff ** 2)))
                ric, _ = spearmanr(df_eval[p_col], df_eval[t_col])
                metrics[f'rank_ic_{h}'] = 0.0 if np.isnan(ric) else float(ric)
                hit = np.mean(np.sign(df_eval[p_col]) == np.sign(df_eval[t_col])) * 100.0
                metrics[f'hit_{h}'] = float(hit)
        return metrics

    def train(self):
        """Bucle principal de entrenamiento con LoRA, gradient accumulation y barra de progreso interactiva."""
        set_windows_keep_awake(True)
        train_start_time = time.time()
        try:
            train_loader, val_loader, test_loader = self.get_dataloaders()
            
            # Parámetros entrenables (LoRA + forecasting_head)
            trainable_params = [p for p in self.model.parameters() if p.requires_grad]
            optimizer = AdamW(trainable_params, lr=self.train_cfg.learning_rate, weight_decay=self.train_cfg.weight_decay)

            total_steps = (len(train_loader) // self.train_cfg.gradient_accumulation_steps) * self.train_cfg.epochs
            if self.train_cfg.max_steps is not None:
                total_steps = min(total_steps, self.train_cfg.max_steps)
            elif self.train_cfg.max_hours is not None:
                total_steps = int((self.train_cfg.max_hours * 3600) / 42.0)

            scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=self.train_cfg.warmup_steps, num_training_steps=total_steps)

            os.makedirs(self.train_cfg.output_dir, exist_ok=True)
            latest_ckpt_path = f"{self.train_cfg.output_dir}/latest_checkpoint.pt"
            best_model_path = f"{self.train_cfg.output_dir}/best_model.pt"
            history_file = f"{self.train_cfg.output_dir}/training_history.csv"

            step = 0
            best_val_rmse = float('inf')

            # Reanudación desde checkpoint si está habilitado (carga segura en CPU para no saturar VRAM)
            if self.train_cfg.resume:
                if os.path.exists(latest_ckpt_path):
                    print(f"[Trainer] Reanudando estado de entrenamiento completo desde {latest_ckpt_path}...", flush=True)
                    ckpt = torch.load(latest_ckpt_path, map_location='cpu', weights_only=False)
                    self.model.load_state_dict(ckpt['model_state_dict'], strict=False)
                    if 'optimizer_state_dict' in ckpt:
                        optimizer.load_state_dict(ckpt['optimizer_state_dict'])
                    step = ckpt.get('step', 0)
                    best_val_rmse = ckpt.get('best_val_rmse', float('inf'))
                    if os.path.exists(history_file):
                        try:
                            h_df = pd.read_csv(history_file)
                            if 'val_rmse' in h_df.columns and len(h_df) > 0:
                                best_val_rmse = min(best_val_rmse, float(h_df['val_rmse'].min()))
                        except Exception:
                            pass

                    # Asegurar initial_lr y regenerar scheduler si el nuevo total_steps extiende el entrenamiento
                    for group in optimizer.param_groups:
                        group.setdefault('initial_lr', self.train_cfg.learning_rate)
                    if self.train_cfg.max_hours is not None and self.train_cfg.max_steps is None:
                        total_steps = step + int((self.train_cfg.max_hours * 3600) / 42.0)
                    if total_steps > step:
                        scheduler = get_linear_schedule_with_warmup(
                            optimizer,
                            num_warmup_steps=max(1, int(self.train_cfg.warmup_steps * 0.1)),
                            num_training_steps=total_steps,
                            last_epoch=step - 1
                        )
                    elif 'scheduler_state_dict' in ckpt:
                        scheduler.load_state_dict(ckpt['scheduler_state_dict'])

                    del ckpt
                    torch.cuda.empty_cache()
                    cur_lr_res = scheduler.get_last_lr()[0] if scheduler.get_last_lr() else self.train_cfg.learning_rate
                    print(f"[Trainer] Reanudado exitosamente en el paso {step} (Best Val RMSE previo: {best_val_rmse:.4f}, LR activo: {cur_lr_res:.2e})", flush=True)
                elif os.path.exists(best_model_path):
                    print(f"[Trainer] Inicializando pesos del modelo desde {best_model_path} (vía CPU)...", flush=True)
                    sd = torch.load(best_model_path, map_location='cpu', weights_only=False)
                    self.model.load_state_dict(sd, strict=False)
                    del sd
                    torch.cuda.empty_cache()
                    if os.path.exists(history_file):
                        try:
                            h_df = pd.read_csv(history_file)
                            if 'val_rmse' in h_df.columns and len(h_df) > 0:
                                best_val_rmse = float(h_df['val_rmse'].min())
                        except Exception:
                            pass
                    print(f"[Trainer] Pesos inicializados con éxito en VRAM dedicada. Memoria liberada. Best Val RMSE de referencia: {best_val_rmse:.4f}", flush=True)

            print(f"[Trainer] Pasos totales de entrenamiento: {total_steps} ({self.train_cfg.epochs} épocas)", flush=True)
            if self.train_cfg.eval_limit:
                print(f"[Trainer] Límite de evaluación ágil activo: {self.train_cfg.eval_limit} muestras por validación", flush=True)

            self.model.train()
            optimizer.zero_grad()
            training_finished = False

            # Barra de progreso principal de entrenamiento
            pbar = tqdm(total=total_steps, initial=step, desc="[LoRA Training]", unit="paso", dynamic_ncols=True)

            for epoch in range(1, self.train_cfg.epochs + 1):
                if training_finished:
                    break
                t0 = time.time()
                epoch_loss = 0.0

                for i, batch in enumerate(train_loader):
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    targets = batch['targets'].to(self.device)

                    outputs = self.model(input_ids, attention_mask, targets=targets)
                    loss = outputs['loss'] / self.train_cfg.gradient_accumulation_steps
                    loss.backward()

                    epoch_loss += outputs['loss'].item()

                    if (i + 1) % self.train_cfg.gradient_accumulation_steps == 0 or (i + 1) == len(train_loader):
                        torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=1.0)
                        optimizer.step()
                        scheduler.step()
                        optimizer.zero_grad()
                        step += 1
                        pbar.update(1)

                        # Métricas de GPU y loss en tiempo real en la barra de progreso
                        cur_loss = outputs['loss'].item()
                        cur_lr = scheduler.get_last_lr()[0] if scheduler.get_last_lr() else self.train_cfg.learning_rate
                        vram_gb = torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0.0
                        elapsed_h = (time.time() - train_start_time) / 3600
                        pbar_data = {
                            'loss': f'{cur_loss:.5f}',
                            'lr': f'{cur_lr:.1e}',
                            'vram': f'{vram_gb:.1f}GB'
                        }
                        if self.train_cfg.max_hours is not None:
                            pbar_data['h'] = f'{elapsed_h:.2f}/{self.train_cfg.max_hours:.1f}'
                        pbar.set_postfix(pbar_data)

                        # Guardado de checkpoint periódico (en CPU para no consumir VRAM)
                        if step % self.train_cfg.save_steps == 0:
                            cpu_sd = get_trainable_state_dict(self.model)
                            torch.save({
                                'step': step,
                                'epoch': epoch,
                                'best_val_rmse': best_val_rmse,
                                'model_state_dict': cpu_sd,
                                'optimizer_state_dict': optimizer.state_dict(),
                                'scheduler_state_dict': scheduler.state_dict()
                            }, latest_ckpt_path)
                            del cpu_sd
                            torch.cuda.empty_cache()

                        # Validación periódica
                        if step % self.train_cfg.eval_steps == 0 or (self.train_cfg.max_steps and step >= self.train_cfg.max_steps):
                            val_metrics = self.evaluate(val_loader, desc=f"Paso {step}")
                            pbar.write(f"\n[Paso {step}/{total_steps}] Val RMSE: {val_metrics['rmse']:.4f} | Rank IC: {val_metrics['rank_ic']:+.4f} | Long-Only Sharpe: {val_metrics['long_only']['sharpe_ratio']:.2f}")
                            if 'rmse_1d' in val_metrics:
                                pbar.write(f"   [Multi-Horizonte] 1d: Hit={val_metrics['hit_1d']:.1f}% IC={val_metrics['rank_ic_1d']:+.4f} | 5d: Hit={val_metrics['hit_5d']:.1f}% IC={val_metrics['rank_ic_5d']:+.4f} | 20d: Hit={val_metrics['hit_20d']:.1f}% IC={val_metrics['rank_ic_20d']:+.4f}")
                            sys.stdout.flush()
                            
                            # Registrar en historial
                            log_entry = pd.DataFrame([{
                                'step': step,
                                'epoch': epoch,
                                'train_loss': cur_loss,
                                'val_rmse': val_metrics['rmse'],
                                'val_rank_ic': val_metrics['rank_ic'],
                                'val_sharpe': val_metrics['long_only']['sharpe_ratio'],
                                'lr': cur_lr,
                                'vram_gb': vram_gb
                            }])
                            log_entry.to_csv(history_file, mode='a', header=not os.path.exists(history_file), index=False)

                            if val_metrics['rmse'] < best_val_rmse:
                                best_val_rmse = val_metrics['rmse']
                                cpu_best_sd = get_trainable_state_dict(self.model)
                                torch.save(cpu_best_sd, best_model_path)
                                del cpu_best_sd
                                torch.cuda.empty_cache()

                            # Restaurar modo de entrenamiento y liberar VRAM residual de validación
                            self.model.train()
                            torch.cuda.empty_cache()

                        del outputs, loss, input_ids, attention_mask, targets

                        # Comprobación de límites de parada (por pasos o por horas)
                        reached_steps = self.train_cfg.max_steps is not None and step >= self.train_cfg.max_steps
                        reached_hours = self.train_cfg.max_hours is not None and (time.time() - train_start_time) >= self.train_cfg.max_hours * 3600
                        if reached_steps or reached_hours:
                            reason = f"max_steps ({self.train_cfg.max_steps})" if reached_steps else f"tiempo ({self.train_cfg.max_hours:.1f}h)"
                            pbar.write(f"\n[Trainer] Límite de {reason} alcanzado en el paso {step}. Guardando checkpoint final...")
                            cpu_sd = get_trainable_state_dict(self.model)
                            torch.save({
                                'step': step,
                                'epoch': epoch,
                                'best_val_rmse': best_val_rmse,
                                'model_state_dict': cpu_sd,
                                'optimizer_state_dict': optimizer.state_dict(),
                                'scheduler_state_dict': scheduler.state_dict()
                            }, latest_ckpt_path)
                            del cpu_sd
                            torch.cuda.empty_cache()
                            training_finished = True
                            break

                dt = time.time() - t0
                pbar.write(f"Época {epoch}/{self.train_cfg.epochs} completada en {dt:.1f}s | Train Loss: {epoch_loss/len(train_loader):.4f}")
                sys.stdout.flush()

            pbar.close()

            # Evaluación final en TEST (Out-of-sample)
            print("\n=== EVALUACIÓN FINAL EN TEST SET (OUT-OF-SAMPLE 2021-2023) ===", flush=True)
            test_metrics = self.evaluate(test_loader, desc="Test Out-of-Sample")
            print(f"  Test RMSE: {test_metrics['rmse']:.4f}", flush=True)
            print(f"  Test Rank IC (Spearman): {test_metrics['rank_ic']:+.4f} (ICIR: {test_metrics['icir']:.2f})", flush=True)
            print(f"  Long-Only Portfolio (Decil 9): Retorno Anualizado = {test_metrics['long_only']['ann_return']*100:.2f}%, Sharpe = {test_metrics['long_only']['sharpe_ratio']:.2f}", flush=True)
            print(f"  Long-Short Portfolio (Decil 9 - 0): Retorno Anualizado = {test_metrics['long_short']['ann_return']*100:.2f}%, Sharpe = {test_metrics['long_short']['sharpe_ratio']:.2f}", flush=True)
            print(f"  Benchmark Mercado (Equally-Weighted): Retorno Anualizado = {test_metrics['benchmark']['ann_return']*100:.2f}%, Sharpe = {test_metrics['benchmark']['sharpe_ratio']:.2f}", flush=True)
            return test_metrics
        finally:
            set_windows_keep_awake(False)


