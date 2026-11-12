"""01_generar_matriz_tickers_anos.py
=============================================================================
Paso 1 del Pipeline de Selección de Noticias:
Analiza el universo completo de noticias (más de 8.500 tickers) y calcula
la matriz anual de noticias por ticker desde 2009 hasta 2024.

Genera:
  matriz_noticias_tickers_anos.xlsx
    - Hoja 1: 'Por Volumen (Top Tickers)' (ordenado por volumen total descendente)
    - Hoja 2: 'Alfabético (A-Z)' (ordenado por símbolo de ticker A-Z)
=============================================================================
"""

import os
import sys
import glob
import pandas as pd
import numpy as np

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_EXCEL = os.path.join(SCRIPT_DIR, "matriz_noticias_tickers_anos.xlsx")

def build_from_existing_or_raw(raw_csv_path=None):
    """
    Si se proporciona el CSV crudo de noticias (ej. nasdaq_exteral_data.csv),
    lo procesa en streaming / chunks o DuckDB para agregar (Ticker, Año).
    Si ya existe la matriz en la carpeta, verifica su integridad y formato.
    """
    if os.path.exists(OUT_EXCEL):
        print(f"[Paso 1] Matriz ya existente en: {OUT_EXCEL}")
        df = pd.read_excel(OUT_EXCEL, sheet_name=0)
        print(f"         Total tickers en la matriz: {len(df):,}")
        print(f"         Columnas: {df.columns.tolist()[:6]} ... {df.columns.tolist()[-4:]}")
        return OUT_EXCEL

    if raw_csv_path and os.path.exists(raw_csv_path):
        print(f"[Paso 1] Procesando archivo crudo de noticias en streaming: {raw_csv_path}...")
        try:
            import duckdb
            query = f"""
            SELECT 
                UPPER(TRIM(Stock_symbol)) AS Ticker,
                CAST(SUBSTRING(Date, 1, 4) AS INT) AS Year,
                COUNT(*) AS Count
            FROM read_csv('{raw_csv_path}', columns={{'Date': 'VARCHAR', 'Stock_symbol': 'VARCHAR'}}, auto_detect=false)
            WHERE Stock_symbol IS NOT NULL AND Date IS NOT NULL
              AND CAST(SUBSTRING(Date, 1, 4) AS INT) BETWEEN 2009 AND 2024
            GROUP BY UPPER(TRIM(Stock_symbol)), Year
            """
            df_counts = duckdb.query(query).to_df()
        except ImportError:
            print("DuckDB no disponible, procesando en chunks con Pandas...")
            chunks = []
            for chunk in pd.read_csv(raw_csv_path, usecols=['Stock_symbol', 'Date'], chunksize=250_000, low_memory=False):
                chunk = chunk.dropna()
                chunk['Year'] = chunk['Date'].astype(str).str[:4]
                chunk = chunk[chunk['Year'].str.isdigit()]
                chunk['Year'] = chunk['Year'].astype(int)
                chunk = chunk[(chunk['Year'] >= 2009) & (chunk['Year'] <= 2024)]
                chunk['Ticker'] = chunk['Stock_symbol'].astype(str).str.strip().str.upper()
                c = chunk.groupby(['Ticker', 'Year']).size().reset_index(name='Count')
                chunks.append(c)
            df_counts = pd.concat(chunks).groupby(['Ticker', 'Year'])['Count'].sum().reset_index()

        pivot = df_counts.pivot(index='Ticker', columns='Year', values='Count').fillna(0).astype(int)
        for y in range(2009, 2025):
            if y not in pivot.columns:
                pivot[y] = 0
        pivot = pivot[[y for y in range(2009, 2025)]]
        pivot['Total'] = pivot.sum(axis=1)

        # Exportar con openpyxl
        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        # Hoja por volumen
        ws_vol = wb.create_sheet('Por Volumen (Top Tickers)')
        df_vol = pivot.sort_values(by='Total', ascending=False).reset_index()
        _write_sheet(ws_vol, df_vol)

        # Hoja alfabética
        ws_az = wb.create_sheet('Alfabético (A-Z)')
        df_az = pivot.sort_values(by='Ticker', ascending=True).reset_index()
        _write_sheet(ws_az, df_az)

        wb.save(OUT_EXCEL)
        print(f"[Paso 1] Generado con éxito: {OUT_EXCEL}")
        return OUT_EXCEL

    print(f"[Aviso] No se encontró {OUT_EXCEL} ni el CSV crudo.")
    return None

def _write_sheet(ws, df):
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    fill_header = PatternFill(start_color="1A237E", end_color="1A237E", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin', color='E0E0E0'), right=Side(style='thin', color='E0E0E0'),
        top=Side(style='thin', color='E0E0E0'), bottom=Side(style='thin', color='E0E0E0')
    )
    ws.views.sheetView[0].showGridLines = True
    ws.freeze_panes = 'B2'

    cols = df.columns.tolist()
    for col_idx, col_name in enumerate(cols, 1):
        cell = ws.cell(row=1, column=col_idx, value=str(col_name))
        cell.font = font_header
        cell.fill = fill_header
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
            else:
                cell.alignment = Alignment(horizontal='right', vertical='center')
                cell.number_format = '#,##0'
        ws.row_dimensions[r_num].height = 18

    for col_idx in range(1, len(cols) + 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 12 if col_idx > 1 else 14

if __name__ == "__main__":
    raw_path = sys.argv[1] if len(sys.argv) > 1 else None
    build_from_existing_or_raw(raw_path)
