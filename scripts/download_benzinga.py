import os
import sys
import time
import urllib.request

URL = "https://huggingface.co/datasets/khaihernlow/massive-stock-news-analysis-db-for-nlpbacktests/resolve/main/data/raw_analyst_ratings.jsonl"
OUT_PATH = "data/benzinga/raw_analyst_ratings.jsonl"
OUT_TMP = OUT_PATH + ".tmp"

os.makedirs("data/benzinga", exist_ok=True)

if os.path.exists(OUT_PATH) and os.path.getsize(OUT_PATH) > 400 * 1024 * 1024:
    print(f"File already downloaded: {OUT_PATH} ({os.path.getsize(OUT_PATH)/(1024*1024):.2f} MB)")
    sys.exit(0)

print(f"Starting download from Hugging Face to {OUT_PATH}...")
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})

t0 = time.time()
last_report = t0
downloaded = 0

with urllib.request.urlopen(req) as resp, open(OUT_TMP, "wb") as f_out:
    total_size = int(resp.headers.get("content-length", 419 * 1024 * 1024))
    print(f"Total file size: {total_size / (1024*1024):.2f} MB")
    
    while True:
        chunk = resp.read(1024 * 1024) # 1 MB
        if not chunk:
            break
        f_out.write(chunk)
        downloaded += len(chunk)
        
        now = time.time()
        if now - last_report >= 5.0:
            speed = (downloaded / (1024 * 1024)) / (now - t0)
            pct = (downloaded / total_size) * 100
            print(f"Progress: {downloaded / (1024*1024):.1f} / {total_size / (1024*1024):.1f} MB ({pct:.1f}%) @ {speed:.2f} MB/s")
            last_report = now

if os.path.exists(OUT_PATH):
    os.remove(OUT_PATH)
os.rename(OUT_TMP, OUT_PATH)

dt = time.time() - t0
print(f"Download complete! Saved to {OUT_PATH} in {dt:.1f}s ({os.path.getsize(OUT_PATH)/(1024*1024):.2f} MB)")
