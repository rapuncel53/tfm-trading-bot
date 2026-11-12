"""Dataset final del panel: noticias (bloques nasdaq) + precios limpios -> etiquetas.
Proceso por ticker:
 1. parsea data/windows/SYM.bin -> filas con Stock_symbol == SYM (genuinas)
 2. deduplicado de titulares casi-identicos (normalizados)
 3. agregacion por DIA mercado: n_noticias, n_novedad (dedup), fuentes
 4. alinea con dias de trading del CSV de precios; la noticia del dia t
    etiqueta el retorno del SIGUIENTE dia de trading (evita lookahead)
 5. etiqueta: ret1d > +0.3% => SUBE, < -0.3% => BAJA, else PLANO; y ret bruto
Salida: data/panel/dataset_parquet (por ticker) + data/panel/panel_stats.csv
"""
import os, re, io, csv, glob
import numpy as np
import pandas as pd

csv.field_size_limit(10**9)
PANEL = [l.strip() for l in open('scripts/panel.txt') if l.strip()]
OUT = 'data/panel'
os.makedirs(f'{OUT}/daily', exist_ok=True)
THRESH = 0.003   # ±0.3% umbral direccional

DATE_RX = re.compile(r'^\d{4}-\d\d-\d\d')

def norm_title(t):
    t = re.sub(r'[^a-z0-9 ]', ' ', str(t).lower())
    return re.sub(r'\s+', ' ', t).strip()

def load_news(sym):
    p = f'data/windows/{sym}.bin'
    if not os.path.exists(p): return None
    raw = open(p, 'rb').read()
    raw = raw[:raw.rfind(b'\n')]
    rd = csv.reader(io.StringIO(raw.decode('utf-8','replace'), newline=''))
    try: next(rd)
    except StopIteration: return None
    rows = []
    seen = set()
    for r in rd:
        if len(r) < 12: continue
        if r[3].strip() != sym: continue
        fecha = r[1].replace(' UTC','').strip()
        if not DATE_RX.match(fecha): continue
        dt = pd.to_datetime(fecha[:19], errors='coerce')
        if pd.isna(dt): continue
        title = r[2].strip()
        key = norm_title(title)
        if not key: continue
        dup = key in seen
        seen.add(key)
        rows.append((dt.date(), dup, r[0].strip(), len(title), title))
    return rows

report = []
frames = []
for sym in PANEL:
    price = pd.read_csv(f'data/panel/prices/{sym}.csv', parse_dates=['date'])
    price = price.sort_values('date').reset_index(drop=True)
    price['ret_next'] = price['close'].shift(-1) / price['close'] - 1
    news = load_news(sym)
    if news is None:
        report.append(dict(sym=sym, err='sin_bin'))
        continue
    nd = pd.DataFrame(news, columns=['datetime','dup','url','tlen','title'])
    daily = (nd.groupby('datetime')
               .agg(n_news=('title','size'),
                    n_unique=('dup', lambda s: int((~s).sum())),
                    titles=('title', lambda s: ' || '.join(s[:3])[:400]),
                    urls=('url', lambda s: s[:3]))
               .reset_index())
    daily['date'] = pd.to_datetime(daily['datetime'])
    # unir con precios: la noticia del dia t -> ret del dia t+1 mercado
    m = price.merge(daily, on='date', how='left')
    m['has_news'] = m['n_news'].notna()
    m = m[m['ret_next'].notna() | m['has_news']]
    m['ticker'] = sym
    m['label'] = np.where(m['ret_next'] > THRESH, 'SUBE',
                  np.where(m['ret_next'] < -THRESH, 'BAJA', 'PLANO'))
    m.to_csv(f'{OUT}/daily/{sym}.csv', index=False)
    frames.append(m[m['has_news']])
    hn = m[m['has_news']]
    # ventana de la news real
    dmin, dmax = hn['date'].min(), hn['date'].max()
    yrs = hn['date'].dt.year.nunique()
    lab = hn['label'].value_counts(normalize=True)
    report.append(dict(
        sym=sym, err=None,
        news_total=int(hn['n_news'].sum()),
        news_unicas=int(hn['n_unique'].sum()),
        dias_con_news=int(len(hn)),
        d0=str(dmin.date()), d1=str(dmax.date()), anios=yrs,
        densidad_diaria=round(len(hn)/max(yrs*252,1), 2),
        pct_subes=round(float(lab.get('SUBE',0)),3),
        pct_baja=round(float(lab.get('BAJA',0)),3),
        pct_plano=round(float(lab.get('PLANO',0)),3),
        mean_ret_next=round(float(hn['ret_next'].mean()),5),
    ))
    print(f"[{sym}] {report[-1]['news_total']} noticias en {report[-1]['dias_con_news']} dias "
          f"| ventana {dmin.date()}->{dmax.date()} | {lab.to_dict()}", flush=True)

R = pd.DataFrame(report)
R.to_csv(f'{OUT}/panel_stats.csv', index=False)
if frames:
    ALL = pd.concat(frames, ignore_index=True)
    ALL.to_csv(f'{OUT}/dataset_news_labels.csv', index=False)
    print(f"\n=== TOTAL: {len(ALL):,} filas (ticker,dia) con noticia y etiqueta ===")
