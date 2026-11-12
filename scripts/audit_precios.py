"""Auditoria exhaustive de los 7,693 CSV de precios de FNSPID.
Mide por ticker: cobertura, orden, nulos, fechas duplicadas, violaciones OHLC,
volume=0, y SALTO-STYLE-SPLIT sin corregir en close y en adj close.
Devuelve agregados defendibles para el capitulo de calidad de datos.
"""
import os, glob, math, json, re
import numpy as np
import pandas as pd

FILES = glob.glob('data/prices/full_history/*.csv')
print(f"ficheros: {len(FILES)}", flush=True)
INT_RATIO = [2,3,4,5,6,7,8,10,20,25,30,40,50,100]

rows = []
for i, f in enumerate(FILES):
    sym = os.path.basename(f)[:-4]
    try:
        d = pd.read_csv(f)
    except Exception as e:
        rows.append(dict(sym=sym, err=str(type(e).__name__))); continue
    if d.shape[1] < 6 or 'date' not in d.columns:
        rows.append(dict(sym=sym, err='esquema')); continue
    n = len(d)
    dt = pd.to_datetime(d['date'], errors='coerce')
    c  = pd.to_numeric(d.get('close'), errors='coerce')
    ac = pd.to_numeric(d.get('adj close'), errors='coerce')
    o  = pd.to_numeric(d.get('open'), errors='coerce')
    hi = pd.to_numeric(d.get('high'), errors='coerce')
    lo = pd.to_numeric(d.get('low'),  errors='coerce')
    v  = pd.to_numeric(d.get('volume'), errors='coerce')

    desc = dt.is_monotonic_decreasing
    dup  = int(dt.duplicated().sum())
    nulls = int(d.isna().sum().sum())
    bad_ohlc = int(((hi < lo) | (o < lo - 1e-9) | (o > hi + 1e-9)).sum())
    zero_v   = int((v == 0).sum())
    flat     = int((c.diff() == 0).sum())

    # salto sospechoso de split: |ret| > 45% y ratio proximo a un entero
    ret = c.pct_change()
    big = ret.abs() > 0.45
    split_like = 0
    split_in_adj = 0
    if big.any():
        prev = c.shift(1)[big]
        cur  = c[big]
        for p, q in zip(prev, cur):
            if not (p > 0 and q > 0): continue
            for base in (p/q, q/p):
                if base < 1: base = 1/base
                near = min(abs(base - k)/k for k in INT_RATIO)
                if near < 0.03:
                    split_like += 1
                    break
        # ?el mismo salto desaparece en adj close? (correcto) o sigue (incorrecto)
        reta = ac.pct_change()
        split_in_adj = int((reta.abs() > 0.45).sum())

    rows.append(dict(sym=sym, n=n, err=None,
        d0=str(dt.min().date()) if pd.notna(dt.min()) else None,
        d1=str(dt.max().date()) if pd.notna(dt.max()) else None,
        desc=int(desc), dup=dup, nulls=nulls, bad_ohlc=bad_ohlc,
        zero_vol=zero_v, flat=flat,
        n_big=int(big.sum()), n_splitlike=split_like, n_split_in_adj=split_in_adj,
        adj_eq_close=int((c == ac).all()),
        last_ret=float(ret.iloc[-1]) if n > 1 and pd.notna(ret.iloc[-1]) else None))
    if (i+1) % 800 == 0:
        print(f"  {i+1}/{len(FILES)}", flush=True)

R = pd.DataFrame(rows)
R.to_csv('data/audit_precios.csv', index=False)
print("\n=== RESUMEN ===")
ok = R[R['err'].isna()]
print(f"tickers leidos OK: {len(ok)} | con error: {int(R['err'].notna().sum())}")
print(f"filas totales: {int(ok['n'].sum()):,} | mediana por ticker: {ok['n'].median():.0f}")
print(f"orden descendente: {int(ok['desc'].sum())} ({ok['desc'].mean()*100:.1f}%)")
print(f"con fechas duplicadas: {int((ok['dup']>0).sum())}")
print(f"con nulos: {int((ok['nulls']>0).sum())}")
print(f"con violaciones OHLC: {int((ok['bad_ohlc']>0).sum())}")
print(f"con volumen=0: {int((ok['zero_vol']>0).sum())} (filas totales vol0: {int(ok['zero_vol'].sum()):,})")
print(f"adj_close == close siempre (sin ajuste dividendo): {int(ok['adj_eq_close'].sum())} "
      f"({ok['adj_eq_close'].mean()*100:.1f}%)")
print("\n=== SPLITS SIN AJUSTAR ===")
print(f"tickers con >=1 salto-like: {int((ok['n_splitlike']>0).sum())} "
      f"({(ok['n_splitlike']>0).mean()*100:.1f}%) | saltos totales: {int(ok['n_splitlike'].sum()):,}")
print(f"...de esos, el salto TAMBIEN esta en adj close (=> NO corregido): "
      f"{int((ok['n_split_in_adj']>0).sum())} tickers | saltos: {int(ok['n_split_in_adj'].sum()):,}")
print(f"corregidos en adj (big en close pero no en adj): "
      f"{int(((ok['n_splitlike']>0)&(ok['n_split_in_adj']==0)).sum())} tickers")

print("\n=== ULTIMO DIA DE DATOS ===")
print(ok['d1'].value_counts().head(6).to_string())
print("\n=== PRIMEROS DIAS (mas antiguos) ===")
print(ok.sort_values('d0').head(5)[['sym','d0','n']].to_string(index=False))
print(f"\ntickers con historial < 100 filas: {int((ok['n']<100).sum())}")
print(f"tickers que terminan antes de 2023-12-01 (posiblemente delistados): "
      f"{int((pd.to_datetime(ok['d1']) < '2023-12-01').sum())}")
