import pandas as pd
import json
import gzip
import os

print("Building company news catalog data...")

# 1. Load summary
df_sum = pd.read_csv('data/resumen_cobertura_y_huecos.csv', sep=';')

# 2. Sample Benzinga news
bz_news = {}
print("Loading Benzinga news samples...")
with gzip.open('data/benzinga/tier1_benzinga_news.csv.gz', 'rt', encoding='utf-8') as f:
    df_bz = pd.read_csv(f)
    for sym, group in df_bz.groupby('ticker'):
        # Pick up to 10 spaced samples
        n = len(group)
        if n <= 8:
            sample = group
        else:
            indices = [int(i * (n - 1) / 7) for i in range(8)]
            sample = group.iloc[indices]
        
        bz_news[sym] = []
        for idx, row in sample.iterrows():
            bz_news[sym].append({
                'source': 'Benzinga',
                'date': str(row['date'])[:19],
                'headline': str(row['headline']),
                'publisher': str(row['publisher']) if pd.notnull(row['publisher']) else 'Benzinga',
                'url': str(row['url']) if pd.notnull(row['url']) else ''
            })

# 3. Sample from benstaf/nasdaq_news for recent / gap news if available
print("Loading NASDAQ news samples from benstaf/nasdaq_news...")
url_benstaf = "https://huggingface.co/datasets/benstaf/nasdaq_news/resolve/main/data/train-00000-of-00001.parquet"
try:
    df_nasdaq = pd.read_parquet(url_benstaf)
    nasdaq_samples = {}
    for sym, group in df_nasdaq.groupby('Stock_symbol'):
        n = len(group)
        if n <= 8:
            sample = group
        else:
            indices = [int(i * (n - 1) / 7) for i in range(8)]
            sample = group.iloc[indices]
        nasdaq_samples[sym] = []
        for idx, row in sample.iterrows():
            nasdaq_samples[sym].append({
                'source': 'NASDAQ (FNSPID)',
                'date': str(row['Date'])[:19],
                'headline': str(row['Article_title']),
                'publisher': str(row['Publisher']) if pd.notnull(row['Publisher']) else 'NASDAQ',
                'url': str(row['Url']) if pd.notnull(row['Url']) else ''
            })
except Exception as e:
    print("Error loading benstaf:", e)
    nasdaq_samples = {}

# 4. Merge company profiles and news samples
catalog = []
for idx, row in df_sum.iterrows():
    sym = row['sym']
    
    # Combined samples
    samples = []
    if sym in bz_news:
        samples.extend(bz_news[sym])
    if sym in nasdaq_samples:
        samples.extend(nasdaq_samples[sym])
    
    # Sort samples chronologically
    samples.sort(key=lambda x: x['date'])
    
    comp_obj = {
        'sym': sym,
        'name': row['sec_name'],
        'sector': row['sector'],
        'n_prices': int(row['n_prices']),
        'categoria': row['categoria'],
        'fn_start': str(row['fn_start']),
        'fn_end': str(row['fn_end']),
        'fn_count': int(row['fn_count']),
        'bz_start': str(row['bz_start']),
        'bz_end': str(row['bz_end']),
        'bz_count': int(row['bz_count']),
        'uni_start': str(row['uni_start']),
        'uni_end': str(row['uni_end']),
        'total_noticias': int(row['total_noticias']),
        'gap_days': int(row['gap_days']),
        'has_bridge_gap': bool(row['has_bridge_gap']),
        'samples': samples
    }
    catalog.append(comp_obj)

os.makedirs('data/catalog', exist_ok=True)
with open('data/catalog/companies_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Catalog data built for {len(catalog)} companies. Saved to data/catalog/companies_catalog.json")
