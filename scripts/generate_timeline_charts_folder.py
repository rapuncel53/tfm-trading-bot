import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime
import os

os.makedirs('analisis_noticias_tfm', exist_ok=True)

# Load master coverage data
df = pd.read_csv('data/desglose_cobertura_noticias_todas_las_companias.csv')

# Select top 22 representative companies (covering Tier 1 leaders, Tier 2 historical, and Tier 2/3 big tech)
selected_tickers = [
    # Tier 1 Elite (Full continuous coverage)
    'ORCL', 'CAT', 'KO', 'NVDA', 'COST', 'V', 'EBAY', 'CRM', 'GILD', 'QCOM', 'ADBE', 'AMD', 'INTC', 'WMT',
    # Tier 2 Historical Benzinga
    'MRK', 'PFE', 'JNJ',
    # Tier 2 / 3 Big Tech (Late coverage / Gaps)
    'GOOG', 'AAPL', 'AMZN', 'MSFT', 'DIS'
]

sub_df = df[df['Ticker'].isin(selected_tickers)].copy()
# Sort by tier rank then total news
tier_priority = {
    'Tier 1: Cobertura Total Continua': 1,
    'Tier 2: Cobertura Parcial Histórica': 2,
    'Tier 2: Cobertura Parcial Tardía': 3,
    'Tier 3: Cobertura Mínima': 4
}
sub_df['tier_p'] = sub_df['Clasificacion_Tier'].map(tier_priority)
sub_df = sub_df.sort_values(by=['tier_p', 'Total_Noticias'], ascending=[True, False]).reset_index(drop=True)

# -------------------------------------------------------------
# FIGURE 1: TIMELINE GANTT CHART (Where news are located and source)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(15, 9.5), dpi=300, facecolor='#F8FAFC')
ax.set_facecolor('white')

# Background split zones (Escenario Optimizado A)
ax.axvspan(datetime(2011,1,1), datetime(2019,12,31), color='#E3F2FD', alpha=0.60, label='Train Optimizado (2011–2019, 69.1% Noticias)')
ax.axvspan(datetime(2020,1,1), datetime(2020,6,10), color='#E8F5E9', alpha=0.65, label='Val Optimizada (Ene–Jun 2020, 9.2% Noticias - COVID)')
ax.axvspan(datetime(2020,6,11), datetime(2021,8,16), color='#FFCDD2', alpha=0.75, label='Embargo / Cuarentena (14 meses sin noticias)')
ax.axvspan(datetime(2021,8,17), datetime(2023,12,31), color='#FFF3E0', alpha=0.60, label='Test Ciego (Ago 2021–Dic 2023, 21.8% Noticias)')

bz_color = '#0072CE'  # Blue for Benzinga
fn_color = '#E65100'  # Orange for FNSPID

y_labels = []
bz_labeled = False
fn_labeled = False

n_comp = len(sub_df)
for i, row in sub_df.iterrows():
    y = n_comp - 1 - i
    ticker = row['Ticker']
    tier_short = 'Tier 1' if 'Tier 1' in row['Clasificacion_Tier'] else ('Tier 2 (Hist)' if 'Histórica' in row['Clasificacion_Tier'] else ('Tier 2 (Tard)' if 'Tardía' in row['Clasificacion_Tier'] else 'Tier 3'))
    y_labels.append(f"{ticker:5s} [{tier_short}] - {row['Empresa'][:20]}")
    
    # Benzinga bar
    bz_s = str(row['Benzinga_Fecha_Inicio'])
    bz_e = str(row['Benzinga_Fecha_Fin'])
    if bz_s != 'Sin datos' and bz_e != 'Sin datos':
        d0 = datetime.strptime(bz_s[:10], '%Y-%m-%d')
        d1 = datetime.strptime(bz_e[:10], '%Y-%m-%d')
        lbl = 'Benzinga Analyst Alerts (2009–2020)' if not bz_labeled else None
        bz_labeled = True
        ax.barh(y + 0.16, (d1 - d0).days, left=d0, height=0.27, color=bz_color, alpha=0.92, label=lbl, edgecolor='#002B49', linewidth=0.6)
        
    # FNSPID bar
    fn_s = str(row['FNSPID_Fecha_Inicio'])
    fn_e = str(row['FNSPID_Fecha_Fin'])
    if fn_s != 'Sin datos' and fn_e != 'Sin datos':
        d0 = datetime.strptime(fn_s[:10], '%Y-%m-%d')
        d1 = datetime.strptime(fn_e[:10], '%Y-%m-%d')
        lbl = 'FNSPID NASDAQ News (2009–2023)' if not fn_labeled else None
        fn_labeled = True
        ax.barh(y - 0.16, (d1 - d0).days, left=d0, height=0.27, color=fn_color, alpha=0.90, label=lbl, edgecolor='#BF360C', linewidth=0.6)

ax.set_yticks(range(n_comp))
ax.set_yticklabels(list(reversed(y_labels)), fontsize=9, fontweight='bold', color='#263238')
ax.set_xlim(datetime(2009, 1, 1), datetime(2024, 5, 1))

ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.set_xlabel('Línea Temporal de Noticias (Años 2009 a 2023)', fontsize=11, fontweight='bold', color='#003366', labelpad=8)
ax.set_title('MAPA TEMPORAL DE NOTICIAS POR COMPAÑÍA: UBICACIÓN Y FUENTE (BENZINGA VS FNSPID)', fontsize=13, fontweight='bold', color='#003366', pad=14)

ax.grid(axis='x', linestyle='--', alpha=0.5)
ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.18), ncol=3, frameon=True, fontsize=9.5, facecolor='white', edgecolor='#B0BEC5')

# Visual separator between tiers
ax.axhline(7.5, color='#90A4AE', linestyle='--', linewidth=1.2)
ax.axhline(4.5, color='#90A4AE', linestyle='--', linewidth=1.2)

plt.tight_layout()
fig1_path = 'analisis_noticias_tfm/mapa_temporal_noticias_por_compania.png'
plt.savefig(fig1_path, bbox_inches='tight')
plt.close()
print(f'SUCCESS: saved {fig1_path}')

# -------------------------------------------------------------
# FIGURE 2: THE 12 ELITE COMPANIES 70 / 10 / 20 DISTRIBUTION
# -------------------------------------------------------------
elite_tickers = ['ORCL', 'CAT', 'KO', 'EBAY', 'V', 'COST', 'CRM', 'GILD', 'QCOM', 'BIIB', 'ADBE', 'NVDA']
edf = df[df['Ticker'].isin(elite_tickers)].copy()

# Calculate percentages in Scenario A (Train: 2011-2019, Val: Ene-Jun 2020, Test: Ago 2021-2023)
train_df = pd.read_parquet('data/splits/train/daily_aligned.parquet')
val_df = pd.read_parquet('data/splits/val/daily_aligned.parquet')
test_df = pd.read_parquet('data/splits/test/daily_aligned.parquet')

all_df = pd.concat([train_df[train_df['has_news']==True], val_df[val_df['has_news']==True], test_df[test_df['has_news']==True]], ignore_index=True)
all_df['date'] = pd.to_datetime(all_df['date'])

elite_stats = []
for t in elite_tickers:
    sub = all_df[all_df['ticker'] == t]
    tot = len(sub)
    tr = ((sub['date'] >= '2011-01-01') & (sub['date'] <= '2019-12-31')).sum()
    va = ((sub['date'] >= '2020-01-01') & (sub['date'] <= '2020-06-10')).sum()
    te = ((sub['date'] >= '2021-08-17') & (sub['date'] <= '2023-12-31')).sum()
    elite_stats.append({
        'Ticker': t,
        'Total': tot,
        'Train_pct': tr / tot * 100,
        'Val_pct': va / tot * 100,
        'Test_pct': te / tot * 100
    })

ed_df = pd.DataFrame(elite_stats).sort_values(by='Train_pct', ascending=True)

fig2, ax2 = plt.subplots(figsize=(12, 7.5), dpi=300, facecolor='#F8FAFC')
ax2.set_facecolor('white')

y_pos2 = np.arange(len(ed_df))
h2 = 0.62

ax2.barh(y_pos2, ed_df['Train_pct'], height=h2, color='#0072CE', label='Train (2011–2019) ~70%', alpha=0.95)
ax2.barh(y_pos2, ed_df['Val_pct'], height=h2, left=ed_df['Train_pct'], color='#2E7D32', label='Val (Ene–Jun 2020) ~10%', alpha=0.90)
ax2.barh(y_pos2, ed_df['Test_pct'], height=h2, left=ed_df['Train_pct'] + ed_df['Val_pct'], color='#E65100', label='Test Ciego (Ago 2021–Dic 2023) ~20%', alpha=0.90)

ax2.set_yticks(y_pos2)
ax2.set_yticklabels(ed_df['Ticker'], fontsize=11, fontweight='bold', color='#263238')
ax2.set_xlabel('Porcentaje del Total de Noticias por Empresa (%)', fontsize=11, fontweight='bold', color='#003366', labelpad=8)
ax2.set_title('SELECCIÓN DE COMPAÑÍAS DE ÉLITE QUE CUMPLEN LA DISTRIBUCIÓN DESEADA (~70 / 10 / 20)', fontsize=12, fontweight='bold', color='#003366', pad=12)

# Ideal reference lines
ax2.axvline(70, color='#0072CE', linestyle=':', linewidth=1.5, alpha=0.7)
ax2.axvline(80, color='#2E7D32', linestyle=':', linewidth=1.5, alpha=0.7)

ax2.set_xlim(0, 105)
ax2.grid(axis='x', linestyle='--', alpha=0.5)
ax2.legend(loc='lower right', frameon=True, fontsize=10, facecolor='white', edgecolor='#B0BEC5')

for i, row in ed_df.reset_index(drop=True).iterrows():
    ax2.text(row['Train_pct']/2, i, f"{row['Train_pct']:.0f}%", va='center', ha='center', color='white', fontweight='bold', fontsize=9)
    if row['Val_pct'] >= 5:
        ax2.text(row['Train_pct'] + row['Val_pct']/2, i, f"{row['Val_pct']:.0f}%", va='center', ha='center', color='white', fontweight='bold', fontsize=8)
    ax2.text(row['Train_pct'] + row['Val_pct'] + row['Test_pct']/2, i, f"{row['Test_pct']:.0f}%", va='center', ha='center', color='white', fontweight='bold', fontsize=9)

plt.tight_layout()
fig2_path = 'analisis_noticias_tfm/distribucion_optimizada_70_10_20.png'
plt.savefig(fig2_path, bbox_inches='tight')
plt.close()
print(f'SUCCESS: saved {fig2_path}')
