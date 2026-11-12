import urllib.request
import json
import pandas as pd

cik_map = {
    'NVDA': 1045810,
    'TSLA': 1318605,
    'AAPL': 320193,
    'AMZN': 1018724,
    'MSFT': 789019,
    'GOOGL': 1652044
}

headers = {'User-Agent': 'TFM_Research_Project student@university.edu'}

print("=== Checking SEC EDGAR 8-K Filings (2020-2022 Gap) ===")
for sym, cik in cik_map.items():
    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        df_sec = pd.DataFrame(data['filings']['recent'])
        df_sec['filingDate'] = pd.to_datetime(df_sec['filingDate'])
        mask = (df_sec['form'] == '8-K') & (df_sec['filingDate'] >= '2020-06-01') & (df_sec['filingDate'] <= '2022-12-31')
        sub = df_sec[mask]
        print(f"  {sym:<6} (CIK {cik}): {len(sub)} material 8-K filings between 2020-06 and 2022-12")
    except Exception as e:
        print(f"  {sym:<6}: Error {e}")
