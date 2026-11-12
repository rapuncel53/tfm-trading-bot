"""Entity linking con mapa minado LIMPIO:
- extrae nombres via patron "(SYM)" pero solo cuando el nombre NO es una frase (heuristica estricta)
- normaliza: quita 'Shares', 'Stocks', 'to Buy', etc.
- clasifica con matching por tokens distintivos
"""
import csv, io, re, json, collections
import pandas as pd

csv.field_size_limit(10**9)
raw = open('data/raw_allext_head.bin','rb').read().decode('utf-8','replace')
raw = raw[:raw.rfind('\n')]
rd = csv.reader(io.StringIO(raw, newline=''))
hdr = next(rd)
rows = [r for r in rd if len(r) >= 11]
df = pd.DataFrame(rows, columns=hdr)
df['Stock_symbol'] = df['Stock_symbol'].str.strip()
df = df[df['Stock_symbol'].str.match(r'^[A-Z][A-Z0-9.\-]{0,6}$', na=False)]

# ---------- 1. Minería LIMPIA de nombres ----------
PAT = re.compile(r'([A-Za-z][A-Za-z&\'\-\. ]{1,40}?)\s*\(([A-Z][A-Z0-9.\-]{0,6})\)')
BAD_WORDS = set('''shares stock stocks buy sell why how what is are the this that week day today after
before vs or and to for in on with now here you should expect gains drop rally surge sinks rises falls
maintains upgrades downgrades initiates reiterate cuts raises pt target earnings report quarterly'''.split())

names = collections.defaultdict(collections.Counter)
for txt in df['Article_title']:
    for nm, sym in PAT.findall(str(txt)):
        if not re.match(r'^[A-Z][A-Z0-9.\-]{0,6}$', sym): continue
        nm = nm.strip().strip(',').strip()
        nm = re.sub(r'^(shares of|shares in)\s+', '', nm, flags=re.I)
        if ',' in nm: nm = nm.split(',')[0].strip()
        toks = nm.split()
        # rechazar frases: >5 tokens, o cualquier token de ruido, o todo en minusculas
        if not (1 <= len(toks) <= 5): continue
        if any(t.lower() in BAD_WORDS for t in toks): continue
        if not any(c.isupper() for c in nm): continue
        if len(nm) < 3: continue
        names[sym][nm] += 1

mined = {}
for sym, ctr in names.items():
    top, c = ctr.most_common(1)[0]
    tot = sum(ctr.values())
    if c >= 5 and c/tot >= 0.4:
        mined[sym] = top
print(f"mapa limpio: {len(mined)} tickers")
for s in ['AAPL','TSLA','MSFT','A','AA','GE','IBM','F','XOM','AAL','ABBV','GOLO','GOGO','BPOP','GEF']:
    print(f"  {s:6s} -> {mined.get(s)!r}")
json.dump(mined, open('data/name_map.json','w'), ensure_ascii=False)

# ---------- 2. Match por token mediante indice invertido (rapido) ----------
def core_tokens(nm):
    toks = [t.strip('.,') for t in nm.split() if t.strip('.,').lower() not in
            ('inc','corp','co','ltd','plc','sa','ag','nv','the','and','of','&')]
    return [t.lower() for t in toks if len(t) >= 3]

req = {}                       # sym -> frozenset(tokens distintivos)
inv = collections.defaultdict(set)   # token -> {syms que lo necesitan}
for sym, nm in mined.items():
    ts = frozenset(core_tokens(nm))
    if ts:
        req[sym] = ts
        rarest = min(ts, key=lambda t: len(inv[t]) if t in inv else 0)
        for t in ts:
            inv[t].add(sym)

OTHER_SYM = re.compile(r'\(([A-Z][A-Z0-9]{0,5})\)')
B = re.compile

def match_names(tx_low, toks):
    """simbolos cuyo nombre completo aparece en la fila (tokens adyacentes aproximados)."""
    cands = set()
    for t in toks:
        if t in inv:
            cands |= inv[t]
    out = set()
    for s in cands:
        need = req[s]
        if need <= toks:      # approximation: bag-of-words
            out.add(s)
    return out

FOUND_CACHE = {}
def found_cached(title, body):
    key = (title, None if not body else str(body)[:300])
    hit = FOUND_CACHE.get(key)
    if hit is None:
        tx = str(title) + ' ' + (str(body)[:600] if body else '')
        toks = set(re.findall(r"[a-z0-9\.'\-]+", tx.lower()))
        hit = match_names(tx.lower(), toks)
        if len(FOUND_CACHE) < 400_000:
            FOUND_CACHE[key] = hit
    return hit

def classify(sym, title, body):
    tx = str(title) + ' ' + (str(body)[:600] if body else '')
    found = found_cached(title, body)
    own = sym in found
    foreign = found - {sym}
    collide = re.search(r'\b[A-Z0-9]{1,8}\.' + re.escape(sym) + r'\b', tx) or \
              re.search(r'\b' + re.escape(sym) + r'\.[A-Z]{1,3}\b', tx)
    if own:
        return 'SECTOR_lista' if len(OTHER_SYM.findall(str(title))) >= 3 else 'REAL_nombre'
    if foreign:
        if re.search(r'\b' + re.escape(sym) + r'\b', tx):
            return 'DUDOSO_ambos'
        return 'FALSO_ajeno'
    if collide:
        return 'FALSO_colision'
    if re.search(r'\b' + re.escape(sym) + r'\b', tx):
        return 'SIMBOLO_sin_nombre'
    return 'SIN_PISTA'

df['clase'] = [classify(s, ti, ar) for s, ti, ar in
               zip(df['Stock_symbol'], df['Article_title'], df['Article'])]

print("\n=== Clasificacion global (mapa limpio) ===")
print(df['clase'].value_counts().to_string())

clas = df[~df['clase'].isin(['SIN_PISTA'])]
print(f"\nEntre {len(clas):,} clasificables ({len(clas)/len(df)*100:.0f}% del total):")
print((clas['clase'].value_counts()/len(clas)*100).round(1).to_string())

tab = clas.groupby('Stock_symbol')['clase'].value_counts().unstack(fill_value=0)
tab['n'] = tab.sum(axis=1)
for c in ('REAL_nombre','FALSO_ajeno','FALSO_colision','DUDOSO_ambos'):
    if c not in tab: tab[c] = 0
tab['%real']  = (tab['REAL_nombre']/tab['n']*100).round(1)
tab['%falso'] = ((tab['FALSO_ajeno']+tab['FALSO_colision'])/tab['n']*100).round(1)
tab = tab[tab['n'] >= 100].sort_values('%falso', ascending=False)
print("\n=== 12 tickers con MAS contaminacion (n>=100) ===")
print(tab.head(12)[['n','%real','%falso']].to_string())
print("\n=== 12 con MENOS ===")
print(tab.tail(12)[['n','%real','%falso']].to_string())

# distribucion agregada de precision
print(f"\nPrecision media ponderada (REAL sobre clasificables): "
      f"{(tab['REAL_nombre'].sum()/tab['n'].sum())*100:.1f}%")

df.drop(columns=['Lsa_summary','Luhn_summary','Textrank_summary','Lexrank_summary'],
        errors='ignore').to_csv('data/allext_con_mapa.csv.gz', index=False, compression='gzip')
print("Guardado: data/allext_con_mapa.csv.gz")
