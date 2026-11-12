# Benzinga Stock News Analysis (`benzinga_stock_analysis`)

## 1. Overview
This module provides an independent analysis tool focused exclusively on the **Benzinga News Feed** dataset (`data/benzinga/raw_analyst_ratings.jsonl`).

It maps news coverage, timeline boundaries, and news temporal distribution across **6,204 unique stock tickers** (including 381 S&P 500 constituents) and over **1,395,000 deduplicated articles** from February 2009 to June 2020.

---

## 2. Deliverables & Output Files

| File | Format | Description |
| :--- | :---: | :--- |
| [`analyze_benzinga_stocks.py`](file:///c:/Users/julia/tfm/benzinga_stock_analysis/analyze_benzinga_stocks.py) | Python | Fast streaming engine that ingests, deduplicates, and analyzes Benzinga news. |
| [`benzinga_stock_analysis.xlsx`](file:///c:/Users/julia/tfm/benzinga_stock_analysis/benzinga_stock_analysis.xlsx) | Excel | Formatted multi-tab workbook with auto-fit columns, freeze panes, and color styling. |
| [`benzinga_stock_analysis.csv`](file:///c:/Users/julia/tfm/benzinga_stock_analysis/benzinga_stock_analysis.csv) | CSV | Complete dataset containing all 6,204 analyzed tickers. |
| [`benzinga_sp500_stocks.csv`](file:///c:/Users/julia/tfm/benzinga_stock_analysis/benzinga_sp500_stocks.csv) | CSV | Filtered dataset focused on the S&P 500 investable universe (381 tickers). |

### Excel Sheets Structure (`benzinga_stock_analysis.xlsx`):
1. **`SP500_Stocks`**: 381 S&P 500 constituents sorted by total news volume.
2. **`All_Benzinga_Stocks`**: All 6,204 unique tickers found across the Benzinga corpus.
3. **`Sector_Summary`**: Aggregated macro metrics by GICS Sector (total stocks, news volume, average news/stock, and average hiatus length).

---

## 3. Metric Definitions & Distribution Measures

To solve the specific problem of detecting uneven news flow across time (e.g., a stock having articles in 2009, zero news in 2011, and resuming in 2012), the script computes:

### A. Core Identification & Boundaries
- **`ticker`**: Stock symbol.
- **`company_name`**: Official corporate name verified against SEC EDGAR database.
- **`sector`**: GICS sector (e.g., *Information Technology, Health Care, Industrials*).
- **`in_sp500_universe`**: Whether the company is an S&P 500 constituent (`Yes` / `No`).
- **`first_news_date`**: Exact date of the earliest recorded news item (`YYYY-MM-DD`).
- **`last_news_date`**: Exact date of the most recent recorded news item (`YYYY-MM-DD`).
- **`total_news`**: Total number of deduplicated news articles mapped to this ticker.

### B. News Distribution & Gap Detection Metrics
- **`span_days` & `span_years`**: Total calendar duration between the first and last news date.
- **`active_days_count`**: Number of distinct trading/calendar days with at least one news item.
- **`calendar_span_years`**: Total number of calendar years encompassing `[first_year, last_year]` ($y_{\text{last}} - y_{\text{first}} + 1$).
- **`active_years_count`**: Number of calendar years in which the stock had $\ge 1$ news article.
- **`missing_years_count`**: Number of calendar years with **0 news** between the first and last year.
- **`missing_years_list`**: Explicit list of silent years (e.g., `"2011"` or `"2018"`).
- **`max_gap_days`**: The largest number of consecutive days without any news article.
- **`max_gap_years`**: `max_gap_days / 365.25`.
- **`continuity_pct`**: Continuity ratio percentage ($\frac{\text{active\_years}}{\text{calendar\_span\_years}} \times 100\%$). A value of $100\%$ indicates continuous year-by-year reporting.
- **`distribution_profile`**: Qualitative classification:
  - `Continuous (Dense across span)`: Continuous news with no missing years and max gap $< 180$ days.
  - `Multi-Year Hiatus`: Identifies multi-year interruptions (missing $\ge 1$ year or gap $\ge 365$ days).
  - `Late Entry Window (2018-2020)`: News started late in the Benzinga dataset.
  - `Historical Window Only (2009-2014)`: News ceased prior to 2015.
  - `Intermittent / Sporadic Flow`: Sparse reporting ($< 3$ active years or low count).

### C. Year-by-Year News Count Columns
Every ticker contains explicit news count columns for each year from **2009 to 2020**:
`news_2009`, `news_2010`, `news_2011`, `news_2012`, `news_2013`, `news_2014`, `news_2015`, `news_2016`, `news_2017`, `news_2018`, `news_2019`, `news_2020`.

This allows instant visual inspection, pivot tables, or conditional formatting in Excel.

---

## 4. Execution Instructions

To re-run the analysis from the workspace root or from within this directory:

```powershell
# Using the workspace virtual environment:
.venv\Scripts\python.exe benzinga_stock_analysis/analyze_benzinga_stocks.py

# Or directly if inside the folder:
cd benzinga_stock_analysis
..\.venv\Scripts\python.exe analyze_benzinga_stocks.py
```

The script runs in approximately **20 seconds** to stream 1.4M records, compute distribution metrics across all 6,204 stocks, and update both CSVs and the styled Excel workbook.
