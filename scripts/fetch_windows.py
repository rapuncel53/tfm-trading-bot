"""Búsqueda binaria por rangos HTTP en nasdaq_exteral_data.csv (23 GB).
El fichero esta ORDENADO por ticker -> localizar bloques de ticker con
sondeos de ~200 KB, sin descargar el fichero entero.
"""
import os, re, io, csv, json, time, urllib.request

csv.field_size_limit(10**9)   # los articulos del nasdaq superan el limite por defecto
URL = "https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/Stock_news/nasdaq_exteral_data.csv"
CACHE = 'data/windows'
os.makedirs(CACHE, exist_ok=True)
SYM_RX = re.compile(r'^[A-Z][A-Z0-9.\-]{0,9}$')

def get_range(a, b, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(URL, headers={'Range': f'bytes={a}-{b}'})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception:
            if i == tries-1: raise
            time.sleep(2*(i+1))

def file_size():
    req = urllib.request.Request(URL, method='HEAD')
    with urllib.request.urlopen(req, timeout=30) as r:
        return int(r.headers['Content-Length'])

def parse_rows(data: bytes):
    text = data.decode('utf-8', 'replace')
    k = text.find('\n')
    if k < 0: return []
    return [r for r in csv.reader(io.StringIO(text[k+1:], newline='')) if len(r) >= 4]

_cache = {}
def symbol_at(off, size):
    """Simbolo del primer registro completo tras el offset off."""
    if off in _cache: return _cache[off]
    n = 300_000
    while n <= 12_000_000:
        rows = parse_rows(get_range(off, min(off+n, size)-1))
        for r in rows:
            s = r[3].strip()
            if SYM_RX.match(s):
                _cache[off] = s
                return s
        n *= 3
    _cache[off] = None
    return None

def find_start(target, size):
    """Primer offset donde el ticker >= target (busqueda binaria).
    Invariante: symbol(lo-1) < target <= symbol(hi)."""
    lo, hi = 1, size - 1
    while hi - lo > 400_000:
        mid = (lo + hi) // 2
        s = symbol_at(mid, size)
        if s is None:
            hi = mid
        elif s < target:
            lo = mid + 1
        else:
            hi = mid
    return hi

def extract_window(target, size, chunk=26_000_000, cap_mb=200):
    """Descarga el bloque del ticker. Si el buffer no contiene el target,
    retrocede mas lejos y reintenta (el binario puede aterrizas pasados bloques cortos)."""
    p = f'{CACHE}/{target}.bin'
    if os.path.exists(p):
        # validar que contiene el target, si no re-extraer
        rows = parse_rows(open(p,'rb').read())
        if any(r[3].strip() == target for r in rows[:200000]):
            return p, True
    start0 = find_start(target, size)
    for back in (1_500_000, 25_000_000, 150_000_000):
        start = max(1, start0 - back)
        buf = bytearray()
        end = start
        has_t = False
        while len(buf) < cap_mb*1_000_000:
            data = get_range(end, min(end+chunk, size)-1)
            buf += data
            end += len(data)
            syms = {r[3].strip() for r in parse_rows(bytes(buf)) if SYM_RX.match(r[3].strip())}
            has_t = target in syms
            beyond = any(s > target for s in syms)
            if has_t and beyond:
                break
            if end >= size-1:
                break
        if has_t:
            open(p, 'wb').write(buf)
            return p, end < size-1
    open(p, 'wb').write(buf)
    return p, False

def main():
    syms = __import__('sys').argv[1:] or ['AAPL','TSLA','MSFT','XOM','F']
    size = file_size()
    print(f"[+] fichero: {size/1e9:.2f} GB", flush=True)
    for t in syms:
        p, complete = extract_window(t, size)
        rows = parse_rows(open(p,'rb').read())
        cnt = sum(1 for r in rows if r[3].strip() == t)
        print(f"[✓] {t}: {len(rows)} filas leidas, {cnt} del ticker "
              f"({'completo' if complete else 'TRUNCADO a 150MB'}) -> {p}", flush=True)

if __name__ == '__main__':
    main()
