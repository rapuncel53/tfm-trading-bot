"""Microestudio multi-ticker: contamination por subcadena segun longitud de ticker.
Fuente: All_external head 200 MB (3,863 tickers, multilinea).
Reglas:
  FALSO  : el ticker aparece SOLO como subcadena de OTRO ticker conocido (AAL.L, GA...),
           o el articulo es claramente de otra empresa (heuristicas fuertes).
  SECTOR : noticia de industria/mercado, menciona el ticker como uno mas de una lista.
  REAL   : menciona la empresa por nombre o "(TICKER)".
  AMBIG  : resto.
Se mide ademas: densidad de menciones del ticker dentro del cuerpo vs titulo.
"""
import csv, io, re, json, sys
import pandas as pd

csv.field_size_limit(10**9)

PATH = 'data/raw_allext_head.bin'
raw = open(PATH, 'rb').read().decode('utf-8', 'replace')
raw = raw[:raw.rfind('\n')]
rd = csv.reader(io.StringIO(raw, newline=''))
hdr = next(rd)

TICKERS = {  # subcadenas-dian para detectar colisiones: ticker mas largo que contenga otro
}

def load_rows():
    rows = []
    for r in rd:
        if len(r) >= 11:
            rows.append(r)
    return rows

def name_from_title(sym, title, body):
    """Heuristica de entity linking barato:
    - busqueda del ticker entre parentesis (TICKER) o Symbol: TICKER
    - busqueda del nombre empresa derivado: no tenemos mapa, usamos co-ocurrencia"""
    pass

def classify(sym, title, body, title_of_other):
    t = (title or '') + ' ' + (body or '')[:400]
    # 1) el ticker aparece como (SYM) en titulo/cuerpo -> real-ish
    paren = re.search(r'\(' + re.escape(sym) + r'\)', t)
    # 2) colision: SYM aparece dentro de otra palabra con punto detras/adelante
    collide = re.search(r'\b[A-Z0-9]{1,8}\.' + re.escape(sym) + r'\b', t) or \
              re.search(r'\b' + re.escape(sym) + r'\.[A-Z]{1,3}\b', t)
    # 3) solo aparece como parte de otra palabra (sin borde)
    if collide and not paren:
        return 'FALSO_colision'
    if paren:
        # ?es lista de varios tickers? -> sector
        others = re.findall(r'\(([A-Z0-9]{1,5})\)', t)
        if len(others) >= 3:
            return 'SECTOR_lista'
        return 'REAL_parentesis'
    # sin paren: menciones de borde
    hits = len(re.findall(r'\b' + re.escape(sym) + r'\b', t))
    if hits >= 2:
        return 'REAL_multi'
    if hits == 1:
        return 'DEBIL_mencion1'
    return 'AMBIGUO'

rows = load_rows()
df = pd.DataFrame(rows, columns=hdr[:len(rows[0])] if len(hdr)>=len(rows[0]) else None)
df = df[df['Stock_symbol'].str.match(r'^[A-Z]{1,6}$', na=False)]
df['sym_len'] = df['Stock_symbol'].str.len()

df['clase'] = [classify(s, ti, ar, None) for s, ti, ar in
               zip(df['Stock_symbol'], df['Article_title'], df['Article'])]

print("=== Clasificacion global (3,863 tickers, 892k filas) ===")
print(df['clase'].value_counts().to_string())

g = df.groupby(['sym_len', 'clase']).size().unstack(fill_value=0)
g['total'] = g.sum(axis=1)
g['%FALSO'] = (g['FALSO_colision'] / g['total'] * 100).round(1)
g['%REAL'] = ((g['REAL_parentesis'] + g['REAL_multi']) / g['total'] * 100).round(1)
g['%DEBIL'] = (g['DEBIL_mencion1'] / g['total'] * 100).round(1)
print("\n=== Contaminacion por LONGITUD del ticker ===")
print(g[['total','%FALSO','%REAL','%DEBIL']].to_string())

# tickers cortos con mas colisiones
short = df[df['sym_len'] <= 3]
fra = short.groupby('Stock_symbol')['clase'].apply(lambda s: (s=='FALSO_colision').mean()*100)
tot = short.groupby('Stock_symbol').size()
worst = pd.DataFrame({'%falso': fra.round(1), 'n': tot}).query('n > 200').sort_values('%falso', ascending=False)
print("\n=== Top 15 peores tickers cortos (n>200) ===")
print(worst.head(15).to_string())

df[['Stock_symbol','Date','Article_title','Url','Publisher','Author','Article','clase']].to_csv('data/allext_classified_head.csv.gz', index=False, compression='gzip')
g.to_csv('data/contaminacion_por_longitud.csv')
print("\nGuardados: data/contaminacion_por_longitud.csv, data/allext_classified_head.csv.gz")
