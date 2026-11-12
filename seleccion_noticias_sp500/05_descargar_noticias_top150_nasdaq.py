"""05_descargar_noticias_top150_nasdaq.py
=============================================================================
Descarga bajo demanda de los artículos completos de noticias de FNSPID (NASDAQ)
para las 150 empresas de élite del S&P 500.

Utiliza peticiones HTTP Range multihilo sobre el volcado masivo en Hugging Face
(nasdaq_exteral_data.csv, 23.2 GB) guiadas por búsqueda binaria de offsets.
Guarda los bloques exactos en data/windows/{TICKER}.bin.
=============================================================================
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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(DATA_DIR, "windows")
os.makedirs(CACHE_DIR, exist_ok=True)

URL_NASDAQ = "https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/Stock_news/nasdaq_exteral_data.csv"
SIZE_NASDAQ = 23232979597
SYM_RX = re.compile(r'^[A-Z][A-Z0-9.\-]{0,9}$')

# Cargar mapa de sondas para búsqueda binaria
DUMP_MAP_PATH = os.path.join(DATA_DIR, "dump_map.json")
if not os.path.exists(DUMP_MAP_PATH):
    raise FileNotFoundError(f"No se encontró {DUMP_MAP_PATH}")

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
    # 1. Búsqueda binaria inicio
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

    # 2. Búsqueda binaria fin
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
    
    # Si ya existe con tamaño significativo, verificar y retornar
    if os.path.exists(bin_path) and os.path.getsize(bin_path) > 1000:
        raw = open(bin_path, "rb").read()
        rows = [r for r in parse_rows(raw) if len(r) >= 4 and r[3].strip() == sym]
        if len(rows) > 0:
            return sym, len(rows), round(len(raw) / 1e6, 2), "ya descargado (cached)"

    t0 = time.time()
    st, en = find_range(sym)
    fetch_start = max(1, st - 200_000)
    fetch_end = min(SIZE_NASDAQ - 1, en + 200_000)
    
    data = get_range(fetch_start, fetch_end)
    if not data:
        return sym, 0, 0.0, "fallo_descarga"

    rows = parse_rows(data)
    sym_rows = [r for r in rows if len(r) >= 4 and r[3].strip() == sym]
    
    if len(sym_rows) == 0:
        data_wide = get_range(max(1, fetch_start - 3_000_000), fetch_end)
        rows_wide = parse_rows(data_wide)
        sym_rows = [r for r in rows_wide if len(r) >= 4 and r[3].strip() == sym]
        if sym_rows:
            data = data_wide

    with open(bin_path, "wb") as f:
        f.write(data)

    elapsed = time.time() - t0
    return sym, len(sym_rows), round(len(data) / 1e6, 2), f"descargado ({elapsed:.1f}s)"

def load_top150():
    excel_path = os.path.join(SCRIPT_DIR, "sp500_noticias_ordenadas_train_val_test.xlsx")
    json_path = os.path.join(DATA_DIR, "top150_tickers.json")
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    if os.path.exists(excel_path):
        import openpyxl
        wb = openpyxl.load_workbook(excel_path, read_only=True)
        ws = wb['Top Empresas Continuas']
        tickers = []
        for row in ws.iter_rows(values_only=True):
            if row[1] and row[1] != 'Ticker':
                tickers.append(row[1])
            if len(tickers) >= 150:
                break
        return tickers

    raise FileNotFoundError("No se encontró la lista de Top 150 empresas.")

def main():
    print("=" * 70)
    print("  DESCARGA DE NOTICIAS ÍNTEGRAS FNSPID (NASDAQ) - TOP 150 S&P 500")
    print("=" * 70)
    
    top150 = load_top150()
    print(f"Total empresas objetivo en el Top 150: {len(top150)}")
    
    existing = {os.path.basename(p).replace(".bin", "").replace(".bad", "") for p in os.listdir(CACHE_DIR) if ".bin" in p}
    to_fetch = [s for s in top150 if s not in existing]
    
    print(f"Empresas ya disponibles en data/windows/: {len(top150) - len(to_fetch)} / {len(top150)}")
    print(f"Empresas pendientes de descarga:         {len(to_fetch)}")
    print("-" * 70)

    if not to_fetch:
        print("[✓] ¡Todas las 150 empresas ya están descargadas en local!")
        return

    # Descarga multihilo concurrente (6 workers para no saturar Hugging Face)
    workers = 6
    print(f"Iniciando descarga multihilo con {workers} conexiones concurrentes...")
    
    success_count = 0
    fail_count = 0
    total_articles = 0
    total_mb = 0.0
    t_start = time.time()
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_ticker, sym): sym for sym in to_fetch}
        for i, future in enumerate(as_completed(futures), 1):
            sym = futures[future]
            try:
                sym_res, n_rows, size_mb, status = future.result()
                if n_rows > 0:
                    success_count += 1
                    total_articles += n_rows
                    total_mb += size_mb
                    print(f"[{i:>3}/{len(to_fetch)}] [✓] {sym_res:<5}: {n_rows:>5} artículos ({size_mb:>5.1f} MB) -> {status}", flush=True)
                else:
                    fail_count += 1
                    print(f"[{i:>3}/{len(to_fetch)}] [?] {sym_res:<5}: 0 artículos detectados ({size_mb:>5.1f} MB) -> {status}", flush=True)
            except Exception as e:
                fail_count += 1
                print(f"[{i:>3}/{len(to_fetch)}] [!] {sym:<5}: Error en descarga -> {e}", flush=True)

    elapsed = time.time() - t_start
    print("=" * 70)
    print(f"Descarga finalizada en {elapsed:.1f} segundos ({elapsed/60:.1f} minutos).")
    print(f"Empresas descargadas con éxito: {success_count} / {len(to_fetch)}")
    print(f"Total artículos incorporados:   {total_articles:,}")
    print(f"Volumen total descargado:       {total_mb:.1f} MB")
    
    # Comprobación final
    final_existing = {os.path.basename(p).replace(".bin", "").replace(".bad", "") for p in os.listdir(CACHE_DIR) if ".bin" in p}
    covered = [s for s in top150 if s in final_existing]
    print(f"\nCobertura final de las Top 150 en data/windows/: {len(covered)} / {len(top150)} ({len(covered)/len(top150)*100:.1f}%)")
    print("=" * 70)

if __name__ == "__main__":
    main()
