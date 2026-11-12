"""Script de Análisis Exhaustivo del Dataset Benzinga (raw_analyst_ratings.jsonl).

Analiza:
  1. Esquema, volumen total de registros (1.4M filas) y tickers únicos (6,204).
  2. Rango temporal global (2009 a 2020), desglose anual y mensual (estacionalidad).
  3. Desglose detallado por compañía: Ticker, Nombre SEC (si aplica), Fecha inicial (d0),
     Fecha final (d1), Días cubiertos, Volumen total de noticias y Tasa anual.
  4. Análisis de editores/fuentes (Publishers) y distribución horaria de publicación.
  5. Longitud y características léxicas de los titulares (headlines).

Salidas:
  - data/analisis_benzinga_companias.csv
  - data/analisis_benzinga_resumen.json
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime

BENZINGA_FILE = "data/benzinga/raw_analyst_ratings.jsonl"
CENSUS_FILE = "data/tier1_fechas_noticias.csv"
OUT_COMPANIES_CSV = "data/analisis_benzinga_companias.csv"
OUT_SUMMARY_JSON = "data/analisis_benzinga_resumen.json"


def analyze_benzinga():
    print("=" * 80)
    print("           ANÁLISIS FORENSE Y EXHAUSTIVO DEL DATASET BENZINGA")
    print("=" * 80)

    if not os.path.exists(BENZINGA_FILE):
        print(f"Error: {BENZINGA_FILE} no encontrado.")
        return

    # Cargar nombres SEC para cruce
    sec_names = {}
    sec_sectors = {}
    if os.path.exists(CENSUS_FILE):
        df_c = pd.read_csv(CENSUS_FILE, sep=";")
        for _, r in df_c.iterrows():
            sym = str(r["sym"]).strip()
            sec_names[sym] = str(r.get("sec_name", ""))
            sec_sectors[sym] = str(r.get("sector", ""))

    print(f"\nLeyendo {BENZINGA_FILE}...")
    total_lines = 0
    valid_records = 0
    corrupt_lines = 0

    stats_by_ticker = {} # ticker -> {'count': 0, 'min_date': str, 'max_date': str}
    publishers = {}
    year_counts = {}
    month_counts = {}
    hour_counts = {}
    headline_lens = []

    with open(BENZINGA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            total_lines += 1
            if total_lines % 300000 == 0:
                print(f"  Procesadas {total_lines:,} líneas...")

            if not line.strip().startswith("{"):
                corrupt_lines += 1
                continue

            try:
                item = json.loads(line)
            except:
                corrupt_lines += 1
                continue

            stock = item.get("stock")
            date_str = item.get("date", "")
            headline = item.get("headline", "")
            publisher = item.get("publisher", "Unknown")

            if not stock or not date_str or not headline:
                continue

            valid_records += 1
            headline_lens.append(len(headline))

            # Publishers
            publishers[publisher] = publishers.get(publisher, 0) + 1

            # Ticker stats
            if stock not in stats_by_ticker:
                stats_by_ticker[stock] = {
                    "count": 0,
                    "min_date": date_str,
                    "max_date": date_str
                }
            stats_by_ticker[stock]["count"] += 1
            if date_str < stats_by_ticker[stock]["min_date"]:
                stats_by_ticker[stock]["min_date"] = date_str
            if date_str > stats_by_ticker[stock]["max_date"]:
                stats_by_ticker[stock]["max_date"] = date_str

            # Temporal distribution
            # Formatos típicos: 2020-06-05 10:30:54-04:00
            try:
                yr = date_str[:4]
                mo = date_str[5:7]
                hr = date_str[11:13]
                year_counts[yr] = year_counts.get(yr, 0) + 1
                month_counts[mo] = month_counts.get(mo, 0) + 1
                if hr.isdigit():
                    hour_counts[hr] = hour_counts.get(hr, 0) + 1
            except:
                pass

    print(f"\n--- 1. RESUMEN GLOBAL DE VOLUMETRÍA ---")
    print(f"Total líneas escaneadas: {total_lines:,}")
    print(f"Total registros válidos de noticias: {valid_records:,}")
    print(f"Líneas corruptas / descartadas: {corrupt_lines:,} ({corrupt_lines/total_lines*100:.3f}%)")
    print(f"Total compañías / tickers únicos: {len(stats_by_ticker):,}")

    # ---------------------------------------------------------
    # 2. Desglose Temporal y Estacionalidad
    # ---------------------------------------------------------
    print("\n--- 2. DISTRIBUCIÓN TEMPORAL Y ESTACIONALIDAD ---")
    sorted_years = sorted(year_counts.items(), key=lambda x: x[0])
    print(f"{'Año':<6} {'Noticias':>10} {'% Total':>10}")
    print("-" * 30)
    for yr, cnt in sorted_years:
        print(f"{yr:<6} {cnt:>10,} {cnt/valid_records*100:>9.2f}%")

    print("\n--- DISTRIBUCIÓN POR HORA DEL DÍA (ZONA HORARIA EDT/EST) ---")
    sorted_hours = sorted(hour_counts.items(), key=lambda x: int(x[0]))
    pre_market = sum(c for h, c in sorted_hours if int(h) < 9)
    market_hours = sum(c for h, c in sorted_hours if 9 <= int(h) <= 16)
    post_market = sum(c for h, c in sorted_hours if int(h) > 16)
    print(f"  - Pre-Market (< 09:00):  {pre_market:>8,} ({pre_market/valid_records*100:.1f}%)")
    print(f"  - Regular (09:00-16:00): {market_hours:>8,} ({market_hours/valid_records*100:.1f}%)")
    print(f"  - Post-Market (> 16:00): {post_market:>8,} ({post_market/valid_records*100:.1f}%)")

    # ---------------------------------------------------------
    # 3. Análisis de Fuentes / Publishers
    # ---------------------------------------------------------
    print("\n--- 3. TOP 10 PUBLISHERS / AUTORES EN BENZINGA ---")
    sorted_pub = sorted(publishers.items(), key=lambda x: x[1], reverse=True)[:10]
    for p, cnt in sorted_pub:
        print(f"  - {p:<30s}: {cnt:>8,} ({cnt/valid_records*100:.2f}%)")

    # ---------------------------------------------------------
    # 4. Longitud de Titulares
    # ---------------------------------------------------------
    print("\n--- 4. ESTADÍSTICAS LÉXICAS DE TITULARES ---")
    print(f"Longitud media de titulares: {np.mean(headline_lens):.1f} caracteres")
    print(f"Mediana: {np.median(headline_lens):.0f} caracteres | Máximo: {np.max(headline_lens)} | Mínimo: {np.min(headline_lens)}")

    # ---------------------------------------------------------
    # 5. Desglose Exhaustivo por Compañía
    # ---------------------------------------------------------
    print("\n--- 5. DESGLOSE DETALLADO POR COMPAÑÍA ---")
    company_rows = []
    for ticker, data in stats_by_ticker.items():
        d0_raw = str(data["min_date"])[:10]
        d1_raw = str(data["max_date"])[:10]
        cnt = data["count"]
        
        days_span = 0
        try:
            dt0 = datetime.strptime(d0_raw, "%Y-%m-%d")
            dt1 = datetime.strptime(d1_raw, "%Y-%m-%d")
            days_span = (dt1 - dt0).days
        except:
            pass

        years_span = round(days_span / 365.25, 2)
        annual_rate = round(cnt / max(1.0, years_span), 1)

        company_rows.append({
            "ticker": ticker,
            "company_name": sec_names.get(ticker, ""),
            "sector": sec_sectors.get(ticker, ""),
            "is_sp500_tier1": ticker in sec_names,
            "d0_news": d0_raw,
            "d1_news": d1_raw,
            "days_span": days_span,
            "years_span": years_span,
            "news_count": cnt,
            "news_per_year": annual_rate
        })

    df_companies = pd.DataFrame(company_rows)
    df_companies.sort_values(by="news_count", ascending=False, inplace=True)
    df_companies.to_csv(OUT_COMPANIES_CSV, index=False, encoding="utf-8-sig")
    print(f"Desglose completo de las 6,204 compañías guardado en: {OUT_COMPANIES_CSV}")

    # Top 25 compañías en Benzinga
    print("\n--- TOP 25 COMPAÑÍAS CON MÁS NOTICIAS EN BENZINGA ---")
    print(f"{'Ticker':<7} {'Nombre':<30} {'Sector':<22} {'Desde':<12} {'Hasta':<12} {'Años':<6} {'Noticias':>8}")
    print("-" * 105)
    for _, r in df_companies.head(25).iterrows():
        name = r["company_name"] if r["company_name"] else "---"
        sec = r["sector"] if r["sector"] else "---"
        print(f"{r['ticker']:<7} {name[:28]:<30} {sec[:20]:<22} {r['d0_news']:<12} {r['d1_news']:<12} {r['years_span']:<6.1f} {r['news_count']:>8,}")

    # Estadísticas para el universo Tier 1 / S&P 500
    df_t1 = df_companies[df_companies["is_sp500_tier1"] == True]
    print(f"\n--- ESTADÍSTICAS DEL UNIVERSO S&P 500 TIER 1 EN BENZINGA ({len(df_t1)} tickers presentes) ---")
    print(f"Total noticias acumuladas en Tier 1: {df_t1['news_count'].sum():,}")
    print(f"Media de noticias por empresa Tier 1: {df_t1['news_count'].mean():.1f}")
    print(f"Mediana: {df_t1['news_count'].median():.1f}")
    print(f"Mínimo: {df_t1['news_count'].min()} | Máximo: {df_t1['news_count'].max():,}")

    # Resumen JSON
    summary_data = {
        "dataset_name": "Benzinga Pro Analyst Ratings & News Feed",
        "total_records": valid_records,
        "unique_tickers": len(stats_by_ticker),
        "global_date_start": min(r["d0_news"] for r in company_rows),
        "global_date_end": max(r["d1_news"] for r in company_rows),
        "mean_headline_length": float(round(np.mean(headline_lens), 1)),
        "yearly_distribution": dict(sorted_years),
        "top_publishers": dict(sorted_pub),
        "top_10_tickers": df_companies.head(10)[["ticker", "news_count", "d0_news", "d1_news"]].to_dict(orient="records")
    }

    with open(OUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    print(f"\nResumen JSON guardado en: {OUT_SUMMARY_JSON}")
    print("=" * 80)
    print("           ANÁLISIS DE BENZINGA COMPLETADO CON ÉXITO")
    print("=" * 80)


if __name__ == "__main__":
    analyze_benzinga()
