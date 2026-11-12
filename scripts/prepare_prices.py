"""Preparacion de precios del panel: orden, duplicados, splits, costura 2020-07-02.
Salida: data/panel/prices/SYM.csv (ascendente, split-corregido) + data/panel/price_report.csv
"""
import os, glob, json
import numpy as np
import pandas as pd

PANEL = [l.strip() for l in open('scripts/panel.txt') if l.strip()]
OUT = 'data/panel/prices'
os.makedirs(OUT, exist_ok=True)
INT_RATIO = [2,3,4,5,6,7,8,9,10,20,25,30,40,50,100]
SEAM = pd.Timestamp('2020-07-02')

def split_fix(d):
    """Corrige splits (caidas ~1/k) hacia atras sobre close/open/high/low.
    Itera del presente al pasado y re-factoriza las filas anteriores."""
    c = d['close'].values.astype(float)
    corr = c.copy()
    splits = []
    for i in range(len(d)-1, 0, -1):
        if corr[i-1] <= 0: continue
        r = corr[i]/corr[i-1]
        if r < 0.55:                    # caida > ~45%
            base = 1/r                  # p.ej. r=0.25 -> split 4:1 -> multiplicar pasado por 4
            near = min(abs(base-k)/k for k in INT_RATIO)
            if near < 0.03:
                corr[:i] *= base
                splits.append((str(d['date'].iloc[i]), round(base, 4)))
    ratio = corr / c
    for col in ['open','high','low','close','adj close']:
        d[col] = d[col] * ratio
    return d, splits

report = []
for sym in PANEL:
    f = f'data/prices/full_history/{sym}.csv'
    if not os.path.exists(f):
        report.append(dict(sym=sym, err='sin_fichero')); continue
    d = pd.read_csv(f)
    d['date'] = pd.to_datetime(d['date'])
    d = d.sort_values('date').drop_duplicates('date').reset_index(drop=True)
    for col in ['open','high','low','close','adj close','volume']:
        d[col] = pd.to_numeric(d[col], errors='coerce')
    d = d.dropna(subset=['close']).reset_index(drop=True)
    d, splits = split_fix(d)
    # costura: salto de |ret|>20% en los 3 dias siguientes a la costura tras corregir splits
    ret = d['close'].pct_change()
    seam_zone = d[(d['date'] > SEAM) & (d['date'] <= SEAM + pd.Timedelta(days=4))]
    seam_jump = float(seam_zone['close'].pct_change().reindex(seam_zone.index).abs().max()) if len(seam_zone) else None
    # saltos residuales
    resid = int((ret.abs() > 0.30).sum())
    d['ret1'] = d['close'].pct_change()
    d['logret1'] = np.log(d['close']).diff()
    d.to_csv(f'{OUT}/{sym}.csv', index=False)
    report.append(dict(sym=sym, rows=len(d), d0=str(d['date'].min().date()),
                       d1=str(d['date'].max().date()), n_splits=len(splits),
                       splits=';'.join(f'{a}x{b:g}' for a,b in splits[:6]),
                       seam_jump=seam_jump, resid_big_jumps=resid))

R = pd.DataFrame(report)
R.to_csv('data/panel/price_report.csv', index=False)
pd.set_option('display.width', 200)
print(R.to_string(index=False))
