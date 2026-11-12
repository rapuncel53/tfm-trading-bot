"""Dataset de PyTorch para predicción de retornos bursátiles a partir de noticias y fundamentales.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union

try:
    import torch
    from torch.utils.data import Dataset
except ImportError:
    # Fallback si torch aún no está instalado
    class Dataset:
        pass


def build_stock_prompt(ticker: str, date_str: str, 
                       close_price: Optional[float], vol_20d: Optional[float],
                       revenue: Optional[float], rev_growth_yoy: Optional[float],
                       net_income: Optional[float], net_margin: Optional[float],
                       operating_margin: Optional[float], eps: Optional[float],
                       eps_growth_yoy: Optional[float], roe: Optional[float],
                       headlines: str, target_horizon: str = "1 sesión") -> str:
    """Construye el prompt multimodal enriquecido con fundamentales y noticias."""
    lines = [
        "<|im_start|>system",
        "Eres un analista financiero cuantitativo experto. Tu tarea es analizar la información contable oficial "
        "y el flujo de noticias de la empresa para estimar el retorno porcentual futuro esperado del precio de la acción.",
        "<|im_end|>",
        "<|im_start|>user",
        f"[PERFIL DE EMPRESA Y FUNDAMENTALES (SEC EDGAR)]",
        f"Empresa: {ticker} | Fecha de Mercado: {date_str}"
    ]

    if close_price is not None and not np.isnan(close_price):
        vol_str = f" | Volatilidad 20d: {vol_20d*100:.1f}%" if vol_20d and not np.isnan(vol_20d) else ""
        lines.append(f"Precio de Cierre: ${close_price:.2f}{vol_str}")

    # Fundamentales
    fund_lines = []
    if revenue is not None and not np.isnan(revenue):
        g_str = f" (Crecimiento YoY: {rev_growth_yoy*100:+.1f}%)" if rev_growth_yoy and not np.isnan(rev_growth_yoy) else ""
        fund_lines.append(f"- Ingresos Trimestrales: ${revenue/1e6:,.1f}M{g_str}")
    if net_income is not None and not np.isnan(net_income):
        m_str = f" (Margen Neto: {net_margin*100:.1f}%)" if net_margin and not np.isnan(net_margin) else ""
        fund_lines.append(f"- Beneficio Neto: ${net_income/1e6:,.1f}M{m_str}")
    if operating_margin is not None and not np.isnan(operating_margin):
        fund_lines.append(f"- Margen Operativo: {operating_margin*100:.1f}%")
    if eps is not None and not np.isnan(eps):
        eg_str = f" (Variación YoY: {eps_growth_yoy*100:+.1f}%)" if eps_growth_yoy and not np.isnan(eps_growth_yoy) else ""
        fund_lines.append(f"- Beneficio por Acción (EPS): ${eps:.2f}{eg_str}")
    if roe is not None and not np.isnan(roe):
        fund_lines.append(f"- Rentabilidad sobre Fondos Propios (ROE): {roe*100:.1f}%")

    if fund_lines:
        lines.append("Últimos Estados Contables Oficiales (10-Q/10-K):")
        lines.extend(fund_lines)
    else:
        lines.append("Estados Contables: Sin informes oficiales previos disponibles.")

    # Noticias
    lines.append("\n[FLUJO DE NOTICIAS DE LA SESIÓN]")
    if headlines and str(headlines).strip():
        items = [h.strip() for h in str(headlines).split("[SEP]") if h.strip()]
        for i, it in enumerate(items, 1):
            lines.append(f"{i}. {it}")
    else:
        lines.append("Sin titulares reportados para esta sesión bursátil.")

    # Instrucción final
    lines.append(
        f"\n[OBJETIVO DE ESTIMACIÓN]\n"
        f"Estima el retorno numérico forward de la acción {ticker} para el horizonte de {target_horizon}."
    )
    lines.append("<|im_end|>")
    lines.append("<|im_start|>assistant\n")
    return "\n".join(lines)


class StockReturnNewsDataset(Dataset):
    """Dataset para entrenar el modelo LLMReturnRegressor con noticias y fundamentales (univariado o multi-horizonte)."""

    def __init__(self, parquet_path: str, tokenizer=None, max_length: int = 2048,
                 target_col: Union[str, List[str]] = "ret_1d", filter_news_only: bool = True):
        self.tokenizer = tokenizer
        self.max_length = max_length
        if isinstance(target_col, str):
            self.target_cols = [target_col]
            self.is_multi = False
        else:
            self.target_cols = list(target_col)
            self.is_multi = len(self.target_cols) > 1
        self.target_col = self.target_cols[0]

        try:
            import pyarrow.parquet as pq
            df = pq.read_table(parquet_path).to_pandas()
        except Exception:
            df = pd.read_parquet(parquet_path)
        
        # Filtrar solo filas con noticias si se especifica
        if filter_news_only and 'has_news' in df.columns:
            df = df[df['has_news']].copy()

        # Filtrar valores nulos en todos los targets de retorno especificados
        valid_cols = [c for c in self.target_cols if c in df.columns]
        if valid_cols:
            df = df.dropna(subset=valid_cols).reset_index(drop=True)
        self.data = df
        print(f"[Dataset] Cargadas {len(self.data):,} muestras de {parquet_path} (Targets: {self.target_cols})")

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        row = self.data.iloc[idx]
        
        ticker = row['ticker']
        date_str = str(row['date'])[:10]
        close_p = row.get('close')
        vol_20d = row.get('vol_20d')
        
        # Fundamentales
        rev = row.get('revenue')
        rev_g = row.get('rev_growth_yoy')
        net = row.get('net_income')
        net_m = row.get('net_margin')
        op_m = row.get('operating_margin')
        eps = row.get('eps_diluted')
        eps_g = row.get('eps_growth_yoy')
        roe = row.get('roe')
        
        # Noticias
        headlines = row.get('headlines_concat', '')
        
        horizon_desc = "1 sesión (1d), 1 semana (5d) y 1 mes (20d)" if self.is_multi else "1 sesión"
        prompt_text = build_stock_prompt(
            ticker=ticker, date_str=date_str,
            close_price=close_p, vol_20d=vol_20d,
            revenue=rev, rev_growth_yoy=rev_g,
            net_income=net, net_margin=net_m,
            operating_margin=op_m, eps=eps,
            eps_growth_yoy=eps_g, roe=roe,
            headlines=headlines, target_horizon=horizon_desc
        )
        
        # Target escalar o vector multi-horizonte
        if self.is_multi:
            target_val = [float(row[c]) for c in self.target_cols]
        else:
            target_val = float(row[self.target_col])

        item = {
            'ticker': ticker,
            'date': date_str,
            'prompt_text': prompt_text,
            'target': target_val
        }

        # Tokenizar si el tokenizer está disponible (dynamic padding en collate_fn)
        if self.tokenizer is not None:
            enc = self.tokenizer(
                prompt_text,
                max_length=self.max_length,
                padding=False,
                truncation=True,
                return_tensors='pt'
            )
            item['input_ids'] = enc['input_ids'].squeeze(0)
            item['attention_mask'] = enc['attention_mask'].squeeze(0)

        return item
