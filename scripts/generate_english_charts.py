import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime
import os

os.makedirs('analisis_noticias_tfm', exist_ok=True)

# -------------------------------------------------------------
# 1. LOAD DATA
# -------------------------------------------------------------
df = pd.read_csv('analisis_noticias_tfm/1_cobertura_noticias_todas_las_acciones.csv')

# Representative companies across Tiers
selected_tickers = [
    # Tier 1 Elite (Continuous coverage)
    'ORCL', 'CAT', 'KO', 'NVDA', 'COST', 'V', 'EBAY', 'CRM', 'GILD', 'QCOM', 'ADBE', 'AMD', 'INTC', 'WMT',
    # Tier 2 Historical Benzinga
    'MRK', 'PFE', 'JNJ',
    # Tier 2 / 3 Late Coverage / Gaps (Big Tech)
    'GOOG', 'AAPL', 'AMZN', 'MSFT', 'DIS'
]

sub_df = df[df['Ticker'].isin(selected_tickers)].copy()

tier_priority = {
    'Tier 1: Cobertura Total Continua': 1,
    'Tier 2: Cobertura Parcial Histórica': 2,
    'Tier 2: Cobertura Parcial Tardía': 3,
    'Tier 3: Cobertura Mínima': 4,
    'Tier 3: Silenciosa': 4
}
sub_df['tier_p'] = sub_df['Clasificacion_Tier'].map(lambda x: next((v for k, v in tier_priority.items() if k in str(x)), 4))
sub_df = sub_df.sort_values(by=['tier_p', 'Total_Noticias_Global'], ascending=[True, False]).reset_index(drop=True)

# -------------------------------------------------------------
# FIGURE 1: TIMELINE GANTT CHART IN ENGLISH
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(15, 9.5), dpi=300, facecolor='#F8FAFC')
ax.set_facecolor('white')

# Shaded background zones
ax.axvspan(datetime(2011,1,1), datetime(2019,12,31), color='#E3F2FD', alpha=0.60, label='Optimized Train (2011–2019, ~70% News)')
ax.axvspan(datetime(2020,1,1), datetime(2020,6,10), color='#E8F5E9', alpha=0.65, label='Optimized Val (Jan–Jun 2020, ~10% News - COVID Shock)')
ax.axvspan(datetime(2020,6,11), datetime(2021,8,16), color='#FFCDD2', alpha=0.75, label='Embargo / Quarantine Period (14 Months Gap)')
ax.axvspan(datetime(2021,8,17), datetime(2023,12,31), color='#FFF3E0', alpha=0.60, label='Blind Test (Aug 2021–Dec 2023, ~20% News - Modern Rates)')

bz_color = '#0072CE'
fn_color = '#E65100'

y_labels = []
bz_labeled = False
fn_labeled = False

n_comp = len(sub_df)
for i, row in sub_df.iterrows():
    y = n_comp - 1 - i
    ticker = row['Ticker']
    tier_raw = str(row['Clasificacion_Tier'])
    tier_short = 'Tier 1' if 'Tier 1' in tier_raw else ('Tier 2 (Hist)' if 'Histórica' in tier_raw else ('Tier 2 (Late)' if 'Tardía' in tier_raw else 'Tier 3'))
    comp_name = str(row['Empresa'])[:20]
    y_labels.append(f"{ticker:5s} [{tier_short}] - {comp_name}")
    
    # Benzinga bar
    bz_s = str(row.get('Benzinga_Fecha_Inicio', ''))
    bz_e = str(row.get('Benzinga_Fecha_Fin', ''))
    if bz_s not in ['Sin datos', 'nan', ''] and bz_e not in ['Sin datos', 'nan', '']:
        d0 = datetime.strptime(bz_s[:10], '%Y-%m-%d')
        d1 = datetime.strptime(bz_e[:10], '%Y-%m-%d')
        lbl = 'Benzinga Fast Analyst Alerts (2009–2020)' if not bz_labeled else None
        bz_labeled = True
        ax.barh(y + 0.16, (d1 - d0).days, left=d0, height=0.27, color=bz_color, alpha=0.92, label=lbl, edgecolor='#002B49', linewidth=0.6)
        
    # FNSPID bar
    fn_s = str(row.get('FNSPID_Fecha_Inicio', ''))
    fn_e = str(row.get('FNSPID_Fecha_Fin', ''))
    if fn_s not in ['Sin datos', 'nan', ''] and fn_e not in ['Sin datos', 'nan', '']:
        d0 = datetime.strptime(fn_s[:10], '%Y-%m-%d')
        d1 = datetime.strptime(fn_e[:10], '%Y-%m-%d')
        lbl = 'FNSPID NASDAQ Full News (2009–2023)' if not fn_labeled else None
        fn_labeled = True
        ax.barh(y - 0.16, (d1 - d0).days, left=d0, height=0.27, color=fn_color, alpha=0.90, label=lbl, edgecolor='#BF360C', linewidth=0.6)

ax.set_yticks(range(n_comp))
ax.set_yticklabels(list(reversed(y_labels)), fontsize=9, fontweight='bold', color='#263238')
ax.set_xlim(datetime(2009, 1, 1), datetime(2024, 5, 1))

ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.set_xlabel('Timeline of Financial Newsflow (Years 2009 to 2023)', fontsize=11, fontweight='bold', color='#003366', labelpad=8)
ax.set_title('COMPANY NEWS TIMELINE COVERAGE: BENZINGA VS. FNSPID (2009–2023)', fontsize=13, fontweight='bold', color='#003366', pad=14)

ax.grid(axis='x', linestyle='--', alpha=0.5)
ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.18), ncol=3, frameon=True, fontsize=9.5, facecolor='white', edgecolor='#B0BEC5')

# Visual separator between tiers
ax.axhline(7.5, color='#90A4AE', linestyle='--', linewidth=1.2)
ax.axhline(4.5, color='#90A4AE', linestyle='--', linewidth=1.2)

plt.tight_layout()
fig1_path = 'analisis_noticias_tfm/mapa_temporal_noticias_por_compania_en.png'
plt.savefig(fig1_path, bbox_inches='tight')
plt.close()
print(f'SUCCESS: saved {fig1_path}')


# -------------------------------------------------------------
# FIGURE 2: ELITE COMPANIES 70 / 10 / 20 IN ENGLISH
# -------------------------------------------------------------
elite_df = pd.read_csv('analisis_noticias_tfm/2_mejores_acciones_seleccionadas_entrenamiento.csv')
elite_tickers = ['ORCL', 'CAT', 'KO', 'EBAY', 'V', 'COST', 'CRM', 'GILD', 'QCOM', 'BIIB', 'ADBE', 'NVDA']

sub_elite = elite_df[elite_df['Ticker'].isin(elite_tickers)].copy()
# Sort by Pct_Train ascending for chart
sub_elite = sub_elite.sort_values(by='Pct_Train', ascending=True).reset_index(drop=True)

fig2, ax2 = plt.subplots(figsize=(12, 7.5), dpi=300, facecolor='#F8FAFC')
ax2.set_facecolor('white')

y_pos2 = np.arange(len(sub_elite))
h2 = 0.62

ax2.barh(y_pos2, sub_elite['Pct_Train'], height=h2, color='#0072CE', label='Train (2011–2019) ~70%', alpha=0.95)
ax2.barh(y_pos2, sub_elite['Pct_Val'], height=h2, left=sub_elite['Pct_Train'], color='#2E7D32', label='Val (COVID 2020) ~10%', alpha=0.90)
ax2.barh(y_pos2, sub_elite['Pct_Test'], height=h2, left=sub_elite['Pct_Train'] + sub_elite['Pct_Val'], color='#E65100', label='Blind Test (2021–2023) ~20%', alpha=0.90)

ax2.set_yticks(y_pos2)
ax2.set_yticklabels(sub_elite['Ticker'], fontsize=11, fontweight='bold', color='#263238')
ax2.set_xlabel('Share of Active News Days Per Company (%)', fontsize=11, fontweight='bold', color='#003366', labelpad=8)
ax2.set_title('ELITE STOCK BASKET: BALANCED MACHINE LEARNING SPLIT (~70 / 10 / 20)', fontsize=12, fontweight='bold', color='#003366', pad=12)

# Ideal reference lines
ax2.axvline(70, color='#0072CE', linestyle=':', linewidth=1.5, alpha=0.7)
ax2.axvline(80, color='#2E7D32', linestyle=':', linewidth=1.5, alpha=0.7)

ax2.set_xlim(0, 105)
ax2.grid(axis='x', linestyle='--', alpha=0.5)
ax2.legend(loc='lower right', frameon=True, fontsize=10, facecolor='white', edgecolor='#B0BEC5')

for i, row in sub_elite.iterrows():
    tr = row['Pct_Train']
    va = row['Pct_Val']
    te = row['Pct_Test']
    ax2.text(tr/2, i, f"{tr:.0f}%", va='center', ha='center', color='white', fontweight='bold', fontsize=9)
    if va >= 4:
        ax2.text(tr + va/2, i, f"{va:.0f}%", va='center', ha='center', color='white', fontweight='bold', fontsize=8)
    ax2.text(tr + va + te/2, i, f"{te:.0f}%", va='center', ha='center', color='white', fontweight='bold', fontsize=9)

plt.tight_layout()
fig2_path = 'analisis_noticias_tfm/distribucion_optimizada_70_10_20_en.png'
plt.savefig(fig2_path, bbox_inches='tight')
plt.close()
print(f'SUCCESS: saved {fig2_path}')
