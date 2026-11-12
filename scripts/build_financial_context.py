import urllib.request
import json
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime

# 1. Load CIK Map
with open('data/sec_tickers.json', 'r') as f:
    sec_data = json.load(f)

ticker_to_cik = {}
for k, v in sec_data.items():
    ticker_to_cik[v['ticker']] = str(v['cik_str']).zfill(10)

# Target list: 25 core panel stocks
PANEL_TICKERS = [l.strip() for l in open('scripts/panel.txt') if l.strip()]
print(f"Targeting {len(PANEL_TICKERS)} panel tickers for SEC XBRL ingestion.")

os.makedirs('data/fundamentals/raw_sec', exist_ok=True)
headers = {'User-Agent': 'TFM_Research_Master student@university.edu'}

# 2. Download missing facts
for sym in PANEL_TICKERS:
    cache_path = f"data/fundamentals/raw_sec/{sym}.json"
    if not os.path.exists(cache_path):
        cik = ticker_to_cik.get(sym)
        if not cik:
            print(f"  Warning: CIK not found for {sym}")
            continue
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
            with open(cache_path, 'wb') as f_out:
                f_out.write(data)
            print(f"  Downloaded SEC facts: {sym}")
            time.sleep(0.12) # SEC rate limit
        except Exception as e:
            print(f"  Error downloading {sym}: {e}")
    else:
        # already cached
        pass

print("All SEC raw facts verified.")

# 3. Helper to extract time series for a concept
def extract_concept_series(facts, concept_names, units_preference=['USD', 'shares', 'USD/shares']):
    for c in concept_names:
        if c in facts:
            units_dict = facts[c]['units']
            for u in units_preference:
                if u in units_dict:
                    items = units_dict[u]
                    # Filter 10-Q and 10-K
                    valid = [it for it in items if it.get('form') in ['10-Q', '10-K'] and 'filed' in it and 'val' in it]
                    if valid:
                        return valid, c
    return [], None

# 4. Parse Quarterly Fundamentals for each company
parsed_rows = []

REV_CONCEPTS = ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'SalesRevenueNet']
NET_INC_CONCEPTS = ['NetIncomeLoss']
OP_INC_CONCEPTS = ['OperatingIncomeLoss']
EPS_CONCEPTS = ['EarningsPerShareDiluted', 'EarningsPerShareBasic']
ASSET_CONCEPTS = ['Assets']
EQUITY_CONCEPTS = ['StockholdersEquity']

for sym in PANEL_TICKERS:
    p = f"data/fundamentals/raw_sec/{sym}.json"
    if not os.path.exists(p): continue
    try:
        with open(p, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        facts = raw.get('facts', {}).get('us-gaap', {})
    except Exception as e:
        print(f"  Error reading {sym}: {e}")
        continue
    
    # Extract records
    rev_items, _ = extract_concept_series(facts, REV_CONCEPTS, ['USD'])
    net_items, _ = extract_concept_series(facts, NET_INC_CONCEPTS, ['USD'])
    op_items, _ = extract_concept_series(facts, OP_INC_CONCEPTS, ['USD'])
    eps_items, _ = extract_concept_series(facts, EPS_CONCEPTS, ['USD/shares'])
    ast_items, _ = extract_concept_series(facts, ASSET_CONCEPTS, ['USD'])
    eq_items, _ = extract_concept_series(facts, EQUITY_CONCEPTS, ['USD'])
    
    # Group by (filed, form, fp, end)
    filings = {}
    
    def process_items(items, col_name, is_flow=True):
        for it in items:
            filed = it.get('filed')
            form = it.get('form')
            fp = it.get('fp', '')
            end = it.get('end')
            val = it.get('val')
            start = it.get('start')
            
            # For flow variables (revenue, income), prefer 3-month duration if available
            if is_flow and start and end:
                duration = (pd.to_datetime(end) - pd.to_datetime(start)).days
                if duration > 120 and form == '10-Q':
                    continue # skip 6-month or 9-month YTD totals in favor of quarterly
            
            key = (filed, form, end)
            if key not in filings:
                filings[key] = {'ticker': sym, 'filed': filed, 'form': form, 'end': end, 'fp': fp}
            
            # store or update
            filings[key][col_name] = val

    process_items(rev_items, 'revenue', is_flow=True)
    process_items(net_items, 'net_income', is_flow=True)
    process_items(op_items, 'operating_income', is_flow=True)
    process_items(eps_items, 'eps_diluted', is_flow=True)
    process_items(ast_items, 'total_assets', is_flow=False)
    process_items(eq_items, 'total_equity', is_flow=False)
    
    for row in filings.values():
        parsed_rows.append(row)

df_fund = pd.DataFrame(parsed_rows)
df_fund['filed'] = pd.to_datetime(df_fund['filed'])
df_fund['end'] = pd.to_datetime(df_fund['end'])
df_fund = df_fund.sort_values(by=['ticker', 'filed', 'end']).reset_index(drop=True)

# Drop filings before 2009
df_fund = df_fund[df_fund['filed'] >= '2009-01-01'].copy()

# Deduplicate by ticker and filed date (keep most complete)
df_fund = df_fund.drop_duplicates(subset=['ticker', 'filed'], keep='last')

# Calculate financial ratios
df_fund['operating_margin'] = df_fund['operating_income'] / df_fund['revenue']
df_fund['net_margin'] = df_fund['net_income'] / df_fund['revenue']
df_fund['roe'] = df_fund['net_income'] / df_fund['total_equity']

# Calculate YoY Growth
df_fund['rev_growth_yoy'] = df_fund.groupby('ticker')['revenue'].pct_change(periods=4)
df_fund['eps_growth_yoy'] = df_fund.groupby('ticker')['eps_diluted'].pct_change(periods=4)

os.makedirs('data/fundamentals', exist_ok=True)
df_fund.to_parquet('data/fundamentals/quarterly_fundamentals.parquet', index=False)
df_fund.to_csv('data/fundamentals/quarterly_fundamentals.csv', index=False)

print(f"\n=== Successfully parsed {len(df_fund)} quarterly fundamentals across {df_fund['ticker'].nunique()} tickers ===")
print("Saved to data/fundamentals/quarterly_fundamentals.parquet")

# Print sample recent fundamentals for NVDA and AAPL
for test_sym in ['NVDA', 'AAPL', 'CAT']:
    sub = df_fund[df_fund['ticker'] == test_sym].tail(3)
    print(f"\n--- {test_sym} Recent Fundamentals ---")
    for idx, r in sub.iterrows():
        rev_str = f"${r['revenue']/1e6:,.1f}M" if pd.notnull(r['revenue']) else "N/A"
        eps_str = f"${r['eps_diluted']:.2f}" if pd.notnull(r['eps_diluted']) else "N/A"
        op_m = f"{r['operating_margin']*100:.1f}%" if pd.notnull(r['operating_margin']) else "N/A"
        rev_g = f"{r['rev_growth_yoy']*100:+.1f}%" if pd.notnull(r['rev_growth_yoy']) else "N/A"
        print(f"  Filed: {str(r['filed'])[:10]} ({r['form']}) | Rev: {rev_str} (YoY: {rev_g}) | EPS: {eps_str} | OpMargin: {op_m}")
