import pandas as pd
import numpy as np

# 1. Load splits using venv
train_df = pd.read_parquet('data/splits/train/daily_aligned.parquet')
val_df = pd.read_parquet('data/splits/val/daily_aligned.parquet')
test_df = pd.read_parquet('data/splits/test/daily_aligned.parquet')

# 2. Load bz metadata
bz_meta = pd.read_csv('data/benzinga/tier1_benzinga_coverage.csv')
meta_dict = {}
for _, row in bz_meta.iterrows():
    sym = str(row['sym']).strip()
    meta_dict[sym] = {
        'sec_name': str(row.get('sec_name', '')),
        'sector': str(row.get('sector', '')),
        'bz_count': row.get('benzinga_count'),
        'bz_start': str(row.get('benzinga_start', '')),
        'bz_end': str(row.get('benzinga_end', '')),
        'fn_count': row.get('n_news'),
        'fn_start': str(row.get('d0_news', '')),
        'fn_end': str(row.get('d1_news', ''))
    }

extra_names = {
    'KO': ('The Coca-Cola Company', 'Consumer Staples'),
    'AMD': ('Advanced Micro Devices, Inc.', 'Information Technology'),
    'ADBE': ('Adobe Inc.', 'Information Technology'),
    'T': ('AT&T Inc.', 'Communication Services'),
    'DIS': ('The Walt Disney Company', 'Communication Services'),
    'JPM': ('JPMorgan Chase & Co.', 'Financials'),
    'PFE': ('Pfizer Inc.', 'Health Care'),
    'JNJ': ('Johnson & Johnson', 'Health Care')
}

all_tickers = sorted(list(set(train_df['ticker'].unique()) | set(val_df['ticker'].unique()) | set(test_df['ticker'].unique()) | set(bz_meta['sym'].unique())))

rows = []

for t in all_tickers:
    tr_sub = train_df[(train_df['ticker'] == t) & (train_df['has_news'] == True)]
    va_sub = val_df[(val_df['ticker'] == t) & (val_df['has_news'] == True)]
    te_sub = test_df[(test_df['ticker'] == t) & (test_df['has_news'] == True)]
    
    tr_cnt = len(tr_sub)
    va_cnt = len(va_sub)
    te_cnt = len(te_sub)
    
    m = meta_dict.get(t, {})
    sec_name = m.get('sec_name', '')
    sector = m.get('sector', '')
    
    if (not sec_name or sec_name == 'nan') and t in extra_names:
        sec_name, sector = extra_names[t]
        
    bz_cnt = m.get('bz_count')
    bz_start = m.get('bz_start')
    bz_end = m.get('bz_end')
    
    fn_cnt = m.get('fn_count')
    fn_start = m.get('fn_start')
    fn_end = m.get('fn_end')
    
    if pd.isna(bz_cnt) or bz_cnt == 0:
        if tr_cnt > 0 or va_cnt > 0:
            bz_cnt = tr_cnt + va_cnt
            if tr_cnt > 0:
                bz_start = str(tr_sub['date'].min())[:10]
            else:
                bz_start = str(va_sub['date'].min())[:10]
            if va_cnt > 0:
                bz_end = str(va_sub['date'].max())[:10]
            else:
                bz_end = str(tr_sub['date'].max())[:10]
        else:
            bz_cnt = 0
            bz_start = 'Sin datos'
            bz_end = 'Sin datos'
    else:
        bz_cnt = int(bz_cnt)
        bz_start = str(bz_start)[:10] if bz_start and str(bz_start) != 'nan' else 'Sin datos'
        bz_end = str(bz_end)[:10] if bz_end and str(bz_end) != 'nan' else 'Sin datos'

    if pd.isna(fn_cnt) or fn_cnt == 0:
        if te_cnt > 0:
            fn_cnt = te_cnt
            fn_start = str(te_sub['date'].min())[:10]
            fn_end = str(te_sub['date'].max())[:10]
        else:
            fn_cnt = 0
            fn_start = 'Sin datos'
            fn_end = 'Sin datos'
    else:
        fn_cnt = int(fn_cnt)
        fn_start = str(fn_start)[:10] if fn_start and str(fn_start) != 'nan' else 'Sin datos'
        fn_end = str(fn_end)[:10] if fn_end and str(fn_end) != 'nan' else 'Sin datos'

    has_bz = "SÍ" if bz_cnt > 0 and bz_start != 'Sin datos' else "NO"
    has_fn = "SÍ" if fn_cnt > 0 and fn_start != 'Sin datos' else "NO"
    
    total_news = bz_cnt + fn_cnt
    
    valid_starts = []
    valid_ends = []
    if bz_start != 'Sin datos':
        valid_starts.append(bz_start)
        valid_ends.append(bz_end)
    if fn_start != 'Sin datos':
        valid_starts.append(fn_start)
        valid_ends.append(fn_end)
        
    if valid_starts:
        d_min = min(valid_starts)
        d_max = max(valid_ends)
        y_min = int(d_min[:4])
        y_max = int(d_max[:4])
        span_years = round((y_max - y_min) + 1, 1)
    else:
        d_min = 'Sin noticias'
        d_max = 'Sin noticias'
        span_years = 0.0

    if tr_cnt > 0 and va_cnt > 0 and te_cnt > 0:
        tier = "Tier 1: Cobertura Total Continua"
        diag = f"Excelente: flujo ininterrumpido en Train ({tr_cnt}d), Val ({va_cnt}d) y Test ({te_cnt}d). Cobertura {d_min[:4]} a {d_max[:4]}."
    elif tr_cnt > 0 and va_cnt > 0 and te_cnt == 0:
        tier = "Tier 2: Cobertura Parcial Histórica"
        diag = f"Histórica Benzinga: cubre Train ({tr_cnt}d) y Val ({va_cnt}d), pero sin noticias en Test (2021-2023)."
    elif (tr_cnt == 0 or tr_cnt < 30) and (va_cnt > 0 or te_cnt > 0):
        tier = "Tier 2: Cobertura Parcial Tardía"
        diag = f"Reciente / Big Tech: pocas o ninguna en Train, pero densa en Val ({va_cnt}d) y Test ({te_cnt}d)."
    elif te_cnt > 0 and tr_cnt == 0 and va_cnt == 0:
        tier = "Tier 3: Cobertura Mínima"
        diag = f"Solo Test: no tiene noticias de 2011 a 2020. Solo aparece en FNSPID ({te_cnt}d en Test)."
    elif total_news == 0 or (tr_cnt == 0 and va_cnt == 0 and te_cnt == 0):
        tier = "Tier 3: Silenciosa (Solo Balances SEC)"
        diag = "Empresa silenciosa: dispone de cotizaciones y balances SEC auditados, pero sin flujo noticioso registrado."
    else:
        tier = "Tier 3: Cobertura Mínima"
        diag = f"Cobertura esporádica: {tr_cnt}d en Train, {va_cnt}d en Val, {te_cnt}d en Test."

    rows.append({
        'Ticker': t,
        'Empresa': sec_name if sec_name and sec_name != 'nan' else t,
        'Sector': sector if sector and sector != 'nan' else 'General',
        'Clasificacion_Tier': tier,
        'Tiene_Benzinga': has_bz,
        'Benzinga_Fecha_Inicio': bz_start,
        'Benzinga_Fecha_Fin': bz_end,
        'Benzinga_Noticias': bz_cnt,
        'Tiene_FNSPID': has_fn,
        'FNSPID_Fecha_Inicio': fn_start,
        'FNSPID_Fecha_Fin': fn_end,
        'FNSPID_Noticias': fn_cnt,
        'Total_Noticias': total_news,
        'Fecha_Inicio_Global': d_min,
        'Fecha_Fin_Global': d_max,
        'Anios_Cobertura': span_years,
        'Dias_Noticias_Train': tr_cnt,
        'Dias_Noticias_Val': va_cnt,
        'Dias_Noticias_Test': te_cnt,
        'Diagnostico_Detallado': diag
    })

res_df = pd.DataFrame(rows)

tier_order = {
    "Tier 1: Cobertura Total Continua": 1,
    "Tier 2: Cobertura Parcial Histórica": 2,
    "Tier 2: Cobertura Parcial Tardía": 3,
    "Tier 3: Cobertura Mínima": 4,
    "Tier 3: Silenciosa (Solo Balances SEC)": 5
}
res_df['tier_rank'] = res_df['Clasificacion_Tier'].map(tier_order)
res_df = res_df.sort_values(by=['tier_rank', 'Total_Noticias'], ascending=[True, False]).drop(columns=['tier_rank'])

csv_path = 'data/desglose_cobertura_noticias_todas_las_companias.csv'
res_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f'SUCCESS: saved {len(res_df)} companies to {csv_path}')
