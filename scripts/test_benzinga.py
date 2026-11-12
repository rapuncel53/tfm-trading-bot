import urllib.request
import csv
import io

url = 'https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/Stock_news/All_external.csv'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Range': f'bytes={50*1024*1024}-{51*1024*1024}'})
with urllib.request.urlopen(req) as resp:
    data = resp.read().decode('utf-8', errors='ignore')

lines = data.split('\n')
msft_items = []
for line in lines:
    if 'MSFT' in line:
        msft_items.append(line)

print(f"Total MSFT lines in 50-51MB of All_external: {len(msft_items)}")
for l in msft_items[:5]:
    print(" ", l[:120])
