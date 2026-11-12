"""Entrenamiento y Evaluación de la Opción A: Mejoras Cuantitativas de Tendencia y Horizonte.

Implementa:
1. Horizontes de inversión ampliados: ret_5d (1 semana) y ret_20d (1 mes, estándar RAM Active Investments).
2. Retorno ajustado por mercado (Market-Adjusted Excess Return: r_i - r_mkt).
3. Factores técnicos pasados estrictamente rezagados (mom_5d_past, mom_20d_past, dist_sma20) sin filtración temporal.
4. Función de pérdida direccional con penalización de signo y correlación de Pearson:
   L_dir = MSE + gamma * ReLU(-y_hat * y) - lambda * Pearson(y_hat, y)
5. Evaluación comparativa exhaustiva del Hit Ratio y Rank IC frente al horizonte diario anterior.
"""

import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import argparse
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
import pyarrow.parquet as pq

from src.multimodal_models import (
    FactorsAlone, NewsAlone, FusionCombination, MixtureModel
)


class DirectionalLoss(nn.Module):
    """Función de pérdida direccional que combina MSE, penalización de signo y correlación de Pearson.
    L = MSE + gamma * mean(ReLU(-y_hat * y)) - lambda * Pearson(y_hat, y)
    """
    def __init__(self, gamma: float = 2.0, lambda_corr: float = 0.5):
        super().__init__()
        self.gamma = gamma
        self.lambda_corr = lambda_corr

    def forward(self, y_pred: torch.Tensor, y_true: torch.Tensor) -> torch.Tensor:
        # 1. Error cuadrático medio base
        mse = F.mse_loss(y_pred, y_true)

        # 2. Penalización de signo: castiga severamente cuando pred y true tienen signos opuestos
        sign_penalty = torch.mean(F.relu(-y_pred * y_true))

        # 3. Correlación de Pearson suave en el batch
        vx = y_pred - torch.mean(y_pred)
        vy = y_true - torch.mean(y_true)
        denom = torch.sqrt(torch.sum(vx ** 2) + 1e-6) * torch.sqrt(torch.sum(vy ** 2) + 1e-6)
        pearson_loss = -torch.sum(vx * vy) / denom

        return mse + self.gamma * sign_penalty + self.lambda_corr * pearson_loss


def build_enhanced_factors_and_targets(split_name: str, dates_list: list, tickers_list: list, 
                                      scaler_dict: dict = None):
    """Construye factores técnicos estrictamente pasados y objetivos forward (5d, 20d, exceso)."""
    parquet_path = f"data/splits/{split_name}/daily_aligned.parquet"
    tbl = pq.read_table(parquet_path)
    df_all = tbl.to_pandas().sort_values(['ticker', 'date']).reset_index(drop=True)
    df_all['date_str'] = df_all['date'].astype(str).str[:10]

    # Objetivos forward
    df_all['ret_20d'] = df_all.groupby('ticker')['close'].shift(-20) / df_all['close'] - 1
    # Rellenar últimos días de ret_20d con ret_5d si no hay 20 sesiones completas
    df_all['ret_20d'] = df_all['ret_20d'].fillna(df_all['ret_5d'])

    # Retorno medio de mercado para cálculo de exceso (Alpha transversal)
    mkt_mean_1d = df_all.groupby('date_str')['ret_1d'].transform('mean')
    mkt_mean_5d = df_all.groupby('date_str')['ret_5d'].transform('mean')
    mkt_mean_20d = df_all.groupby('date_str')['ret_20d'].transform('mean')

    df_all['ret_1d_excess'] = df_all['ret_1d'] - mkt_mean_1d
    df_all['ret_5d_excess'] = df_all['ret_5d'] - mkt_mean_5d
    df_all['ret_20d_excess'] = df_all['ret_20d'] - mkt_mean_20d

    # Factores técnicos estrictamente pasados (backward-looking)
    df_all['mom_5d_past'] = df_all.groupby('ticker')['close'].pct_change(5).fillna(0.0)
    df_all['mom_20d_past'] = df_all.groupby('ticker')['close'].pct_change(20).fillna(0.0)
    df_all['sma_20'] = df_all.groupby('ticker')['close'].transform(lambda s: s.rolling(20, min_periods=1).mean())
    df_all['dist_sma20'] = (df_all['close'] / df_all['sma_20'] - 1.0).fillna(0.0)

    # Filtrar exactamente las filas correspondientes a las muestras del bundle
    # Para preservar orden 1:1, crear DataFrame con la lista de muestras
    df_ref = pd.DataFrame({'ticker': tickers_list, 'date_str': dates_list, 'order_id': range(len(tickers_list))})
    merged = pd.merge(df_ref, df_all, on=['ticker', 'date_str'], how='left')
    merged = merged.sort_values('order_id').reset_index(drop=True)

    # Extraer los 14 factores cuantitativos limpios y sin lookahead
    factors = []
    # 1. log_revenue
    rev = pd.to_numeric(merged.get('revenue', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.log1p(np.maximum(0.0, rev.values)))
    # 2. rev_growth_yoy
    rev_g = pd.to_numeric(merged.get('rev_growth_yoy', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(rev_g.values, -2.0, 5.0))
    # 3. log_net_income
    net_inc = pd.to_numeric(merged.get('net_income', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.sign(net_inc.values) * np.log1p(np.abs(net_inc.values)))
    # 4. net_margin
    net_m = pd.to_numeric(merged.get('net_margin', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(net_m.values, -1.0, 1.0))
    # 5. operating_margin
    op_m = pd.to_numeric(merged.get('operating_margin', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(op_m.values, -1.0, 1.0))
    # 6. eps_diluted
    eps = pd.to_numeric(merged.get('eps_diluted', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(eps.values, -20.0, 20.0))
    # 7. eps_growth_yoy
    eps_g = pd.to_numeric(merged.get('eps_growth_yoy', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(eps_g.values, -5.0, 5.0))
    # 8. roe
    roe = pd.to_numeric(merged.get('roe', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(roe.values, -2.0, 2.0))
    # 9. vol_20d
    vol = pd.to_numeric(merged.get('vol_20d', 0.3), errors='coerce').fillna(0.3)
    factors.append(np.clip(vol.values, 0.01, 2.0))
    # 10. log_volume
    volume = pd.to_numeric(merged.get('volume', 1e6), errors='coerce').fillna(1e6)
    factors.append(np.log1p(np.maximum(0.0, volume.values)))
    # 11. log_close
    close = pd.to_numeric(merged.get('close', 50.0), errors='coerce').fillna(50.0)
    factors.append(np.log1p(np.maximum(1.0, close.values)))
    # 12. mom_5d_past (estrictamente pasado)
    m5 = pd.to_numeric(merged.get('mom_5d_past', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(m5.values, -0.5, 0.5))
    # 13. mom_20d_past (estrictamente pasado)
    m20 = pd.to_numeric(merged.get('mom_20d_past', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(m20.values, -0.5, 0.5))
    # 14. dist_sma20 (estrictamente pasado)
    dsma = pd.to_numeric(merged.get('dist_sma20', 0.0), errors='coerce').fillna(0.0)
    factors.append(np.clip(dsma.values, -0.5, 0.5))

    X_f = np.stack(factors, axis=1).astype(np.float32)
    names = [
        'log_revenue', 'rev_growth_yoy', 'log_net_income', 'net_margin', 
        'operating_margin', 'eps_diluted', 'eps_growth_yoy', 'roe', 
        'vol_20d', 'log_volume', 'log_close', 'mom_5d_past', 'mom_20d_past', 'dist_sma20'
    ]

    if scaler_dict is None:
        mean = np.mean(X_f, axis=0)
        std = np.std(X_f, axis=0)
        std[std < 1e-6] = 1.0
        scaler_dict = {'mean': mean, 'std': std}

    X_f_norm = (X_f - scaler_dict['mean']) / scaler_dict['std']

    targets = {
        'ret_1d': torch.tensor(pd.to_numeric(merged['ret_1d'], errors='coerce').fillna(0.0).values, dtype=torch.float32),
        'ret_5d': torch.tensor(pd.to_numeric(merged['ret_5d'], errors='coerce').fillna(0.0).values, dtype=torch.float32),
        'ret_20d': torch.tensor(pd.to_numeric(merged['ret_20d'], errors='coerce').fillna(0.0).values, dtype=torch.float32),
        'ret_5d_excess': torch.tensor(pd.to_numeric(merged['ret_5d_excess'], errors='coerce').fillna(0.0).values, dtype=torch.float32),
        'ret_20d_excess': torch.tensor(pd.to_numeric(merged['ret_20d_excess'], errors='coerce').fillna(0.0).values, dtype=torch.float32),
    }

    return torch.tensor(X_f_norm, dtype=torch.float32), targets, names, scaler_dict


def compute_metrics(y_pred: np.ndarray, y_true: np.ndarray) -> dict:
    """Calcula métricas estadísticas y financieras."""
    err = y_pred - y_true
    mse = float(np.mean(err ** 2))
    rmse = float(np.sqrt(mse))
    mae = float(np.mean(np.abs(err)))

    sp_corr, _ = spearmanr(y_pred, y_true)
    pr_corr, _ = pearsonr(y_pred, y_true)
    sp_corr = 0.0 if np.isnan(sp_corr) else float(sp_corr)
    pr_corr = 0.0 if np.isnan(pr_corr) else float(pr_corr)

    # Hit Ratio Direccional (¿Acierta si la acción sube o baja?)
    valid = y_true != 0
    hit = float(np.mean(np.sign(y_pred[valid]) == np.sign(y_true[valid]))) if valid.sum() > 0 else 0.5

    ranks = pd.Series(y_pred).rank(method='first')
    deciles = pd.qcut(ranks, q=10, labels=False)
    dec_df = pd.DataFrame({'pred': y_pred, 'target': y_true, 'decile': deciles})
    dec_means = dec_df.groupby('decile')['target'].mean().to_dict()

    d0_ret = float(dec_means.get(0, 0.0)) * 100
    d9_ret = float(dec_means.get(9, 0.0)) * 100
    ls_spread = d9_ret - d0_ret

    d9_returns = dec_df[dec_df['decile'] == 9]['target'].values
    d0_returns = dec_df[dec_df['decile'] == 0]['target'].values
    ls_returns = d9_returns - d0_returns[:len(d9_returns)] if len(d0_returns) == len(d9_returns) else d9_returns

    lo_mean = np.mean(d9_returns) * 12 * 100  # Anualizado a 12 meses
    lo_vol = (np.std(d9_returns) * np.sqrt(12) * 100) + 1e-6
    lo_sharpe = float(lo_mean / lo_vol)

    ls_mean = np.mean(ls_returns) * 12 * 100
    ls_vol = (np.std(ls_returns) * np.sqrt(12) * 100) + 1e-6
    ls_sharpe = float(ls_mean / ls_vol)

    return {
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
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


def train_single_model(model: nn.Module, train_loader: DataLoader, 
                       val_xf: torch.Tensor, val_xn: torch.Tensor, val_y: torch.Tensor,
                       device: torch.device, epochs: int = 40, lr: float = 1e-3, 
                       use_directional_loss: bool = True, is_mixture: bool = False) -> nn.Module:
    """Entrenamiento con soporte para pérdida direccional."""
    model = model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    loss_fn = DirectionalLoss(gamma=2.0, lambda_corr=0.5) if use_directional_loss else nn.MSELoss()
    best_loss = float('inf')
    best_weights = None

    for epoch in range(epochs):
        model.train()
        for b_xf, b_xn, b_y in train_loader:
            b_xf = b_xf.to(device)
            b_xn = b_xn.to(device)
            b_y = b_y.to(device)

            optimizer.zero_grad()
            if is_mixture:
                if use_directional_loss:
                    outs = model(b_xf, b_xn)
                    loss = loss_fn(outs['pred_mix'], b_y)
                else:
                    loss = model.compute_decoupled_loss(b_xf, b_xn, b_y)['loss_total']
            elif isinstance(model, FactorsAlone):
                preds = model(b_xf)
                loss = loss_fn(preds, b_y)
            elif isinstance(model, NewsAlone):
                preds = model(b_xn)
                loss = loss_fn(preds, b_y)
            else:
                preds = model(b_xf, b_xn)
                loss = loss_fn(preds, b_y)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        # Validación
        model.eval()
        with torch.no_grad():
            v_xf = val_xf.to(device)
            v_xn = val_xn.to(device)
            v_y = val_y.to(device)
            if is_mixture:
                v_p = model(v_xf, v_xn)['pred_mix']
            elif isinstance(model, FactorsAlone):
                v_p = model(v_xf)
            elif isinstance(model, NewsAlone):
                v_p = model(v_xn)
            else:
                v_p = model(v_xf, v_xn)
            val_loss = float(F.mse_loss(v_p, v_y))

        if val_loss < best_loss:
            best_loss = val_loss
            best_weights = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    if best_weights is not None:
        model.load_state_dict(best_weights)
    return model


def main():
    parser = argparse.ArgumentParser(description="Evaluación de la Opción A: Mejoras de Tendencia y Horizonte")
    parser.add_argument("--features_path", type=str, default="checkpoints/multimodal/features.pt")
    parser.add_argument("--output_dir", type=str, default="checkpoints/multimodal/option_a_experiments")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Opción A] Dispositivo seleccionado: {device}")

    # 1. Cargar bundle existente con representaciones de noticias LLM
    bundle = torch.load(args.features_path, map_location='cpu', weights_only=False)
    news_dim = bundle['train']['x_n'].shape[1]

    # 2. Construir factores sin filtración y objetivos ampliados
    print("[Opción A] Construyendo factores pasados rezagados y objetivos a 5d y 20d (1 mes)...")
    train_xf, train_targets, factor_names, scaler = build_enhanced_factors_and_targets(
        'train', bundle['train']['dates'], bundle['train']['tickers'], scaler_dict=None
    )
    val_xf, val_targets, _, _ = build_enhanced_factors_and_targets(
        'val', bundle['val']['dates'], bundle['val']['tickers'], scaler_dict=scaler
    )
    test_xf, test_targets, _, _ = build_enhanced_factors_and_targets(
        'test', bundle['test']['dates'], bundle['test']['tickers'], scaler_dict=scaler
    )

    num_factors = len(factor_names)
    print(f"[Opción A] Factores cuantitativos ({num_factors}): {factor_names}")

    # 3. Comparar Horizontes y Pérdidas
    horizons = [
        ('1d (Diario Anterior - Baseline)', 'ret_1d', False),
        ('5d (1 Semana - MSE)', 'ret_5d', False),
        ('5d (1 Semana - Pérdida Direccional)', 'ret_5d', True),
        ('20d (1 Mes RAM AI - MSE)', 'ret_20d', False),
        ('20d (1 Mes RAM AI - Pérdida Direccional)', 'ret_20d', True),
        ('20d Excess (1 Mes Market-Adjusted - Pérdida Direccional)', 'ret_20d_excess', True),
    ]

    all_comparison_rows = []

    print("\n" + "="*115)
    print("                 EVALUACIÓN COMPARATIVA DE HORIZONTES TEMPORALES Y PÉRDIDA DIRECCIONAL (TEST SET)              ")
    print("="*115)
    print(f"{'Configuración / Horizonte':<55} | {'Hit Ratio%':<11} {'Rank IC':<10} {'Pearson r':<11} {'L/S Spread':<11} {'Sharpe L/S':<10}")
    print("-" * 115)

    for desc, target_key, use_dir_loss in horizons:
        y_train = train_targets[target_key]
        y_val = val_targets[target_key]
        y_test = test_targets[target_key]

        train_ds = TensorDataset(train_xf, bundle['train']['x_n'], y_train)
        train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)

        # Entrenar el modelo estrella Fusion Combination (Eq. 3 de RAM AI)
        model = FusionCombination(num_factors=num_factors, news_dim=news_dim, bottleneck_dim=256, fusion_dim=128)
        model = train_single_model(
            model, train_loader, val_xf, bundle['val']['x_n'], y_val,
            device=device, epochs=45, lr=1e-3, use_directional_loss=use_dir_loss
        )

        model.eval()
        with torch.no_grad():
            preds_test = model(test_xf.to(device), bundle['test']['x_n'].to(device)).cpu().numpy()

        m = compute_metrics(preds_test, y_test.numpy())
        print(f"{desc:<55} | {m['hit_ratio']:>9.2f}% {m['rank_ic']:>+9.4f} {m['pearson']:>+10.4f} {m['ls_spread']:>+10.2f}% {m['ls_sharpe']:>9.2f}")

        all_comparison_rows.append({
            'Configuracion': desc,
            'Horizonte': target_key,
            'Perdida_Direccional': use_dir_loss,
            'Hit_Ratio': m['hit_ratio'],
            'Rank_IC': m['rank_ic'],
            'Pearson_r': m['pearson'],
            'LS_Spread': m['ls_spread'],
            'LS_Sharpe': m['ls_sharpe'],
            'RMSE': m['rmse'],
            'D0_Ret': m['d0_return'],
            'D9_Ret': m['d9_return']
        })

    print("="*115)

    # 4. Guardar resultados y gráfico comparativo
    df_results = pd.DataFrame(all_comparison_rows)
    csv_path = os.path.join(args.output_dir, "comparativa_horizontes_y_perdida.csv")
    df_results.to_csv(csv_path, index=False)

    # Generar gráfico comparativo de Hit Ratio y Rank IC
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

    short_names = [
        "1d Diario (Base)",
        "5d Semana (MSE)",
        "5d Semana (DirLoss)",
        "20d Mes (MSE)",
        "20d Mes (DirLoss)",
        "20d Excess (DirLoss)"
    ]

    hit_ratios = df_results['Hit_Ratio'].values
    rank_ics = df_results['Rank_IC'].values

    # Gráfico Hit Ratio
    colors_hit = ['#d9534f' if h < 55 else ('#f0ad4e' if h < 65 else '#5cb85c') for h in hit_ratios]
    bars1 = ax1.bar(short_names, hit_ratios, color=colors_hit, alpha=0.85)
    ax1.axhline(50.0, color='black', linestyle='--', linewidth=0.9, label='Paseo Aleatorio (50%)')
    ax1.set_title("Acierto Direccional (Hit Ratio %) en Test Set", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Hit Ratio (%)", fontsize=11)
    ax1.set_ylim(40, max(85, max(hit_ratios) + 5))
    ax1.tick_params(axis='x', rotation=30)
    for b in bars1:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2, h + 1.0, f"{h:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax1.legend()

    # Gráfico Rank IC
    colors_ic = ['#d9534f' if r < 0 else ('#5bc0de' if r < 0.2 else '#0275d8') for r in rank_ics]
    bars2 = ax2.bar(short_names, rank_ics, color=colors_ic, alpha=0.85)
    ax2.axhline(0.0, color='black', linestyle='--', linewidth=0.9)
    ax2.axhline(0.03, color='gray', linestyle=':', linewidth=0.8, label='Umbral Institucional (+0.03)')
    ax2.set_title("Poder de Ordenación (Rank IC de Spearman)", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Rank IC", fontsize=11)
    ax2.tick_params(axis='x', rotation=30)
    for b in bars2:
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width()/2, h + (0.02 if h>=0 else -0.05), f"{h:+.3f}", ha='center', va='bottom' if h>=0 else 'top', fontsize=9, fontweight='bold')
    ax2.legend()

    plt.tight_layout()
    chart_path = os.path.join(args.output_dir, "comparativa_horizontes_hit_ratio_ic.png")
    plt.savefig(chart_path)
    plt.close()
    print(f"\n[Gráfico de Mejoras] Guardado en: {chart_path}")


if __name__ == "__main__":
    main()
