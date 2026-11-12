"""Métricas y Evaluación de Cartera Cuantitativa según el Paper EMNLP 2024.

Calcula:
  - Decile RMSE, Decile Precision y Decile Return (Fig. 3 del paper).
  - Rendimiento de Carteras Long-Only (Decil 9) y Long-Short (Decil 9 - Decil 0) (Tabla 1 del paper).
  - Ratio de Sharpe anualizado y Retorno acumulado.
  - Information Coefficient (Rank IC / Correlación de Spearman).
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from scipy.stats import spearmanr


class PortfolioEvaluator:
    """Evaluador de estrategias de cartera cuantitativas a partir de las predicciones del LLM."""

    def __init__(self, risk_free_rate: float = 0.0):
        self.rf = risk_free_rate

    def evaluate_deciles(self, df_eval: pd.DataFrame, pred_col: str = "pred", 
                         target_col: str = "target", date_col: str = "date") -> Dict[str, Any]:
        """Calcula el rendimiento por deciles de predicción (Decil 0 a Decil 9)."""
        df = df_eval.copy()
        
        # Calcular deciles de predicción por cada fecha de mercado (cross-sectional ranking)
        def rank_to_deciles(group):
            if len(group) < 10:
                # Si hay pocos activos, asigna deciles proporcionales
                return pd.qcut(group[pred_col], q=min(len(group), 10), labels=False, duplicates='drop')
            return pd.qcut(group[pred_col], q=10, labels=False, duplicates='drop')

        df['pred_decile'] = df.groupby(date_col).apply(rank_to_deciles).reset_index(level=0, drop=True)
        
        # Deciles verdaderos para calcular precisión
        def rank_true_deciles(group):
            if len(group) < 10:
                return pd.qcut(group[target_col], q=min(len(group), 10), labels=False, duplicates='drop')
            return pd.qcut(group[target_col], q=10, labels=False, duplicates='drop')
        df['true_decile'] = df.groupby(date_col).apply(rank_true_deciles).reset_index(level=0, drop=True)

        # 1. Decile Returns & Decile Precision
        decile_stats = []
        for d in range(10):
            sub = df[df['pred_decile'] == d]
            if sub.empty:
                continue
            avg_ret = sub[target_col].mean()
            rmse = np.sqrt(np.mean((sub[pred_col] - sub[target_col])**2))
            precision = (sub['true_decile'] == d).mean()
            decile_stats.append({
                'decile': d,
                'avg_return': float(avg_ret),
                'rmse': float(rmse),
                'precision': float(precision),
                'count': len(sub)
            })

        # 2. Rendimiento Long-Only (Decil 9) y Long-Short (Decil 9 - Decil 0)
        daily_perf = df.groupby([date_col, 'pred_decile'])[target_col].mean().unstack()
        
        # Retornos diarios de la cartera
        ret_long = daily_perf[9].fillna(0) if 9 in daily_perf else pd.Series(0, index=daily_perf.index)
        ret_short = daily_perf[0].fillna(0) if 0 in daily_perf else pd.Series(0, index=daily_perf.index)
        ret_long_short = ret_long - ret_short

        # Retorno de mercado igualmente ponderado (Benchmark)
        ret_universe = df.groupby(date_col)[target_col].mean()

        def compute_portfolio_metrics(ret_series: pd.Series, periods_per_year: int = 252) -> Dict[str, float]:
            if len(ret_series) < 2 or ret_series.std() == 0:
                return {'ann_return': 0.0, 'volatility': 0.0, 'sharpe_ratio': 0.0}
            ann_ret = (1 + ret_series.mean()) ** periods_per_year - 1
            ann_vol = ret_series.std() * np.sqrt(periods_per_year)
            sharpe = (ann_ret - self.rf) / ann_vol if ann_vol > 0 else 0.0
            return {
                'ann_return': float(ann_ret),
                'volatility': float(ann_vol),
                'sharpe_ratio': float(sharpe)
            }

        # 3. Information Coefficient (Rank IC diario o global si hay pocas acciones por día)
        def calc_ic(grp):
            if len(grp) < 3: return np.nan
            return spearmanr(grp[pred_col], grp[target_col])[0]
        
        try:
            daily_ic = df.groupby(date_col).apply(calc_ic, include_groups=False).dropna()
        except TypeError:
            daily_ic = df.groupby(date_col).apply(calc_ic).dropna()

        if len(daily_ic) > 0:
            mean_ic = float(daily_ic.mean())
            icir = float(daily_ic.mean() / daily_ic.std()) if daily_ic.std() > 0 else 0.0
        else:
            # Fallback en evaluaciones reducidas / pilotos con pocos activos por fecha
            global_ic = spearmanr(df[pred_col], df[target_col])[0] if len(df) >= 3 else 0.0
            mean_ic = float(global_ic) if not np.isnan(global_ic) else 0.0
            icir = 0.0

        return {
            'decile_stats': decile_stats,
            'long_only': compute_portfolio_metrics(ret_long),
            'long_short': compute_portfolio_metrics(ret_long_short),
            'benchmark': compute_portfolio_metrics(ret_universe),
            'rank_ic': mean_ic,
            'icir': icir,
            'n_sessions': len(daily_perf)
        }
