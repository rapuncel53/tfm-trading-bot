"""02_filtrar_matriz_sp500.py
=============================================================================
Paso 2 del Pipeline de Selección de Noticias:
Toma la matriz completa (8.552 tickers) y filtra únicamente las 503 empresas
oficiales que componen el índice S&P 500.

Enriquece los datos con:
  - Nombre oficial de la empresa (Security)
  - Clasificación de Sector GICS oficial

Genera:
  matriz_noticias_sp500.xlsx
    - Hoja 1: 'S&P 500 (Por Volumen)' (ordenado por volumen total descendente)
    - Hoja 2: 'S&P 500 (Por Sector)' (agrupado por sector y volumen)
    - Hoja 3: 'S&P 500 (Alfabético A-Z)' (ordenado de la A a la Z por ticker)
    - Hoja 4: 'Resumen por Sector GICS' (conteo consolidado por sector)
=============================================================================
"""

import os
import sys
import json
import pandas as pd
import numpy as np

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

IN_EXCEL = os.path.join(SCRIPT_DIR, "matriz_noticias_tickers_anos.xlsx")
OUT_EXCEL = os.path.join(SCRIPT_DIR, "matriz_noticias_sp500.xlsx")
SP500_JSON = os.path.join(BASE_DIR, "data", "sp500_constituents.json")

def load_sp500_metadata():
    if not os.path.exists(SP500_JSON):
        raise FileNotFoundError(f"No se encontró el archivo de constituyentes del S&P 500 en {SP500_JSON}")
    with open(SP500_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df_sp = pd.DataFrame(data)
    # Estandarizar columnas
    sym_col = 'Symbol_std' if 'Symbol_std' in df_sp.columns else 'Symbol'
    df_sp['Ticker'] = df_sp[sym_col].astype(str).str.strip().str.upper()
    df_sp['Empresa'] = df_sp['Security'].astype(str).str.strip()
    df_sp['Sector GICS'] = df_sp['GICS Sector'].astype(str).str.strip()
    return df_sp[['Ticker', 'Empresa', 'Sector GICS']].drop_duplicates(subset=['Ticker'])

def main():
    print(f"[Paso 2] Cargando matriz completa de noticias desde: {IN_EXCEL}")
    if not os.path.exists(IN_EXCEL):
        raise FileNotFoundError(f"No se encontró {IN_EXCEL}. Ejecuta primero el Paso 1.")

    df_full = pd.read_excel(IN_EXCEL, sheet_name=0)
    df_full['Ticker'] = df_full['Ticker'].astype(str).str.strip().str.upper()

    print(f"[Paso 2] Cargando constituyentes del S&P 500 ({SP500_JSON})...")
    df_meta = load_sp500_metadata()
    print(f"         Total constituyentes S&P 500 cargados: {len(df_meta)}")

    # Unir datos
    df_merged = pd.merge(df_meta, df_full, on='Ticker', how='left')

    year_cols = [str(y) for y in range(2009, 2025)]
    # Renombrar columnas si vienen como enteros
    rename_dict = {col: str(col) for col in df_merged.columns if str(col).isdigit()}
    df_merged = df_merged.rename(columns=rename_dict)

    for y in year_cols:
        if y not in df_merged.columns:
            df_merged[y] = 0
        else:
            df_merged[y] = pd.to_numeric(df_merged[y], errors='coerce').fillna(0).astype(int)

    df_merged['Total Noticias'] = df_merged[year_cols].sum(axis=1)

    display_cols = ['Ticker', 'Empresa', 'Sector GICS'] + year_cols + ['Total Noticias']
    df_base = df_merged[display_cols].copy()

    # Preparar las hojas ordenadas
    df_vol = df_base.sort_values(by='Total Noticias', ascending=False).reset_index(drop=True)
    df_sec = df_base.sort_values(by=['Sector GICS', 'Total Noticias'], ascending=[True, False]).reset_index(drop=True)
    df_az = df_base.sort_values(by='Ticker', ascending=True).reset_index(drop=True)

    # Resumen por Sector GICS
    df_res_sec = df_base.groupby('Sector GICS')[year_cols + ['Total Noticias']].sum().reset_index()
    df_res_sec = df_res_sec.sort_values(by='Total Noticias', ascending=False).reset_index(drop=True)

    # Exportar con OpenPyXL
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    _format_and_save_sheet(wb, df_vol, 'S&P 500 (Por Volumen)', freeze='D2')
    _format_and_save_sheet(wb, df_sec, 'S&P 500 (Por Sector)', freeze='D2')
    _format_and_save_sheet(wb, df_az, 'S&P 500 (Alfabético A-Z)', freeze='D2')
    _format_and_save_sheet(wb, df_res_sec, 'Resumen por Sector GICS', freeze='B2')

    wb.save(OUT_EXCEL)
    print(f"[Paso 2] Matriz S&P 500 generada exitosamente en: {OUT_EXCEL}")
    print(f"         Empresas procesadas: {len(df_base)}")
    print(f"         Noticias totales identificadas: {df_base['Total Noticias'].sum():,}")

def _format_and_save_sheet(wb, df, title, freeze='B2'):
    ws = wb.create_sheet(title=title)
    ws.views.sheetView[0].showGridLines = True
    ws.freeze_panes = freeze

    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    fill_navy = PatternFill(start_color="1A237E", end_color="1A237E", fill_type="solid")
    fill_sec = PatternFill(start_color="283593", end_color="283593", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin', color='E0E0E0'), right=Side(style='thin', color='E0E0E0'),
        top=Side(style='thin', color='E0E0E0'), bottom=Side(style='thin', color='E0E0E0')
    )

    cols = df.columns.tolist()
    for col_idx, col_name in enumerate(cols, 1):
        cell = ws.cell(row=1, column=col_idx, value=str(col_name))
        cell.font = font_header
        cell.fill = fill_sec if col_name == 'Total Noticias' else fill_navy
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border
    ws.row_dimensions[1].height = 25

    for row_idx, row in df.iterrows():
        r_num = row_idx + 2
        for col_idx, col_name in enumerate(cols, 1):
            val = row[col_name]
            cell = ws.cell(row=r_num, column=col_idx, value=val)
            cell.border = thin_border

            if col_name == 'Ticker':
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.font = Font(name="Calibri", size=11, bold=True)
            elif col_name in ['Empresa', 'Sector GICS']:
                cell.alignment = Alignment(horizontal='left', vertical='center')
            else:
                cell.alignment = Alignment(horizontal='right', vertical='center')
                cell.number_format = '#,##0'
                if col_name == 'Total Noticias':
                    cell.font = Font(name="Calibri", size=11, bold=True)
        ws.row_dimensions[r_num].height = 19

    for col_idx in range(1, len(cols) + 1):
        col_letter = get_column_letter(col_idx)
        cname = cols[col_idx - 1]
        if cname == 'Ticker':
            ws.column_dimensions[col_letter].width = 10
        elif cname == 'Empresa':
            ws.column_dimensions[col_letter].width = 30
        elif cname == 'Sector GICS':
            ws.column_dimensions[col_letter].width = 24
        elif cname == 'Total Noticias':
            ws.column_dimensions[col_letter].width = 16
        else:
            ws.column_dimensions[col_letter].width = 10

if __name__ == "__main__":
    main()
