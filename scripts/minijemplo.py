import pandas as pd, difflib, textwrap

# ---------- 1. Noticias (muestra texto completo, 23 GB -> 15 MB) ----------
news = pd.read_csv('data/sample_nasdaq.csv', engine='python', on_bad_lines='skip')
news = news[news['Date'] != 'Date']
news['Date'] = pd.to_datetime(news['Date'].str.replace(' UTC','',regex=False), format='mixed')

print("Columnas reales:", list(news.columns))
print("Noticias en la muestra:", len(news))
print("Tickers:", news['Stock_symbol'].unique().tolist())

# ventana de 30 dias mas densa por ticker
best = None
for tk, g in news.groupby('Stock_symbol'):
    g = g.sort_values('Date')
    dates = pd.DatetimeIndex(sorted(g['Date']))
    cnt = pd.Series(1, index=dates).resample('30D').size()
    if len(cnt) and (best is None or cnt.max() > best[1]):
        best = (tk, int(cnt.max()), cnt.idxmax())
tk, n, wstart = best
print(f"\n>>> Ticker elegido: {tk} | ventana: {wstart.date()} -> {(wstart+pd.Timedelta(days=30)).date()} | {n} noticias")

sel = news[(news['Stock_symbol']==tk) & (news['Date']>=wstart) & (news['Date']<wstart+pd.Timedelta(days=21))].sort_values('Date').head(8)
print(f"    {len(sel)} noticias en ventana de 21 dias")

# ---------- 2. Precios de esa empresa ----------
px = pd.read_csv(f'data/prices/full_history/{tk}.csv')
px['date'] = pd.to_datetime(px['date'])
px = px.sort_values('date')
px['ret_pct'] = (px['adj close'].pct_change()*100).round(2)

# ---------- 3. Emparejar noticia -> siguiente dia de mercado, y novedad ----------
def es_novedad(titulo, vistos):
    if not vistos: return 1.0, None
    sims = [(difflib.SequenceMatcher(None, titulo.lower(), p.lower()).ratio(), p) for p in vistos]
    s, p = max(sims)
    return round(1-s, 2), (p if s > 0.55 else None)

print("\n" + "="*100)
print("MINIEJEMPLO: noticia -> etiqueta -> precio")
print("="*100)
vistos = []
filas = []
for _, r in sel.iterrows():
    d = r['Date'].normalize()
    con_hora_real = r['Date'].time() != pd.Timestamp('00:00:00').time()
    nxt = px[px['date'] > d] if con_hora_real else px[px['date'] >= d + pd.Timedelta(days=1)]
    nxt = nxt.head(1)
    if nxt.empty: continue
    nrow = nxt.iloc[0]
    etiqueta = 'SUBE ⬆️' if nrow['ret_pct'] > 0 else ('BAJA ⬇️' if nrow['ret_pct'] < 0 else 'PLANO')
    nov, dup = es_novedad(str(r['Article_title']), vistos)
    vistos.append(str(r['Article_title']))
    print(f"\n📰 {r['Date']}   ticker {tk}   novedad={nov}")
    print(f"   titular: {textwrap.shorten(str(r['Article_title']), 92)}")
    print(f"   texto:   «{textwrap.shorten(str(r['Article']), 130)}»")
    if dup: print(f"   ⚠️ se parece a: «{textwrap.shorten(dup, 70)}»")
    print(f"   -> siguiente dia mercado: {nrow['date'].date()}  ret={nrow['ret_pct']:+.2f}%  ETIQUETA: {etiqueta}")
    filas.append((r['Date'], str(r['Article_title'])[:55], nov, nrow['date'].date(), nrow['ret_pct'], etiqueta))

print("\n" + "="*100)
print(f"PRECIOS {tk} alrededor de la ventana")
print("="*100)
lo, hi = wstart - pd.Timedelta(days=4), wstart + pd.Timedelta(days=16)
print(px[(px['date']>=lo)&(px['date']<=hi)][['date','open','high','low','close','ret_pct']].to_string(index=False))

print("\n" + "="*100)
print(f"RESUMEN: {len(filas)} pares noticia->movimiento")
print("="*100)
sube = sum(1 for f in filas if 'SUBE' in f[5]); baja = sum(1 for f in filas if 'BAJA' in f[5])
print(f"  SUBE: {sube}   BAJA: {baja}")
print(f"  novedad media: {sum(f[2] for f in filas)/len(filas):.2f}")
print("\n>>> OJO: 8 noticias es una nada estadistica. Esto es para VER el mecanismo, no para afirmar nada.")
