"""Script de Análisis Exhaustivo del Dataset FNSPID (Financial News and Stock Price Integration Dataset).

Analiza:
  1. Esquema, volumen global y completitud de campos (titular, texto completo, resúmenes LSA/Luhn/Textrank/Lexrank).
  2. Rango temporal global y desglose anual de noticias.
  3. Desglose detallado por compañía: Ticker, Nombre, Sector, Fecha inicial (d0), Fecha final (d1),
     Días de cobertura, Total de noticias y Perfil temporal.
  4. Estadísticas de longitud de texto (titulares y cuerpos de artículo).

Fuentes procesadas:
  - data/windows/*.bin (volcado real de nasdaq_exteral_data.csv)
  - data/sample_nasdaq.csv y data/sample_all_external.csv
  - data/tier1_fechas_noticias.csv (censo integral de 202 empresas S&P 500)
  - data/splits/*/news.parquet (noticias FNSPID procesadas en el pipeline)

Salidas:
  - data/analisis_fnspid_companias.csv
  - data/analisis_fnspid_resumen.json
"""

import os
import sys
import glob
import json
import csv
import io
import numpy as np
import pandas as pd
from datetime import datetime

csv.field_size_limit(10**9)

DATA_DIR = "data"
WINDOWS_DIR = os.path.join(DATA_DIR, "windows")
CENSUS_FILE = os.path.join(DATA_DIR, "tier1_fechas_noticias.csv")
OUT_COMPANIES_CSV = os.path.join(DATA_DIR, "analisis_fnspid_companias.csv")
OUT_SUMMARY_JSON = os.path.join(DATA_DIR, "analisis_fnspid_resumen.json")


def analyze_fnspid():
    print("=" * 80)
    print("           ANÁLISIS FORENSE Y EXHAUSTIVO DEL DATASET FNSPID")
    print("=" * 80)

    # ---------------------------------------------------------
    # 1. Inspección de Esquema y Muestras (sample_nasdaq y sample_all_external)
    # ---------------------------------------------------------
    print("\n--- 1. ESQUEMA DE CAMPOS Y MUESTRAS ORIGINALES ---")
    schema_info = {}
    for sample_name in ["sample_nasdaq.csv", "sample_all_external.csv"]:
        sample_path = os.path.join(DATA_DIR, sample_name)
        if os.path.exists(sample_path):
            df_s = pd.read_csv(sample_path, nrows=500)
            null_pct = (df_s.isnull().mean() * 100).to_dict()
            schema_info[sample_name] = {
                "columns": df_s.columns.tolist(),
                "shape_sample": df_s.shape,
                "null_pct": {k: round(v, 2) for k, v in null_pct.items()}
            }
            print(f"\nArchivo: {sample_name} (Columnas: {len(df_s.columns)})")
            print(f"Columnas: {df_s.columns.tolist()}")
            print("Porcentaje de nulos en muestra de 500 filas:")
            for col, pct in schema_info[sample_name]["null_pct"].items():
                print(f"  - {col:20s}: {pct:6.2f}% nulos")

    # ---------------------------------------------------------
    # 2. Análisis del Volcado Real de Noticias en data/windows/*.bin
    # ---------------------------------------------------------
    print("\n--- 2. PROCESAMIENTO DEL VOLCADO REAL DE NOTICIAS (data/windows/*.bin) ---")
    bin_files = sorted(glob.glob(os.path.join(WINDOWS_DIR, "*.bin")))
    print(f"Archivos binarios locales encontrados: {len(bin_files)}")

    raw_records = []
    article_lens = []
    headline_lens = []
    summary_counts = {"lsa": 0, "luhn": 0, "textrank": 0, "lexrank": 0}

    for fpath in bin_files:
        sym_file = os.path.basename(fpath).replace(".bin", "")
        with open(fpath, "rb") as f:
            raw = f.read()
        raw = raw[:raw.rfind(b"\n")]
        reader = csv.reader(io.StringIO(raw.decode("utf-8", "replace"), newline=""))
        
        for r in reader:
            if len(r) >= 4:
                url = r[0].strip() if len(r) > 0 else ""
                date_str = r[1].replace(" UTC", "").strip()[:19] if len(r) > 1 else ""
                title = r[2].strip() if len(r) > 2 else ""
                ticker = r[3].strip() if len(r) > 3 else ""
                publisher = r[4].strip() if len(r) > 4 else ""
                author = r[5].strip() if len(r) > 5 else ""
                article = r[6].strip() if len(r) > 6 else ""
                lsa = r[7].strip() if len(r) > 7 else ""
                luhn = r[8].strip() if len(r) > 8 else ""
                trank = r[9].strip() if len(r) > 9 else ""
                lrank = r[10].strip() if len(r) > 10 else ""

                if not ticker or not title or len(date_str) < 10:
                    continue

                if lsa: summary_counts["lsa"] += 1
                if luhn: summary_counts["luhn"] += 1
                if trank: summary_counts["textrank"] += 1
                if lrank: summary_counts["lexrank"] += 1

                headline_lens.append(len(title))
                if article:
                    article_lens.append(len(article))

                raw_records.append({
                    "ticker": ticker,
                    "date": date_str,
                    "headline": title,
                    "publisher": publisher,
                    "has_article": bool(article),
                    "article_len": len(article)
                })

    print(f"Total de noticias crudas parseadas de los volcados: {len(raw_records):,}")
    df_raw = pd.DataFrame(raw_records)
    df_raw["dt"] = pd.to_datetime(df_raw["date"], errors="coerce")
    df_raw = df_raw.dropna(subset=["dt"])

    if not df_raw.empty:
        print(f"Rango temporal en volcados locales: {df_raw['dt'].min().strftime('%Y-%m-%d')} a {df_raw['dt'].max().strftime('%Y-%m-%d')}")
        print("\nEstadísticas de longitud de texto:")
        print(f"  - Longitud media de Titulares: {np.mean(headline_lens):.1f} caracteres (Mediana: {np.median(headline_lens):.0f})")
        if article_lens:
            print(f"  - Longitud media de Artículos completos: {np.mean(article_lens):.1f} caracteres (Mediana: {np.median(article_lens):.0f}, Máx: {np.max(article_lens):,})")
        print("\nPresencia de resúmenes extractivos:")
        for sm_name, cnt in summary_counts.items():
            pct = (cnt / len(raw_records)) * 100 if raw_records else 0
            print(f"  - Resumen {sm_name.upper():8s}: {cnt:,} noticias ({pct:.1f}%)")

    # ---------------------------------------------------------
    # 3. Censo y Desglose por Compañía (Fechas d0 a d1, Conteos y Perfiles)
    # ---------------------------------------------------------
    print("\n--- 3. DESGLOSE INTEGRAL DE COMPAÑÍAS (FECHAS Y VOLUMEN) ---")
    
    # Combinamos el censo oficial de las 202 empresas con los conteos reales
    company_stats = []
    
    if os.path.exists(CENSUS_FILE):
        df_census = pd.read_csv(CENSUS_FILE, sep=";")
        print(f"Censo global S&P 500 cargado: {len(df_census)} empresas.")
        
        # Agrupación local de data/windows
        local_grp = df_raw.groupby("ticker").agg(
            local_count=("headline", "count"),
            local_min_date=("dt", "min"),
            local_max_date=("dt", "max")
        ).reset_index()
        
        merged_companies = pd.merge(df_census, local_grp, left_on="sym", right_on="ticker", how="left")
        
        for _, row in merged_companies.iterrows():
            sym = row["sym"]
            sec_name = row.get("sec_name", "")
            sector = row.get("sector", "")
            n_news_census = row.get("n_news", 0)
            d0_census = str(row.get("d0_news", ""))[:10]
            d1_census = str(row.get("d1_news", ""))[:10]
            perfil = row.get("perfil_temporal", "No clasificado")
            
            # Si tenemos datos locales detallados, verificamos
            loc_cnt = row.get("local_count", 0)
            loc_d0 = row.get("local_min_date")
            loc_d1 = row.get("local_max_date")
            
            # Usar fecha más precisa disponible
            if pd.notna(loc_d0) and loc_cnt > 10:
                final_d0 = loc_d0.strftime("%Y-%m-%d")
                final_d1 = loc_d1.strftime("%Y-%m-%d")
                final_cnt = int(loc_cnt)
            else:
                final_d0 = d0_census if d0_census and d0_census != "nan" else "Sin fecha"
                final_d1 = d1_census if d1_census and d1_census != "nan" else "Sin fecha"
                final_cnt = int(n_news_census) if pd.notna(n_news_census) else 0

            days_span = 0
            if final_d0 != "Sin fecha" and final_d1 != "Sin fecha":
                try:
                    dt0 = datetime.strptime(final_d0, "%Y-%m-%d")
                    dt1 = datetime.strptime(final_d1, "%Y-%m-%d")
                    days_span = (dt1 - dt0).days
                except:
                    pass

            company_stats.append({
                "ticker": sym,
                "company_name": sec_name,
                "sector": sector,
                "d0_news": final_d0,
                "d1_news": final_d1,
                "days_span": days_span,
                "years_span": round(days_span / 365.25, 1),
                "news_count": final_cnt,
                "temporal_profile": perfil
            })

    df_companies = pd.DataFrame(company_stats)
    df_companies.sort_values(by="news_count", ascending=False, inplace=True)
    df_companies.to_csv(OUT_COMPANIES_CSV, index=False, encoding="utf-8-sig")
    print(f"\nDesglose guardado en: {OUT_COMPANIES_CSV} ({len(df_companies)} compañías)")

    # ---------------------------------------------------------
    # 4. Estadísticas del Universo de Compañías
    # ---------------------------------------------------------
    total_companies = len(df_companies)
    with_news = df_companies[df_companies["news_count"] > 0]
    total_news_all = df_companies["news_count"].sum()

    print(f"\nTotal compañías censadas en FNSPID: {total_companies}")
    print(f"Compañías con al menos 1 noticia: {len(with_news)} ({len(with_news)/total_companies*100:.1f}%)")
    print(f"Total estimado de noticias acumuladas en universo S&P 500: {total_news_all:,}")
    print(f"Media de noticias por compañía: {df_companies['news_count'].mean():.1f}")
    print(f"Mediana de noticias por compañía: {df_companies['news_count'].median():.1f}")
    print(f"Desviación estándar: {df_companies['news_count'].std():.1f}")
    print(f"Mínimo: {df_companies['news_count'].min()} | Máximo: {df_companies['news_count'].max():,}")

    print("\n--- DISTRIBUCIÓN POR PERFIL TEMPORAL DE NOTICIAS ---")
    perfil_counts = df_companies["temporal_profile"].value_counts()
    for perfil, cnt in perfil_counts.items():
        print(f"  - {perfil:50s}: {cnt:3d} empresas ({cnt/total_companies*100:5.1f}%)")

    print("\n--- TOP 20 COMPAÑÍAS CON MÁS NOTICIAS EN FNSPID ---")
    print(f"{'Ticker':<7} {'Nombre':<32} {'Sector':<24} {'Desde':<12} {'Hasta':<12} {'Años':<6} {'Noticias':>8}")
    print("-" * 105)
    for _, r in df_companies.head(20).iterrows():
        print(f"{r['ticker']:<7} {str(r['company_name'])[:30]:<32} {str(r['sector'])[:22]:<24} {str(r['d0_news']):<12} {str(r['d1_news']):<12} {r['years_span']:<6.1f} {r['news_count']:>8,}")

    print("\n--- DISTRIBUCIÓN POR SECTOR GICS ---")
    sector_summary = df_companies.groupby("sector").agg(
        empresas=("ticker", "count"),
        total_noticias=("news_count", "sum"),
        media_noticias=("news_count", "mean")
    ).reset_index().sort_values(by="total_noticias", ascending=False)
    for _, r in sector_summary.iterrows():
        print(f"  - {r['sector']:<26}: {r['empresas']:2d} empresas | {r['total_noticias']:>8,} noticias (media: {r['media_noticias']:.0f}/empresa)")

    # ---------------------------------------------------------
    # 5. Generar Resumen JSON
    # ---------------------------------------------------------
    summary_data = {
        "dataset_name": "FNSPID (Financial News and Stock Price Integration Dataset)",
        "source": "Zihan1004/FNSPID (Hugging Face) / NASDAQ Articles",
        "total_sp500_companies": total_companies,
        "companies_with_news": int(len(with_news)),
        "total_sp500_news": int(total_news_all),
        "mean_news_per_company": float(round(df_companies['news_count'].mean(), 1)),
        "median_news_per_company": float(df_companies['news_count'].median()),
        "max_news_company": {
            "ticker": df_companies.iloc[0]["ticker"],
            "name": df_companies.iloc[0]["company_name"],
            "news_count": int(df_companies.iloc[0]["news_count"]),
            "d0": df_companies.iloc[0]["d0_news"],
            "d1": df_companies.iloc[0]["d1_news"]
        },
        "profiles": {k: int(v) for k, v in perfil_counts.items()},
        "sectors": sector_summary.to_dict(orient="records")
    }

    with open(OUT_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    print(f"\nResumen JSON guardado en: {OUT_SUMMARY_JSON}")
    print("=" * 80)
    print("           ANÁLISIS DE FNSPID COMPLETADO CON ÉXITO")
    print("=" * 80)


if __name__ == "__main__":
    analyze_fnspid()
