# Financial News Coverage Heatmaps (`news_coverage_heatmaps`)

## 1. Overview
This module provides a unified, publication-quality heatmap generation engine that visualizes historical news distribution across all available calendar years for the **FNSPID** (2009–2023, 15 years) and **Benzinga** (2009–2020, 12 years) financial news datasets.

### Key Enhancement: 100% S&P 500 Stock Coverage
Unlike truncated or sampled plots, this system guarantees that **every single stock** in the S&P 500 universe (all 343 for FNSPID, all 381 for Benzinga) is accounted for and rendered:
1. **Consecutive Paginated Heatmaps (50 stocks/page):**
   - Every single stock is clearly displayed with its ranking, ticker, company name, total news volume, active years, and continuity percentage.
   - Exact news counts are annotated inside each cell with high-contrast dynamic text (white on dark cells, dark navy on light cells, and grey dashes `'-'` for silent years).
2. **Complete S&P 500 Macro Master Panorama:**
   - Single high-resolution continuous canvas ($17 \times 98$ inches for FNSPID, $17 \times 108$ inches for Benzinga) with **all 343 / 381 stocks rendered with individual, explicit tick labels on the y-axis (zero skipped ticks)**.
3. **Specialized Analytical Focus Heatmaps:**
   - Full timeline continuity (stocks active in 100% of tracked years).
   - Multi-year reporting hiatuses (stocks with missing intermediate calendar years or silences $\ge 365$ days).
   - Sparse coverage / late entrants (stocks with $\le 4$ active years).
4. **Full Market Universe Overview:**
   - High-resolution macro heatmap of the top 500 stocks across the broader market universe (3,954 stocks in FNSPID, 6,204 stocks in Benzinga).

---

## 2. Directory Structure

```
news_coverage_heatmaps/
├── generate_news_heatmaps.py          # Unified Python script generating heatmaps for any dataset
├── README.md                          # Methodology and visualization documentation
├── fnspid_heatmaps/                   # Heatmaps generated from fnspid_stock_analysis.xlsx (2009–2023)
│   ├── 00_complete_sp500_master_heatmap_all_343_stocks.png
│   ├── 01_page_01_rank_001_to_050_best_distributed.png
│   ├── 01_page_02_rank_051_to_100_coverage_group_2.png
│   ├── 01_page_03_rank_101_to_150_coverage_group_3.png
│   ├── 01_page_04_rank_151_to_200_coverage_group_4.png
│   ├── 01_page_05_rank_201_to_250_coverage_group_5.png
│   ├── 01_page_06_rank_251_to_300_coverage_group_6.png
│   ├── 01_page_07_rank_301_to_343_fewest_active_years.png
│   ├── 02_focus_stocks_with_all_15_years_active.png
│   ├── 03_focus_stocks_with_multi_year_gaps.png
│   ├── 04_focus_stocks_with_fewest_years_recent_or_sparse.png
│   └── 05_full_universe_top500_macro_heatmap.png
└── benzinga_heatmaps/                 # Heatmaps generated from benzinga_stock_analysis.xlsx (2009–2020)
    ├── 00_complete_sp500_master_heatmap_all_381_stocks.png
    ├── 01_page_01_rank_001_to_050_best_distributed.png
    ├── 01_page_02_rank_051_to_100_best_distributed.png
    ├── 01_page_03_rank_101_to_150_best_distributed.png
    ├── 01_page_04_rank_151_to_200_best_distributed.png
    ├── 01_page_05_rank_201_to_250_best_and_continuous.png
    ├── 01_page_06_rank_251_to_300_coverage_group_6.png
    ├── 01_page_07_rank_301_to_350_coverage_group_7.png
    ├── 01_page_08_rank_351_to_381_fewest_active_years.png
    ├── 02_focus_stocks_with_all_12_years_active_overview.png
    ├── 03_focus_stocks_with_multi_year_gaps.png
    ├── 04_focus_stocks_with_fewest_years_recent_or_sparse.png
    └── 05_full_universe_top500_macro_heatmap.png
```

---

## 3. Standardized Visual System & Color Scale

To ensure direct visual equivalence between FNSPID and Benzinga, all heatmaps enforce an **identical logarithmic color scale**:

| Value Range | Color Appearance | Visual Meaning |
| :--- | :--- | :--- |
| **0 News Articles** | **Neutral Light Grey (`#ECEFF1`)** | **Reporting Hiatus / Silence** (Immediate visual indicator of missing years) |
| **1 – 10 Articles** | Light Yellow-Green | Low / sporadic coverage |
| **10 – 100 Articles** | Emerald Green / Teal | Moderate reporting |
| **100 – 500 Articles** | Ocean Blue | Established corporate coverage |
| **500 – 2,000 Articles** | Deep Cobalt Blue | Dense institutional reporting |
| **2,000 – 6,000+ Articles** | Midnight Navy Blue | High-frequency Wall Street newsflow |

* **Colormap:** Matplotlib `YlGnBu` (Yellow-Green-Blue) with `cmap.set_bad('#ECEFF1')`.
* **Normalization:** Logarithmic scaling `mcolors.LogNorm(vmin=1, vmax=6000)`.
* **Text Contrast:** Dynamic luminance switching (white font on dark cells $\ge 800$ news, navy `#1A237E` font on lighter cells $< 800$, and grey dash `'-'` on zero cells).

---

## 4. Sorting and Ranking Methodology

All heatmaps sort stocks hierarchically:
1. `active_years_count` (Descending): Stocks present across all calendar years appear first.
2. `continuity_pct` (Descending): Highest percentage of non-silent years within active span.
3. `missing_years_count` (Ascending): Zero missing intermediate years prioritized over gapped stocks.
4. `total_news` (Descending): Highest cumulative volume breaks ties within each tier.

This guarantees that:
- **Rank 1 to 50** contains the absolute highest-quality, dense continuous stocks (e.g., `KO`, `CRM`, `CAT`, `ADBE`, `ORCL` in FNSPID; `MRK`, `GILD`, `DAL`, `KO`, `FDX` in Benzinga).
- **Final Pages** systematically group late-entering IPOs or sparse single-year assets (e.g., `LIN`, `BBY`, `GM`, `HPQ`, `JPM` in FNSPID; `JPM`, `SCHW`, `T`, `V`, `WMT` in Benzinga).

---

## 5. Execution Instructions

The script can be executed from the command line:

```powershell
# Generate heatmaps for BOTH datasets (all pages + macros):
python news_coverage_heatmaps/generate_news_heatmaps.py

# Custom page size (e.g. 60 stocks per page):
python news_coverage_heatmaps/generate_news_heatmaps.py --page-size 60

# Generate only FNSPID heatmaps:
python news_coverage_heatmaps/generate_news_heatmaps.py --dataset fnspid

# Generate only Benzinga heatmaps:
python news_coverage_heatmaps/generate_news_heatmaps.py --dataset benzinga
```
