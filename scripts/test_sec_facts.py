import urllib.request
import json
import pandas as pd

cik = '0001045810' # NVDA
url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'
headers = {'User-Agent': 'TFM_Research student@university.edu'}

print(f"Connecting to SEC EDGAR for CIK {cik} (NVDA)...")
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))

entity = data.get('entityName')
facts = data.get('facts', {}).get('us-gaap', {})
print(f"Entity: {entity}")
print(f"Total US-GAAP concepts: {len(facts)}")

# Let's inspect NetIncomeLoss, Revenues, and EPS
for concept in ['Revenues', 'SalesRevenueNet', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'NetIncomeLoss', 'OperatingIncomeLoss', 'EarningsPerShareDiluted', 'Assets', 'StockholdersEquity']:
    if concept in facts:
        units = list(facts[concept]['units'].keys())[0]
        items = facts[concept]['units'][units]
        filings = [it for it in items if it.get('form') in ['10-Q', '10-K'] and 'filed' in it]
        if filings:
            last = filings[-1]
            first = filings[0]
            print(f"  {concept:<45}: {len(filings):3d} records | {first['filed']} ({first['val']}) -> {last['filed']} ({last['val']})")
    else:
        print(f"  {concept:<45}: NOT FOUND")
