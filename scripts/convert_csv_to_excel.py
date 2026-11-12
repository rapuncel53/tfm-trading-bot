import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

csv_path = 'data/desglose_cobertura_noticias_todas_las_companias.csv'
excel_path = 'data/desglose_cobertura_noticias_todas_las_companias.xlsx'

df = pd.read_csv(csv_path)

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Cobertura_Noticias_207_Empresas"

# Styles
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="0072CE", end_color="0072CE", fill_type="solid")
border_thin = Side(border_style="thin", color="CCCCCC")
cell_border = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

# Fills for Tiers
tier1_fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")  # Verde claro
tier2_hist_fill = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")  # Azul claro
tier2_tard_fill = PatternFill(start_color="FFF3E0", end_color="FFF3E0", fill_type="solid")  # Naranja claro
tier3_fill = PatternFill(start_color="ECEFF1", end_color="ECEFF1", fill_type="solid")  # Gris claro

headers = list(df.columns)
ws.append(headers)

for col_num, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col_num)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

for row_idx, r_data in enumerate(df.values.tolist(), 2):
    ws.append(r_data)
    tier_val = str(r_data[3])
    row_fill = None
    if "Tier 1" in tier_val:
        row_fill = tier1_fill
    elif "Histórica" in tier_val:
        row_fill = tier2_hist_fill
    elif "Tardía" in tier_val:
        row_fill = tier2_tard_fill
    elif "Tier 3" in tier_val:
        row_fill = tier3_fill
        
    for col_idx in range(1, len(headers) + 1):
        c = ws.cell(row=row_idx, column=col_idx)
        c.border = cell_border
        
        # Center align codes, dates, booleans
        if col_idx in [1, 4, 5, 8, 9, 14, 15, 16, 17, 18]:
            c.alignment = Alignment(horizontal="center", vertical="center")
        elif col_idx in [7, 11, 12]:
            c.alignment = Alignment(horizontal="right", vertical="center")
            c.number_format = "#,##0"
        else:
            c.alignment = Alignment(horizontal="left", vertical="center")
            
        if col_idx == 4 and row_fill:
            c.fill = row_fill

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
    ws.column_dimensions[col_letter].width = min(max(max_len + 3, 11), 60)

wb.save(excel_path)
print(f'SUCCESS: Excel saved to {excel_path} ({len(df)} companies)')
