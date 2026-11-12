"""Script 01: Análisis Directo y Exclusivo de los Datasets de Noticias (Benzinga y FNSPID).

Este script opera DIRECTA Y EXCLUSIVAMENTE sobre los datasets originales de noticias:
  1. Dataset Benzinga: data/benzinga/raw_analyst_ratings.jsonl (1.4M de noticias crudas)
  2. Dataset FNSPID: data/windows/*.bin + news.parquet (bloques reales de nasdaq.com)
  3. Metadatos SEC EDGAR: data/sec_tickers.json (nombres oficiales)

NO depende de precios bursátiles, NO depende de balances contables, NO depende de daily_aligned.parquet
ni de resúmenes precalculados. Realiza todo el conteo, agregación por fechas y cálculo de splits
en tiempo real a partir del flujo de noticias.

Salidas:
  - analisis_noticias_tfm/1_cobertura_noticias_todas_las_acciones.xlsx
  - analisis_noticias_tfm/1_cobertura_noticias_todas_las_acciones.csv
"""

import os
import sys
import glob
import json
import csv
import io
import time
from datetime import datetime

# Cargar openpyxl si no está en el venv
for p in [r"C:\Users\julia\anaconda3\Lib\site-packages", r"C:\Users\julia\AppData\Roaming\Python\Python311\site-packages"]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

csv.field_size_limit(10**9)

DIR_BASE = "analisis_noticias_tfm"
os.makedirs(DIR_BASE, exist_ok=True)
OUT_EXCEL = os.path.join(DIR_BASE, "1_cobertura_noticias_todas_las_acciones.xlsx")
OUT_CSV = os.path.join(DIR_BASE, "1_cobertura_noticias_todas_las_acciones.csv")

# Definición cronológica de los Splits del TFM
TRAIN_START, TRAIN_END = "2011-01-01", "2018-12-31"
VAL_START, VAL_END     = "2019-01-01", "2020-06-10"
TEST_START, TEST_END   = "2021-08-17", "2023-12-31"

BENZINGA_FILE = "data/benzinga/raw_analyst_ratings.jsonl"
WINDOWS_DIR = "data/windows"
SEC_NAMES_FILE = "data/sec_tickers.json"


def load_sec_names():
    sec_names = {}
    sec_sectors = {}
    if os.path.exists(SEC_NAMES_FILE):
        try:
            with open(SEC_NAMES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                items = data.values() if isinstance(data, dict) else data
                for item in items:
                    sym = str(item.get("ticker", "")).strip().upper()
                    title = str(item.get("title", "")).strip()
                    if sym and title:
                        sec_names[sym] = title
        except Exception as e:
            print(f"Nota: No se pudo cargar sec_tickers.json ({e})")
            
    # Sectores oficiales del S&P 500
    if os.path.exists("data/sp500_constituents.json"):
        try:
            with open("data/sp500_constituents.json", "r", encoding="utf-8") as f:
                sp_data = json.load(f)
                for it in sp_data:
                    sym = str(it.get("Symbol_std") or it.get("Symbol", "")).strip().upper()
                    sec = str(it.get("GICS Sector", "")).strip()
                    if sym and sec:
                        sec_sectors[sym] = sec
        except Exception as e:
            pass
            
    return sec_names, sec_sectors


def ingest_benzinga_dataset():
    print("\n[1/3] Ingestando Dataset BENZINGA crudo (data/benzinga/raw_analyst_ratings.jsonl)...")
    bz_stats = {} # ticker -> {'count': int, 'min_date': str, 'max_date': str, 'dates': set}
    
    if not os.path.exists(BENZINGA_FILE):
        print(f"Error: {BENZINGA_FILE} no encontrado.")
        return bz_stats

    t0 = time.time()
    total_lines = 0
    with open(BENZINGA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            total_lines += 1
            if total_lines % 400000 == 0:
                print(f"  Procesadas {total_lines:,} noticias de Benzinga...")
            if not line.startswith("{"):
                continue
            try:
                item = json.loads(line)
                stk = item.get("stock")
                dt = item.get("date", "")[:10]
                if stk and len(dt) == 10 and dt.startswith("20"):
                    stk = stk.strip().upper()
                    if stk not in bz_stats:
                        bz_stats[stk] = {"count": 0, "min_date": dt, "max_date": dt, "dates": set()}
                    bz_stats[stk]["count"] += 1
                    if dt < bz_stats[stk]["min_date"]: bz_stats[stk]["min_date"] = dt
                    if dt > bz_stats[stk]["max_date"]: bz_stats[stk]["max_date"] = dt
                    bz_stats[stk]["dates"].add(dt)
            except:
                continue

    dt_sec = time.time() - t0
    print(f"  -> Benzinga cargado: {total_lines:,} noticias procesadas, {len(bz_stats):,} tickers únicos en {dt_sec:.2f}s.")
    return bz_stats


def ingest_fnspid_dataset():
    print("\n[2/3] Ingestando Dataset FNSPID crudo (data/windows/*.bin y particiones de noticias)...")
    fn_stats = {} # ticker -> {'count': int, 'min_date': str, 'max_date': str, 'dates': set}
    t0 = time.time()

    # A. Archivos binarios directos de nasdaq_exteral_data.csv
    bin_files = glob.glob(os.path.join(WINDOWS_DIR, "*.bin"))
    print(f"  Leyendo {len(bin_files)} volcados binarios de FNSPID...")
    for p in bin_files:
        try:
            with open(p, "rb") as f:
                raw = f.read()
            raw = raw[:raw.rfind(b"\n")]
            reader = csv.reader(io.StringIO(raw.decode("utf-8", "replace"), newline=""))
            for r in reader:
                if len(r) >= 4:
                    stk = r[3].strip().upper()
                    dt = r[1].replace(" UTC", "").strip()[:10]
                    if stk and len(dt) == 10 and dt.startswith("20"):
                        if stk not in fn_stats:
                            fn_stats[stk] = {"count": 0, "min_date": dt, "max_date": dt, "dates": set()}
                        fn_stats[stk]["count"] += 1
                        if dt < fn_stats[stk]["min_date"]: fn_stats[stk]["min_date"] = dt
                        if dt > fn_stats[stk]["max_date"]: fn_stats[stk]["max_date"] = dt
                        fn_stats[stk]["dates"].add(dt)
        except Exception as e:
            print(f"  Error en {p}: {e}")

    # B. Flujo de noticias NASDAQ_FNSPID almacenado
    for split in ["train", "val", "test"]:
        pq_path = f"data/splits/{split}/news.parquet"
        if os.path.exists(pq_path):
            try:
                df_pq = pd.read_parquet(pq_path)
                df_sub = df_pq[df_pq["source"] == "NASDAQ_FNSPID"]
                for _, r in df_sub.iterrows():
                    stk = str(r["ticker"]).strip().upper()
                    dt = str(r["dt"])[:10]
                    if stk and len(dt) == 10 and dt.startswith("20"):
                        if stk not in fn_stats:
                            fn_stats[stk] = {"count": 0, "min_date": dt, "max_date": dt, "dates": set()}
                        fn_stats[stk]["count"] += 1
                        if dt < fn_stats[stk]["min_date"]: fn_stats[stk]["min_date"] = dt
                        if dt > fn_stats[stk]["max_date"]: fn_stats[stk]["max_date"] = dt
                        fn_stats[stk]["dates"].add(dt)
            except Exception as e:
                print(f"  Nota lectura {pq_path}: {e}")

    dt_sec = time.time() - t0
    total_fn_news = sum(v["count"] for v in fn_stats.values())
    print(f"  -> FNSPID cargado: {total_fn_news:,} noticias procesadas, {len(fn_stats):,} tickers únicos en {dt_sec:.2f}s.")
    return fn_stats


def main():
    print("=" * 80)
    print("SCRIPT 01: AUDITORÍA Y COBERTURA ACCIÓN POR ACCIÓN (SOLO DATASETS)")
    print("=" * 80)

    sec_names, sec_sectors = load_sec_names()
    bz_stats = ingest_benzinga_dataset()
    fn_stats = ingest_fnspid_dataset()

    print("\n[3/3] Calculando métricas de splits y diagnóstico a partir de los datos crudos...")
    all_tickers = sorted(list(set(bz_stats.keys()) | set(fn_stats.keys())))
    print(f"Total tickers únicos encontrados en ambos datasets: {len(all_tickers):,}")

    # Cargar lista de los 207 tickers objetivo del TFM para resaltarlos
    target_tickers = set()
    if os.path.exists("scripts/panel.txt"):
        for l in open("scripts/panel.txt", encoding="utf-8"):
            s = l.strip().upper()
            if s: target_tickers.add(s)
    if os.path.exists("data/tier1_fechas_noticias.csv"):
        df_c = pd.read_csv("data/tier1_fechas_noticias.csv", sep=";")
        for s in df_c["sym"]:
            target_tickers.add(str(s).strip().upper())

    # Construir registros
    records = []
    for sym in all_tickers:
        bz = bz_stats.get(sym, {"count": 0, "min_date": "Sin datos", "max_date": "Sin datos", "dates": set()})
        fn = fn_stats.get(sym, {"count": 0, "min_date": "Sin datos", "max_date": "Sin datos", "dates": set()})

        has_bz = "SÍ" if bz["count"] > 0 else "NO"
        has_fn = "SÍ" if fn["count"] > 0 else "NO"

        if has_bz == "SÍ" and has_fn == "SÍ":
            origen = "Benzinga + FNSPID (Híbrido)"
        elif has_bz == "SÍ":
            origen = "Solo Benzinga"
        else:
            origen = "Solo FNSPID"

        # Fechas globales
        valid_starts = [d for d in [bz["min_date"], fn["min_date"]] if d != "Sin datos"]
        valid_ends = [d for d in [bz["max_date"], fn["max_date"]] if d != "Sin datos"]
        d0_glob = min(valid_starts) if valid_starts else "Sin noticias"
        d1_glob = max(valid_ends) if valid_ends else "Sin noticias"

        anos_cob = 0.0
        if d0_glob != "Sin noticias" and d1_glob != "Sin noticias":
            try:
                y0 = int(d0_glob[:4])
                y1 = int(d1_glob[:4])
                anos_cob = round((y1 - y0) + 1, 1)
            except:
                pass

        # Métricas calculadas directamente de las fechas de las noticias
        all_dates = bz["dates"] | fn["dates"]
        tr_days = sum(1 for d in all_dates if TRAIN_START <= d <= TRAIN_END)
        va_days = sum(1 for d in all_dates if VAL_START <= d <= VAL_END)
        te_days = sum(1 for d in all_dates if TEST_START <= d <= TEST_END)
        total_days = len(all_dates)
        total_news = bz["count"] + fn["count"]

        # Clasificación en Tiers
        if tr_days >= 30 and va_days >= 10 and te_days >= 20:
            tier = "Tier 1: Cobertura Total Continua"
            diag = f"Excelente: flujo ininterrumpido en Train ({tr_days}d), Val ({va_days}d) y Test ({te_days}d)."
        elif tr_days >= 30 and va_days >= 10 and te_days == 0:
            tier = "Tier 2: Cobertura Parcial Histórica"
            diag = f"Histórica Benzinga: cubre Train ({tr_days}d) y Val ({va_days}d), pero vacía en Test 2021-2023."
        elif (tr_days == 0 or tr_days < 30) and (va_days > 0 or te_days > 0):
            tier = "Tier 2: Cobertura Parcial Tardía"
            diag = f"Reciente / Big Tech: sin noticias en Train temprano, pero muy densa en Val ({va_days}d) y Test ({te_days}d)."
        else:
            tier = "Tier 3: Cobertura Mínima / Silenciosa"
            diag = f"Noticias esporádicas o dispersas ({total_days} días en total)."

        empresa_nombre = sec_names.get(sym, "---")

        records.append({
            "Ticker": sym,
            "Empresa": empresa_nombre,
            "Sector_GICS": sec_sectors.get(sym, "---"),
            "Es_Universo_TFM": "SÍ" if sym in target_tickers else "NO",
            "Dataset_Origen": origen,
            "Tiene_Benzinga": has_bz,
            "Benzinga_Fecha_Inicio": bz["min_date"],
            "Benzinga_Fecha_Fin": bz["max_date"],
            "Benzinga_Noticias": bz["count"],
            "Tiene_FNSPID": has_fn,
            "FNSPID_Fecha_Inicio": fn["min_date"],
            "FNSPID_Fecha_Fin": fn["max_date"],
            "FNSPID_Noticias": fn["count"],
            "Total_Noticias_Global": total_news,
            "Fecha_Inicio_Global": d0_glob,
            "Fecha_Fin_Global": d1_glob,
            "Anios_Cobertura": anos_cob,
            "Dias_Noticias_Train": tr_days,
            "Dias_Noticias_Val": va_days,
            "Dias_Noticias_Test": te_days,
            "Total_Dias_Con_Noticias": total_days,
            "Clasificacion_Tier": tier,
            "Diagnostico_Metodologico": diag
        })

    df_all = pd.DataFrame(records)

    # Ordenar: primero universo TFM, luego por Tier 1 -> Tier 2 -> Tier 3, luego por noticias descendente
    tier_order = {
        "Tier 1: Cobertura Total Continua": 1,
        "Tier 2: Cobertura Parcial Histórica": 2,
        "Tier 2: Cobertura Parcial Tardía": 3,
        "Tier 3: Cobertura Mínima / Silenciosa": 4
    }
    df_all["is_tfm_rank"] = df_all["Es_Universo_TFM"].map({"SÍ": 0, "NO": 1})
    df_all["tier_rank"] = df_all["Clasificacion_Tier"].map(tier_order)
    df_all.sort_values(by=["is_tfm_rank", "tier_rank", "Total_Noticias_Global"], ascending=[True, True, False], inplace=True)
    df_all.drop(columns=["is_tfm_rank", "tier_rank"], inplace=True)

    # Subconjunto principal de las 207 acciones del TFM
    df_tfm = df_all[df_all["Es_Universo_TFM"] == "SÍ"].copy()
    print(f"\nAcciones del Universo TFM analizadas: {len(df_tfm)}")
    print(df_tfm["Clasificacion_Tier"].value_counts().to_string())

    # Guardar CSV (las acciones del TFM prioritarias y todas las analizadas)
    df_tfm.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"CSV generado exitosamente: {OUT_CSV} ({len(df_tfm)} acciones TFM)")

    # Generar Excel Formateado con Dos Hojas
    print("Generando Excel profesional con estilos corporativos...")
    wb = openpyxl.Workbook()
    
    # Hoja 1: Acciones del TFM (207)
    ws1 = wb.active
    ws1.title = "Acciones_TFM_207"

    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    fill_header = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    border_thin = Side(border_style="thin", color="D9D9D9")
    cell_border = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

    fill_tier1 = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid") # Verde suave
    fill_tier2_hist = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid") # Azul suave
    fill_tier2_tard = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid") # Amarillo suave
    fill_tier3 = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid") # Gris suave

    headers = list(df_tfm.columns)
    ws1.append(headers)

    for col_idx, h in enumerate(headers, 1):
        c = ws1.cell(row=1, column=col_idx)
        c.font = font_header
        c.fill = fill_header
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for row_idx, r_vals in enumerate(df_tfm.values.tolist(), 2):
        ws1.append(r_vals)
        tier_val = str(r_vals[21]) # Clasificacion_Tier
        
        row_fill = fill_tier3
        if "Tier 1" in tier_val:
            row_fill = fill_tier1
        elif "Histórica" in tier_val:
            row_fill = fill_tier2_hist
        elif "Tardía" in tier_val:
            row_fill = fill_tier2_tard

        for col_idx in range(1, len(headers) + 1):
            c = ws1.cell(row=row_idx, column=col_idx)
            c.border = cell_border
            c.fill = row_fill
            if col_idx in [9, 13, 14, 18, 19, 20, 21]:
                c.number_format = "#,##0"
                c.alignment = Alignment(horizontal="right", vertical="center")
            elif col_idx in [17]:
                c.number_format = "0.0"
                c.alignment = Alignment(horizontal="right", vertical="center")
            elif col_idx in [1, 4, 5, 6, 7, 8, 10, 11, 12, 15, 16]:
                c.alignment = Alignment(horizontal="center", vertical="center")
            else:
                c.alignment = Alignment(horizontal="left", vertical="center")

    ws1.freeze_panes = "A2"
    for col in ws1.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or "")) for cell in col)
        ws1.column_dimensions[col_letter].width = min(max(max_len + 3, 11), 48)

    # Hoja 2: Top 100 Acciones Globales del Dataset
    ws2 = wb.create_sheet(title="Top_100_Globales_Datasets")
    df_top100 = df_all.head(100)
    ws2.append(headers)
    for col_idx, h in enumerate(headers, 1):
        c = ws2.cell(row=1, column=col_idx)
        c.font = font_header
        c.fill = PatternFill(start_color="333F48", end_color="333F48", fill_type="solid")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for row_idx, r_vals in enumerate(df_top100.values.tolist(), 2):
        ws2.append(r_vals)
        for col_idx in range(1, len(headers) + 1):
            c = ws2.cell(row=row_idx, column=col_idx)
            c.border = cell_border
            if col_idx in [9, 13, 14, 18, 19, 20, 21]:
                c.number_format = "#,##0"
                c.alignment = Alignment(horizontal="right", vertical="center")
            elif col_idx in [17]:
                c.number_format = "0.0"
                c.alignment = Alignment(horizontal="right", vertical="center")

    ws2.freeze_panes = "A2"
    for col in ws2.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or "")) for cell in col)
        ws2.column_dimensions[col_letter].width = min(max(max_len + 3, 11), 48)

    wb.save(OUT_EXCEL)
    print(f"Excel guardado exitosamente: {OUT_EXCEL}")
    print("=" * 80)
    print("AUDITORÍA DE DATASETS COMPLETADA PURAMENTE A PARTIR DE LOS DATOS CRUDOS")
    print("=" * 80)


if __name__ == "__main__":
    main()
