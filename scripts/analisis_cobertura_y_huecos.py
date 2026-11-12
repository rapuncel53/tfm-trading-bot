import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('data/benzinga/tier1_benzinga_coverage.csv')

# Parse dates
df['fn_d0'] = pd.to_datetime(df['d0_news'])
df['fn_d1'] = pd.to_datetime(df['d1_news'])
df['bz_d0'] = pd.to_datetime(df['benzinga_start'])
df['bz_d1'] = pd.to_datetime(df['benzinga_end'])

# Calculate unified dates and gaps
records = []
for idx, row in df.iterrows():
    sym = row['sym']
    name = row['sec_name']
    sector = row['sector']
    n_prices = row['n_prices']
    
    # FNSPID
    fn_start = row['fn_d0']
    fn_end = row['fn_d1']
    fn_count = row['n_news']
    
    # Benzinga
    bz_start = row['bz_d0']
    bz_end = row['bz_d1']
    bz_count = row['benzinga_count'] if pd.notnull(row['benzinga_count']) else 0
    
    # Unified coverage
    valid_starts = [d for d in [fn_start, bz_start] if pd.notnull(d)]
    valid_ends = [d for d in [fn_end, bz_end] if pd.notnull(d)]
    uni_start = min(valid_starts) if valid_starts else None
    uni_end = max(valid_ends) if valid_ends else None
    
    # Gap analysis
    # If Benzinga ends before FNSPID starts
    gap_days = 0
    has_bridge_gap = False
    
    # Check if FNSPID starts after Benzinga ends
    if pd.notnull(bz_end) and pd.notnull(fn_start):
        if fn_start > bz_end:
            gap_days = (fn_start - bz_end).days
            has_bridge_gap = True
        else:
            # They overlap! (e.g. FNSPID starts in 2009/2010 and Benzinga ends in 2020)
            gap_days = 0
            has_bridge_gap = False
    elif pd.isnull(bz_start):
        # Only FNSPID
        gap_days = 0
        has_bridge_gap = False
    
    # Categorization
    # Category 1: Continuous Full History (FNSPID starts <= 2012, reaches 2023, NO gap)
    if fn_start <= pd.Timestamp('2012-12-31') and fn_end >= pd.Timestamp('2023-10-01'):
        cat = "1. CONTINUA_TOTAL_SIN_HUECOS"
    elif has_bridge_gap and gap_days > 180:
        cat = "2. HIBRIDA_CON_HUECO"
    elif fn_start <= pd.Timestamp('2019-12-31') and fn_end >= pd.Timestamp('2023-10-01') and not has_bridge_gap:
        cat = "3. CONTINUA_MEDIA_SIN_HUECOS"
    else:
        cat = "4. RECIENTE_O_FRAGMENTADA"
        
    records.append({
        'sym': sym,
        'sec_name': name,
        'sector': sector,
        'n_prices': n_prices,
        'categoria': cat,
        'fn_start': str(row['d0_news']),
        'fn_end': str(row['d1_news']),
        'fn_count': int(fn_count),
        'bz_start': str(row['benzinga_start']) if pd.notnull(row['benzinga_start']) else "-",
        'bz_end': str(row['benzinga_end']) if pd.notnull(row['benzinga_end']) else "-",
        'bz_count': int(bz_count),
        'uni_start': str(uni_start)[:10] if uni_start else "-",
        'uni_end': str(uni_end)[:10] if uni_end else "-",
        'total_noticias': int(fn_count + bz_count),
        'gap_days': gap_days,
        'has_bridge_gap': has_bridge_gap
    })

df_res = pd.DataFrame(records)
df_res.to_csv('data/resumen_cobertura_y_huecos.csv', index=False, sep=';')

# Print summary counts
print("=== DISTRIBUCIÓN POR CATEGORÍA ===")
print(df_res['categoria'].value_counts())

print("\n=== TOP EMPRESAS CATEGORÍA 1 (CONTINUA TOTAL SIN HUECOS) ===")
c1 = df_res[df_res['categoria'] == "1. CONTINUA_TOTAL_SIN_HUECOS"]
print(f"Total en Categoría 1: {len(c1)}")
for idx, r in c1.sort_values(by='total_noticias', ascending=False).head(15).iterrows():
    print(f"  {r['sym']:<5} | {r['sec_name'][:25]:<25} | {r['sector']:<22} | Noticias={r['total_noticias']:<6} | Fechas={r['uni_start']} a {r['uni_end']}")

print("\n=== TOP EMPRESAS CATEGORÍA 2 (HÍBRIDA CON HUECO 2020-2021) ===")
c2 = df_res[df_res['categoria'] == "2. HIBRIDA_CON_HUECO"]
print(f"Total en Categoría 2: {len(c2)}")
for idx, r in c2.sort_values(by='total_noticias', ascending=False).head(10).iterrows():
    print(f"  {r['sym']:<5} | {r['sec_name'][:25]:<25} | BZ={r['bz_start']}..{r['bz_end']} | FN={r['fn_start']}..{r['fn_end']} | HUECO={r['gap_days']} días ({r['gap_days']/30:.1f} meses)")

print("\n=== RESUMEN POR SECTOR EN CATEGORÍA 1 ===")
print(c1['sector'].value_counts())
