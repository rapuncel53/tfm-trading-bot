"""Benzinga Stock News Analysis Script.

Analyzes the Benzinga News Feed dataset exclusively (data/benzinga/raw_analyst_ratings.jsonl).
For each stock ticker, extracts and calculates:
  1. Core Identity: Ticker symbol, official company name (SEC EDGAR), and GICS sector.
  2. News Timeline: First news date, last news date, and total number of unique news items.
  3. News Distribution & Gap Metrics:
     - Total span in calendar days and years.
     - Distinct calendar days with news.
     - Active years count vs. total calendar span years.
     - Missing calendar years (e.g., news in 2009, none in 2010, resuming in 2011).
     - Maximum gap between consecutive news articles (in days and years).
     - Continuity ratio percentage (active years / calendar span years * 100%).
     - Categorical distribution profile (Continuous, Multi-Year Hiatus, Late Entry, etc.).
     - Year-by-year news breakdown (2009 through 2020).

Outputs:
  - benzinga_stock_analysis/benzinga_stock_analysis.xlsx (Multi-tab formatted Excel)
  - benzinga_stock_analysis/benzinga_stock_analysis.csv  (Complete universe CSV)
  - benzinga_stock_analysis/benzinga_sp500_stocks.csv   (S&P 500 universe CSV)
"""

import os
import sys
import json
import csv
import io
import time
import datetime
from collections import defaultdict

# Add potential Python site-packages directories for openpyxl fallback
for p in [
    r"C:\Users\julia\anaconda3\Lib\site-packages",
    r"C:\Users\julia\AppData\Roaming\Python\Python311\site-packages",
]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

import pandas as pd
import numpy as np

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

csv.field_size_limit(10**9)

# Resolve workspace directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..")) if os.path.basename(SCRIPT_DIR) == "benzinga_stock_analysis" else os.path.abspath(".")
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = SCRIPT_DIR if os.path.basename(SCRIPT_DIR) == "benzinga_stock_analysis" else os.path.join(BASE_DIR, "benzinga_stock_analysis")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUT_EXCEL = os.path.join(OUTPUT_DIR, "benzinga_stock_analysis.xlsx")
OUT_CSV_ALL = os.path.join(OUTPUT_DIR, "benzinga_stock_analysis.csv")
OUT_CSV_SP500 = os.path.join(OUTPUT_DIR, "benzinga_sp500_stocks.csv")

BENZINGA_FILE = os.path.join(DATA_DIR, "benzinga", "raw_analyst_ratings.jsonl")

# Standard years tracked for the yearly distribution breakdown (Benzinga: 2009-2020)
YEARS_TRACKED = list(range(2009, 2021))  # 2009 through 2020


def load_metadata():
    """Load official SEC company names, S&P 500 constituents, and GICS sectors."""
    print("\n[Step 1/4] Loading company metadata (SEC EDGAR & S&P 500)...")
    sec_names = {}
    sp500_sectors = {}
    sp500_set = set()

    # 1. Official SEC company names
    sec_file = os.path.join(DATA_DIR, "sec_tickers.json")
    if os.path.exists(sec_file):
        try:
            with open(sec_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                items = data.values() if isinstance(data, dict) else data
                for item in items:
                    sym = str(item.get("ticker", "")).strip().upper()
                    title = str(item.get("title", "")).strip()
                    if sym and title:
                        sec_names[sym] = title
            print(f"  -> SEC EDGAR: Loaded {len(sec_names):,} official company names.")
        except Exception as e:
            print(f"  -> Warning loading {sec_file}: {e}")

    # 2. S&P 500 constituents and GICS sectors
    sp_file = os.path.join(DATA_DIR, "sp500_constituents.json")
    if os.path.exists(sp_file):
        try:
            with open(sp_file, "r", encoding="utf-8") as f:
                sp_data = json.load(f)
                for item in sp_data:
                    sym = str(item.get("Symbol_std") or item.get("Symbol", "")).strip().upper()
                    sec = str(item.get("GICS Sector", "")).strip()
                    name = str(item.get("Security", "")).strip()
                    if sym:
                        sp500_set.add(sym)
                        if sec:
                            sp500_sectors[sym] = sec
                        if name and sym not in sec_names:
                            sec_names[sym] = name
            print(f"  -> S&P 500: Loaded {len(sp500_set):,} constituents and sectors.")
        except Exception as e:
            print(f"  -> Warning loading {sp_file}: {e}")

    # 3. Supplemental company catalog
    cat_file = os.path.join(DATA_DIR, "catalog", "companies_catalog.json")
    if os.path.exists(cat_file):
        try:
            with open(cat_file, "r", encoding="utf-8") as f:
                cat_data = json.load(f)
                for item in cat_data:
                    sym = str(item.get("sym", "")).strip().upper()
                    if sym:
                        sp500_set.add(sym)
                        if item.get("name") and sym not in sec_names:
                            sec_names[sym] = str(item.get("name")).strip()
                        if item.get("sector") and sym not in sp500_sectors:
                            sp500_sectors[sym] = str(item.get("sector")).strip()
        except Exception as e:
            print(f"  -> Warning loading {cat_file}: {e}")

    # 4. Fallback from censo_global_tickers.csv
    censo_file = os.path.join(DATA_DIR, "censo_global_tickers.csv")
    if os.path.exists(censo_file):
        try:
            df_censo = pd.read_csv(censo_file)
            for _, r in df_censo.iterrows():
                sym = str(r.get("sym", "")).strip().upper()
                if sym:
                    if pd.notna(r.get("sec_name")) and sym not in sec_names:
                        sec_names[sym] = str(r.get("sec_name")).strip()
                    if pd.notna(r.get("sp500_sector")) and sym not in sp500_sectors:
                        sp500_sectors[sym] = str(r.get("sp500_sector")).strip()
        except Exception:
            pass

    return sec_names, sp500_sectors, sp500_set


def load_benzinga_dataset():
    """Stream and deduplicate all news records from the Benzinga JSONL file."""
    print("\n[Step 2/4] Ingesting and deduplicating Benzinga news feed...")
    t0 = time.time()

    if not os.path.exists(BENZINGA_FILE):
        raise FileNotFoundError(f"Benzinga news file not found: {BENZINGA_FILE}")

    seen_articles = set()
    ticker_dates = defaultdict(list)
    ticker_news_count = defaultdict(int)

    total_lines = 0
    with open(BENZINGA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            total_lines += 1
            if total_lines % 350000 == 0:
                print(f"  -> Processed {total_lines:,} lines ({len(seen_articles):,} unique news)...")
            if not line.startswith("{"):
                continue
            try:
                item = json.loads(line)
                stk = item.get("stock")
                raw_d = str(item.get("date", ""))[:10]
                headline = str(item.get("headline", ""))[:60].strip()

                if stk and len(raw_d) == 10 and raw_d[:4].isdigit():
                    sym = stk.strip().upper()
                    dedup_key = (sym, raw_d, headline)
                    if dedup_key not in seen_articles:
                        seen_articles.add(dedup_key)
                        try:
                            d_obj = datetime.date(int(raw_d[:4]), int(raw_d[5:7]), int(raw_d[8:10]))
                            ticker_dates[sym].append(d_obj)
                            ticker_news_count[sym] += 1
                        except ValueError:
                            continue
            except Exception:
                continue

    elapsed = time.time() - t0
    total_unique_news = sum(ticker_news_count.values())
    print(f"  -> Ingestion complete in {elapsed:.2f}s: {total_unique_news:,} deduplicated news across {len(ticker_dates):,} tickers (from {total_lines:,} raw lines).")
    return ticker_dates, ticker_news_count


def compute_stock_metrics(ticker_dates, ticker_news_count, sec_names, sp500_sectors, sp500_set):
    """Compute distribution measures, temporal gaps, and year-by-year counts for each stock."""
    print("\n[Step 3/4] Computing distribution metrics, temporal gaps, and coverage...")

    all_tickers = sorted(list(ticker_dates.keys()))
    results = []

    for sym in all_tickers:
        dates_list = ticker_dates.get(sym, [])
        if not dates_list:
            continue

        company_name = sec_names.get(sym, f"{sym} Corporation")
        sector = sp500_sectors.get(sym, "Unclassified / Other")
        is_sp500 = "Yes" if sym in sp500_set else "No"

        unique_dates = sorted(list(set(dates_list)))
        first_date = unique_dates[0]
        last_date = unique_dates[-1]
        total_news = len(dates_list)
        active_days = len(unique_dates)

        span_days = (last_date - first_date).days
        span_years = round(span_days / 365.25, 2)
        cal_span_years = (last_date.year - first_date.year) + 1

        # Count news per year
        year_counts = defaultdict(int)
        for d in dates_list:
            year_counts[d.year] += 1

        active_years = sorted([y for y, c in year_counts.items() if c > 0])
        active_years_cnt = len(active_years)

        # Years between first_date.year and last_date.year with zero news
        full_year_range = list(range(first_date.year, last_date.year + 1))
        missing_years = [y for y in full_year_range if year_counts[y] == 0]
        missing_years_cnt = len(missing_years)
        missing_years_str = ", ".join(map(str, missing_years)) if missing_years else "None"
        active_years_str = ", ".join(map(str, active_years))

        # Maximum gap in days between consecutive news
        if len(unique_dates) > 1:
            gaps = [(unique_dates[i + 1] - unique_dates[i]).days for i in range(len(unique_dates) - 1)]
            max_gap_days = max(gaps)
        else:
            max_gap_days = 0
        max_gap_years = round(max_gap_days / 365.25, 2)

        # Continuity percentage
        continuity_pct = round((active_years_cnt / cal_span_years) * 100, 1) if cal_span_years > 0 else 100.0

        # Qualitative distribution profile
        if missing_years_cnt == 0 and max_gap_days < 180 and cal_span_years >= 3:
            profile = "Continuous (Dense across span)"
        elif missing_years_cnt > 0 or max_gap_days >= 365:
            profile = f"Multi-Year Hiatus (Max gap {max_gap_days}d / {missing_years_cnt} missing yrs)"
        elif first_date.year >= 2018:
            profile = "Late Entry Window (2018-2020)"
        elif last_date.year <= 2014:
            profile = "Historical Window Only (2009-2014)"
        else:
            profile = "Intermittent / Sporadic Flow"

        row = {
            "ticker": sym,
            "company_name": company_name,
            "sector": sector,
            "in_sp500_universe": is_sp500,
            "first_news_date": first_date.strftime("%Y-%m-%d"),
            "last_news_date": last_date.strftime("%Y-%m-%d"),
            "total_news": total_news,
            "span_days": span_days,
            "span_years": span_years,
            "active_years_count": active_years_cnt,
            "calendar_span_years": cal_span_years,
            "missing_years_count": missing_years_cnt,
            "missing_years_list": missing_years_str,
            "max_gap_days": max_gap_days,
            "max_gap_years": max_gap_years,
            "continuity_pct": continuity_pct,
            "active_days_count": active_days,
            "active_years_list": active_years_str,
            "distribution_profile": profile,
            "data_source": "Benzinga News Feed",
        }

        # Add year breakdown columns (2009 to 2020)
        for yr in YEARS_TRACKED:
            row[f"news_{yr}"] = year_counts.get(yr, 0)

        results.append(row)

    df_out = pd.DataFrame(results)

    # Sort primarily: S&P 500 first, then by total news descending
    df_out["sp_rank"] = df_out["in_sp500_universe"].map({"Yes": 0, "No": 1})
    df_out.sort_values(by=["sp_rank", "total_news"], ascending=[True, False], inplace=True)
    df_out.drop(columns=["sp_rank"], inplace=True)

    print(f"  -> Successfully processed {len(df_out):,} stocks.")
    return df_out


def export_results(df):
    """Export the structured analysis to CSV and styled Excel."""
    print("\n[Step 4/4] Exporting results to CSV and Excel...")

    # 1. Export CSV files
    df.to_csv(OUT_CSV_ALL, index=False, encoding="utf-8-sig")
    print(f"  -> Complete CSV saved: {OUT_CSV_ALL} ({len(df):,} stocks)")

    df_sp500 = df[df["in_sp500_universe"] == "Yes"].copy()
    df_sp500.to_csv(OUT_CSV_SP500, index=False, encoding="utf-8-sig")
    print(f"  -> S&P 500 CSV saved: {OUT_CSV_SP500} ({len(df_sp500):,} stocks)")

    # 2. Sector summary table
    sector_summary = df_sp500.groupby("sector").agg(
        total_stocks=("ticker", "count"),
        total_news=("total_news", "sum"),
        avg_news_per_stock=("total_news", "mean"),
        median_news_per_stock=("total_news", "median"),
        avg_max_gap_days=("max_gap_days", "mean"),
    ).reset_index().sort_values(by="total_news", ascending=False)
    sector_summary["avg_news_per_stock"] = sector_summary["avg_news_per_stock"].round(1)
    sector_summary["avg_max_gap_days"] = sector_summary["avg_max_gap_days"].round(1)

    # 3. Formatted Excel file
    if HAS_OPENPYXL:
        print("  -> Creating styled Excel spreadsheet with openpyxl...")
        wb = openpyxl.Workbook()

        header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")  # Dark Navy
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        regular_font = Font(name="Calibri", size=10)
        bold_font = Font(name="Calibri", size=10, bold=True)
        thin_border = Border(
            left=Side(style="thin", color="E0E0E0"),
            right=Side(style="thin", color="E0E0E0"),
            top=Side(style="thin", color="E0E0E0"),
            bottom=Side(style="thin", color="E0E0E0")
        )

        fill_green = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")  # Continuous
        fill_yellow = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid") # Gapped
        fill_blue = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")   # Late Entry
        fill_gray = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")   # Sporadic

        def style_worksheet(ws, dataframe, title_name):
            ws.title = title_name
            ws.views.sheetView[0].showGridLines = True

            # Write header
            headers = list(dataframe.columns)
            ws.append(headers)
            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            ws.row_dimensions[1].height = 28

            # Write rows
            for r_idx, row_data in enumerate(dataframe.itertuples(index=False), start=2):
                ws.append(list(row_data))
                ws.row_dimensions[r_idx].height = 20

                # Color-code based on distribution profile
                prof = getattr(row_data, "distribution_profile", "")
                row_fill = None
                if "Continuous" in prof:
                    row_fill = fill_green
                elif "Hiatus" in prof or "Gapped" in prof:
                    row_fill = fill_yellow
                elif "Late Entry" in prof:
                    row_fill = fill_blue
                elif "Sporadic" in prof or "Historical" in prof:
                    row_fill = fill_gray

                for c_idx, val in enumerate(row_data, start=1):
                    c = ws.cell(row=r_idx, column=c_idx)
                    c.font = regular_font
                    c.border = thin_border

                    # Profile column fill
                    col_name = headers[c_idx - 1]
                    if col_name == "distribution_profile" and row_fill:
                        c.fill = row_fill
                        c.font = bold_font

                    # Numeric and date alignment
                    if isinstance(val, (int, np.integer)):
                        c.alignment = Alignment(horizontal="right")
                        c.number_format = "#,##0"
                    elif isinstance(val, (float, np.floating)):
                        c.alignment = Alignment(horizontal="right")
                        c.number_format = "#,##0.0"
                    elif isinstance(val, str) and (val.startswith("20") and len(val) == 10):
                        c.alignment = Alignment(horizontal="center")
                    elif col_name in ["ticker", "in_sp500_universe"]:
                        c.alignment = Alignment(horizontal="center")

            # Auto-fit column widths (sampling header and top 100 rows for high performance)
            for col_idx in range(1, len(headers) + 1):
                col_letter = get_column_letter(col_idx)
                max_len = len(headers[col_idx - 1])
                for r in range(1, min(ws.max_row, 100) + 1):
                    v_str = str(ws.cell(row=r, column=col_idx).value or "")
                    if len(v_str) > max_len:
                        max_len = len(v_str)
                ws.column_dimensions[col_letter].width = min(max(max_len + 3, 11), 38)

            ws.freeze_panes = "C2"

        # Sheet 1: S&P 500 Universe
        ws1 = wb.active
        style_worksheet(ws1, df_sp500, "SP500_Stocks")

        # Sheet 2: All Benzinga Tickers
        ws2 = wb.create_sheet(title="All_Benzinga_Stocks")
        style_worksheet(ws2, df, "All_Benzinga_Stocks")

        # Sheet 3: Sector Summary
        ws3 = wb.create_sheet(title="Sector_Summary")
        style_worksheet(ws3, sector_summary, "Sector_Summary")

        wb.save(OUT_EXCEL)
        print(f"  -> Multi-tab Excel saved: {OUT_EXCEL}")
    else:
        print("  -> Notice: openpyxl not available. Skipping .xlsx export (CSVs generated).")

    print("\n" + "=" * 80)
    print("                    BENZINGA STOCK ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Total Unique Tickers Analyzed:   {len(df):,}")
    print(f"S&P 500 Constituents Identified: {len(df_sp500):,}")
    print(f"Total News Articles Mapped:      {df['total_news'].sum():,}")
    print(f"Average News per Ticker:         {df['total_news'].mean():.1f}")
    print(f"Median News per Ticker:          {df['total_news'].median():.0f}")
    print("\nBreakdown by Distribution Profile (S&P 500 Universe):")
    print(df_sp500["distribution_profile"].value_counts().to_string())
    print("\nTop 10 Stocks by Total News in Benzinga:")
    for _, r in df_sp500.head(10).iterrows():
        print(f"  {r['ticker']:<6} | {str(r['company_name'])[:28]:<28} | {r['sector']:<22} | "
              f"{r['first_news_date']} to {r['last_news_date']} | News: {r['total_news']:>5,} | "
              f"Max Gap: {r['max_gap_days']:>4}d | Missing Yrs: {r['missing_years_count']}")
    print("=" * 80)


def main():
    sec_names, sp500_sectors, sp500_set = load_metadata()
    ticker_dates, ticker_news_count = load_benzinga_dataset()
    df_results = compute_stock_metrics(ticker_dates, ticker_news_count, sec_names, sp500_sectors, sp500_set)
    export_results(df_results)


if __name__ == "__main__":
    main()
