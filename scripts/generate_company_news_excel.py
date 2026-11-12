import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# 1. Load splits
train_df = pd.read_parquet('data/splits/train/daily_aligned.parquet')
val_df = pd.read_parquet('data/splits/val/daily_aligned.parquet')
test_df = pd.read_parquet('data/splits/test/daily_aligned.parquet')

# 2. Load bz metadata
bz_meta = pd.read_csv('data/benzinga/tier1_benzinga_coverage.csv')
meta_dict = {}
for _, row in bz_meta.iterrows():
    sym = str(row['sym']).strip()
    meta_dict[sym] = {
        'sec_name': str(row.get('sec_name', '')),
        'sector': str(row.get('sector', '')),
        'bz_count': row.get('benzinga_count'),
        'bz_start': str(row.get('benzinga_start', '')),
        'bz_end': str(row.get('benzinga_end', '')),
        'fn_count': row.get('n_news'),
        'fn_start': str(row.get('d0_news', '')),
        'fn_end': str(row.get('d1_news', ''))
    }

# Known names for extra tickers
extra_names = {
    'KO': ('The Coca-Cola Company', 'Consumer Staples'),
    'AMD': ('Advanced Micro Devices, Inc.', 'Information Technology'),
    'ADBE': ('Adobe Inc.', 'Information Technology'),
    'T': ('AT&T Inc.', 'Communication Services'),
    'DIS': ('The Walt Disney Company', 'Communication Services'),
    'JPM': ('JPMorgan Chase & Co.', 'Financials'),
    'PFE': ('Pfizer Inc.', 'Health Care'),
    'JNJ': ('Johnson & Johnson', 'Health Care')
}

all_tickers = sorted(list(set(train_df['ticker'].unique()) | set(val_df['ticker'].unique()) | set(test_df['ticker'].unique()) | set(bz_meta['sym'].unique())))

rows = []

for t in all_tickers:
    # Split observations with news
    tr_sub = train_df[(train_df['ticker'] == t) & (train_df['has_news'] == True)]
    va_sub = val_df[(val_df['ticker'] == t) & (val_df['has_news'] == True)]
    te_sub = test_df[(test_df['ticker'] == t) & (test_df['has_news'] == True)]
    
    tr_cnt = len(tr_sub)
    va_cnt = len(va_sub)
    te_cnt = len(te_sub)
    
    # Metadata lookup
    m = meta_dict.get(t, {})
    sec_name = m.get('sec_name', '')
    sector = m.get('sector', '')
    
    if (not sec_name or sec_name == 'nan') and t in extra_names:
        sec_name, sector = extra_names[t]
        
    bz_cnt = m.get('bz_count')
    bz_start = m.get('bz_start')
    bz_end = m.get('bz_end')
    
    fn_cnt = m.get('fn_count')
    fn_start = m.get('fn_start')
    fn_end = m.get('fn_end')
    
    # Fallback to split dates if missing in bz_meta
    if pd.isna(bz_cnt) or bz_cnt == 0:
        if tr_cnt > 0 or va_cnt > 0:
            bz_cnt = tr_cnt + va_cnt
            if tr_cnt > 0:
                bz_start = str(tr_sub['date'].min())[:10]
            else:
                bz_start = str(va_sub['date'].min())[:10]
            if va_cnt > 0:
                bz_end = str(va_sub['date'].max())[:10]
            else:
                bz_end = str(tr_sub['date'].max())[:10]
        else:
            bz_cnt = 0
            bz_start = 'Sin datos'
            bz_end = 'Sin datos'
    else:
        bz_cnt = int(bz_cnt)
        bz_start = str(bz_start)[:10] if bz_start and str(bz_start) != 'nan' else 'Sin datos'
        bz_end = str(bz_end)[:10] if bz_end and str(bz_end) != 'nan' else 'Sin datos'

    if pd.isna(fn_cnt) or fn_cnt == 0:
        if te_cnt > 0:
            fn_cnt = te_cnt
            fn_start = str(te_sub['date'].min())[:10]
            fn_end = str(te_sub['date'].max())[:10]
        else:
            fn_cnt = 0
            fn_start = 'Sin datos'
            fn_end = 'Sin datos'
    else:
        fn_cnt = int(fn_cnt)
        fn_start = str(fn_start)[:10] if fn_start and str(fn_start) != 'nan' else 'Sin datos'
        fn_end = str(fn_end)[:10] if fn_end and str(fn_end) != 'nan' else 'Sin datos'

    has_bz = "SÍ" if bz_cnt > 0 and bz_start != 'Sin datos' else "NO"
    has_fn = "SÍ" if fn_cnt > 0 and fn_start != 'Sin datos' else "NO"
    
    total_news = bz_cnt + fn_cnt
    
    # Dates list
    valid_starts = []
    valid_ends = []
    if bz_start != 'Sin datos':
        valid_starts.append(bz_start)
        valid_ends.append(bz_end)
    if fn_start != 'Sin datos':
        valid_starts.append(fn_start)
        valid_ends.append(fn_end)
        
    if valid_starts:
        d_min = min(valid_starts)
        d_max = max(valid_ends)
        y_min = int(d_min[:4])
        y_max = int(d_max[:4])
        span_years = round((y_max - y_min) + 1, 1)
    else:
        d_min = 'Sin noticias'
        d_max = 'Sin noticias'
        span_years = 0.0

    # Tier Classification
    if tr_cnt > 0 and va_cnt > 0 and te_cnt > 0:
        tier = "Tier 1: Cobertura Total Continua"
        diag = f"Excelente: flujo ininterrumpido en Train ({tr_cnt}d), Val ({va_cnt}d) y Test ({te_cnt}d). Cobertura {d_min[:4]} a {d_max[:4]}."
    elif tr_cnt > 0 and va_cnt > 0 and te_cnt == 0:
        tier = "Tier 2: Cobertura Parcial Histórica"
        diag = f"Histórica Benzinga: cubre Train ({tr_cnt}d) y Val ({va_cnt}d), pero no tiene noticias en Test (2021-2023)."
    elif (tr_cnt == 0 or tr_cnt < 30) and (va_cnt > 0 or te_cnt > 0):
        tier = "Tier 2: Cobertura Parcial Tardía"
        diag = f"Reciente / Big Tech: pocas o ninguna noticia en Train, pero densa en Val ({va_cnt}d) y Test ({te_cnt}d)."
    elif te_cnt > 0 and tr_cnt == 0 and va_cnt == 0:
        tier = "Tier 3: Cobertura Mínima"
        diag = f"Solo Test: no tiene noticias de 2011 a 2020. Solo aparece en FNSPID ({te_cnt}d en Test)."
    elif total_news == 0 or (tr_cnt == 0 and va_cnt == 0 and te_cnt == 0):
        tier = "Tier 3: Silenciosa (Solo Balances SEC)"
        diag = "Empresa silenciosa: dispone de cotizaciones y balances SEC auditados, pero sin flujo noticioso registrado."
    else:
        tier = "Tier 3: Cobertura Mínima"
        diag = f"Cobertura esporádica: {tr_cnt}d en Train, {va_cnt}d en Val, {te_cnt}d en Test."

    rows.append({
        'Ticker': t,
        'Empresa': sec_name if sec_name and sec_name != 'nan' else t,
        'Sector': sector if sector and sector != 'nan' else 'General',
        'Clasificacion_Tier': tier,
        'Tiene_Benzinga': has_bz,
        'Benzinga_Fecha_Inicio': bz_start,
        'Benzinga_Fecha_Fin': bz_end,
        'Benzinga_Noticias': bz_cnt,
        'Tiene_FNSPID': has_fn,
        'FNSPID_Fecha_Inicio': fn_start,
        'FNSPID_Fecha_Fin': fn_end,
        'FNSPID_Noticias': fn_cnt,
        'Total_Noticias': total_news,
        'Fecha_Inicio_Global': d_min,
        'Fecha_Fin_Global': d_max,
        'Anios_Cobertura': span_years,
        'Dias_Noticias_Train': tr_cnt,
        'Dias_Noticias_Val': va_cnt,
        'Dias_Noticias_Test': te_cnt,
        'Diagnostico_Detallado': diag
    })

res_df = pd.DataFrame(rows)

# Sort by Tier then by Total_Noticias descending
tier_order = {
    "Tier 1: Cobertura Total Continua": 1,
    "Tier 2: Cobertura Parcial Histórica": 2,
    "Tier 2: Cobertura Parcial Tardía": 3,
    "Tier 3: Cobertura Mínima": 4,
    "Tier 3: Silenciosa (Solo Balances SEC)": 5
}
res_df['tier_rank'] = res_df['Clasificacion_Tier'].map(tier_order)
res_df = res_df.sort_values(by=['tier_rank', 'Total_Noticias'], ascending=[True, False]).drop(columns=['tier_rank'])

# Save CSV
csv_path = 'data/desglose_cobertura_noticias_todas_las_companias.csv'
res_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f'CSV saved to {csv_path} ({len(res_df)} companies)')

# Save Excel with OpenPyXL formatting
excel_path = 'data/desglose_cobertura_noticias_todas_las_companias.xlsx'
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Cobertura_Noticias_Por_Empresa"

# Styles
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="0072CE", end_color="0072CE", fill_type="solid")
border_thin = Side(border_style="thin", color="CCCCCC")
cell_border = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

# Fills for Tiers
tier1_fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")  # Light green
tier2_fill = PatternFill(start_color="FFF3E0", end_color="FFF3E0", fill_type="solid")  # Light orange
tier3_fill = PatternFill(start_color="ECEFF1", end_color="ECEFF1", fill_type="solid")  # Light gray

# Write headers
headers = list(res_df.columns)
ws.append(headers)

for col_num, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col_num)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

# Write rows
for row_idx, r_data in enumerate(res_df.values.tolist(), 2):
    ws.append(r_data)
    tier_val = str(r_data[3])
    row_fill = None
    if "Tier 1" in tier_val:
        row_fill = tier1_fill
    elif "Tier 2" in tier_val:
        row_fill = tier2_fill
    elif "Tier 3" in tier_val:
        row_fill = tier3_fill
        
    for col_idx in range(1, len(headers) + 1):
        c = ws.cell(row=row_idx, column=col_idx)
        c.border = cell_border
        if col_idx in [1, 4, 5, 8, 9, 14, 15, 16, 17, 18]:
            c.alignment = Alignment(horizontal="center", vertical="center")
        elif col_idx in [7, 11, 12]:
            c.alignment = Alignment(horizontal="right", vertical="center")
            c.number_format = "#,##0"
        else:
            c.alignment = Alignment(horizontal="left", vertical="center")
            
        if col_idx == 4 and row_fill:
            c.fill = row_fill

# Freeze panes & Auto-filter
ws.freeze_panes = "A2"
ws.auto_filter.ref = ws.dimensions

# Auto column widths
for col in ws.columns:
    max_len = 0
    col_letter = get_column_letter(col[0].column)
    for cell in col:
        val = str(cell.value or '')
        if len(val) > max_len:
            max_len = len(val)
    ws.column_dimensions[col_letter].width = min(max(max_len + 3, 11), 50)

wb.save(excel_path)
print(f'Excel saved to {excel_path} ({len(res_df)} companies)')
