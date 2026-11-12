"""Mapa de dumps: sondea 120 offsets del nasdaq_exteral_data.csv.
El fichero parece contener N dumps concatenados (cada uno ordenado A..Z).
Detecta los cortes: un offset cuyo ticker < el del offset anterior => reset.
"""
import re, csv, io, urllib.request, json

csv.field_size_limit(10**9)
URL = "https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/Stock_news/nasdaq_exteral_data.csv"
SYM = re.compile(r'^[A-Z0-9.\-]{1,8}$')
SIZE = 23232979597

def probe(off):
    req = urllib.request.Request(URL, headers={'Range': f'bytes={off}-{off+250_000}'})
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                text = r.read().decode('utf-8', 'replace')
            break
        except Exception as e:
            print(f"  retry {off}: {e}", flush=True)
    else:
        return None, None
    text = text[text.find('\n') + 1:]
    for row in csv.reader(io.StringIO(text, newline='')):
        if len(row) >= 12 and SYM.match(row[3].strip()):
            return row[3].strip(), row[1]
    return None, None

prev = None
rows = []
for i in range(120):
    off = int(SIZE * (i + 0.5) / 120)
    s, d = probe(off)
    rows.append((off, s, d))
    print(f"{off/1e9:7.2f} GB  {str(s):8s} {d}", flush=True)
    prev = s or prev

resets = []
for j in range(1, len(rows)):
    a, b = rows[j-1][1], rows[j][1]
    if a and b and b < a and len(b) <= len(a):   # retroceso alfabetico
        resets.append({'off_gb': round(rows[j][0]/1e9, 2), 'off': rows[j][0],
                       'before': a, 'after': b})
print("\nRESETS detectados (frontera dump anterior -> dump nuevo):")
for r in resets:
    print(" ", r)
json.dump({'probes': [[o, s, d] for o, s, d in rows], 'resets': resets},
          open('data/dump_map.json', 'w'), indent=1)
print("[ok] data/dump_map.json")
