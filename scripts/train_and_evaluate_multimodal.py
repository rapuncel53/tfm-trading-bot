"""Entrenamiento y Evaluación Comparativa Multimodal (RAM Active Investments Nov 2025).

Compara sobre el conjunto de Test (2021-2023) y Validación (2019-2020):
1. Universe (Equally Weighted Benchmark)
2. Factors Alone
3. News Alone (LLM Qwen3.5-9B)
4. FININ (Wang et al., 2024)
5. Fusion Combination (Ecuación 3)
6. Fusion Summation (Ecuación 4)
7. Fusion Attention (Ecuaciones 5-6)
8. Mixture Conventional (Ecuación 9)
9. Mixture Decoupled (Ecuaciones 12-15)

Genera la tabla comparativa oficial idéntica a la Tabla 1 de RAM AI y gráficos de cartera.
"""

import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import argparse
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from src.multimodal_models import (
    FactorsAlone, NewsAlone, FusionCombination, FusionSummation,
    FusionAttention, FININ, MixtureModel
)


def compute_metrics(y_pred: np.ndarray, y_true: np.ndarray) -> dict:
    """Calcula todas las métricas cuantitativas y estadísticas."""
    err = y_pred - y_true
    mse = float(np.mean(err ** 2))
    rmse = float(np.sqrt(mse))
    mae = float(np.mean(np.abs(err)))
    
    # MAPE con regularización numérica
    mape = float(np.mean(np.abs(err) / (np.abs(y_true) + 0.05)))
    
    # Correlaciones
    sp_corr, _ = spearmanr(y_pred, y_true)
    pr_corr, _ = pearsonr(y_pred, y_true)
    sp_corr = 0.0 if np.isnan(sp_corr) else float(sp_corr)
    pr_corr = 0.0 if np.isnan(pr_corr) else float(pr_corr)
    
    # Hit Ratio Direccional
    valid = y_true != 0
    if valid.sum() > 0:
        hit = float(np.mean(np.sign(y_pred[valid]) == np.sign(y_true[valid])))
    else:
        hit = 0.5
        
    # Análisis por Deciles (D0 a D9)
    # Si hay empates, pd.qcut con rank
    ranks = pd.Series(y_pred).rank(method='first')
    deciles = pd.qcut(ranks, q=10, labels=False)
    
    dec_df = pd.DataFrame({'pred': y_pred, 'target': y_true, 'decile': deciles})
    dec_means = dec_df.groupby('decile')['target'].mean().to_dict()
    
    # Retornos de cartera (en porcentaje)
    d0_ret = float(dec_means.get(0, 0.0)) * 100
    d9_ret = float(dec_means.get(9, 0.0)) * 100
    ls_spread = d9_ret - d0_ret
    
    # Simulación simple de Sharpe Ratio anualizado (asumiendo rebalanceos diarios/mensuales)
    # Long-only: retornos de las acciones en D9
    d9_returns = dec_df[dec_df['decile'] == 9]['target'].values
    d0_returns = dec_df[dec_df['decile'] == 0]['target'].values
    ls_returns = d9_returns - d0_returns[:len(d9_returns)] if len(d0_returns) == len(d9_returns) else d9_returns
    
    lo_mean = np.mean(d9_returns) * 252 * 100
    lo_vol = (np.std(d9_returns) * np.sqrt(252) * 100) + 1e-6
    lo_sharpe = float(lo_mean / lo_vol)
    
    ls_mean = np.mean(ls_returns) * 252 * 100
    ls_vol = (np.std(ls_returns) * np.sqrt(252) * 100) + 1e-6
    ls_sharpe = float(ls_mean / ls_vol)
    
    return {
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'mape': mape,
        'rank_ic': sp_corr,
        'pearson': pr_corr,
        'hit_ratio': hit * 100,
        'd0_return': d0_ret,
        'd9_return': d9_ret,
        'ls_spread': ls_spread,
        'lo_return_ann': lo_mean,
        'lo_sharpe': lo_sharpe,
        'ls_return_ann': ls_mean,
        'ls_sharpe': ls_sharpe,
        'decile_returns': dec_means
    }


def train_model(model: nn.Module, train_loader: DataLoader, 
                val_xf: torch.Tensor, val_xn: torch.Tensor, val_y: torch.Tensor,
                device: torch.device, epochs: int = 40, lr: float = 1e-3, 
                is_mixture_decoupled: bool = False, is_mixture_conv: bool = False) -> nn.Module:
    """Bucle de entrenamiento ágil para modelos de fusión y mixture."""
    model = model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    best_loss = float('inf')
    best_weights = None
    
    for epoch in range(epochs):
        model.train()
        for batch_xf, batch_xn, batch_y in train_loader:
            batch_xf = batch_xf.to(device)
            batch_xn = batch_xn.to(device)
            batch_y = batch_y.to(device)
            
            optimizer.zero_grad()
            
            if is_mixture_decoupled:
                loss_dict = model.compute_decoupled_loss(batch_xf, batch_xn, batch_y, lambda_kl=1.0)
                loss = loss_dict['loss_total']
            elif is_mixture_conv:
                outputs = model(batch_xf, batch_xn)
                loss = nn.functional.mse_loss(outputs['pred_mix'], batch_y)
            else:
                if isinstance(model, FactorsAlone):
                    preds = model(batch_xf)
                elif isinstance(model, NewsAlone):
                    preds = model(batch_xn)
                elif isinstance(model, FusionAttention):
                    preds, _ = model(batch_xf, batch_xn)
                else:
                    preds = model(batch_xf, batch_xn)
                loss = nn.functional.mse_loss(preds, batch_y)
                
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
        # Validación
        model.eval()
        with torch.no_grad():
            v_xf = val_xf.to(device)
            v_xn = val_xn.to(device)
            v_y = val_y.to(device)
            if is_mixture_decoupled or is_mixture_conv:
                v_preds = model(v_xf, v_xn)['pred_mix']
            elif isinstance(model, FactorsAlone):
                v_preds = model(v_xf)
            elif isinstance(model, NewsAlone):
                v_preds = model(v_xn)
            elif isinstance(model, FusionAttention):
                v_preds, _ = model(v_xf, v_xn)
            else:
                v_preds = model(v_xf, v_xn)
            val_loss = float(nn.functional.mse_loss(v_preds, v_y))
            
        if val_loss < best_loss:
            best_loss = val_loss
            best_weights = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            
    if best_weights is not None:
        model.load_state_dict(best_weights)
    return model


def main():
    parser = argparse.ArgumentParser(description="Entrenamiento y Evaluación Multimodal RAM AI")
    parser.add_argument("--features_path", type=str, default="checkpoints/multimodal/features.pt")
    parser.add_argument("--output_dir", type=str, default="checkpoints/multimodal")
    parser.add_argument("--epochs", type=int, default=45)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--batch_size", type=int, default=32)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Multimodal] Usando dispositivo: {device}")

    # 1. Cargar Features Precalculadas
    if not os.path.exists(args.features_path):
        print(f"[Error] No se encontró el bundle de features en {args.features_path}. Ejecuta primero extract_multimodal_features.py")
        sys.exit(1)

    print(f"[Multimodal] Cargando bundle de características desde {args.features_path}...")
    bundle = torch.load(args.features_path, map_location='cpu', weights_only=False)
    
    train_data = bundle['train']
    val_data = bundle['val']
    test_data = bundle['test']
    factor_names = bundle['factor_names']
    num_factors = len(factor_names)
    news_dim = train_data['x_n'].shape[1]
    
    print(f"[Multimodal] Factores cuantitativos: {num_factors} ({factor_names[:4]}...)")
    print(f"[Multimodal] Dimensión de noticias LLM: {news_dim}")
    print(f"[Multimodal] Muestras: Train={len(train_data['targets'])}, Val={len(val_data['targets'])}, Test={len(test_data['targets'])}")

    # 2. Preparar DataLoaders
    train_ds = TensorDataset(train_data['x_f'], train_data['x_n'], train_data['targets'])
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)

    # 3. Diccionario de Modelos a Entrenar
    models = {
        'Factors Alone': FactorsAlone(num_factors=num_factors, hidden_dim=64),
        'News Alone': NewsAlone(news_dim=news_dim),
        'FININ': FININ(num_factors=num_factors, news_dim=news_dim, proj_dim=128),
        'Fusion Combination': FusionCombination(num_factors=num_factors, news_dim=news_dim, bottleneck_dim=256, fusion_dim=128),
        'Fusion Summation': FusionSummation(num_factors=num_factors, news_dim=news_dim, proj_dim=128),
        'Fusion Attention': FusionAttention(num_factors=num_factors, news_dim=news_dim, proj_dim=128),
        'Mixture Conventional': MixtureModel(num_factors=num_factors, news_dim=news_dim, bottleneck_dim=256, fusion_dim=128),
        'Mixture Decoupled': MixtureModel(num_factors=num_factors, news_dim=news_dim, bottleneck_dim=256, fusion_dim=128, temperature=1.0)
    }

    results_val = {}
    results_test = {}
    all_predictions_test = {
        'ticker': test_data['tickers'],
        'date': test_data['dates'],
        'actual_return': test_data['targets'].numpy()
    }

    # Benchmark: Universe (Equally Weighted)
    u_val_pred = np.zeros_like(val_data['targets'].numpy())
    u_test_pred = np.zeros_like(test_data['targets'].numpy())
    results_val['Universe (Equally-Weighted)'] = compute_metrics(u_val_pred, val_data['targets'].numpy())
    results_test['Universe (Equally-Weighted)'] = compute_metrics(u_test_pred, test_data['targets'].numpy())

    # También registrar la predicción original directa del LLM (Paper 1)
    llm_val_pred = val_data['pred_llm'].numpy()
    llm_test_pred = test_data['pred_llm'].numpy()
    results_val['News-Only LLM (Paper 1)'] = compute_metrics(llm_val_pred, val_data['targets'].numpy())
    results_test['News-Only LLM (Paper 1)'] = compute_metrics(llm_test_pred, test_data['targets'].numpy())
    all_predictions_test['News_Only_LLM'] = llm_test_pred

    print("\n" + "="*80)
    print("           ENTRENANDO Y EVALUANDO ARQUITECTURAS MULTIMODALES          ")
    print("="*80)

    for name, model in models.items():
        print(f"\n[Entrenando] Modelo: {name}...")
        is_mix_dec = (name == 'Mixture Decoupled')
        is_mix_conv = (name == 'Mixture Conventional')
        
        trained_model = train_model(
            model, train_loader, 
            val_data['x_f'], val_data['x_n'], val_data['targets'],
            device=device, epochs=args.epochs, lr=args.lr,
            is_mixture_decoupled=is_mix_dec, is_mixture_conv=is_mix_conv
        )
        
        # Inferencia en Val y Test
        trained_model.eval()
        with torch.no_grad():
            # Validación
            v_xf = val_data['x_f'].to(device)
            v_xn = val_data['x_n'].to(device)
            if is_mix_dec or is_mix_conv:
                v_p = trained_model(v_xf, v_xn)['pred_mix'].cpu().numpy()
            elif isinstance(trained_model, FactorsAlone):
                v_p = trained_model(v_xf).cpu().numpy()
            elif isinstance(trained_model, NewsAlone):
                v_p = trained_model(v_xn).cpu().numpy()
            elif isinstance(trained_model, FusionAttention):
                v_p, _ = trained_model(v_xf, v_xn)
                v_p = v_p.cpu().numpy()
            else:
                v_p = trained_model(v_xf, v_xn).cpu().numpy()
                
            # Test
            t_xf = test_data['x_f'].to(device)
            t_xn = test_data['x_n'].to(device)
            if is_mix_dec or is_mix_conv:
                out_test = trained_model(t_xf, t_xn)
                t_p = out_test['pred_mix'].cpu().numpy()
                if is_mix_dec:
                    p_f_mean = float(out_test['p_f'].mean())
                    p_u_mean = float(out_test['p_u'].mean())
                    print(f"  [Gating Decoupled] P(Factors)={p_f_mean:.3f}, P(Fusion)={p_u_mean:.3f}")
            elif isinstance(trained_model, FactorsAlone):
                t_p = trained_model(t_xf).cpu().numpy()
            elif isinstance(trained_model, NewsAlone):
                t_p = trained_model(t_xn).cpu().numpy()
            elif isinstance(trained_model, FusionAttention):
                t_p, _ = trained_model(t_xf, t_xn)
                t_p = t_p.cpu().numpy()
            else:
                t_p = trained_model(t_xf, t_xn).cpu().numpy()

        results_val[name] = compute_metrics(v_p, val_data['targets'].numpy())
        results_test[name] = compute_metrics(t_p, test_data['targets'].numpy())
        all_predictions_test[name.replace(' ', '_')] = t_p
        
        print(f"  -> Test RMSE: {results_test[name]['rmse']*100:.2f}% | Rank IC: {results_test[name]['rank_ic']:+.4f} | Hit: {results_test[name]['hit_ratio']:.2f}% | L/S Spread: {results_test[name]['ls_spread']:+.2f}%")

    # Guardar CSV de predicciones
    pred_df = pd.DataFrame(all_predictions_test)
    csv_path = os.path.join(args.output_dir, "test_predictions_multimodal.csv")
    pred_df.to_csv(csv_path, index=False)
    print(f"\n[Guardado] Predicciones de test guardadas en: {csv_path}")

    # =========================================================================
    # TABLA COMPARATIVA OFICIAL ESTILO RAM ACTIVE INVESTMENTS
    # =========================================================================
    print("\n" + "="*110)
    print("            TABLA 1: COMPARATIVA DE ESTRATEGIAS DE CARTERA Y PREDICCIÓN (TEST SET 2021-2023)           ")
    print("="*110)
    header = f"{'Modelo':<24} | {'Long-Only Ret%':<14} {'LO Sharpe':<10} | {'Long-Short Ret%':<15} {'LS Sharpe':<10} | {'Rank IC':<9} {'Hit Ratio%':<10} {'RMSE%':<7}"
    print(header)
    print("-" * 110)
    
    rows = []
    for model_name, m in results_test.items():
        line = f"{model_name:<24} | {m['lo_return_ann']:>12.2f}% {m['lo_sharpe']:>9.2f}  | {m['ls_return_ann']:>13.2f}% {m['ls_sharpe']:>9.2f}  | {m['rank_ic']:>+8.4f} {m['hit_ratio']:>9.2f}% {m['rmse']*100:>6.2f}%"
        print(line)
        rows.append({
            'Model': model_name,
            'LO_Ann_Return': m['lo_return_ann'],
            'LO_Sharpe': m['lo_sharpe'],
            'LS_Ann_Return': m['ls_ann_return'] if 'ls_ann_return' in m else m['ls_return_ann'],
            'LS_Sharpe': m['ls_sharpe'],
            'Rank_IC': m['rank_ic'],
            'Hit_Ratio': m['hit_ratio'],
            'RMSE_pct': m['rmse'] * 100,
            'MAE_pct': m['mae'] * 100,
            'D0_Return': m['d0_return'],
            'D9_Return': m['d9_return'],
            'LS_Spread': m['ls_spread']
        })
    print("="*110)

    # =========================================================================
    # GENERACIÓN DE GRÁFICOS OFICIALES PARA LA MEMORIA
    # =========================================================================
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # Gráfico 1: Monotonía por Deciles (Figure 6 / 9 / 15 del Paper)
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    decile_indices = np.arange(10)
    bar_width = 0.18
    
    selected_models = ['Factors Alone', 'News Alone', 'Fusion Combination', 'Mixture Decoupled']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, mod in enumerate(selected_models):
        if mod in results_test:
            rets = [results_test[mod]['decile_returns'].get(d, 0.0) * 100 for d in range(10)]
            offset = (i - 1.5) * bar_width
            ax.bar(decile_indices + offset, rets, width=bar_width, label=mod, color=colors[i], alpha=0.9)
            
    ax.set_title("Rendimiento por Deciles de Cartera en Test Set (2021–2023) — Réplica RAM AI", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Decil de Pronóstico ($D_0$ = Cartera Corta / Venta, $D_9$ = Cartera Larga / Compra)", fontsize=12)
    ax.set_ylabel("Retorno Promedio Realizado (%)", fontsize=12)
    ax.set_xticks(decile_indices)
    ax.set_xticklabels([f"D{d}" for d in range(10)])
    ax.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.7)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=11)
    
    chart_path1 = os.path.join(args.output_dir, "multimodal_decile_returns_comparison.png")
    plt.tight_layout()
    plt.savefig(chart_path1)
    plt.close()
    print(f"[Gráfico 1] Guardado en: {chart_path1}")

    # Gráfico 2: Comparativa de Sharpe Ratio Long-Short
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    mod_names = [m for m in results_test.keys() if m != 'Universe (Equally-Weighted)']
    sharpes = [results_test[m]['ls_sharpe'] for m in mod_names]
    bar_colors = ['#2b5c8f' if 'Mixture' in m else ('#2ca02c' if 'Fusion' in m else '#888888') for m in mod_names]
    
    bars = ax.barh(mod_names, sharpes, color=bar_colors, height=0.6, alpha=0.85)
    ax.set_title("Sharpe Ratio de la Estrategia Long/Short ($D_9 - D_0$) en Test — Réplica RAM AI", fontsize=13, fontweight='bold')
    ax.set_xlabel("Sharpe Ratio Anualizado", fontsize=11)
    ax.axvline(0, color='black', linestyle='--', linewidth=0.8)
    
    for bar in bars:
        w = bar.get_width()
        ax.text(w + (0.05 if w >= 0 else -0.15), bar.get_y() + bar.get_height()/2, f"{w:.2f}", va='center', ha='left' if w>=0 else 'right', fontsize=9, fontweight='bold')
        
    chart_path2 = os.path.join(args.output_dir, "multimodal_long_short_sharpe_comparison.png")
    plt.tight_layout()
    plt.savefig(chart_path2)
    plt.close()
    print(f"[Gráfico 2] Guardado en: {chart_path2}")

    return results_test


if __name__ == "__main__":
    main()
