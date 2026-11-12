"""Módulo de Contexto Financiero y Fundamentales Oficiales de la SEC (EDGAR XBRL).

Diseñado para el TFM: "Fine-Tuning LLMs for Stock Return Prediction Using Newsflow + Financial Context"
Inyecta datos financieros corporativos oficiales (10-Q / 10-K) sin sesgo de anticipación (Zero Look-ahead Bias)
junto a los titulares de noticias antes de alimentar al LLM.
"""

import os
import json
import time
import urllib.request
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

CACHE_DIR = "data/fundamentals/raw_sec"
OUTPUT_PARQUET = "data/fundamentals/quarterly_fundamentals.parquet"
SEC_TICKERS_JSON = "data/sec_tickers.json"

# Conceptos contables US-GAAP soportados
CONCEPTS_MAP = {
    'revenue': [
        'RevenueFromContractWithCustomerExcludingAssessedTax',
        'SalesRevenueNet',
        'Revenues',
        'SalesRevenueServicesGross'
    ],
    'net_income': [
        'NetIncomeLoss',
        'ProfitLoss'
    ],
    'operating_income': [
        'OperatingIncomeLoss'
    ],
    'eps_diluted': [
        'EarningsPerShareDiluted',
        'EarningsPerShareBasic'
    ],
    'total_assets': [
        'Assets'
    ],
    'total_equity': [
        'StockholdersEquity',
        'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'
    ]
}


class FinancialContextEngine:
    def __init__(self, cache_dir: str = CACHE_DIR, sec_tickers_path: str = SEC_TICKERS_JSON):
        self.cache_dir = cache_dir
        self.sec_tickers_path = sec_tickers_path
        os.makedirs(self.cache_dir, exist_ok=True)
        self.ticker_to_cik = self._load_cik_map()
        self.df_fundamentals: Optional[pd.DataFrame] = None
        self._load_or_build_fundamentals()

    def _load_cik_map(self) -> Dict[str, str]:
        if not os.path.exists(self.sec_tickers_path):
            raise FileNotFoundError(f"No se encontró el mapa de CIKs en {self.sec_tickers_path}")
        with open(self.sec_tickers_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        cik_map = {}
        for k, v in data.items():
            sym = v.get('ticker')
            cik = v.get('cik_str')
            if sym and cik:
                cik_map[sym] = str(cik).zfill(10)
        return cik_map

    def ingest_tickers(self, tickers: List[str], headers: Optional[dict] = None) -> List[str]:
        """Descarga y almacena en caché los archivos JSON oficiales XBRL de la SEC."""
        if headers is None:
            headers = {'User-Agent': 'TFM_Research_Master student@university.edu'}
        downloaded = []
        for sym in tickers:
            p = os.path.join(self.cache_dir, f"{sym}.json")
            if os.path.exists(p):
                continue
            cik = self.ticker_to_cik.get(sym)
            if not cik:
                print(f"[FinancialContext] Advertencia: CIK no encontrado para {sym}")
                continue
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req) as resp:
                    raw = resp.read()
                with open(p, 'wb') as f_out:
                    f_out.write(raw)
                downloaded.append(sym)
                time.sleep(0.12)  # Respetar límite legal SEC de 10 req/s
            except Exception as e:
                print(f"[FinancialContext] Error descargando {sym} (CIK {cik}): {e}")
        return downloaded

    def parse_quarterly_fundamentals(self, tickers: Optional[List[str]] = None) -> pd.DataFrame:
        """Parsea y consolida los estados trimestrales oficiales (10-Q / 10-K) de los archivos en caché."""
        if tickers is None:
            tickers = [f.replace('.json', '') for f in os.listdir(self.cache_dir) if f.endswith('.json')]

        records = []
        for sym in tickers:
            p = os.path.join(self.cache_dir, f"{sym}.json")
            if not os.path.exists(p):
                continue
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                facts = raw_data.get('facts', {}).get('us-gaap', {})
            except Exception:
                continue

            filings_dict = {}

            # Helper para recolectar conceptos contables
            for standard_name, usgaap_aliases in CONCEPTS_MAP.items():
                unit_key = 'USD/shares' if standard_name == 'eps_diluted' else 'USD'
                
                # Probar cada alias en orden de prioridad
                for alias in usgaap_aliases:
                    if alias in facts and unit_key in facts[alias]['units']:
                        items = facts[alias]['units'][unit_key]
                        for it in items:
                            form = it.get('form')
                            filed = it.get('filed')
                            val = it.get('val')
                            start = it.get('start')
                            end = it.get('end')
                            fp = it.get('fp', '')

                            if not filed or form not in ['10-Q', '10-K'] or val is None:
                                continue

                            # En 10-Q, filtrar acumulados YTD de 6 o 9 meses para quedarnos con el trimestre puro (~90 días)
                            if start and end and form == '10-Q' and standard_name in ['revenue', 'net_income', 'operating_income']:
                                dur = (pd.to_datetime(end) - pd.to_datetime(start)).days
                                if dur > 125:
                                    continue

                            key = (filed, form, end)
                            if key not in filings_dict:
                                filings_dict[key] = {
                                    'ticker': sym,
                                    'filed': filed,
                                    'form': form,
                                    'end': end,
                                    'fp': fp
                                }

                            # Asignar si no estaba o si era nulo
                            if standard_name not in filings_dict[key] or pd.isnull(filings_dict[key][standard_name]):
                                filings_dict[key][standard_name] = val

            for row in filings_dict.values():
                records.append(row)

        df = pd.DataFrame(records)
        if df.empty:
            return df

        df['filed'] = pd.to_datetime(df['filed'])
        df['end'] = pd.to_datetime(df['end'])
        df = df.sort_values(by=['ticker', 'filed', 'end']).reset_index(drop=True)

        # Filtrar datos anteriores a 2008
        df = df[df['filed'] >= '2008-01-01'].copy()

        # Deduplicar por ticker y filed (mantener el más reciente/completo)
        df = df.drop_duplicates(subset=['ticker', 'filed'], keep='last')

        # Calcular métricas y ratios financieros
        df['operating_margin'] = df['operating_income'] / df['revenue']
        df['net_margin'] = df['net_income'] / df['revenue']
        df['roe'] = df['net_income'] / df['total_equity']
        df['debt_to_equity'] = (df['total_assets'] - df['total_equity']) / df['total_equity']

        # Crecimiento interanual YoY (frente a 4 trimestres atrás)
        df['rev_growth_yoy'] = df.groupby('ticker')['revenue'].pct_change(periods=4)
        df['eps_growth_yoy'] = df.groupby('ticker')['eps_diluted'].pct_change(periods=4)

        os.makedirs(os.path.dirname(OUTPUT_PARQUET), exist_ok=True)
        df.to_parquet(OUTPUT_PARQUET, index=False)
        self.df_fundamentals = df
        return df

    def _load_or_build_fundamentals(self):
        if os.path.exists(OUTPUT_PARQUET):
            self.df_fundamentals = pd.read_parquet(OUTPUT_PARQUET)
        else:
            self.parse_quarterly_fundamentals()

    def get_latest_fundamental(self, ticker: str, as_of_date: pd.Timestamp) -> Optional[dict]:
        """Obtiene el último estado financiero oficial publicado en o antes de as_of_date (Causal / No lookahead)."""
        if self.df_fundamentals is None or self.df_fundamentals.empty:
            return None
        sub = self.df_fundamentals[
            (self.df_fundamentals['ticker'] == ticker) & 
            (self.df_fundamentals['filed'] <= as_of_date)
        ]
        if sub.empty:
            return None
        return sub.iloc[-1].to_dict()

    def format_prompt_block(self, ticker: str, as_of_date: pd.Timestamp, 
                            current_price: Optional[float] = None, 
                            vol_20d: Optional[float] = None) -> str:
        """Formatea un bloque estructurado de fundamentales para inyección directa en el prompt del LLM."""
        f = self.get_latest_fundamental(ticker, as_of_date)
        lines = [f"[PERFIL FINANCIERO Y FUNDAMENTALES DE LA EMPRESA (SEC EDGAR)]"]
        lines.append(f"Ticker: {ticker} | Fecha de Mercado: {str(as_of_date)[:10]}")
        
        if current_price is not None:
            vol_str = f" | Volatilidad 20d: {vol_20d*100:.1f}%" if vol_20d else ""
            lines.append(f"Cotización Actual: ${current_price:.2f}{vol_str}")

        if not f:
            lines.append("Estado Financiero: No hay informes 10-Q/10-K previos disponibles en la fecha.")
            return "\n".join(lines)

        filed_str = str(f['filed'])[:10]
        form = f.get('form', '10-Q')
        fp = f.get('fp', 'Q')
        lines.append(f"Último Informe Oficial: Form {form} ({fp}) publicado el {filed_str}")

        # Revenue
        rev = f.get('revenue')
        rev_g = f.get('rev_growth_yoy')
        if pd.notnull(rev):
            g_str = f" (Crecimiento YoY: {rev_g*100:+.1f}%)" if pd.notnull(rev_g) else ""
            lines.append(f"- Ingresos Trimestrales (Revenue): ${rev/1e6:,.1f}M{g_str}")

        # Net Income & Margins
        net = f.get('net_income')
        net_m = f.get('net_margin')
        op_m = f.get('operating_margin')
        if pd.notnull(net):
            m_str = f" (Margen Neto: {net_m*100:.1f}%)" if pd.notnull(net_m) else ""
            lines.append(f"- Beneficio Neto (Net Income): ${net/1e6:,.1f}M{m_str}")
        if pd.notnull(op_m):
            lines.append(f"- Margen Operativo: {op_m*100:.1f}%")

        # EPS
        eps = f.get('eps_diluted')
        eps_g = f.get('eps_growth_yoy')
        if pd.notnull(eps):
            eg_str = f" (Variación YoY: {eps_g*100:+.1f}%)" if pd.notnull(eps_g) else ""
            lines.append(f"- Beneficio por Acción Diluido (EPS): ${eps:.2f}{eg_str}")

        # Ratios
        roe = f.get('roe')
        if pd.notnull(roe):
            lines.append(f"- Rentabilidad sobre Fondos Propios (ROE): {roe*100:.1f}%")

        return "\n".join(lines)

    def enrich_dataframe_asof(self, df: pd.DataFrame, date_col: str = 'date', ticker_col: str = 'ticker') -> pd.DataFrame:
        """Une mediante merge_asof los fundamentales al panel diario garantizando CERO look-ahead bias."""
        if self.df_fundamentals is None or self.df_fundamentals.empty:
            raise ValueError("No hay fundamentales disponibles.")

        df_target = df.copy()
        df_target[date_col] = pd.to_datetime(df_target[date_col])
        df_target = df_target.sort_values(by=[date_col, ticker_col]).reset_index(drop=True)

        fund_clean = self.df_fundamentals[[
            'ticker', 'filed', 'revenue', 'rev_growth_yoy', 'net_income', 
            'net_margin', 'operating_margin', 'eps_diluted', 'eps_growth_yoy', 'roe'
        ]].copy()
        fund_clean = fund_clean.rename(columns={'filed': 'sec_filed_date'})
        fund_clean = fund_clean.sort_values(by=['sec_filed_date', 'ticker']).reset_index(drop=True)

        # Merge ASOF por ticker garantizando sec_filed_date <= market_date
        merged_chunks = []
        for sym, grp in df_target.groupby(ticker_col):
            fund_sym = fund_clean[fund_clean['ticker'] == sym].sort_values('sec_filed_date')
            grp_sorted = grp.sort_values(date_col)
            if not fund_sym.empty:
                enriched = pd.merge_asof(
                    grp_sorted, fund_sym.drop(columns=['ticker']),
                    left_on=date_col, right_on='sec_filed_date',
                    direction='backward'
                )
            else:
                enriched = grp_sorted.copy()
                for col in fund_sym.columns:
                    if col not in enriched.columns:
                        enriched[col] = np.nan
            merged_chunks.append(enriched)

        res = pd.concat(merged_chunks, ignore_index=True)
        return res.sort_values(by=[ticker_col, date_col]).reset_index(drop=True)


if __name__ == "__main__":
    print("Iniciando motor de contexto financiero...")
    engine = FinancialContextEngine()
    print(f"Total registros cargados: {len(engine.df_fundamentals):,}")
    
    # Prueba con NVDA en la fecha de resultados de mayo 2023
    sample_block = engine.format_prompt_block(
        ticker="NVDA", 
        as_of_date=pd.Timestamp("2023-05-25"), 
        current_price=305.38, 
        vol_20d=0.342
    )
    print("\n=== Ejemplo de Bloque Generado para Prompt ===")
    print(sample_block)
