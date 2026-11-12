import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

companies = [
    # Tier 1: Cobertura Total Continua (2011 a 2023)
    {'ticker': 'ORCL', 'tier': 'Tier 1 (Total)',   'bz_start': '2011-01-25', 'bz_end': '2020-06-11', 'fn_start': '2009-11-22', 'fn_end': '2023-12-16'},
    {'ticker': 'CAT',  'tier': 'Tier 1 (Total)',   'bz_start': '2011-08-23', 'bz_end': '2020-06-08', 'fn_start': '2009-11-04', 'fn_end': '2023-12-16'},
    {'ticker': 'QCOM', 'tier': 'Tier 1 (Total)',   'bz_start': '2011-11-03', 'bz_end': '2020-06-08', 'fn_start': '2010-02-01', 'fn_end': '2023-12-16'},
    {'ticker': 'NVDA', 'tier': 'Tier 1 (Total)',   'bz_start': '2011-03-03', 'bz_end': '2020-06-10', 'fn_start': '2021-08-17', 'fn_end': '2023-12-16'},
    {'ticker': 'ADBE', 'tier': 'Tier 1 (Total)',   'bz_start': '2011-03-22', 'bz_end': '2020-06-10', 'fn_start': '2010-03-10', 'fn_end': '2023-12-16'},
    {'ticker': 'AMD',  'tier': 'Tier 1 (Total)',   'bz_start': '2011-04-14', 'bz_end': '2020-06-10', 'fn_start': '2012-05-15', 'fn_end': '2023-12-16'},
    # Tier 2: Cobertura Parcial / Concentrada
    {'ticker': 'MRK',  'tier': 'Tier 2 (Histórica)','bz_start': '2009-07-27', 'bz_end': '2020-06-11', 'fn_start': '2009-11-04', 'fn_end': '2020-06-11'},
    {'ticker': 'GOOG', 'tier': 'Tier 2 (Tardía)',  'bz_start': '2018-11-13', 'bz_end': '2020-06-10', 'fn_start': '2023-01-10', 'fn_end': '2023-12-16'},
    {'ticker': 'AAPL', 'tier': 'Tier 2 (Tardía)',  'bz_start': '2020-03-09', 'bz_end': '2020-06-10', 'fn_start': '2022-06-03', 'fn_end': '2023-12-16'},
    {'ticker': 'AMZN', 'tier': 'Tier 2 (Tardía)',  'bz_start': '2020-04-27', 'bz_end': '2020-06-10', 'fn_start': '2023-03-09', 'fn_end': '2023-12-16'},
    # Tier 3: Cobertura Mínima
    {'ticker': 'MSFT', 'tier': 'Tier 3 (Mínima)',  'bz_start': None,         'bz_end': None,         'fn_start': '2022-04-26', 'fn_end': '2023-12-16'},
    {'ticker': 'AEP',  'tier': 'Tier 3 (Silenciosa)', 'bz_start': None,      'bz_end': None,         'fn_start': None,         'fn_end': None}
]

fig, ax = plt.subplots(figsize=(13.5, 7.2), dpi=300)

y_positions = range(len(companies))
tickers = [c['ticker'] + "  [" + c['tier'] + "]" for c in companies]

# Background split zones
ax.axvspan(datetime(2011,1,1), datetime(2018,12,31), color='#E3F2FD', alpha=0.55, label='Split Train (2011-2018)')
ax.axvspan(datetime(2019,1,1), datetime(2020,6,10), color='#E8F5E9', alpha=0.55, label='Split Val (2019-Jun 2020)')
ax.axvspan(datetime(2020,6,11), datetime(2021,8,16), color='#FFCDD2', alpha=0.75, label='Embargo / Cuarentena (14 meses sin noticias)')
ax.axvspan(datetime(2021,8,17), datetime(2023,12,31), color='#FFF3E0', alpha=0.55, label='Split Test Ciego (Ago 2021-Dic 2023)')

# Colors
bz_color = '#0072CE'  # Blue for Benzinga
fn_color = '#E65100'  # Orange for FNSPID

bz_labeled = False
fn_labeled = False

for i, c in enumerate(companies):
    y = len(companies) - 1 - i
    # Benzinga bar
    if c['bz_start'] and c['bz_end']:
        d0 = datetime.strptime(c['bz_start'], '%Y-%m-%d')
        d1 = datetime.strptime(c['bz_end'], '%Y-%m-%d')
        lbl = 'Benzinga Analyst Alerts (2009-2020)' if not bz_labeled else None
        bz_labeled = True
        ax.barh(y + 0.16, (d1 - d0).days, left=d0, height=0.26, color=bz_color, alpha=0.9, label=lbl, edgecolor='#003366', linewidth=0.8)
    
    # FNSPID bar
    if c['fn_start'] and c['fn_end']:
        d0 = datetime.strptime(c['fn_start'], '%Y-%m-%d')
        d1 = datetime.strptime(c['fn_end'], '%Y-%m-%d')
        lbl = 'FNSPID NASDAQ News (2009-2023)' if not fn_labeled else None
        fn_labeled = True
        ax.barh(y - 0.16, (d1 - d0).days, left=d0, height=0.26, color=fn_color, alpha=0.9, label=lbl, edgecolor='#BF360C', linewidth=0.8)

ax.set_yticks(range(len(companies)))
ax.set_yticklabels(list(reversed(tickers)), fontsize=9.5, fontweight='bold')
ax.set_xlim(datetime(2009, 1, 1), datetime(2024, 6, 1))

ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.set_xlabel('Línea Temporal (Años)', fontsize=11, fontweight='bold', labelpad=8)
ax.set_title('Mapa de Cobertura Temporal de Noticias por Empresa (Benzinga vs FNSPID)', fontsize=13, fontweight='bold', pad=14)

ax.grid(axis='x', linestyle='--', alpha=0.6)
ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.22), ncol=3, frameon=True, fontsize=9.5)

# Tier separators
ax.axhline(5.5, color='gray', linestyle=':', linewidth=1.2)
ax.axhline(1.5, color='gray', linestyle=':', linewidth=1.2)

plt.tight_layout()
out_plot = 'data/grafico_cobertura_temporal_companias.png'
plt.savefig(out_plot, bbox_inches='tight')
print('SUCCESS: saved plot to', out_plot)
