"""Analisis del panel: noticias -> etiqueta direccional del dia siguiente.
Metricas por ticker y agregadas:
 - distribucion SUBE/BAJA/PLANO (dias con noticia vs todos los dias)
 - densidad: n_noticias del dia vs |ret_next| (volatilidad) — correlacion
 - efecto de la novedad: dias solo-noticias-duplicadas vs con novedad
 - baseline 'siempre mayoria' y Lift de una regla tonta (signo del ret1 del dia)
Salida: data/panel/ANALISIS.md
"""
import glob, os
import numpy as np
import pandas as pd

PANEL = [l.strip() for l in open('scripts/panel.txt') if l.strip()]
files = glob.glob('data/panel/daily/*.csv')
frames = []
for f in files:
    sym = os.path.basename(f)[:-4]
    m = pd.read_csv(f, parse_dates=['date'])
    if 'ticker' not in m: m['ticker'] = sym
    frames.append(m)
if not frames:
    raise SystemExit('sin daily/*.csv todavia')
A = pd.concat(frames, ignore_index=True)
HN = A[A['has_news']].copy()

lines = []
def out(s=''): lines.append(s); print(s)

out('# Análisis del panel piloto (noticias → dirección día siguiente)')
out()
out(f'- Tickers: **{A["ticker"].nunique()}** | filas día-mercado: **{len(A):,}** | '
    f'días con ≥1 noticia: **{len(HN):,}** ({len(HN)/len(A)*100:.1f}%)')
out(f'- Noticias totales: **{HN["n_news"].sum():,.0f}** | '
    f'únicas (dedup titular normalizado): **{HN["n_unique"].sum():,.0f}** '
    f'→ tasa de duplicación **{(1-HN["n_unique"].sum()/HN["n_news"].sum())*100:.1f}%**')
out()

# --- distribucion de etiquetas ---
out('## 1. Distribución direccional (umbral ±0.3%)')
out()
all_dist = A['label'].value_counts(normalize=True)
hn_dist  = HN['label'].value_counts(normalize=True)
out('| etiqueta | todos los días | días con noticia |')
out('|---|---|---|')
for k in ['SUBE','BAJA','PLANO']:
    out(f'| {k} | {all_dist.get(k,0)*100:.1f}% | {hn_dist.get(k,0)*100:.1f}% |')
base = max(all_dist)
base_lab = all_dist.idxmax(); base = all_dist.max()
out(f'**Baseline mayoritario (siempre `{base_lab}`) sobre todos los días: '
    f'{base*100:.1f}%** — cualquier modelo debe batir esto en el conjunto de días con noticia.')
out()

# --- por ticker ---
out('## 2. Por ticker (solo días con noticia)')
out()
out('| ticker | días | noticias | dup% | SUBE% | BAJA% | PLANO% | media ret_next | |ret_next| medio |')
out('|---|---|---|---|---|---|---|---|---|')
for sym in sorted(HN['ticker'].unique()):
    h = HN[HN['ticker']==sym]
    d = A[A['ticker']==sym]
    dist = h['label'].value_counts(normalize=True)
    dup = 1 - h['n_unique'].sum()/h['n_news'].sum()
    out(f"| {sym} | {len(h)} | {h['n_news'].sum():.0f} | {dup*100:.0f}% | "
        f"{dist.get('SUBE',0)*100:.0f} | {dist.get('BAJA',0)*100:.0f} | {dist.get('PLANO',0)*100:.0f} | "
        f"{h['ret_next'].mean()*100:+.2f}% | {h['ret_next'].abs().mean()*100:.2f}% |")
out()

# --- densidad vs volatilidad ---
out('## 3. ¿Densidad de noticias predice volatilidad?')
out()
hn = HN.dropna(subset=['ret_next'])
c_np = np.corrcoef(np.log1p(hn['n_news']), hn['ret_next'].abs())[0,1]
from scipy import stats as st
r1, p1 = st.spearmanr(hn['n_news'], hn['ret_next'].abs())
r2, p2 = st.spearmanr(hn['n_news'], hn['ret_next'])
out(f'- Spearman ρ(n_noticias, |ret_next|) = **{r1:.3f}** (p={p1:.4f}) — densidad vs volatilidad')
out(f'- Spearman ρ(n_noticias, ret_next)  = **{r2:.3f}** (p={p2:.4f}) — densidad vs dirección')
out()
# por terciles de densidad
hn['tercil'] = pd.qcut(hn['n_news'], 3, duplicates='drop')
g = hn.groupby('tercil').agg(n=('ret_next','size'),
                             vol=('ret_next', lambda s: s.abs().mean()*100),
                             sube=('label', lambda s: (s=='SUBE').mean()*100))
out('| terciles n_noticias/día | días | vol medio | %SUBE |')
out('|---|---|---|---|')
for i, r in g.iterrows():
    out(f'| {i} | {int(r["n"])} | {r["vol"]:.2f}% | {r["sube"]:.1f}% |')
out()

# --- novedad: dias 100% duplicados vs con novedad ---
out('## 4. Efecto de la novedad (dedup de titulares)')
out()
hn['solo_dup'] = hn['n_unique'] <= 0.5 * hn['n_news']
g2 = hn.groupby('solo_dup').agg(n=('ret_next','size'),
                                vol=('ret_next', lambda s: s.abs().mean()*100),
                                sube=('label', lambda s: (s=='SUBE').mean()*100))
out('| ¿día con >50% titulares repetidos? | días | vol medio | %SUBE |')
out('|---|---|---|---|')
for i, r in g2.iterrows():
    out(f'| {"sí (eco)" if i else "no (novedad)"} | {int(r["n"])} | {r["vol"]:.2f}% | {r["sube"]:.1f}% |')
out()

# --- baseline momento ---
out('## 5. Baselines ingenuas en días con noticia')
out()
mom = np.sign(hn['ret1'])
hit = ((mom > 0) & (hn['label']=='SUBE') | (mom < 0) & (hn['label']=='BAJA')).mean()
out(f'- Momentum (mismo signo ret1→ret_next): **{hit*100:.1f}%** direccional (SUBE vs BAJA)')
out(f'- Mayoría absoluta: **{max(hn["label"].value_counts(normalize=True))*100:.1f}%**')
out()
out('## 6. Ventana temporal por ticker (noticias nasdaq)')
out()
out('| ticker | primer día news | último día news | días únicos | años cubiertos |')
out('|---|---|---|---|---|')
for sym in sorted(HN['ticker'].unique()):
    h = HN[HN['ticker']==sym]
    out(f'| {sym} | {h["date"].min().date()} | {h["date"].max().date()} | '
        f'{len(h)} | {h["date"].dt.year.nunique()} |')
out()
open('data/panel/ANALISIS.md','w',encoding='utf-8').write('\n'.join(lines))
print('\n[guardado] data/panel/ANALISIS.md')
