import io, re, urllib.request
import pandas as pd

URL = "https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/Stock_news/All_external.csv"
COLS = ['Date','Article_title','Stock_symbol','Url','Publisher','Author','Article',
        'Lsa_summary','Luhn_summary','Textrank_summary','Lexrank_summary']

for offset_mb in (500, 3000, 4800):
    start = offset_mb * 1_000_000
    req = urllib.request.Request(URL, headers={'Range': f'bytes={start}-{start+40_000_000}'})
    raw = urllib.request.urlopen(req, timeout=240).read().decode('utf-8', 'replace')
    nl = raw.find('\n') + 1
    m = re.search(r'^\d{4}-\d{2}-\d{2}', raw[nl:], re.M)
    if not m:
        print(offset_mb, "no line start found"); continue
    df = pd.read_csv(io.StringIO(raw[nl + m.start():]), names=COLS,
                     engine='python', on_bad_lines='skip')
    print("=" * 70)
    print(f"OFFSET {offset_mb} MB | filas alineadas: {len(df)}")
    print("  rangos fechas:", df['Date'].min(), "->", df['Date'].max())
    filled = {c: int(df[c].notna().sum()) for c in COLS[4:]}
    print("  no-nulos:", filled)
    print("  Publisher top:", df['Publisher'].value_counts().head(3).to_dict())
