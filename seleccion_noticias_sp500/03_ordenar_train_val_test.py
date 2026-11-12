"""03_ordenar_train_val_test.py
=============================================================================
Paso 3 del Pipeline de Selección de Noticias:
Ordena las empresas del S&P 500 según su idoneidad temporal para entrenar
modelos de Machine Learning y LLMs con un reparto canónico:
  - TRAIN : 2009–2018 (Objetivo: ~70% del flujo de noticias)
  - VAL   : 2019–2020 (Objetivo: ~10% - Shock COVID y calibración)
  - TEST  : 2021–2023 (Objetivo: ~20% - Out-of-sample estricto)

Criterios Clave:
  1. Continuidad: descarta activos con huecos totales o cortes temporales.
  2. Desviación 70/10/20: penaliza asimetrías extremas.
  3. Volumen: premia masa crítica de noticias para un entrenamiento denso.
  4. Deciles de Cartera: las primeras 100 empresas continuas permiten
     construir deciles equilibrados de 10 activos cada uno (D0 a D9).

Genera:
  sp500_noticias_ordenadas_train_val_test.xlsx
    - Hoja 1: 'S&P 500 (Ranking Splits)' (Todas las 503 empresas ordenadas)
    - Hoja 2: 'Top Empresas Continuas' (343 empresas continuas sin huecos)
    - Hoja 3: 'Empresas Descartadas' (160 empresas con cortes/silencios)
    - Hoja 4: 'Resumen por Sector' (Estadísticas consolidadas por sector)
=============================================================================
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IN_FILE = os.path.join(SCRIPT_DIR, "matriz_noticias_sp500.xlsx")
OUT_FILE = os.path.join(SCRIPT_DIR, "sp500_noticias_ordenadas_train_val_test.xlsx")

def main():
    print(f"[Paso 3] Leyendo matriz del S&P 500 desde: {IN_FILE}")
    if not os.path.exists(IN_FILE):
        raise FileNotFoundError(f"No se encontró {IN_FILE}. Ejecuta primero el Paso 2.")

    wb_in = openpyxl.load_workbook(IN_FILE)
    ws_in = wb_in['S&P 500 (Por Volumen)']
    data = list(ws_in.values)
    cols = list(data[0])

    rows = []
    for r in data[1:]:
        if r[0] and str(r[0]).strip() != 'Ticker' and len(str(r[0]).strip()) <= 10:
            rows.append(list(r))

    df = pd.DataFrame(rows, columns=cols)
    df = df.drop_duplicates(subset=['Ticker']).copy()

    year_cols = [c for c in cols if str(c).isdigit()]
    for c in year_cols + ['Total Noticias']:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)

    train_cols = [str(y) for y in range(2009, 2019)]
    val_cols = ['2019', '2020']
    test_cols = ['2021', '2022', '2023']

    df['News_Train'] = df[train_cols].sum(axis=1)
    df['News_Val'] = df[val_cols].sum(axis=1)
    df['News_Test'] = df[test_cols].sum(axis=1)
    df['Total_Tracked'] = df['News_Train'] + df['News_Val'] + df['News_Test']

    df['Pct_Train'] = np.where(df['Total_Tracked'] > 0, np.round((df['News_Train'] / df['Total_Tracked']) * 100, 1), 0.0)
    df['Pct_Val'] = np.where(df['Total_Tracked'] > 0, np.round((df['News_Val'] / df['Total_Tracked']) * 100, 1), 0.0)
    df['Pct_Test'] = np.where(df['Total_Tracked'] > 0, np.round((df['News_Test'] / df['Total_Tracked']) * 100, 1), 0.0)

    df['Has_Train'] = df['News_Train'] > 0
    df['Has_Val'] = df['News_Val'] > 0
    df['Has_Test'] = df['News_Test'] > 0
    df['Is_Continuous'] = df['Has_Train'] & df['Has_Val'] & df['Has_Test']

    # Desviación frente al objetivo 70% Train, 10% Val, 20% Test
    df['Dev_70_10_20'] = np.round(np.abs(df['Pct_Train'] - 70.0) + np.abs(df['Pct_Val'] - 10.0) + np.abs(df['Pct_Test'] - 20.0), 1)

    vol_score = np.minimum(50.0, np.log10(np.maximum(10, df['Total_Tracked'])) * 12.5)
    balance_score = np.maximum(0.0, 50.0 - (df['Dev_70_10_20'] * 0.7))
    df['Score_Idoneidad'] = np.where(df['Is_Continuous'], np.round(vol_score + balance_score, 1), 0.0)

    def categorize(r):
        if not r['Is_Continuous']:
            if not r['Has_Train'] and not r['Has_Val']:
                return 'Descartada: Solo Test Reciente (2021-2023)'
            elif not r['Has_Train']:
                return 'Descartada: Sin histórico en Train'
            elif not r['Has_Test']:
                return 'Descartada: Corte en 2020 (Sin Test)'
            elif not r['Has_Val']:
                return 'Descartada: Laguna total en Validación'
            else:
                return 'Descartada: Incompleta'
        if r['Pct_Train'] >= 60.0 and r['Pct_Test'] >= 15.0 and r['Total_Tracked'] >= 3000:
            return 'Núcleo de Élite (Ajuste Óptimo 70/10/20)'
        elif r['Total_Tracked'] >= 2000 and r['Score_Idoneidad'] >= 75.0:
            return 'Apto de Alta Calidad (Balanceado)'
        elif r['Total_Tracked'] >= 1000:
            return 'Apto Complementario'
        else:
            return 'Flujo Bajo / Muestra Reducida'

    df['Categoria_Idoneidad'] = df.apply(categorize, axis=1)

    # Ordenar estrictamente: Continuas arriba, mayor Score de Idoneidad y volumen
    df_sorted = df.sort_values(
        by=['Is_Continuous', 'Score_Idoneidad', 'Total_Tracked'], 
        ascending=[False, False, False]
    ).reset_index(drop=True)
    df_sorted['Ranking_Idoneidad'] = df_sorted.index + 1

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    fill_header = PatternFill(start_color="1A237E", end_color="1A237E", fill_type="solid")
    fill_split = PatternFill(start_color="283593", end_color="283593", fill_type="solid")
    fill_elite = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")
    fill_warn = PatternFill(start_color="FFEBEE", end_color="FFEBEE", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='E0E0E0'), right=Side(style='thin', color='E0E0E0'),
        top=Side(style='thin', color='E0E0E0'), bottom=Side(style='thin', color='E0E0E0')
    )

    display_cols = [
        ('Ranking_Idoneidad', 'Ranking', 'center'),
        ('Ticker', 'Ticker', 'center'),
        ('Empresa', 'Empresa', 'left'),
        ('Sector GICS', 'Sector GICS', 'left'),
        ('Score_Idoneidad', 'Score Idoneidad (0-100)', 'center'),
        ('Categoria_Idoneidad', 'Diagnóstico / Idoneidad Split', 'left'),
        ('News_Train', 'Noticias Train (2009-18)', 'right'),
        ('Pct_Train', '% Train', 'right'),
        ('News_Val', 'Noticias Val (2019-20)', 'right'),
        ('Pct_Val', '% Val', 'right'),
        ('News_Test', 'Noticias Test (2021-23)', 'right'),
        ('Pct_Test', '% Test', 'right'),
        ('Dev_70_10_20', 'Desv. vs 70/10/20', 'right'),
        ('Total Noticias', 'Total Noticias', 'right'),
    ] + [(y, str(y), 'right') for y in year_cols]

    def populate_sheet(ws, dataframe, title):
        ws.title = title
        ws.views.sheetView[0].showGridLines = True
        ws.freeze_panes = 'E2'

        for col_idx, (col_key, col_label, align) in enumerate(display_cols, 1):
            cell = ws.cell(row=1, column=col_idx, value=col_label)
            cell.font = font_header
            cell.fill = fill_split if 'Train' in col_label or 'Val' in col_label or 'Test' in col_label else fill_header
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = thin_border
        ws.row_dimensions[1].height = 28

        for row_idx, row in dataframe.iterrows():
            excel_row = row_idx + 2
            ws.row_dimensions[excel_row].height = 20
            is_elite = 'Núcleo de Élite' in str(row['Categoria_Idoneidad'])
            is_bad = not row['Is_Continuous']

            for col_idx, (col_key, col_label, align) in enumerate(display_cols, 1):
                val = row[col_key]
                cell = ws.cell(row=excel_row, column=col_idx, value=val)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal=align, vertical='center')

                if isinstance(val, (int, np.integer)):
                    cell.number_format = '#,##0'
                elif isinstance(val, (float, np.floating)):
                    if 'Pct' in col_key or '%' in col_label:
                        cell.number_format = '0.0"%"'
                    elif 'Score' in col_key or 'Dev' in col_key:
                        cell.number_format = '0.0'

                if is_elite and col_key in ['Ranking_Idoneidad', 'Ticker', 'Score_Idoneidad', 'Categoria_Idoneidad']:
                    cell.fill = fill_elite
                    cell.font = Font(name="Calibri", size=11, bold=True, color="1B5E20")
                elif is_bad and col_key in ['Ranking_Idoneidad', 'Ticker', 'Score_Idoneidad', 'Categoria_Idoneidad']:
                    cell.fill = fill_warn
                    cell.font = Font(name="Calibri", size=11, color="B71C1C")
                elif col_key == 'Score_Idoneidad':
                    cell.font = Font(name="Calibri", size=11, bold=True)

        for col_idx, (col_key, col_label, _) in enumerate(display_cols, 1):
            col_letter = get_column_letter(col_idx)
            max_len = max(len(str(col_label)), 8)
            for cell in ws[col_letter][1:50]:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = min(max_len + 3, 35)

    # 1. Todas las empresas
    ws_all = wb.create_sheet('S&P 500 (Ranking Splits)')
    populate_sheet(ws_all, df_sorted, 'S&P 500 (Ranking Splits)')

    # 2. Top Continuas
    df_cont = df_sorted[df_sorted['Is_Continuous']].copy().reset_index(drop=True)
    df_cont['Ranking_Idoneidad'] = df_cont.index + 1
    ws_cont = wb.create_sheet('Top Empresas Continuas')
    populate_sheet(ws_cont, df_cont, 'Top Empresas Continuas')

    # 3. Descartadas
    df_disc = df_sorted[~df_sorted['Is_Continuous']].copy().reset_index(drop=True)
    df_disc['Ranking_Idoneidad'] = df_disc.index + 1
    ws_disc = wb.create_sheet('Empresas Descartadas')
    populate_sheet(ws_disc, df_disc, 'Empresas Descartadas')

    # 4. Resumen por Sector
    ws_sec = wb.create_sheet('Resumen por Sector')
    ws_sec.views.sheetView[0].showGridLines = True
    sec_summary = df.groupby('Sector GICS').agg(
        Total_Acciones=('Ticker', 'count'),
        Continuas=('Is_Continuous', 'sum'),
        Total_Noticias=('Total_Tracked', 'sum'),
        Noticias_Train=('News_Train', 'sum'),
        Noticias_Val=('News_Val', 'sum'),
        Noticias_Test=('News_Test', 'sum'),
    ).reset_index()
    sec_summary['Pct_Exito_Continuo'] = np.round((sec_summary['Continuas'] / sec_summary['Total_Acciones']) * 100, 1)
    sec_summary['Pct_Train'] = np.round((sec_summary['Noticias_Train'] / sec_summary['Total_Noticias']) * 100, 1)
    sec_summary['Pct_Val'] = np.round((sec_summary['Noticias_Val'] / sec_summary['Total_Noticias']) * 100, 1)
    sec_summary['Pct_Test'] = np.round((sec_summary['Noticias_Test'] / sec_summary['Total_Noticias']) * 100, 1)
    sec_summary = sec_summary.sort_values(by='Continuas', ascending=False).reset_index(drop=True)

    sec_cols = [
        ('Sector GICS', 'Sector GICS', 'left'),
        ('Total_Acciones', 'Total Acciones', 'right'),
        ('Continuas', 'Empresas Continuas (Válidas)', 'right'),
        ('Pct_Exito_Continuo', '% Éxito Continuo', 'right'),
        ('Total_Noticias', 'Total Noticias', 'right'),
        ('Noticias_Train', 'Noticias Train', 'right'),
        ('Pct_Train', '% Train', 'right'),
        ('Noticias_Val', 'Noticias Val', 'right'),
        ('Pct_Val', '% Val', 'right'),
        ('Noticias_Test', 'Noticias Test', 'right'),
        ('Pct_Test', '% Test', 'right'),
    ]

    for col_idx, (ck, cl, al) in enumerate(sec_cols, 1):
        c = ws_sec.cell(row=1, column=col_idx, value=cl)
        c.font = font_header
        c.fill = fill_header
        c.alignment = Alignment(horizontal='center', vertical='center')
        c.border = thin_border
    ws_sec.row_dimensions[1].height = 25

    for r_idx, r in sec_summary.iterrows():
        rn = r_idx + 2
        for col_idx, (ck, cl, al) in enumerate(sec_cols, 1):
            val = r[ck]
            c = ws_sec.cell(row=rn, column=col_idx, value=val)
            c.border = thin_border
            c.alignment = Alignment(horizontal=al, vertical='center')
            if isinstance(val, (int, np.integer)):
                c.number_format = '#,##0'
            elif isinstance(val, (float, np.floating)):
                if 'Pct' in ck:
                    c.number_format = '0.0"%"'
        ws_sec.row_dimensions[rn].height = 20

    for col_idx, (ck, cl, _) in enumerate(sec_cols, 1):
        col_letter = get_column_letter(col_idx)
        ws_sec.column_dimensions[col_letter].width = max(len(cl) + 4, 16)

    wb.save(OUT_FILE)
    print(f"[Paso 3] Excel generado exitosamente en: {OUT_FILE}")
    print(f"         Total Continuas Válidas: {len(df_cont)} de {len(df)}")
    print(f"         Total Descartadas por Incompletitud: {len(df_disc)}")

if __name__ == '__main__':
    main()
