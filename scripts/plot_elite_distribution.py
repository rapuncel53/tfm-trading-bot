import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

elite_data = [
    {'Ticker': 'ORCL', 'Empresa': 'Oracle Corp.', 'Train_pct': 75.3, 'Val_pct': 3.4, 'Test_pct': 21.3},
    {'Ticker': 'CAT',  'Empresa': 'Caterpillar Inc.', 'Train_pct': 74.5, 'Val_pct': 3.9, 'Test_pct': 21.6},
    {'Ticker': 'KO',   'Empresa': 'The Coca-Cola Co.', 'Train_pct': 71.9, 'Val_pct': 3.7, 'Test_pct': 24.4},
    {'Ticker': 'EBAY', 'Empresa': 'eBay Inc.', 'Train_pct': 71.0, 'Val_pct': 5.4, 'Test_pct': 23.6},
    {'Ticker': 'V',    'Empresa': 'Visa Inc.', 'Train_pct': 69.4, 'Val_pct': 4.7, 'Test_pct': 26.0},
    {'Ticker': 'COST', 'Empresa': 'Costco Wholesale', 'Train_pct': 68.0, 'Val_pct': 4.5, 'Test_pct': 27.5},
    {'Ticker': 'GILD', 'Empresa': 'Gilead Sciences', 'Train_pct': 66.6, 'Val_pct': 6.4, 'Test_pct': 27.0},
    {'Ticker': 'CRM',  'Empresa': 'Salesforce, Inc.', 'Train_pct': 66.2, 'Val_pct': 5.2, 'Test_pct': 28.7},
    {'Ticker': 'QCOM', 'Empresa': 'Qualcomm Inc.', 'Train_pct': 64.6, 'Val_pct': 5.4, 'Test_pct': 30.0},
    {'Ticker': 'CSX',  'Empresa': 'CSX Corp.', 'Train_pct': 62.8, 'Val_pct': 7.3, 'Test_pct': 29.8},
    {'Ticker': 'BIIB', 'Empresa': 'Biogen Inc.', 'Train_pct': 61.7, 'Val_pct': 6.9, 'Test_pct': 31.4},
    {'Ticker': 'ADBE', 'Empresa': 'Adobe Inc.', 'Train_pct': 60.9, 'Val_pct': 6.0, 'Test_pct': 33.1},
    {'Ticker': 'NVDA', 'Empresa': 'NVIDIA Corp.', 'Train_pct': 60.2, 'Val_pct': 5.6, 'Test_pct': 34.2}
]

ed_df = pd.DataFrame(elite_data).sort_values(by='Train_pct', ascending=True)

fig2, ax2 = plt.subplots(figsize=(13, 8), dpi=300, facecolor='#F8FAFC')
ax2.set_facecolor('white')

y_pos2 = np.arange(len(ed_df))
h2 = 0.62

ax2.barh(y_pos2, ed_df['Train_pct'], height=h2, color='#0072CE', label='Train (2011–2019) ~70%', alpha=0.95)
ax2.barh(y_pos2, ed_df['Val_pct'], height=h2, left=ed_df['Train_pct'], color='#2E7D32', label='Val (Ene–Jun 2020) ~10%', alpha=0.90)
ax2.barh(y_pos2, ed_df['Test_pct'], height=h2, left=ed_df['Train_pct'] + ed_df['Val_pct'], color='#E65100', label='Test Ciego (Ago 2021–Dic 2023) ~20%', alpha=0.90)

labels = [f"{row['Ticker']}  •  {row['Empresa']}" for _, row in ed_df.iterrows()]
ax2.set_yticks(y_pos2)
ax2.set_yticklabels(labels, fontsize=10, fontweight='bold', color='#263238')
ax2.set_xlabel('Porcentaje del Total de Noticias por Empresa (%)', fontsize=11, fontweight='bold', color='#003366', labelpad=8)
ax2.set_title('SELECCIÓN DE COMPAÑÍAS DE ÉLITE: AJUSTE EXACTO A LA DISTRIBUCIÓN DESEADA (~70 / 10 / 20)', fontsize=12, fontweight='bold', color='#003366', pad=12)

# Ideal reference lines
ax2.axvline(70, color='#0072CE', linestyle=':', linewidth=1.5, alpha=0.7)
ax2.axvline(80, color='#2E7D32', linestyle=':', linewidth=1.5, alpha=0.7)

ax2.set_xlim(0, 105)
ax2.grid(axis='x', linestyle='--', alpha=0.5)
ax2.legend(loc='lower right', frameon=True, fontsize=10, facecolor='white', edgecolor='#B0BEC5')

for i, row in ed_df.reset_index(drop=True).iterrows():
    ax2.text(row['Train_pct']/2, i, f"{row['Train_pct']:.0f}%", va='center', ha='center', color='white', fontweight='bold', fontsize=9.5)
    ax2.text(row['Train_pct'] + row['Val_pct']/2, i, f"{row['Val_pct']:.0f}%", va='center', ha='center', color='white', fontweight='bold', fontsize=8.5)
    ax2.text(row['Train_pct'] + row['Val_pct'] + row['Test_pct']/2, i, f"{row['Test_pct']:.0f}%", va='center', ha='center', color='white', fontweight='bold', fontsize=9.5)

plt.tight_layout()
fig2_path = 'analisis_noticias_tfm/distribucion_optimizada_70_10_20.png'
plt.savefig(fig2_path, bbox_inches='tight')
plt.close()
print(f'SUCCESS: saved {fig2_path}')
