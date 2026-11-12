"""Script de Análisis Exhaustivo de Duplicados y Solapes en Datasets de Noticias (FNSPID y Benzinga).

Analiza 3 dimensiones críticas:
  1. DUPLICADOS INTERNOS EN FNSPID:
     - Duplicados exactos (Ticker + Fecha + Titular).
     - Sindicación multi-ticker (mismo titular en varios tickers).
     - Repetición temporal de titulares para una misma empresa.
  2. DUPLICADOS INTERNOS EN BENZINGA:
     - Duplicados exactos (Stock + Timestamp + Titular).
     - Difusión multi-ticker en masa (artículos de lista asignados a decenas de tickers).
     - Repetición de titulares idénticos en distintas fechas.
  3. SOLAPE Y DUPLICADOS CRUZADOS (BENZINGA vs. FNSPID):
     - Titulares idénticos compartidos entre ambos datasets.
     - Detección de sindicación institucional (Zacks, Benzinga, PR Newswire, Reuters).
     - Impacto metodológico en el entrenamiento y particionado de datos (Train/Val vs Test).

Salidas:
  - data/analisis_duplicados_resumen.json
"""

import os
import sys
import glob
import json
import csv
import io
import re
from collections import Counter
import numpy as np
import pandas as pd

csv.field_size_limit(10**9)

DATA_DIR = "data"
BENZINGA_FILE = os.path.join(DATA_DIR, "benzinga", "raw_analyst_ratings.jsonl")
WINDOWS_DIR = os.path.join(DATA_DIR, "windows")
OUT_JSON = os.path.join(DATA_DIR, "analisis_duplicados_resumen.json")


def clean_headline(h):
    if not h: return ""
    h = h.lower().strip()
    h = re.sub(r'\s+', ' ', h)
    return h


def analyze_duplicates():
    print("=" * 80)
    print("      AUDITORÍA DE DUPLICADOS, SINDICACIÓN Y SOLAPE ENTRE DATASETS")
    print("=" * 80)

    # =========================================================================
    # 1. DUPLICADOS INTERNOS EN FNSPID
    # =========================================================================
    print("\n" + "="*40)
    print("1. ANÁLISIS DE DUPLICADOS INTERNOS EN FNSPID")
    print("="*40)

    bin_files = sorted(glob.glob(os.path.join(WINDOWS_DIR, "*.bin")))
    print(f"Cargando noticias crudas de FNSPID desde {len(bin_files)} volcados locales...")
    
    fn_records = []
    for fpath in bin_files:
        with open(fpath, "rb") as f:
            raw = f.read()
        raw = raw[:raw.rfind(b"\n")]
        reader = csv.reader(io.StringIO(raw.decode("utf-8", "replace"), newline=""))
        for r in reader:
            if len(r) >= 4:
                date_str = r[1].replace(" UTC", "").strip()[:10] if len(r) > 1 else ""
                title = r[2].strip() if len(r) > 2 else ""
                ticker = r[3].strip() if len(r) > 3 else ""
                if ticker and title and len(date_str) == 10:
                    fn_records.append({
                        "ticker": ticker,
                        "date": date_str,
                        "headline": title,
                        "clean_title": clean_headline(title)
                    })

    df_fn = pd.DataFrame(fn_records)
    total_fn = len(df_fn)
    print(f"Total noticias FNSPID analizadas: {total_fn:,}")

    # Duplicados exactos: (ticker, date, clean_title)
    dup_exact_fn = df_fn.duplicated(subset=["ticker", "date", "clean_title"], keep="first").sum()
    pct_exact_fn = (dup_exact_fn / total_fn) * 100 if total_fn > 0 else 0
    print(f"\n[A] Duplicados exactos (mismo ticker + misma fecha + mismo titular):")
    print(f"    {dup_exact_fn:,} filas ({pct_exact_fn:.2f}%)")

    # Mismo titular repetido en diferentes fechas para el mismo ticker
    dup_ticker_title_fn = df_fn.duplicated(subset=["ticker", "clean_title"], keep="first").sum()
    pct_ticker_title_fn = (dup_ticker_title_fn / total_fn) * 100 if total_fn > 0 else 0
    print(f"\n[B] Titulares repetidos en distintas fechas para la misma empresa:")
    print(f"    {dup_ticker_title_fn:,} filas ({pct_ticker_title_fn:.2f}%)")

    # Sindicación multi-ticker en FNSPID (mismo titular en varios tickers en la misma fecha)
    title_ticker_counts_fn = df_fn.groupby(["clean_title", "date"])["ticker"].nunique()
    multi_ticker_titles_fn = title_ticker_counts_fn[title_ticker_counts_fn > 1]
    print(f"\n[C] Eventos de sindicación multi-ticker (mismo titular en >1 ticker el mismo día):")
    print(f"    {len(multi_ticker_titles_fn):,} titulares únicos sindicados")

    top_multi_fn = df_fn[df_fn["clean_title"].isin(multi_ticker_titles_fn.head(10).index.get_level_values(0))]
    print("\nEjemplos de noticias sindicadas multi-ticker en FNSPID:")
    seen_examples = set()
    for _, r in top_multi_fn.iterrows():
        t = r["clean_title"]
        if t not in seen_examples and len(seen_examples) < 4:
            seen_examples.add(t)
            matching = df_fn[df_fn["clean_title"] == t]["ticker"].unique().tolist()
            print(f"  * \"{r['headline']}\" -> Asociada a {len(matching)} tickers: {matching[:6]}")

    # =========================================================================
    # 2. DUPLICADOS INTERNOS EN BENZINGA
    # =========================================================================
    print("\n" + "="*40)
    print("2. ANÁLISIS DE DUPLICADOS INTERNOS EN BENZINGA")
    print("="*40)

    print(f"Escaneando dataset completo de Benzinga: {BENZINGA_FILE}...")
    bz_exact_seen = set() # (stock, date, clean_title)
    bz_ticker_title_seen = set() # (stock, clean_title)
    bz_title_counter = Counter() # clean_title -> count total
    bz_title_to_tickers = {} # clean_title -> set of stocks

    total_bz = 0
    bz_exact_dups = 0
    bz_temporal_dups = 0

    with open(BENZINGA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            total_bz += 1
            if total_bz % 400000 == 0:
                print(f"  Procesadas {total_bz:,} noticias de Benzinga...")
            if not line.strip().startswith("{"):
                continue
            try:
                item = json.loads(line)
            except:
                continue

            stock = item.get("stock")
            date_str = item.get("date", "")[:10]
            headline = item.get("headline", "")
            if not stock or not headline or len(date_str) < 10:
                continue

            clean_h = clean_headline(headline)

            # Exact dup (stock, date, clean_h)
            exact_key = (stock, date_str, clean_h)
            if exact_key in bz_exact_seen:
                bz_exact_dups += 1
            else:
                bz_exact_seen.add(exact_key)

            # Temporal dup (stock, clean_h)
            temporal_key = (stock, clean_h)
            if temporal_key in bz_ticker_title_seen:
                bz_temporal_dups += 1
            else:
                bz_ticker_title_seen.add(temporal_key)

            bz_title_counter[clean_h] += 1
            if clean_h not in bz_title_to_tickers:
                bz_title_to_tickers[clean_h] = set()
            if len(bz_title_to_tickers[clean_h]) < 50:
                bz_title_to_tickers[clean_h].add(stock)

    pct_exact_bz = (bz_exact_dups / total_bz) * 100 if total_bz > 0 else 0
    pct_temp_bz = (bz_temporal_dups / total_bz) * 100 if total_bz > 0 else 0

    print(f"\nTotal registros analizados en Benzinga: {total_bz:,}")
    print(f"\n[A] Duplicados exactos (mismo stock + misma fecha + mismo titular):")
    print(f"    {bz_exact_dups:,} filas ({pct_exact_bz:.2f}%)")
    print(f"\n[B] Titulares repetidos en diferentes fechas para la misma empresa:")
    print(f"    {bz_temporal_dups:,} filas ({pct_temp_bz:.2f}%)")

    # Titulares masivamente difundidos a múltiples tickers
    multi_broadcast = [(h, len(stks), bz_title_counter[h]) for h, stks in bz_title_to_tickers.items() if len(stks) >= 10]
    multi_broadcast.sort(key=lambda x: x[2], reverse=True)
    print(f"\n[C] Titulares con difusión masiva multi-ticker (>=10 tickers con el mismo titular):")
    print(f"    {len(multi_broadcast):,} titulares distintos distribuidos en masa")
    print("\nTop 5 titulares más repetidos en Benzinga a través de múltiples tickers:")
    for h, num_stks, cnt in multi_broadcast[:5]:
        print(f"  * \"{h}\"")
        print(f"    -> Repetido {cnt:,} veces en {num_stks} tickers distintos.")

    # =========================================================================
    # 3. SOLAPE Y DUPLICADOS CRUZADOS (BENZINGA vs. FNSPID)
    # =========================================================================
    print("\n" + "="*40)
    print("3. ANÁLISIS DE SOLAPE CRUZADO (BENZINGA vs. FNSPID)")
    print("="*40)

    fn_unique_titles = set(df_fn["clean_title"].unique())
    print(f"Total titulares únicos en volcado FNSPID: {len(fn_unique_titles):,}")
    print(f"Total titulares únicos en Benzinga: {len(bz_title_counter):,}")

    cross_overlap = fn_unique_titles.intersection(set(bz_title_counter.keys()))
    print(f"\n[A] Titulares IDÉNTICOS compartidos entre Benzinga y FNSPID:")
    print(f"    {len(cross_overlap):,} titulares únicos idénticos encontrados en ambos datasets")
    pct_cross_fn = (len(cross_overlap) / len(fn_unique_titles)) * 100 if fn_unique_titles else 0
    print(f"    -> Representan el {pct_cross_fn:.2f}% de la diversidad de titulares de FNSPID")

    print("\nEjemplos reales de noticias idénticas compartidas entre Benzinga y FNSPID:")
    sample_overlap = sorted(list(cross_overlap), key=lambda x: bz_title_counter[x], reverse=True)[:8]
    for h in sample_overlap:
        bz_cnt = bz_title_counter[h]
        fn_matches = df_fn[df_fn["clean_title"] == h]["ticker"].unique()
        print(f"  * \"{h}\"")
        print(f"    -> En Benzinga: {bz_cnt} veces | En FNSPID: {len(fn_matches)} tickers ({list(fn_matches)[:4]})")

    # =========================================================================
    # 4. GUARDAR INFORME DE RESULTADOS
    # =========================================================================
    results = {
        "fnspid": {
            "total_news_analyzed": total_fn,
            "exact_duplicates": int(dup_exact_fn),
            "exact_duplicates_pct": float(round(pct_exact_fn, 3)),
            "temporal_duplicates": int(dup_ticker_title_fn),
            "temporal_duplicates_pct": float(round(pct_ticker_title_fn, 3)),
            "multi_ticker_titles_count": len(multi_ticker_titles_fn)
        },
        "benzinga": {
            "total_news_analyzed": total_bz,
            "exact_duplicates": int(bz_exact_dups),
            "exact_duplicates_pct": float(round(pct_exact_bz, 3)),
            "temporal_duplicates": int(bz_temporal_dups),
            "temporal_duplicates_pct": float(round(pct_temp_bz, 3)),
            "multi_ticker_broadcast_titles": len(multi_broadcast),
            "top_repeated_headlines": [
                {"headline": h, "tickers_count": n, "total_occurrences": c}
                for h, n, c in multi_broadcast[:10]
            ]
        },
        "cross_dataset": {
            "fnspid_unique_headlines": len(fn_unique_titles),
            "benzinga_unique_headlines": len(bz_title_counter),
            "shared_exact_headlines": len(cross_overlap),
            "overlap_pct_of_fnspid": float(round(pct_cross_fn, 2)),
            "sample_shared_headlines": sample_overlap[:10]
        }
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nInforme de duplicados guardado en: {OUT_JSON}")
    print("=" * 80)
    print("      AUDITORÍA DE DUPLICADOS COMPLETADA CON ÉXITO")
    print("=" * 80)


if __name__ == "__main__":
    analyze_duplicates()
