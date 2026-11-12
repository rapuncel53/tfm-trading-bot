import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import numpy as np

# Load coverage data
df = pd.read_csv('data/desglose_cobertura_noticias_todas_las_companias.csv')
t1 = df[df['Clasificacion_Tier'].str.contains('Tier 1', na=False)].copy()

# Sort by total active days with news in splits (Train + Val + Test)
t1['dias_totales'] = t1['Dias_Noticias_Train'] + t1['Dias_Noticias_Val'] + t1['Dias_Noticias_Test']
t1 = t1.sort_values(by='dias_totales', ascending=True).reset_index(drop=True)

# Colors UPC Institutional
c_train = '#0072CE'      # UPC Blue
c_val = '#2E7D32'        # Forest Green
c_test = '#E65100'       # Deep Orange
c_navy = '#003366'
c_bg = '#F8FAFC'
c_card = '#FFFFFF'
c_text = '#263238'

fig = plt.figure(figsize=(18, 10.5), dpi=300, facecolor=c_bg)

# Grid layout: 1 row, 2 main columns (Left: bars, Right: stats & sectors)
gs = fig.add_gridspec(2, 2, width_ratios=[1.7, 1.0], height_ratios=[1.0, 1.0], left=0.06, right=0.96, top=0.90, bottom=0.07, wspace=0.18, hspace=0.25)

# --- PANEL 1: HORIZONTAL STACKED BARS (All 36 Tier 1 Companies) ---
ax_bars = fig.add_subplot(gs[:, 0], facecolor='white')

y_pos = np.arange(len(t1))
h = 0.65

# Data
train_days = t1['Dias_Noticias_Train'].values
val_days = t1['Dias_Noticias_Val'].values
test_days = t1['Dias_Noticias_Test'].values

# Labels: Ticker + clean company name
labels = [f"{row['Ticker']}  •  {row['Empresa'][:24]}" for _, row in t1.iterrows()]

b1 = ax_bars.barh(y_pos, train_days, height=h, color=c_train, label='Train (2011–2018)', edgecolor='none', alpha=0.95)
b2 = ax_bars.barh(y_pos, val_days, height=h, left=train_days, color=c_val, label='Val (2019–Jun 2020)', edgecolor='none', alpha=0.90)
b3 = ax_bars.barh(y_pos, test_days, height=h, left=train_days + val_days, color=c_test, label='Test Ciego (Ago 2021–Dic 2023)', edgecolor='none', alpha=0.90)

ax_bars.set_yticks(y_pos)
ax_bars.set_yticklabels(labels, fontsize=8.5, fontweight='bold', color=c_text)
ax_bars.set_xlabel('Días con Noticias Activas en Cada Partición Temporal', fontsize=11, fontweight='bold', color=c_navy, labelpad=8)
ax_bars.set_title('Distribución de Días con Noticias por Split (36 Acciones Tier 1)', fontsize=13, fontweight='bold', color=c_navy, pad=12)

# Value annotations for total days
for i, total in enumerate(t1['dias_totales']):
    ax_bars.text(total + 25, i, f"{total:,}d", va='center', ha='left', fontsize=8, fontweight='bold', color=c_navy)

ax_bars.set_xlim(0, max(t1['dias_totales']) * 1.12)
ax_bars.grid(axis='x', linestyle='--', alpha=0.5)
ax_bars.legend(loc='lower right', frameon=True, fontsize=10, facecolor='#FFFFFF', edgecolor='#B0BEC5')

# Spine styling
for spine in ax_bars.spines.values():
    spine.set_color('#CFD8DC')

# --- PANEL 2: SECTOR BREAKDOWN (Donut Chart) ---
ax_pie = fig.add_subplot(gs[0, 1], facecolor='white')

sector_counts = t1['Sector'].value_counts()
sector_colors = [
    '#0072CE', '#20B2AA', '#E65100', '#F57C00', 
    '#7B1FA2', '#0288D1', '#388E3C', '#5D4037', '#78909C'
]

wedges, texts, autotexts = ax_pie.pie(
    sector_counts.values,
    labels=None,
    autopct='%1.0f%%',
    pctdistance=0.78,
    startangle=140,
    colors=sector_colors[:len(sector_counts)],
    textprops=dict(color='white', fontweight='bold', fontsize=9)
)

# Donut hole
donut_hole = plt.Circle((0,0), 0.56, fc='white')
ax_pie.add_artist(donut_hole)
ax_pie.set_title('Composición Sectorial del Universo Tier 1', fontsize=12, fontweight='bold', color=c_navy, pad=10)

# Legend for sectors with count
legend_labels = [f"{sec} ({cnt})" for sec, cnt in zip(sector_counts.index, sector_counts.values)]
ax_pie.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(0.92, 0.5), fontsize=8.5, frameon=True, facecolor='white')

# --- PANEL 3: SUMMARY CARDS / KEY STATS ---
ax_stats = fig.add_subplot(gs[1, 1], facecolor='white')
ax_stats.axis('off')

# Draw clean summary box
card_rect = patches.FancyBboxPatch((0.02, 0.05), 0.96, 0.90, boxstyle="round,pad=0.03,rounding_size=0.04", linewidth=1.2, edgecolor='#0072CE', facecolor='#F4F9FD')
ax_stats.add_patch(card_rect)

ax_stats.text(0.08, 0.82, "Métricas Clave del Universo Tier 1", fontsize=12, fontweight='bold', color=c_navy)
ax_stats.plot([0.08, 0.90], [0.77, 0.77], color='#0072CE', linewidth=1.0)

stats_items = [
    ("36", "Empresas con Cobertura Continua", "Presencia simultánea en Train (11–18), Val (19–20) y Test (21–23)."),
    ("178.643", "Noticias Totales Acumuladas", "Flujo masivo de alertas de analistas (Benzinga) y noticias NASDAQ (FNSPID)."),
    ("100%", "Disponibilidad Contable SEC", "Balances auditados 10-Q/10-K continuos durante más de dos décadas (2000–2023)."),
    ("0%", "Fuga de Información (Leakage)", "Partición Walk-Forward con 14 meses de embargo entre Val y Test.")
]

y_anchor = 0.65
for num, title, desc in stats_items:
    ax_stats.text(0.08, y_anchor, num, fontsize=13, fontweight='bold', color='#0072CE')
    ax_stats.text(0.24, y_anchor + 0.015, title, fontsize=9.5, fontweight='bold', color=c_navy)
    ax_stats.text(0.24, y_anchor - 0.045, desc, fontsize=7.5, color='#546E7A')
    y_anchor -= 0.16

# --- GLOBAL HEADER ---
fig.suptitle('UNIVERSO TIER 1: 36 ACCIONES CON COBERTURA TOTAL Y CONTINUA (2011 – 2023)', fontsize=15, fontweight='bold', color=c_navy, y=0.96)
fig.text(0.5, 0.925, 'Empresas cotizadas de máxima calidad con flujo ininterrumpido en Train, Validación y Test Ciego | TFM - MERIT Master (UPC Manresa)', ha='center', fontsize=10, color='#546E7A')

# Save figures
out_main = 'data/universo_tier1_acciones.png'
out_slides = 'latex_slides/universo_tier1_acciones.png'
out_artifact = 'C:/Users/julia/.gemini/antigravity/brain/cc439e90-51d4-4cb8-a041-93097f11deb7/universo_tier1_acciones.png'

plt.savefig(out_main, bbox_inches='tight')
plt.savefig(out_slides, bbox_inches='tight')
plt.savefig(out_artifact, bbox_inches='tight')

print('SUCCESS: generated Tier 1 dashboard image at:')
print('  -', out_main)
print('  -', out_slides)
print('  -', out_artifact)
