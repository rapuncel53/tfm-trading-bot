"""Pipeline de Generación de Splits Temporales para el TFM.

Partición estrictamente temporal:
  - TRAIN:  2011-01-01 a 2018-12-31 (8 años, Benzinga + Precios)
  - VAL:    2019-01-01 a 2020-06-10 (1.5 años, Pre-COVID + Shock COVID)
  - BUFFER: 2020-06-11 a 2021-08-16 (14 meses, Embargo temporal / Purge)
  - TEST:   2021-08-17 a 2023-12-31 (2.5 años, FNSPID / NASDAQ Out-of-Sample)

Genera:
  data/splits/train/ (prices.parquet, news.parquet, daily_aligned.parquet)
  data/splits/val/   (prices.parquet, news.parquet, daily_aligned.parquet)
  data/splits/test/  (prices.parquet, news.parquet, daily_aligned.parquet)
  data/splits/SPLIT_SUMMARY.md
"""

import os
import sys
import re
import io
import csv
import gzip
import json
import numpy as np
import pandas as pd
from datetime import datetime

csv.field_size_limit(2147483647)

SPLITS_DIR = "data/splits"
for s in ['train', 'val', 'test']:
    os.makedirs(f"{SPLITS_DIR}/{s}", exist_ok=True)

# 1. Definir Universo de Empresas
# Cargamos los 24 blue-chips del panel piloto más las 136 continuas del Grupo 1
PANEL_TICKERS = [l.strip() for l in open('scripts/panel.txt') if l.strip()]

# Cargar también las empresas de tier1_fechas_noticias.csv
df_t1 = pd.read_csv('data/tier1_fechas_noticias.csv', sep=';')
TARGET_TICKERS = sorted(list(set(PANEL_TICKERS + df_t1['sym'].tolist())))
print(f"Total empresas objetivo en el pipeline: {len(TARGET_TICKERS)}")

# 2. Cargar Precios y Calcular Retornos
print("Cargando precios diarios y calculando retornos futuros...")
price_frames = []

for sym in TARGET_TICKERS:
    price_file = f"data/prices/full_history/{sym}.csv"
    if not os.path.exists(price_file):
        continue
    
    df_p = pd.read_csv(price_file)
    df_p['date'] = pd.to_datetime(df_p['date'])
    df_p = df_p.sort_values('date').reset_index(drop=True)
    
    # Filtrar rango general 2010 a 2023
    df_p = df_p[(df_p['date'] >= '2010-01-01') & (df_p['date'] <= '2023-12-31')].copy()
    if len(df_p) < 100:
        continue
    
    df_p['ticker'] = sym
    
    # Calcular retornos futuros (shift negativo: información del futuro para predecir)
    # ret_1d: retorno al cierre siguiente
    df_p['ret_1d'] = df_p['close'].shift(-1) / df_p['close'] - 1.0
    df_p['ret_3d'] = df_p['close'].shift(-3) / df_p['close'] - 1.0
    df_p['ret_5d'] = df_p['close'].shift(-5) / df_p['close'] - 1.0
    
    # Etiquetas direccionales
    # 1: SUBE (> +0.33%), -1: BAJA (< -0.33%), 0: NEUTRAL
    THRESH = 0.0033
    df_p['target_dir_1d'] = np.where(df_p['ret_1d'] > THRESH, 1, np.where(df_p['ret_1d'] < -THRESH, -1, 0))
    df_p['target_bin_1d'] = np.where(df_p['ret_1d'] > 0, 1, 0) # Binario simple (Up/Down)
    
    df_p['target_dir_3d'] = np.where(df_p['ret_3d'] > THRESH * 1.5, 1, np.where(df_p['ret_3d'] < -THRESH * 1.5, -1, 0))
    df_p['target_dir_5d'] = np.where(df_p['ret_5d'] > THRESH * 2.0, 1, np.where(df_p['ret_5d'] < -THRESH * 2.0, -1, 0))
    
    # Volatilidad móvil 20 sesiones
    df_p['vol_20d'] = (df_p['close'].pct_change()).rolling(20).std() * np.sqrt(252)
    
    price_frames.append(df_p)

df_all_prices = pd.concat(price_frames, ignore_index=True)
print(f"Total registros de precios procesados: {len(df_all_prices):,} filas.")

# 3. Cargar y Unificar Noticias
print("Cargando y unificando noticias de Benzinga y NASDAQ/FNSPID...")
news_records = []

# A. Noticias Benzinga (2009 a 2020)
bz_file = "data/benzinga/tier1_benzinga_news.csv.gz"
if os.path.exists(bz_file):
    print("  Procesando Benzinga...")
    with gzip.open(bz_file, 'rt', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            sym = r.get('ticker')
            if sym in TARGET_TICKERS:
                dt_str = r.get('date', '')[:19]
                news_records.append({
                    'ticker': sym,
                    'datetime': dt_str,
                    'headline': r.get('headline', ''),
                    'source': 'Benzinga',
                    'publisher': r.get('publisher', 'Benzinga'),
                    'url': r.get('url', '')
                })

# B. Noticias de NASDAQ desde data/windows/*.bin
print("  Procesando data/windows/*.bin...")
for fn in os.listdir('data/windows'):
    if not fn.endswith('.bin') or fn.endswith('.bad'):
        continue
    sym = fn.replace('.bin', '')
    p = os.path.join('data/windows', fn)
    try:
        with open(p, 'rb') as f:
            raw = f.read()
        raw = raw[:raw.rfind(b'\n')]
        rd = csv.reader(io.StringIO(raw.decode('utf-8', 'replace'), newline=''))
        for r in rd:
            if len(r) >= 12 and r[3].strip() == sym:
                fecha = r[1].replace(' UTC', '').strip()[:19]
                title = r[2].strip()
                if len(title) > 5 and len(fecha) >= 10:
                    news_records.append({
                        'ticker': sym,
                        'datetime': fecha,
                        'headline': title,
                        'source': 'NASDAQ_FNSPID',
                        'publisher': r[5].strip() if len(r) > 5 else 'NASDAQ',
                        'url': r[0].strip() if len(r) > 0 else ''
                    })
    except Exception as e:
        print(f"    Error leyendo {fn}: {e}")

# C. Noticias de benstaf/nasdaq_news (para Google, AMD, etc.)
print("  Procesando benstaf/nasdaq_news...")
try:
    url_benstaf = "https://huggingface.co/datasets/benstaf/nasdaq_news/resolve/main/data/train-00000-of-00001.parquet"
    df_benstaf = pd.read_parquet(url_benstaf)
    for idx, r in df_benstaf.iterrows():
        sym = r['Stock_symbol']
        if sym in TARGET_TICKERS:
            news_records.append({
                'ticker': sym,
                'datetime': str(r['Date'])[:19],
                'headline': str(r['Article_title']),
                'source': 'NASDAQ_FNSPID',
                'publisher': str(r['Publisher']),
                'url': str(r['Url'])
            })
except Exception as e:
    print(f"    Nota: benstaf no disponible online o error: {e}")

df_all_news = pd.DataFrame(news_records)
print(f"Total noticias en bruto recolectadas: {len(df_all_news):,} filas.")

# Parsear fechas y deduplicar
df_all_news['dt'] = pd.to_datetime(df_all_news['datetime'], errors='coerce')
df_all_news = df_all_news.dropna(subset=['dt', 'headline'])
df_all_news['headline_clean'] = df_all_news['headline'].str.lower().str.strip()
df_all_news = df_all_news.drop_duplicates(subset=['ticker', 'dt', 'headline_clean'])
print(f"Total noticias tras deduplicar: {len(df_all_news):,} filas.")

# Asignar fecha de sesión bursátil efectiva (trading_date)
# Si la noticia sale después de las 16:00 (o fin de semana), afecta a la siguiente sesión
df_all_news['news_date'] = df_all_news['dt'].dt.date
df_all_news['news_hour'] = df_all_news['dt'].dt.hour
# Si es después de las 16h o fin de semana, sumamos 1 día como aproximación de sesión
df_all_news['effective_date'] = pd.to_datetime(
    np.where(df_all_news['news_hour'] >= 16, 
             df_all_news['dt'] + pd.Timedelta(days=1), 
             df_all_news['dt'])
).date

# 4. Agregación Diaria de Noticias
print("Agregando noticias por sesión bursátil...")
daily_news_grouped = df_all_news.groupby(['ticker', 'effective_date']).agg(
    n_news=('headline', 'count'),
    headlines_concat=('headline', lambda s: ' [SEP] '.join(list(dict.fromkeys(s))[:5])), # Top 5 noticias del día
    sources=('source', lambda s: ', '.join(set(s)))
).reset_index()
daily_news_grouped['date'] = pd.to_datetime(daily_news_grouped['effective_date'])

# 5. Fusionar Precios y Noticias a nivel Diario (Panel Aligned)
print("Fusionando panel de precios con noticias agregadas...")
df_aligned = pd.merge(df_all_prices, daily_news_grouped[['ticker', 'date', 'n_news', 'headlines_concat', 'sources']], 
                      on=['ticker', 'date'], how='left')

df_aligned['n_news'] = df_aligned['n_news'].fillna(0).astype(int)
df_aligned['has_news'] = df_aligned['n_news'] > 0
df_aligned['headlines_concat'] = df_aligned['headlines_concat'].fillna("")

# 6. Partición Estricta en TRAIN / VAL / TEST
print("Aplicando partición temporal estricta...")

# Fechas de corte
TRAIN_START = pd.Timestamp('2011-01-01')
TRAIN_END   = pd.Timestamp('2018-12-31')

VAL_START   = pd.Timestamp('2019-01-01')
VAL_END     = pd.Timestamp('2020-06-10')

# BUFFER / EMBARGO: 2020-06-11 a 2021-08-16

TEST_START  = pd.Timestamp('2021-08-17')
TEST_END    = pd.Timestamp('2023-12-31')

splits_def = {
    'train': (TRAIN_START, TRAIN_END),
    'val':   (VAL_START,   VAL_END),
    'test':  (TEST_START,  TEST_END)
}

summary_stats = []

for split_name, (start_dt, end_dt) in splits_def.items():
    print(f"\n--- Generando Split: {split_name.upper()} ({start_dt.date()} a {end_dt.date()}) ---")
    
    # Filtrar precios
    p_split = df_all_prices[(df_all_prices['date'] >= start_dt) & (df_all_prices['date'] <= end_dt)].copy()
    p_split.to_parquet(f"{SPLITS_DIR}/{split_name}/prices.parquet", index=False)
    p_split.to_csv(f"{SPLITS_DIR}/{split_name}/prices.csv.gz", index=False, compression='gzip')
    
    # Filtrar noticias individuales
    n_split = df_all_news[(df_all_news['dt'] >= start_dt) & (df_all_news['dt'] <= end_dt)].copy()
    n_split.to_parquet(f"{SPLITS_DIR}/{split_name}/news.parquet", index=False)
    n_split.to_csv(f"{SPLITS_DIR}/{split_name}/news.csv.gz", index=False, compression='gzip')
    
    # Filtrar panel diario alineado
    a_split = df_aligned[(df_aligned['date'] >= start_dt) & (df_aligned['date'] <= end_dt)].copy()
    a_split.to_parquet(f"{SPLITS_DIR}/{split_name}/daily_aligned.parquet", index=False)
    a_split.to_csv(f"{SPLITS_DIR}/{split_name}/daily_aligned.csv.gz", index=False, compression='gzip')
    
    # Métricas del split
    n_sessions = len(p_split['date'].unique())
    n_prices = len(p_split)
    n_news_total = len(n_split)
    n_days_with_news = len(a_split[a_split['has_news']])
    pct_days_news = (n_days_with_news / len(a_split) * 100) if len(a_split) > 0 else 0
    
    # Balance de clases
    up_cnt = (a_split['target_dir_1d'] == 1).sum()
    down_cnt = (a_split['target_dir_1d'] == -1).sum()
    neutral_cnt = (a_split['target_dir_1d'] == 0).sum()
    
    summary_stats.append({
        'split': split_name.upper(),
        'start': str(start_dt.date()),
        'end': str(end_dt.date()),
        'years': round((end_dt - start_dt).days / 365.25, 2),
        'trading_sessions': n_sessions,
        'total_price_rows': n_prices,
        'total_news_rows': n_news_total,
        'aligned_rows': len(a_split),
        'days_with_news': n_days_with_news,
        'pct_days_with_news': round(pct_days_news, 1),
        'up_pct': round(up_cnt / len(a_split) * 100, 1),
        'down_pct': round(down_cnt / len(a_split) * 100, 1),
        'neutral_pct': round(neutral_cnt / len(a_split) * 100, 1)
    })
    
    print(f"  Precios: {n_prices:,} filas ({n_sessions} sesiones bursátiles)")
    print(f"  Noticias: {n_news_total:,} artículos")
    print(f"  Días con noticias: {n_days_with_news:,} ({pct_days_news:.1f}%)")
    print(f"  Distribución target 1d: Sube {up_cnt/len(a_split)*100:.1f}% | Baja {down_cnt/len(a_split)*100:.1f}% | Plano {neutral_cnt/len(a_split)*100:.1f}%")

# 7. Escribir Resumen Ejecutivo en Markdown
md_lines = [
    "# Resumen Ejecutivo de Splits de Datos para el TFM",
    "",
    "> **Estrategia Metodológica:** Partición estrictamente temporal (*Walk-Forward*) con **Purged Embargo Buffer** entre entrenamiento y test para garantizar cero fuga de información (*zero data leakage*) y evaluación fuera de muestra (*out-of-sample*).",
    "",
    "## 1. Tabla Comparativa de las Particiones",
    "",
    "| Partición | Rango de Fechas | Duración | Sesiones Mercado | Filas Precios | Total Noticias | Días con Noticias | Distribución Target 1D (Sube / Baja / Plano) |",
    "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
]

for s in summary_stats:
    md_lines.append(
        f"| **{s['split']}** | `{s['start']} a {s['end']}` | {s['years']} años | {s['trading_sessions']} | {s['total_price_rows']:,} | {s['total_news_rows']:,} | {s['days_with_news']:,} ({s['pct_days_with_news']}%) | {s['up_pct']}% / {s['down_pct']}% / {s['neutral_pct']}% |"
    )

md_lines.extend([
    "",
    "---",
    "",
    "## 2. Definición y Justificación de Cada Split",
    "",
    "### 🔵 TRAIN SET (2011-01-01 a 2018-12-31)",
    "* **Objetivo:** Aprendizaje de representaciones textuales y dinámicas de precios en un ciclo económico secular.",
    "* **Fuente principal:** Noticias financieras de Benzinga + precios OHLCV diarios.",
    "* **Propiedad:** Mercado con tipos de interés al 0%, baja inflación y crecimiento de empresas tecnológicas.",
    "",
    "### 🟡 VALIDATION SET (2019-01-01 a 2020-06-10)",
    "* **Objetivo:** Selección de hiperparámetros, ajuste de la arquitectura temporal (Jev / Transformer / LSTM) y calibración de *early stopping*.",
    "* **Propiedad:** Incluye la fase final del ciclo alcista y el shock de volatilidad extremo de la pandemia (febrero-marzo 2020).",
    "",
    "### 🛡️ BUFFER / EMBARGO (2020-06-11 a 2021-08-16)",
    "* **Duración:** 14 meses.",
    "* **Función:** **Embargo temporal natural (*Purged Split*).** Garantiza que no exista ningún sesgo de anticipación o inercia residual a corto plazo entre la optimización del modelo y la evaluación final.",
    "",
    "### 🟢 TEST SET OUT-OF-SAMPLE (2021-08-17 a 2023-12-31)",
    "* **Objetivo:** **Prueba de fuego final del TFM.** Evaluación estricta fuera de muestra simulando el despliegue del modelo en condiciones reales de mercado.",
    "* **Fuente principal:** FNSPID (NASDAQ) con textos completos y resúmenes estructurados.",
    "* **Propiedad:** Régimen macroeconómico opuesto al de entrenamiento (inflación elevada, subidas agresivas de tipos de la Fed, mercado bajista de 2022 y boom de la IA en 2023).",
    "",
    "---",
    "",
    "## 3. Estructura de Archivos Generados",
    "Los datos están listos para ser consumidos en PyTorch, Hugging Face Transformers o Scikit-Learn en formato Parquet de alto rendimiento y CSV comprimido:",
    "",
    "```",
    "data/splits/",
    "├── train/",
    "│   ├── prices.parquet         # Cotizaciones OHLCV y retornos futuros (ret_1d, ret_3d, ret_5d)",
    "│   ├── news.parquet           # Noticias individuales con fecha y titular",
    "│   └── daily_aligned.parquet  # Panel diario alineado (Precios + Titulares concatenados [SEP])",
    "├── val/",
    "│   ├── prices.parquet",
    "│   ├── news.parquet",
    "│   └── daily_aligned.parquet",
    "└── test/",
    "    ├── prices.parquet",
    "    ├── news.parquet",
    "    └── daily_aligned.parquet",
    "```"
])

summary_content = "\n".join(md_lines)
with open(f"{SPLITS_DIR}/SPLIT_SUMMARY.md", "w", encoding="utf-8") as f:
    f.write(summary_content)

print(f"\nResumen guardado con éxito en {SPLITS_DIR}/SPLIT_SUMMARY.md")
print("Pipeline de partición completado.")
