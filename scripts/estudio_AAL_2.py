"""Parte 2 del microestudio AAL: novedad bien calculada + auditoria de AMBIGUOS."""
import io, re, difflib, textwrap
import pandas as pd

A = pd.read_csv('data/estudio_AAL_clasificadas.csv')
A['Date'] = pd.to_datetime(A['Date'])
V = A[A['clase']=='VERDADERO (AA)'].sort_values('Date').copy()
print(f"VERDADERAS: {len(V)}")

# ---------- novedad acumulativa correcta ----------
def novedad(t, vistos):
    if not vistos: return 1.0, None
    s, p = max((difflib.SequenceMatcher(None, t.lower()[:140], v.lower()[:140]).ratio(), v) for v in vistos)
    return round(1-s, 2), p

vistos = []
nov, dupde = [], []
for t in V['Article_title']:
    n, p = novedad(str(t), vistos)
    nov.append(n); dupde.append(p if n < 0.35 else None)
    vistos.append(str(t))
V['nov'] = nov
V['casi_repetida_de'] = dupde

n_rep = int((V['nov'] < 0.35).sum())
print(f"casi-repetidas (nov<0.35): {n_rep} = {n_rep/len(V)*100:.1f}%")
print(f"dias-empresa con >=1 casi-repetida: "
      f"{V[V['nov']<0.35].groupby(V['Date'].dt.normalize()).ngroups}")

print("\n--- 10 parejas casi-repetidas reales (misma noticia, otra fuente) ---")
for _, r in V[V['nov']<0.35].head(10).iterrows():
    print(f"{r['Date'].date()} nov={r['nov']:.2f}")
    print(f"  NUEVA : {textwrap.shorten(str(r['Article_title']), 90)}")
    print(f"  PREVIA: {textwrap.shorten(str(r['casi_repetida_de']), 90)}")

# ---------- AMBIGUOS: que son realmente? ----------
AM = A[A['clase']=='AMBIGUO (revisar)']
print(f"\n=== AMBIGUOS: {len(AM)} ===")
print("Top autores:")
print(AM['Author'].value_counts().head(8).to_string())
print("\nTop 15 titulares ambigueos frecuentes:")
top = AM['Article_title'].value_counts().head(15)
for t, c in top.items():
    print(f"  {c:>4}x  {textwrap.shorten(str(t), 85)}")

# patron: noticias tipo Zacks "Ticker X Rises/Declines while..."
ZACKS = re.compile(r'\(AAL\)|\bAAL\b', re.I)
es_aal = AM['Article_title'].str.contains(r'\bAAL\b', case=False, na=False) | \
         AM['Article'].astype(str).str.contains(r'American Airlines', case=False, na=False)
print(f"\nDe los {len(AM)} ambiguos: {int(es_aal.sum())} mencionan AAL/AmericanAirlines en titulo o texto "
      f"({es_aal.mean()*100:.0f}%)")

# ---------- baseline direccional ingenuo sobre dias-empresa agregados ----------
px = pd.read_csv('data/prices/full_history/AAL.csv')
px['date'] = pd.to_datetime(px['date']); px = px.sort_values('date')
px['ret'] = px['adj close'].pct_change()*100
V['d0'] = V['Date'].dt.normalize()
dias = V.groupby('d0').agg(n=('nov','size'), nov_med=('nov','mean')).reset_index()
lab = []
for _, r in dias.iterrows():
    after = False
    # hora real? si todas las noticias del dia son 00:00 -> t+1
    ts = V[V['d0']==r['d0']]['Date']
    after = (ts.dt.time != pd.Timestamp('00:00:00').time()).any()
    nxt = px[(px['date'] > r['d0'])] if after else px[(px['date'] >= r['d0'] + pd.Timedelta(days=1))]
    lab.append(nxt.iloc[0]['ret'] if len(nxt) else None)
dias['ret_d1'] = lab
dias = dias.dropna()
print(f"\n=== BASELINE 'todo-dia-cuenta' sobre {len(dias)} dias-empresa ===")
sube = int((dias['ret_d1']>0).sum()); baja = int((dias['ret_d1']<0).sum())
print(f"SUBE {sube} / BAJA {baja} -> majority class = {max(sube,baja)/len(dias)*100:.1f}% "
      f"(ese es el umbral a batir, trivialmente)")
for umbral in (0.5, 0.7, 0.9):
    sel = dias[dias['nov_med'] >= umbral]
    if len(sel) >= 30:
        acc = (sel['ret_d1'] > 0).mean()
        print(f"  dias con novedad_media>={umbral}: {len(sel):>4} | %sube {acc*100:.1f}%")
    sel_b = dias[dias['nov_med'] <  umbral] if umbral==0.5 else None
    if sel_b is not None:
        acc_b = (sel_b['ret_d1'] > 0).mean()
        print(f"  dias con novedad_media<0.5 (relleno): {len(sel_b):>4} | %sube {acc_b*100:.1f}%")

V.to_csv('data/estudio_AAL_verdaderas.csv', index=False)
dias.to_csv('data/estudio_AAL_dias.csv', index=False)
print("\nGuardados: data/estudio_AAL_verdaderas.csv, data/estudio_AAL_dias.csv")
