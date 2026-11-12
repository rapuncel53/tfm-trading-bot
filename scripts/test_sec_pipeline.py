import urllib.request
import json
import os
import time
import pandas as pd
import numpy as np

# Load CIK map
with open('data/sec_tickers.json', 'r') as f:
    sec_data = json.load(f)

ticker_to_cik = {}
for k, v in sec_data.items():
    ticker_to_cik[v['ticker']] = str(v['cik_str']).zfill(10)

test_tickers = ['NVDA', 'AAPL', 'MSFT', 'CAT', 'JPM', 'PFE', 'COST', 'TSLA']
headers = {'User-Agent': 'TFM_Research_Master student@university.edu'}
os.makedirs('data/fundamentals/raw_sec', exist_ok=True)

print("=== Fetching & Testing SEC EDGAR XBRL Facts ===")

for sym in test_tickers:
    cik = ticker_to_cik.get(sym)
    if not cik:
        print(f"CIK not found for {sym}")
        continue
    
    cache_file = f"data/fundamentals/raw_sec/{sym}.json"
    if not os.path.exists(cache_file):
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                raw_json = resp.read()
            with open(cache_file, 'wb') as f_out:
                f_out.write(raw_json)
            time.sleep(0.15) # respect SEC 10 req/s rate limit
            print(f"  Downloaded & cached {sym} (CIK {cik})")
        except Exception as e:
            print(f"  Error downloading {sym}: {e}")
            continue
    else:
        print(f"  Found cached {sym} (CIK {cik})")

print("\nVerifying parsed facts...")
with open(f"data/fundamentals/raw_sec/NVDA.json", "r") as f:
    nvda_facts = json.load(f)['facts']['us-gaap']

# Inspect units for Revenues and NetIncomeLoss
rev_units = list(nvda_facts['Revenues']['units'].keys())[0]
rev_list = nvda_facts['Revenues']['units'][rev_units]
df_rev = pd.DataFrame(rev_list)
# filter 10-Q and 10-K
df_rev_q = df_rev[df_rev['form'].isin(['10-Q', '10-K']) & df_rev['filed'].notnull()].sort_values('filed')
print(f"NVDA Revenue entries: {len(df_rev_q)}")
print("Sample NVDA recent revenue filings:")
for idx, r in df_rev_q.tail(5).iterrows():
    print(f"  Filed: {r['filed']} | Period End: {r['end']} | Form: {r['form']} | Val: ${r['val']/1e6:,.1f}M")
