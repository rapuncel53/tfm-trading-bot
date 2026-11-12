"""Contaminacion por longitud de ticker a escala.
Usa el head de 200MB de nasdaq_exteral_data (cubre A..ABM: 25 tickers completos,
longitudes 1-5, texto real). Para cada noticia comprueba si el ticker-objeto esta
REALMENTE mencionado (simbolo con borde O nombre empresa), y si hay SENAL de otro.
Metrica clave: % de noticias SIN ninguna pista del ticker asignado (etiquetado puro
de metadatos) y % con pista de otra empresa.
"""
import csv, io, re, json, collections
import pandas as pd

csv.field_size_limit(10**9)
raw = open('data/raw_nasdaq_head.bin','rb').read().decode('utf-8','replace')
raw = raw[:raw.rfind('\n')]
rd = csv.reader(io.StringIO(raw, newline=''))
hdr = next(rd)
rows = [r for r in rd if len(r) >= 12]
df = pd.DataFrame(rows, columns=hdr)
df['Stock_symbol'] = df['Stock_symbol'].str.strip()
# solo tickers completos dentro del bloque (excluir el ultimo, troncado)
cnt = df['Stock_symbol'].value_counts()
df = df[df['Stock_symbol'].isin(cnt[cnt.index[:-1]].index)]
print(f"filas: {len(df):,} | tickers: {df['Stock_symbol'].nunique()}")

# ---------- minar nombres empresa del propio dataset (nasdaq estilo "Name (SYM)") ----------
PAT = re.compile(r'([A-Za-z][A-Za-z&\'\.\- ]{2,40}?)\s*\(([A-Z][A-Z0-9.\-]{0,5})\)')
PAT2 = re.compile(r'Name:\s*([A-Za-z][A-Za-z&\'\.\-, ]{2,60}?)\s*\n')
names = collections.defaultdict(collections.Counter)
for ti in df['Article_title']:
    for nm, sym in PAT.findall(str(ti)):
        nm = nm.strip().strip(',')
        if ',' in nm: nm = nm.split(',')[0]
        names[sym.strip()][nm.strip()] += 1

mined = {}
for sym, ctr in names.items():
    if not ctr: continue
    top, c = ctr.most_common(1)[0]
    tot = sum(ctr.values())
    if c >= 3 and c/tot >= 0.4 and 2 < len(top) <= 40:
        mined[sym] = top
print(f"nombres minados: {len(mined)}")
for s in ['A','AA','AAAU','AAL','AAPL','ABBV','ABM','AAN','AAOI','AAON','AAP','AAT','AAU','AAXJ','AB']:
    print(f"  {s:6s} -> {mined.get(s)!r}")
json.dump(mined, open('data/name_map_nasdaq.json','w'), ensure_ascii=False, indent=2)

# ---------- clasificar ----------
STOP = {'technologies','technology','group','holdings','holding','inc','corp','corporation',
        'company','co','ltd','plc','sa','ag','nv','lp','llc','the','and','of','industries',
        'international','global','systems','solutions','enterprises','inc.'}
def toks(nm):
    return [w.lower() for w in re.sub(r"[^A-Za-z0-9'& ]",' ',nm).split()
            if w.lower() not in STOP and len(w) >= 3]

name_tok = {s: set(toks(n)) for s, n in mined.items()}
CACHE = {}

def analyze(title, body, sym):
    key = (title, str(body)[:400])
    if key in CACHE: return CACHE[key]
    tx = str(title) + ' ' + str(body)[:800]
    txset = set(re.findall(r"[a-z0-9'&]+", tx.lower()))
    own_sym = re.search(r'(?<![A-Z0-9])' + re.escape(sym) + r'(?![A-Z0-9.$])', tx) is not None
    own_name = sym in name_tok and name_tok[sym] <= txset
    others = [s2 for s2, tt in name_tok.items()
              if s2 != sym and tt and tt <= txset]
    r = (own_sym, own_name, others)
    if len(CACHE) < 300_000: CACHE[key] = r
    return r

def classify(row):
    own_sym, own_name, others = analyze(row['Article_title'], row['Article'], row['Stock_symbol'])
    if own_sym or own_name:
        if others and not own_name:
            return 'AMBIGUA_otro_nombre'
        return 'MENCIONADA'
    if others:
        return 'FALSO_nombre_ajeno'
    return 'SIN_PISTA_metadato'

df['clase'] = df.apply(classify, axis=1)
print("\n=== global ===")
print(df['clase'].value_counts().to_string())

tab = df.groupby('Stock_symbol')['clase'].value_counts().unstack(fill_value=0)
tab['n'] = tab.sum(axis=1)
tab['%mencionada'] = (tab.get('MENCIONADA',0)/tab['n']*100).round(1)
tab['%sin_pista'] = (tab.get('SIN_PISTA_metadato',0)/tab['n']*100).round(1)
tab['%falsa'] = ((tab.get('FALSO_nombre_ajeno',0)+tab.get('AMBIGUA_otro_nombre',0))/tab['n']*100).round(1)
tab['len'] = tab.index.str.len()
print("\n=== por ticker ===")
print(tab[['n','len','%mencionada','%sin_pista','%falsa']].sort_values('%sin_pista', ascending=False).to_string())

g = tab.groupby('len')[['n','%sin_pista','%mencionada']].apply(
    lambda x: pd.Series({'filas': x['n'].sum(),
                         '%sin_pista': (x['%sin_pista']*x['n']).sum()/x['n'].sum(),
                         '%mencionada': (x['%mencionada']*x['n']).sum()/x['n'].sum()}).round(1))
print("\n=== AGREGADO POR LONGITUD DE TICKER ===")
print(g.to_string())
tab.to_csv('data/longitud_tickers.csv')
