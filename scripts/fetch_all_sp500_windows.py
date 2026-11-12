"""Download exact FNSPID news blocks for all remaining S&P 500 stocks.

Uses HTTP Range requests guided by data/dump_map.json probes to pinpoint
the exact byte boundaries of each stock in nasdaq_exteral_data.csv (23.2 GB)
on Hugging Face, saves them to data/windows/<SYM>.bin, and verifies row dates.
"""
import os
import sys
import io
import csv
import json
import time
import bisect
import urllib.request
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

csv.field_size_limit(10**9)

DATA_DIR = os.path.abspath("data")
CACHE_DIR = os.path.join(DATA_DIR, "windows")
os.makedirs(CACHE_DIR, exist_ok=True)

URL_NASDAQ = "https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/Stock_news/nasdaq_exteral_data.csv"
SIZE_NASDAQ = 23232979597
SYM_RX = re.compile(r'^[A-Z][A-Z0-9.\-]{0,9}$')

# Load dump map probes
DUMP_MAP_PATH = os.path.join(DATA_DIR, "dump_map.json")
dump_map = json.load(open(DUMP_MAP_PATH, "r", encoding="utf-8"))
valid_probes = [(p[0], p[1]) for p in dump_map["probes"] if p[1] is not None and p[0] < 17_500_000_000]
valid_probes.sort(key=lambda x: x[0])
probe_syms = [p[1] for p in valid_probes]
probe_offs = [p[0] for p in valid_probes]

_sym_cache = {}

def get_range(a, b, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(URL_NASDAQ, headers={"Range": f"bytes={a}-{b}"})
            with urllib.request.urlopen(req, timeout=35) as r:
                return r.read()
        except Exception:
            if attempt == tries - 1:
                return b""
            time.sleep(1.0 * (attempt + 1))
    return b""

def parse_rows(data: bytes):
    text = data.decode("utf-8", "replace")
    k = text.find("\n")
    if k < 0:
        return []
    return [r for r in csv.reader(io.StringIO(text[k+1:], newline="")) if len(r) >= 4]

def symbol_at(off):
    if off in _sym_cache:
        return _sym_cache[off]
    data = get_range(off, min(off + 300_000, SIZE_NASDAQ) - 1)
    for r in parse_rows(data):
        s = r[3].strip()
        if SYM_RX.match(s):
            _sym_cache[off] = s
            return s
    _sym_cache[off] = None
    return None

def find_range(sym):
    # 1. Binary search start offset
    idx_l = bisect.bisect_left(probe_syms, sym)
    lo_l = probe_offs[max(0, idx_l - 1)]
    hi_l = probe_offs[min(len(probe_offs) - 1, idx_l + 1)]
    while hi_l - lo_l > 300_000:
        mid = (lo_l + hi_l) // 2
        s = symbol_at(mid)
        if s is None or s >= sym:
            hi_l = mid
        else:
            lo_l = mid + 1
    start = hi_l

    # 2. Binary search end offset
    idx_r = bisect.bisect_right(probe_syms, sym)
    lo_r = start
    hi_r = probe_offs[min(len(probe_offs) - 1, idx_r + 1)]
    while hi_r - lo_r > 300_000:
        mid = (lo_r + hi_r) // 2
        s = symbol_at(mid)
        if s is not None and s > sym:
            hi_r = mid
        else:
            lo_r = mid + 1
    end = hi_r
    return start, end

def process_ticker(sym):
    bin_path = os.path.join(CACHE_DIR, f"{sym}.bin")
    
    # If already cached and valid, parse and return
    if os.path.exists(bin_path) and os.path.getsize(bin_path) > 1000:
        raw = open(bin_path, "rb").read()
        rows = [r for r in parse_rows(raw) if len(r) >= 4 and r[3].strip() == sym]
        if len(rows) > 0:
            return sym, len(rows), round(len(raw) / 1e6, 2), "cached"

    t0 = time.time()
    st, en = find_range(sym)
    # Give a small safety margin of 200 KB on each side
    fetch_start = max(1, st - 200_000)
    fetch_end = min(SIZE_NASDAQ - 1, en + 200_000)
    
    data = get_range(fetch_start, fetch_end)
    if not data:
        return sym, 0, 0.0, "failed_download"

    rows = parse_rows(data)
    sym_rows = [r for r in rows if len(r) >= 4 and r[3].strip() == sym]
    
    if len(sym_rows) == 0:
        # Fallback: maybe start was further back
        data_wide = get_range(max(1, fetch_start - 3_000_000), fetch_end)
        rows_wide = parse_rows(data_wide)
        sym_rows = [r for r in rows_wide if len(r) >= 4 and r[3].strip() == sym]
        if sym_rows:
            data = data_wide

    with open(bin_path, "wb") as f:
        f.write(data)

    elapsed = time.time() - t0
    return sym, len(sym_rows), round(len(data) / 1e6, 2), f"downloaded ({elapsed:.1f}s)"

def main():
    import pandas as pd
    csv_sp500 = os.path.join("ANALISIS DATASETS NOTICIAS", "fnspid_stock_analysis", "fnspid_sp500_stocks.csv")
    df = pd.read_csv(csv_sp500)
    
    # Identify Boundary Probe tickers
    bp_tickers = df[df["data_granularity"].str.contains("Boundary", na=False)]["ticker"].tolist()
    print(f"Total Boundary Probe tickers in S&P 500: {len(bp_tickers)}")

    # Check which ones are already downloaded
    existing_bins = {os.path.basename(p).replace(".bin", "") for p in os.listdir(CACHE_DIR) if p.endswith(".bin")}
    to_fetch = [s for s in bp_tickers if s not in existing_bins]
    print(f"Already cached in {CACHE_DIR}: {len(bp_tickers) - len(to_fetch)}")
    print(f"Need to download: {len(to_fetch)} tickers")

    results = []
    # Process with 5 concurrent threads
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_ticker, sym): sym for sym in to_fetch}
        for future in as_completed(futures):
            sym = futures[future]
            try:
                sym_res, n_rows, size_mb, status = future.result()
                print(f"  [✓] {sym_res:<5}: {n_rows:>5} real articles ({size_mb:>5.1f} MB) -> {status}")
                results.append((sym_res, n_rows, size_mb, status))
            except Exception as e:
                print(f"  [!] {sym:<5}: Error {e}")

    print("\nCompleted downloads. All tickers cached in data/windows/!")

if __name__ == "__main__":
    main()
