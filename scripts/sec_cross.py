"""Cruzamiento de universos con fuente autorizada externa (SEC EDGAR):
  - tickers de PRECIOS (7,693 CSV) 
  - tickers de NOTICIAS (head All_external 200MB + muestra nasdaq)
  - tickers oficiales SEC (10,422) con su nombre legal
Mide: intersecciones, tickers FNSPID validados por SEC, nombres que el periodismo
no usa nunca (GOOG->Google), y % de noticias cuyo titular menciona el nombre oficial.
"""
import csv, io, json, re, glob, os
import pandas as pd

csv.field_size_limit(10**9)

# ---------- cargar SEC ----------
sec = json.load(open('data/sec_tickers.json'))
sec_t = {}
for v in sec.values():
    sec_t[v['ticker'].upper()] = v['title']
print(f"SEC: {len(sec_t)} tickers oficiales")

# ---------- universos locales ----------
price_syms = {os.path.basename(f)[:-4] for f in glob.glob('data/prices/full_history/*.csv')}
raw = open('data/raw_allext_head.bin','rb').read().decode('utf-8','replace')
raw = raw[:raw.rfind('\n')]
rd = csv.reader(io.StringIO(raw, newline=''))
next(rd)
news_rows = [r for r in rd if len(r) >= 11]
news_syms = {r[2].strip() for r in news_rows}
print(f"precios: {len(price_syms)} | noticias(head): {len(news_syms)}")

# ---------- intersecciones ----------
P_SEC = price_syms & set(sec_t)
N_SEC = news_syms & set(sec_t)
P_N   = price_syms & news_syms
print(f"\nprecios ∩ SEC   : {len(P_SEC)} ({len(P_SEC)/len(price_syms)*100:.1f}% de precios validados)")
print(f"noticias ∩ SEC  : {len(N_SEC)} ({len(N_SEC)/len(news_syms)*100:.1f}% de noticias validadas)")
print(f"precios ∩ noticias: {len(P_N)} ({len(P_N)/len(price_syms)*100:.1f}% de precios con noticias)")
print(f"noticias SIN precios: {len(news_syms - price_syms)}")
print(f"precios SIN SEC (ETFs/otros): {len(price_syms - set(sec_t))}")

# ---------- nombres: SEC oficial vs lo que usan los artículos ----------
SUF = re.compile(r'\b(inc|corp|corporation|co|company|ltd|plc|sa|ag|nv|lp|llc|holdings?|group|the)\b', re.I)
def core(t):
    toks = [w for w in re.sub(r'[^A-Za-z0-9& ]', ' ', t).split() if w.lower() not in
            ('inc','corp','corporation','co','company','ltd','plc','sa','ag','nv','lp','llc',
             'holdings','holding','group','the','and','of')]
    return toks

# muestrear titulares por ticker y ver si el nombre oficial esta presente
from collections import defaultdict
by_sym = defaultdict(list)
for r in news_rows:
    s = r[2].strip()
    if s in sec_t and len(by_sym[s]) < 60:
        by_sym[s].append(str(r[1]))

hits, misses_examples = [], []
for sym, titles in by_sym.items():
    toks = [t.lower() for t in core(sec_t[sym]) if len(t) >= 3]
    if not toks: continue
    okc = 0
    for ti in titles:
        til = ' ' + re.sub(r'[^a-z0-9 ]', ' ', ti.lower()) + ' '
        if all(f' {t} ' in til for t in toks):
            okc += 1
    frac = okc / len(titles)
    hits.append((sym, frac, len(titles), sec_t[sym]))

H = pd.DataFrame(hits, columns=['sym','frac','n','sec_name'])
print(f"\n=== % del tiempo que el titular usa el NOMBRE OFICIAL SEC ({len(H)} tickers muestreados) ===")
print(f"media ponderada: {(H['frac']*H['n']).sum()/H['n'].sum()*100:.1f}%")
print(f"tickers donde NUNCA aparece (frac=0, n>=30): {(H[(H['frac']==0)&(H['n']>=30)]).shape[0]}")
print("\nEjemplos de frac=0 (el periodismo usa OTRO nombre):")
for _, r in H[(H['frac']==0)&(H['n']>=30)].head(15).iterrows():
    print(f"  {r['sym']:7s} SEC={r['sec_name'][:45]!r}")
print("\nEjemplos de frac=1 (SEC == uso periodistico):")
for _, r in H[(H['frac']>=0.95)&(H['n']>=30)].head(8).iterrows():
    print(f"  {r['sym']:7s} SEC={r['sec_name'][:45]!r}")

H.to_csv('data/sec_nombre_vs_uso.csv', index=False)
json.dump({'P_SEC':len(P_SEC),'N_SEC':len(N_SEC),'P_N':len(P_N)}, open('data/universos.json','w'))
print("\nGuardados: data/sec_nombre_vs_uso.csv, data/universos.json")
