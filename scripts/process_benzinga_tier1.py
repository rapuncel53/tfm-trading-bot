import json
import os
import pandas as pd
from datetime import datetime

BENZINGA_FILE = "data/benzinga/raw_analyst_ratings.jsonl"
TIER1_FILE = "data/tier1_fechas_noticias.csv"
OUT_NEWS_CSV = "data/benzinga/tier1_benzinga_news.csv.gz"
OUT_SUMMARY_CSV = "data/benzinga/tier1_benzinga_coverage.csv"

def main():
    if not os.path.exists(BENZINGA_FILE):
        print(f"Error: {BENZINGA_FILE} not found.")
        return

    # Load Tier 1 tickers
    df_t1 = pd.read_csv(TIER1_FILE, sep=';')
    t1_tickers = set(df_t1['sym'].tolist())
    # Also add GOOGL if GOOG is present
    if 'GOOG' in t1_tickers:
        t1_tickers.add('GOOGL')
    print(f"Loaded {len(t1_tickers)} target tickers from {TIER1_FILE}")

    # Process Benzinga JSONL
    print(f"Reading and filtering {BENZINGA_FILE}...")
    records = []
    stats = {} # ticker -> {'count': 0, 'min_date': None, 'max_date': None}

    total_lines = 0
    with open(BENZINGA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            total_lines += 1
            if not line.strip().startswith('{'):
                continue
            try:
                item = json.loads(line)
            except:
                continue
            
            stock = item.get('stock')
            if stock in t1_tickers:
                dt_str = item.get('date', '')
                headline = item.get('headline', '')
                publisher = item.get('publisher', '')
                url = item.get('url', '')
                
                records.append({
                    'ticker': stock,
                    'date': dt_str,
                    'headline': headline,
                    'publisher': publisher,
                    'url': url
                })
                
                # Update stats
                if stock not in stats:
                    stats[stock] = {'count': 0, 'min_date': dt_str, 'max_date': dt_str}
                stats[stock]['count'] += 1
                if dt_str < stats[stock]['min_date']:
                    stats[stock]['min_date'] = dt_str
                if dt_str > stats[stock]['max_date']:
                    stats[stock]['max_date'] = dt_str

    print(f"Scanned {total_lines} total lines in Benzinga dataset.")
    print(f"Found {len(records)} news articles matching target Tier 1 tickers across {len(stats)} companies.")

    # Save filtered records
    df_records = pd.DataFrame(records)
    df_records.sort_values(by=['ticker', 'date'], inplace=True)
    df_records.to_csv(OUT_NEWS_CSV, index=False, compression='gzip')
    print(f"Saved filtered articles to {OUT_NEWS_CSV} ({os.path.getsize(OUT_NEWS_CSV)/(1024*1024):.2f} MB)")

    # Build coverage summary
    summary_rows = []
    for ticker, data in stats.items():
        summary_rows.append({
            'sym': ticker,
            'benzinga_count': data['count'],
            'benzinga_start': data['min_date'][:10] if data['min_date'] else None,
            'benzinga_end': data['max_date'][:10] if data['max_date'] else None
        })

    df_summary = pd.DataFrame(summary_rows)
    df_merged = pd.merge(df_t1, df_summary, on='sym', how='left')
    df_merged.to_csv(OUT_SUMMARY_CSV, index=False)
    print(f"Saved coverage comparison to {OUT_SUMMARY_CSV}")

    # Print highlights
    print("\n=== TOP HIGHLIGHTS ===")
    for test_sym in ['NVDA', 'AAPL', 'GOOG', 'GOOGL', 'AMZN', 'AMD', 'INTC', 'TSLA', 'META', 'FB']:
        row = df_summary[df_summary['sym'] == test_sym]
        if not row.empty:
            r = row.iloc[0]
            print(f"  {r['sym']}: {r['benzinga_count']} news from {r['benzinga_start']} to {r['benzinga_end']}")

if __name__ == '__main__':
    main()
