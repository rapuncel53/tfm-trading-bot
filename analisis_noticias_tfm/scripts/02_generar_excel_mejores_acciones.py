"""Script 02: Selección de las Mejores Acciones para el Nuevo Entrenamiento del TFM.

A partir del Documento Maestro (1_cobertura_noticias_todas_las_acciones.csv), este script:
  1. Filtra estrictamente las acciones con cobertura continua ininterrumpida en los 3 splits:
     - Train (2011-2018)
     - Validación (2019-2020)
     - Test Ciego (2021-2023)
  2. Calcula métricas de volumen, densidad temporal y adherencia al split ideal 70 / 10 / 20.
  3. Establece un ranking multidimensional de idoneidad.
  4. Segmenta entre el 'Núcleo de Élite 70/10/20' y el 'Universo Extendido Tier 1'.
  5. Genera el documento final en Excel (con formato visual ejecutivo) y CSV.

Salidas:
  - analisis_noticias_tfm/2_mejores_acciones_seleccionadas_entrenamiento.xlsx
  - analisis_noticias_tfm/2_mejores_acciones_seleccionadas_entrenamiento.csv
"""

import os
import sys

# Permitir cargar openpyxl
for p in [r"C:\Users\julia\anaconda3\Lib\site-packages", r"C:\Users\julia\AppData\Roaming\Python\Python311\site-packages"]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

DIR_BASE = "analisis_noticias_tfm"
IN_CSV = os.path.join(DIR_BASE, "1_cobertura_noticias_todas_las_acciones.csv")
OUT_EXCEL = os.path.join(DIR_BASE, "2_mejores_acciones_seleccionadas_entrenamiento.xlsx")
OUT_CSV = os.path.join(DIR_BASE, "2_mejores_acciones_seleccionadas_entrenamiento.csv")


def main():
    print("=" * 80)
    print("SCRIPT 02: GENERANDO DOCUMENTO DE LAS MEJORES ACCIONES PARA ENTRENAMIENTO")
    print("=" * 80)

    if not os.path.exists(IN_CSV):
        print(f"Error: {IN_CSV} no encontrado. Ejecuta primero el Script 01.")
        return

    print(f"Leyendo documento base: {IN_CSV}...")
    df_all = pd.read_csv(IN_CSV)

    # 1. Filtrar solo compañías Tier 1 con presencia obligatoria en Train, Val y Test
    df_t1 = df_all[
        (df_all["Clasificacion_Tier"].str.contains("Tier 1", na=False)) &
        (df_all["Dias_Noticias_Train"] > 0) &
        (df_all["Dias_Noticias_Val"] > 0) &
        (df_all["Dias_Noticias_Test"] > 0)
    ].copy()

    print(f"Compañías continuas identificadas en los 3 splits: {len(df_t1)}")

    # 2. Calcular porcentajes y ajuste al patrón ideal 70 / 10 / 20
    elite_records = []

    for _, row in df_t1.iterrows():
        t = row["Ticker"]
        emp = row["Empresa"]
        sec = row["Sector_GICS"]
        tot_news = int(row["Total_Noticias_Global"])
        
        tr_d = int(row["Dias_Noticias_Train"])
        va_d = int(row["Dias_Noticias_Val"])
        te_d = int(row["Dias_Noticias_Test"])
        tot_d = tr_d + va_d + te_d

        pct_tr = round((tr_d / tot_d) * 100, 1) if tot_d > 0 else 0.0
        pct_va = round((va_d / tot_d) * 100, 1) if tot_d > 0 else 0.0
        pct_te = round((te_d / tot_d) * 100, 1) if tot_d > 0 else 0.0

        # Desviación respecto al objetivo 70 / 10 / 20
        # Penaliza si Train < 50% o Test < 15%
        dev = abs(pct_tr - 70.0) + abs(pct_va - 10.0) + abs(pct_te - 20.0)
        
        # Puntuación de idoneidad (0 a 100) combinando volumen y equilibrio
        # Factor volumen logarítmico + factor ajuste
        vol_score = min(50.0, np.log10(max(10, tot_news)) * 12.5)
        balance_score = max(0.0, 50.0 - (dev * 0.7))
        total_score = round(vol_score + balance_score, 1)

        # Clasificación en Núcleo de Élite vs Universo Extendido
        if pct_tr >= 58.0 and pct_te >= 18.0 and tot_d >= 1000:
            grupo = "Núcleo de Élite (Óptimo 70/10/20)"
            rol = "Acción prioritaria: máxima representatividad y flujo equilibrado para calibrar el LLM sin sesgo temporal."
        elif tr_d >= 100 and tot_news >= 3000:
            grupo = "Universo Extendido Tier 1"
            rol = "Acción complementaria de alta liquidez: enriquece la muestra cross-sectional y diversifica sectores."
        else:
            grupo = "Tier 1 Específico"
            rol = "Acción con flujo moderado: apta para evaluación de robustez sectorial."

        elite_records.append({
            "Ticker": t,
            "Empresa": emp,
            "Sector_GICS": sec,
            "Grupo_Entrenamiento": grupo,
            "Score_Idoneidad_100": total_score,
            "Total_Noticias_Global": tot_news,
            "Total_Dias_Noticias": tot_d,
            "Dias_Train_2011_2018": tr_d,
            "Pct_Train": pct_tr,
            "Dias_Val_2019_2020": va_d,
            "Pct_Val": pct_va,
            "Dias_Test_2021_2023": te_d,
            "Pct_Test": pct_te,
            "Desviacion_Obj_70_10_20": round(dev, 1),
            "Dataset_Train": "Benzinga (Alertas y Ratings en Pre-Market)",
            "Dataset_Val": "Benzinga + FNSPID (Híbrido Crash COVID)",
            "Dataset_Test": "FNSPID NASDAQ (Artículos Completos y Resúmenes)",
            "Fecha_Inicio_Global": row["Fecha_Inicio_Global"],
            "Fecha_Fin_Global": row["Fecha_Fin_Global"],
            "Anios_Cobertura": row["Anios_Cobertura"],
            "Rol_Metodologico_Entrenamiento": rol
        })

    df_elite = pd.DataFrame(elite_records)

    # Ordenar por Score de Idoneidad y Total de Noticias
    df_elite.sort_values(by=["Score_Idoneidad_100", "Total_Dias_Noticias"], ascending=[False, False], inplace=True)
    df_elite.reset_index(drop=True, inplace=True)
    df_elite.insert(0, "Ranking_Seleccion", range(1, len(df_elite) + 1))

    # Guardar CSV
    df_elite.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"CSV de Mejores Acciones generado: {OUT_CSV} ({len(df_elite)} acciones seleccionadas)")

    # 3. Generar Excel de Alta Gama con Formato Condicional y Estilos
    print("Generando archivo Excel estilizado...")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mejores_Acciones_Entrenamiento"

    font_title = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    fill_header = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid") # Navy Blue oscuro
    fill_elite = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid") # Verde esmeralda suave
    fill_extended = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid") # Azul profesional suave
    fill_specific = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid") # Ámbar suave

    border_thin = Side(border_style="thin", color="CCCCCC")
    cell_border = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

    headers = list(df_elite.columns)
    ws.append(headers)

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = font_title
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for row_idx, r_vals in enumerate(df_elite.values.tolist(), 2):
        ws.append(r_vals)
        grupo_val = str(r_vals[4]) # Grupo_Entrenamiento
        
        row_fill = fill_extended
        if "Núcleo de Élite" in grupo_val:
            row_fill = fill_elite
        elif "Específico" in grupo_val:
            row_fill = fill_specific

        for col_idx in range(1, len(headers) + 1):
            c = ws.cell(row=row_idx, column=col_idx)
            c.border = cell_border
            c.fill = row_fill

            # Alineación y formato
            if col_idx in [1]: # Ranking
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.font = Font(name="Calibri", size=11, bold=True)
            elif col_idx in [2, 18, 19]: # Ticker, Fechas
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx in [5, 6, 7, 8, 10, 12]: # Conteos y Score
                c.alignment = Alignment(horizontal="right", vertical="center")
                if col_idx in [6, 7, 8, 10, 12]:
                    c.number_format = "#,##0"
                else:
                    c.number_format = "0.0"
            elif col_idx in [9, 11, 13, 14, 20]: # Porcentajes y Años
                c.alignment = Alignment(horizontal="right", vertical="center")
                c.number_format = "0.0"
            else:
                c.alignment = Alignment(horizontal="left", vertical="center")

    ws.freeze_panes = "A2"

    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 11), 45)

    wb.save(OUT_EXCEL)
    print(f"Excel guardado exitosamente: {OUT_EXCEL}")
    print("=" * 80)


if __name__ == "__main__":
    main()
