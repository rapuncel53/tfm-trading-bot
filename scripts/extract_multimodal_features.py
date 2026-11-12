"""Extractor de características multimodales: Factores Cuantitativos (x_f) y Embeddings LLM (x_n).

Guarda un dataset unificado en disco (checkpoints/multimodal/features.pt) para permitir el entrenamiento
y comparación ultra-rápida de todas las arquitecturas de fusión y mixture de RAM AI (Nov 2025).
"""

import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import argparse
import time
import math
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import torch
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from src.config import ModelConfig, DataConfig
from src.dataset import StockReturnNewsDataset
from src.model import LLMReturnRegressor


def extract_quantitative_factors(df: pd.DataFrame, scaler=None):
    """Extrae y normaliza los 14 factores cuantitativos de balances y mercado."""
    factors = []
    
    # 1. log_revenue
    rev = pd.to_numeric(df.get('revenue', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.log1p(np.maximum(0.0, rev.values)))
    
    # 2. rev_growth_yoy (winsorizado)
    rev_g = pd.to_numeric(df.get('rev_growth_yoy', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(rev_g.values, -2.0, 5.0))
    
    # 3. log_net_income
    net_inc = pd.to_numeric(df.get('net_income', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.sign(net_inc.values) * np.log1p(np.abs(net_inc.values)))
    
    # 4. net_margin
    net_m = pd.to_numeric(df.get('net_margin', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(net_m.values, -1.0, 1.0))
    
    # 5. operating_margin
    op_m = pd.to_numeric(df.get('operating_margin', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(op_m.values, -1.0, 1.0))
    
    # 6. eps_diluted
    eps = pd.to_numeric(df.get('eps_diluted', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(eps.values, -20.0, 20.0))
    
    # 7. eps_growth_yoy
    eps_g = pd.to_numeric(df.get('eps_growth_yoy', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(eps_g.values, -5.0, 5.0))
    
    # 8. roe
    roe = pd.to_numeric(df.get('roe', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(roe.values, -2.0, 2.0))
    
    # 9. vol_20d (volatilidad a 20 días)
    vol = pd.to_numeric(df.get('vol_20d', 0.3), errors='coerce').fillna(0.3)
    factors.append(np.clip(vol.values, 0.01, 2.0))
    
    # 10. log_volume
    volume = pd.to_numeric(df.get('volume', 1e6), errors='coerce').fillna(1e6)
    factors.append(np.log1p(np.maximum(0.0, volume.values)))
    
    # 11. log_close
    close = pd.to_numeric(df.get('close', 50.0), errors='coerce').fillna(50.0)
    factors.append(np.log1p(np.maximum(1.0, close.values)))
    
    # 12. ret_1d (lagged price momentum)
    r1 = pd.to_numeric(df.get('ret_1d', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(r1.values, -0.3, 0.3))
    
    # 13. ret_3d (momentum 3 días)
    r3 = pd.to_numeric(df.get('ret_3d', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(r3.values, -0.5, 0.5))
    
    # 14. ret_5d (momentum 5 días)
    r5 = pd.to_numeric(df.get('ret_5d', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(r5.values, -0.5, 0.5))
    
    X = np.stack(factors, axis=1).astype(np.float32)
    names = [
        'log_revenue', 'rev_growth_yoy', 'log_net_income', 'net_margin', 
        'operating_margin', 'eps_diluted', 'eps_growth_yoy', 'roe', 
        'vol_20d', 'log_volume', 'log_close', 'ret_1d_lag', 'ret_3d_lag', 'ret_5d_lag'
    ]
    
    if scaler is None:
        mean = np.mean(X, axis=0)
        std = np.std(X, axis=0)
        std[std < 1e-6] = 1.0
        scaler = {'mean': mean, 'std': std}
        
    X_norm = (X - scaler['mean']) / scaler['std']
    return X_norm, names, scaler


def extract_split_features(split_name: str, parquet_path: str, model: LLMReturnRegressor, 
                           tokenizer, device: torch.device, num_samples: int, 
                           batch_size: int, scaler=None):
    """Extrae x_f, x_n y targets para un split específico."""
    print(f"\n[Extrayendo] Split: {split_name.upper()} desde {parquet_path} (límite: {num_samples} muestras)...")
    
    # 1. Cargar dataset con pq para evitar bugs de pyarrow
    tbl = pq.read_table(parquet_path)
    df_full = tbl.to_pandas()
    if 'has_news' in df_full.columns:
        df_full = df_full[df_full['has_news']].copy()
    df_full = df_full.dropna(subset=['ret_1d']).reset_index(drop=True)
    
    if num_samples > 0 and len(df_full) > num_samples:
        df_subset = df_full.head(num_samples).copy()
    else:
        df_subset = df_full.copy()
        
    print(f"[Dataset] {len(df_subset):,} muestras seleccionadas para {split_name.upper()}. Fechas: {df_subset['date'].min()} a {df_subset['date'].max()}")
    
    # 2. Factores Cuantitativos
    X_f, factor_names, scaler = extract_quantitative_factors(df_subset, scaler=scaler)
    
    # 3. Dataset y Dataloader para LLM
    dataset = StockReturnNewsDataset(
        parquet_path=parquet_path,
        tokenizer=tokenizer,
        max_length=2048,
        target_col='ret_1d',
        filter_news_only=True
    )
    # Limitar dataset a las muestras de df_subset
    dataset.data = df_subset
    
    def collate_fn(batch):
        input_ids_list = [item['input_ids'] for item in batch]
        attention_mask_list = [item['attention_mask'] for item in batch]
        max_len = max(len(ids) for ids in input_ids_list)
        aligned_len = ((max_len + 15) // 16) * 16
        padded_ids, padded_mask = [], []
        pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0
        for ids, mask in zip(input_ids_list, attention_mask_list):
            p = aligned_len - len(ids)
            if p > 0:
                padded_ids.append(torch.cat([ids, torch.full((p,), pad_id, dtype=ids.dtype)]))
                padded_mask.append(torch.cat([mask, torch.zeros(p, dtype=mask.dtype)]))
            else:
                padded_ids.append(ids)
                padded_mask.append(mask)
        return {
            'input_ids': torch.stack(padded_ids, dim=0),
            'attention_mask': torch.stack(padded_mask, dim=0),
            'targets': torch.tensor([item['target'] for item in batch], dtype=torch.float32),
            'tickers': [item['ticker'] for item in batch],
            'dates': [item['date'] for item in batch]
        }
        
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)
    
    all_xn = []
    all_pred_llm = []
    all_targets = []
    all_tickers = []
    all_dates = []
    
    pbar = tqdm(loader, desc=f"Inferencia LLM ({split_name})", dynamic_ncols=True)
    with torch.inference_mode():
        for batch in pbar:
            ids = batch['input_ids'].to(device)
            mask = batch['attention_mask'].to(device)
            targs = batch['targets'].to(device)
            
            outputs = model(ids, mask, targets=targs)
            
            emb = outputs['pooled_embeddings'].cpu()  # [batch, 4096]
            preds = outputs['preds'].cpu()            # [batch]
            
            all_xn.append(emb)
            all_pred_llm.append(preds)
            all_targets.append(batch['targets'])
            all_tickers.extend(batch['tickers'])
            all_dates.extend(batch['dates'])
            
            del outputs, emb, preds, ids, mask, targs
            
    torch.cuda.empty_cache()
    
    tensor_xn = torch.cat(all_xn, dim=0).float()
    tensor_xf = torch.tensor(X_f, dtype=torch.float32)
    tensor_pred_llm = torch.cat(all_pred_llm, dim=0).float()
    tensor_targets = torch.cat(all_targets, dim=0).float()
    
    return {
        'x_f': tensor_xf,
        'x_n': tensor_xn,
        'pred_llm': tensor_pred_llm,
        'targets': tensor_targets,
        'tickers': all_tickers,
        'dates': all_dates,
        'factor_names': factor_names
    }, scaler


def main():
    parser = argparse.ArgumentParser(description="Extracción de características multimodales para RAM AI")
    parser.add_argument("--checkpoint", type=str, default="checkpoints/llm_return_regressor/best_model.pt")
    parser.add_argument("--output_file", type=str, default="checkpoints/multimodal/features.pt")
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--train_samples", type=int, default=800)
    parser.add_argument("--val_samples", type=int, default=300)
    parser.add_argument("--test_samples", type=int, default=300)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Extractor] Dispositivo: {device}")

    # 1. Cargar Tokenizer y Modelo
    model_cfg = ModelConfig()
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_cfg.model_name_or_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"[Extractor] Cargando modelo base con QLoRA...")
    model = LLMReturnRegressor(model_cfg)
    
    if os.path.exists(args.checkpoint):
        print(f"[Extractor] Cargando pesos entrenados desde {args.checkpoint}...")
        ckpt = torch.load(args.checkpoint, map_location='cpu', weights_only=False)
        sd = ckpt['model_state_dict'] if isinstance(ckpt, dict) and 'model_state_dict' in ckpt else ckpt
        model.load_state_dict(sd, strict=False)
        del ckpt, sd
        torch.cuda.empty_cache()
        print("[Extractor] Checkpoint cargado con éxito.")
        
    model.eval()

    # 2. Extracción secuencial Train -> Val -> Test
    data_cfg = DataConfig()
    
    # Train primero para calcular scaler de factores
    train_data, scaler = extract_split_features(
        'train', data_cfg.train_path, model, tokenizer, device,
        num_samples=args.train_samples, batch_size=args.batch_size, scaler=None
    )
    
    val_data, _ = extract_split_features(
        'val', data_cfg.val_path, model, tokenizer, device,
        num_samples=args.val_samples, batch_size=args.batch_size, scaler=scaler
    )
    
    test_data, _ = extract_split_features(
        'test', data_cfg.test_path, model, tokenizer, device,
        num_samples=args.test_samples, batch_size=args.batch_size, scaler=scaler
    )

    # 3. Guardar en disco
    bundle = {
        'train': train_data,
        'val': val_data,
        'test': test_data,
        'factor_names': train_data['factor_names'],
        'scaler': scaler
    }
    torch.save(bundle, args.output_file)
    print(f"\n[Completado] Características multimodales guardadas exitosamente en: {args.output_file}")
    print(f"Dimensiones de matrices:")
    print(f"  Train: x_f={train_data['x_f'].shape}, x_n={train_data['x_n'].shape}, targets={train_data['targets'].shape}")
    print(f"  Val:   x_f={val_data['x_f'].shape}, x_n={val_data['x_n'].shape}, targets={val_data['targets'].shape}")
    print(f"  Test:  x_f={test_data['x_f'].shape}, x_n={test_data['x_n'].shape}, targets={test_data['targets'].shape}")


if __name__ == "__main__":
    main()
