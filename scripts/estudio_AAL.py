"""Microestudio AAL: extrae todas las noticias con Stock_symbol==AAL de los
cabezones de los dos ficheros grandes, y las clasifica:
  - noticia REAL de American Airlines
  - falsa por subcadena (AAL.L = Anglo American, Air Canada, etc.)
  - macro/general
Incluye audit de titular-vs-direccion del dia siguiente.
"""
import io, re, json
import pandas as pd, difflib, textwrap

TARGET = 'AAL'   # American Airlines Group (NASDAQ)

def load_head(path):
    """Lee el cabezon de un CSV (descarga desde byte 0 -> la 1a linea ES la cabecera)."""
    raw = open(path, 'rb').read()
    text = raw.decode('utf-8', 'replace')
    # la ultima linea puede estar tronzada por el corte de bytes -> la quitamos
    k = text.rfind('\n')
    text = text[:k]
    df = pd.read_csv(io.StringIO(text), engine='python', on_bad_lines='skip')
    return df

# ---------- 1. Extraer ----------
nas = load_head('data/raw_nasdaq_head.bin')
ale = load_head('data/raw_allext_head.bin')
print(f"nasdaq_head: {len(nas):>7} filas | columnas: {list(nas.columns)[:4]}...")
print(f"allext_head: {len(ale):>7} filas | columnas: {list(ale.columns)[:4]}...")

nas['Stock_symbol'] = nas['Stock_symbol'].astype(str).str.strip()
ale['Stock_symbol'] = ale['Stock_symbol'].astype(str).str.strip()

nasA = nas[nas['Stock_symbol'] == TARGET].copy(); nasA['fuente'] = 'nasdaq'
aleA = ale[ale['Stock_symbol'] == TARGET].copy(); aleA['fuente'] = 'allext'
print(f"\nFilas con symbol==AAL -> nasdaq_head: {len(nasA)} | allext_head: {len(aleA)}")

# hasta donde llega cada cabezon (fecha max del tramo AAL) para honestidad
for nm, d in [('nasdaq', nas), ('allext', ale)]:
    last = d[d['Stock_symbol'] == TARGET] if 'Stock_symbol' in d else None
    print(f"  {nm}: ultimo ticker del cabezon = {d['Stock_symbol'].iloc[-1]!r} "
          f"(el cabezon de 200MB cubre A..{d['Stock_symbol'].iloc[-1]})")

# ---------- 2. Fusionar y deduplicar ----------
cols = ['Date','Article_title','Stock_symbol','Url','Publisher','Author','Article','fuente']
for c in cols:
    if c not in nasA.columns: nasA[c] = None
    if c not in aleA.columns: aleA[c] = None
A = pd.concat([nasA[cols], aleA[cols]], ignore_index=True)
A['Date'] = pd.to_datetime(A['Date'].astype(str).str.replace(' UTC','',regex=False), format='mixed', errors='coerce')
A = A.dropna(subset=['Date','Article_title'])
A['titulo_norm'] = A['Article_title'].str.lower().str.strip().str.slice(0,120)
dup = A.duplicated(subset=['titulo_norm','Date'], keep='first')
print(f"Total fusionado: {len(A)} | duplicados titulo+fecha eliminados: {dup.sum()} -> {len(A)-int(dup.sum())}")
A = A[~dup].sort_values('Date').reset_index(drop=True)

# ---------- 3. Clasificar: es realmente American Airlines? ----------
# pistas de Anglo American en texto: AAL.L / Anglo American / Kumba / iron ore
# pistas de Air Canada: Air Canada, ACDVF
AA_TRUE = re.compile(r'\bamerican airlines|american\s+airlines|a\.a\. group|aabeoy|advantage\s*pay|a\.com\b', re.I)
FALSE_HINT = [
    (re.compile(r'\baal\.l\b|anglo american|kumba iron|iron ore|mining', re.I), 'Anglo American (AAL.L, Londres)'),
    (re.compile(r'air canada|acdvf|achr\b', re.I), 'Air Canada (ACDVF)'),
]
MACRO = re.compile(r'stock[s]? (that|market|moving|movers)|market update|52-week|most active|roundup|sector|etf|dow jones|s&p 500|spx|spy|bond[s]? (rout|yields|sell)|fed\b|inflation', re.I)

def classify(row):
    t = str(row['Article_title']) + ' ' + str(row['Article'])[:600]
    for rx, label in FALSE_HINT:
        if rx.search(t) and not AA_TRUE.search(t):
            return 'FALSO:' + label
    if AA_TRUE.search(t):
        return 'VERDADERO (AA)'
    if MACRO.search(str(row['Article_title'])) and not AA_TRUE.search(t):
        return 'MACRO/general'
    return 'AMBIGUO (revisar)'

A['clase'] = A.apply(classify, axis=1)
print("\n=== CLASIFICACION ===")
print(A['clase'].value_counts().to_string())
print(f"\nPrecision estimada sobre 'símbolo==AAL': "
      f"{(A['clase']=='VERDADERO (AA)').mean()*100:.1f}% noticias realmente de American Airlines")

# ---------- 4. Duplicados tematicos (novedad) sobre las VERDADERAS ----------
V = A[A['clase']=='VERDADERO (AA)'].copy()
seen_titles = []
def novedad(t, vistos):
    if not vistos: return 1.0
    return round(1 - max(difflib.SequenceMatcher(None, t.lower()[:140], v.lower()[:140]).ratio() for v in vistos), 2)
V['nov'] = [novedad(t, seen_titles + []) for t in V['Article_title']]
print(f"\nVERDADERAS: {len(V)} | novedad<0.35 (casi-repetida): {int((V['nov']<0.35).sum())} "
      f"({(V['nov']<0.35).mean()*100:.0f}%)")

# ---------- 5. Colision dia-empresa ----------
by_day = V.groupby(V['Date'].dt.normalize()).size()
print(f"\nCOLISION: {int((by_day>1).sum())} dias con >1 noticia (max {int(by_day.max())} en un dia)")
print(f"  dias-empresa (unidades de label): {len(by_day)} vs {len(V)} noticias -> "
      f"reduccion del {(1-len(by_day)/len(V))*100:.0f}%")

# ---------- 6. Etiqueta direccion vs noticia (audit solo VERDADERAS) ----------
px = pd.read_csv(f'data/prices/full_history/{TARGET}.csv')
px['date'] = pd.to_datetime(px['date']); px = px.sort_values('date')
px['ret'] = px['adj close'].pct_change()*100
V['d0'] = V['Date'].dt.normalize()
def next_ret(row):
    after = row['Date'].time() != pd.Timestamp('00:00:00').time()
    nxt = px[(px['date'] > row['d0'])] if after else px[(px['date'] >= row['d0'] + pd.Timedelta(days=1))]
    return nxt.iloc[0]['ret'] if len(nxt) else None
V['ret_d1'] = V.apply(next_ret, axis=1)
lab = V.dropna(subset=['ret_d1'])
print(f"\n=== AUDIT DIRECTIONAL (n={len(lab)} verdaderas con etiqueta) ===")
print(f"  SUBE: {(lab['ret_d1']>0).sum()}  BAJA: {(lab['ret_d1']<0).sum()}")

# firmas de titulares
print("\n--- 12 ejemplos VERDADERAS con novedad ---")
for _, r in V.nlargest(12, 'Date').iterrows():
    print(f"{r['Date'].date()} nov={r['nov']:.2f} [{r['fuente']:6s}] {str(r['Article_title'])[:78]}")

print("\n--- 12 ejemplos FALSOS (roban ticker por subcadena) ---")
for _, r in A[A['clase'].str.startswith('FALSO')].head(12).iterrows():
    print(f"{r['Date'].date()} {r['clase'][:28]:28s} {str(r['Article_title'])[:60]}")

# resumen JSON para el informe
V.to_csv('data/estudio_AAL_verdaderas.csv', index=False)
A.to_csv('data/estudio_AAL_clasificadas.csv', index=False)
summary = dict(total=len(A), verdaderas=int((A['clase']=='VERDADERO (AA)').sum()),
               falsos=int(A['clase'].str.startswith('FALSO').sum()),
               macro=int((A['clase']=='MACRO/general').sum()),
               ambiguos=int((A['clase']=='AMBIGUO (revisar)').sum()),
               dup_titulo=int(dup.sum()))
print("\nJSON:", json.dumps(summary))
