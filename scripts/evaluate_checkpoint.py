"""Script de Evaluación Detallada y Análisis de Predicciones del Checkpoint Entrenado.

Permite inspeccionar a fondo cómo predice el LLM sobre el conjunto de Validación (o Test),
calculando métricas cuantitativas, desglose por deciles, precisión direccional (Hit Ratio)
y casos prácticos individuales (Top Ganadores y Top Perdedores pronosticados).
"""

import os
import sys
sys.path.insert(0, '.')
import argparse
import math
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
from tqdm.auto import tqdm

import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from src.config import ModelConfig, DataConfig
from src.dataset import StockReturnNewsDataset
from src.model import LLMReturnRegressor
from src.metrics import PortfolioEvaluator
from src.train import make_collate_fn


def main():
    parser = argparse.ArgumentParser(description="Evaluación de Predicciones del LLM (TFM EMNLP 2024)")
    parser.add_argument("--checkpoint", type=str, default="checkpoints/llm_return_regressor/best_model.pt", help="Ruta al checkpoint")
    parser.add_argument("--split", type=str, default="val", choices=["val", "test", "train"], help="Split a evaluar")
    parser.add_argument("--samples", type=int, default=300, help="Número de muestras a evaluar (0 o None para todas)")
    parser.add_argument("--batch_size", type=int, default=2, help="Batch size de inferencia")
    parser.add_argument("--target", type=str, default="ret_1d", choices=["ret_1d", "ret_3d", "ret_5d"], help="Target evaluado")
    parser.add_argument("--output_csv", type=str, default="checkpoints/llm_return_regressor/val_predictions.csv", help="Ruta de guardado de predicciones")
    args = parser.parse_args()

    print("=================================================================")
    print("   TFM: EVALUACIÓN DETALLADA DE PREDICCIONES (CHECKPOINT LLM)")
    print("=================================================================")
    print(f"Checkpoint          : {args.checkpoint}")
    print(f"Split seleccionado  : {args.split.upper()}")
    print(f"Muestras a evaluar  : {args.samples if args.samples > 0 else 'TODO EL DATASET'}")
    print(f"Target de retorno   : {args.target}")
    print("-----------------------------------------------------------------")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Info] Dispositivo de inferencia: {device}")

    # 1. Configurar y Cargar Tokenizer
    model_cfg = ModelConfig(use_qlora=True)
    data_cfg = DataConfig(target_return=args.target)
    split_paths = {
        'val': data_cfg.val_path,
        'test': data_cfg.test_path,
        'train': data_cfg.train_path
    }
    split_file = split_paths[args.split]

    print(f"[Info] Cargando tokenizer para {model_cfg.model_name_or_path}...")
    tokenizer = AutoTokenizer.from_pretrained(model_cfg.model_name_or_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 2. Cargar Dataset
    print(f"[Info] Cargando datos desde {split_file}...")
    dataset = StockReturnNewsDataset(
        split_file,
        tokenizer=tokenizer,
        max_length=data_cfg.max_token_length,
        target_col=args.target,
        filter_news_only=True
    )

    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0
    collate = make_collate_fn(pad_id)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collate)

    # 3. Instanciar Modelo y Cargar Pesos Entrenados
    print(f"[Info] Inicializando arquitectura LLMReturnRegressor...")
    model = LLMReturnRegressor(model_cfg)

    if os.path.exists(args.checkpoint):
        print(f"[Info] Cargando pesos entrenados desde {args.checkpoint} (vía CPU)...")
        ckpt = torch.load(args.checkpoint, map_location='cpu', weights_only=False)
        sd = ckpt['model_state_dict'] if isinstance(ckpt, dict) and 'model_state_dict' in ckpt else ckpt
        incompatible = model.load_state_dict(sd, strict=False)
        del ckpt, sd
        torch.cuda.empty_cache()
        print(f"[Info] Checkpoint cargado con éxito. (Parámetros adaptados correctamente)")
    else:
        print(f"[Aviso] No se encontró el checkpoint en {args.checkpoint}. Se usará el modelo base sin fine-tuning.")

    model.eval()
    if hasattr(model.backbone, 'gradient_checkpointing_disable'):
        model.backbone.gradient_checkpointing_disable()

    # 4. Inferencia sobre el Dataset con guardado incremental
    os.makedirs(os.path.dirname(args.output_csv), exist_ok=True)
    records = []
    
    # Cargar registros previos si se desea reanudar
    if os.path.exists(args.output_csv) and os.path.getsize(args.output_csv) > 10:
        try:
            df_prev = pd.read_csv(args.output_csv)
            records = df_prev.to_dict('records')
            print(f"[Info] Reanudando desde {len(records)} predicciones ya guardadas en {args.output_csv}")
        except Exception:
            records = []

    already_done = len(records)
    total_eval = len(dataloader) if args.samples <= 0 else min(len(dataloader), math.ceil(args.samples / args.batch_size))
    pbar = tqdm(total=total_eval, initial=already_done // args.batch_size, desc=f"Evaluando {args.split.upper()}", dynamic_ncols=True)

    with torch.inference_mode():
        for i, batch in enumerate(dataloader):
            if (i + 1) * args.batch_size <= already_done:
                continue
            if args.samples > 0 and len(records) >= args.samples:
                break

            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            targets = batch['targets'].to(device)

            outputs = model(input_ids, attention_mask, targets=targets)
            preds = outputs['preds'].cpu().numpy()
            targs = targets.cpu().numpy()

            for idx_in_batch, (t, d, p, y) in enumerate(zip(batch['tickers'], batch['dates'], preds, targs)):
                # Recuperar titular y fundamentales originales del dataset
                original_row = dataset.data.iloc[len(records)]
                headlines = str(original_row.get('headlines_concat', ''))[:180]
                close_p = original_row.get('close', np.nan)
                eps = original_row.get('eps_diluted', np.nan)
                rev_g = original_row.get('rev_growth_yoy', np.nan)
                net_m = original_row.get('net_margin', np.nan)

                records.append({
                    'ticker': t,
                    'date': d,
                    'pred_return': float(p),
                    'actual_return': float(y),
                    'error': float(p - y),
                    'abs_error': abs(float(p - y)),
                    'pred_sign': 1 if p > 0 else (-1 if p < 0 else 0),
                    'actual_sign': 1 if y > 0 else (-1 if y < 0 else 0),
                    'close_price': close_p,
                    'eps': eps,
                    'rev_growth_yoy': rev_g,
                    'net_margin': net_m,
                    'headlines': headlines
                })

            del outputs, preds, targs, input_ids, attention_mask, targets
            pbar.update(1)
            # Guardado incremental a disco tras cada batch para evitar pérdidas si el PC se apaga
            pd.DataFrame(records).to_csv(args.output_csv, index=False)

            if args.samples > 0 and len(records) >= args.samples:
                break

    pbar.close()
    torch.cuda.empty_cache()

    df_res = pd.DataFrame(records)
    print(f"\n[Guardado] {len(df_res)} predicciones disponibles en: {args.output_csv}")

    # =========================================================================
    # 5. ANÁLISIS ESTADÍSTICO Y CUANTITATIVO
    # =========================================================================
    y_pred = df_res['pred_return'].values
    y_true = df_res['actual_return'].values

    # Errores estándar
    mse = np.mean((y_pred - y_true)**2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(y_pred - y_true))

    # Correlaciones
    spearman_corr, sp_pval = spearmanr(y_pred, y_true)
    pearson_corr, pr_pval = pearsonr(y_pred, y_true)

    # Precisión Direccional (Hit Ratio de Signo: ¿predice si sube o baja?)
    correct_direction = (df_res['pred_sign'] == df_res['actual_sign']) & (df_res['actual_sign'] != 0)
    total_directional = (df_res['actual_sign'] != 0).sum()
    hit_ratio = correct_direction.sum() / total_directional if total_directional > 0 else 0.0

    print("\n=================================================================")
    print("                RESUMEN DE RENDIMIENTO ESTADÍSTICO               ")
    print("=================================================================")
    print(f"Muestras Evaluadas         : {len(df_res):,}")
    print(f"Error Cuadrático Medio (MSE): {mse:.6f}")
    print(f"Error RMSE                 : {rmse*100:.3f}%")
    print(f"Error Absoluto Medio (MAE) : {mae*100:.3f}%")
    print("-----------------------------------------------------------------")
    print(f"Rank IC (Spearman rho)     : {spearman_corr:+.4f} (p-value: {sp_pval:.4e})")
    print(f"Correlación Lineal (Pearson): {pearson_corr:+.4f} (p-value: {pr_pval:.4e})")
    print(f"Precisión Direccional (Hit) : {hit_ratio*100:.2f}% (Acierto en predecir subida/bajada)")
    print("-----------------------------------------------------------------")

    # =========================================================================
    # 6. ANÁLISIS POR DECILES (FIGURA 3 DEL PAPER EMNLP 2024)
    # =========================================================================
    print("\n=================================================================")
    print("      DISTRIBUCIÓN POR DECILES DE PREDICCIÓN (EMNLP 2024)        ")
    print("=================================================================")
    evaluator = PortfolioEvaluator()
    eval_df = df_res.rename(columns={'pred_return': 'pred', 'actual_return': 'target'})
    portfolio_res = evaluator.evaluate_deciles(eval_df)

    print(f"{'Decil':<8}{'Nº Casos':<10}{'Ret. Predicho':<16}{'Ret. Real':<16}{'RMSE':<12}")
    print("-" * 62)
    # Crear deciles globales sobre las muestras
    df_res['decile'] = pd.qcut(df_res['pred_return'], q=min(10, len(df_res)), labels=False, duplicates='drop')
    for d in sorted(df_res['decile'].unique()):
        sub = df_res[df_res['decile'] == d]
        p_mean = sub['pred_return'].mean() * 100
        a_mean = sub['actual_return'].mean() * 100
        d_rmse = np.sqrt(np.mean((sub['pred_return'] - sub['actual_return'])**2)) * 100
        print(f"Decil {d:<2}  {len(sub):<10}{p_mean:>+8.3f}%        {a_mean:>+8.3f}%        {d_rmse:>6.3f}%")

    print("-----------------------------------------------------------------")
    print(f"Retorno Cartera Long-Only (Decil 9)  : {portfolio_res['long_only']['ann_return']*100:+.2f}% (Sharpe: {portfolio_res['long_only']['sharpe_ratio']:.2f})")
    print(f"Retorno Cartera Long-Short (D9 - D0) : {portfolio_res['long_short']['ann_return']*100:+.2f}% (Sharpe: {portfolio_res['long_short']['sharpe_ratio']:.2f})")
    print(f"Retorno Benchmark de Mercado         : {portfolio_res['benchmark']['ann_return']*100:+.2f}% (Sharpe: {portfolio_res['benchmark']['sharpe_ratio']:.2f})")

    # =========================================================================
    # 7. CASOS DE ESTUDIO INDIVIDUALES
    # =========================================================================
    print("\n=================================================================")
    print("     TOP 5 MAYORES SUBIDAS PRONOSTICADAS POR EL MODELO (LONG)    ")
    print("=================================================================")
    top_longs = df_res.sort_values(by='pred_return', ascending=False).head(5)
    for i, (_, r) in enumerate(top_longs.iterrows(), 1):
        clean_hl = str(r['headlines']).encode('ascii', 'replace').decode('ascii')
        print(f"{i}. [{r['ticker']} | {r['date']}] Precio: ${r['close_price']:.2f}")
        print(f"   Predicción LLM : {r['pred_return']*100:+.2f}% | Retorno Real: {r['actual_return']*100:+.2f}% (Error: {r['error']*100:+.2f}%)")
        print(f"   Titular noticia: \"{clean_hl}...\"\n")

    print("=================================================================")
    print("    TOP 5 MAYORES BAJADAS PRONOSTICADAS POR EL MODELO (SHORT)    ")
    print("=================================================================")
    top_shorts = df_res.sort_values(by='pred_return', ascending=True).head(5)
    for i, (_, r) in enumerate(top_shorts.iterrows(), 1):
        clean_hl = str(r['headlines']).encode('ascii', 'replace').decode('ascii')
        print(f"{i}. [{r['ticker']} | {r['date']}] Precio: ${r['close_price']:.2f}")
        print(f"   Predicción LLM : {r['pred_return']*100:+.2f}% | Retorno Real: {r['actual_return']*100:+.2f}% (Error: {r['error']*100:+.2f}%)")
        print(f"   Titular noticia: \"{clean_hl}...\"\n")


if __name__ == '__main__':
    main()
