"""News Coverage Heatmaps Generator for Financial Datasets (FNSPID & Benzinga).

This script reads the structured stock analysis Excel files and generates a comprehensive,
publication-quality suite of heatmaps visualizing news distribution across all available years.

Key Design Principles:
  1. 100% Stock Coverage (Zero Arbitrary Truncation):
     - Every single stock in the S&P 500 universe (all 343 for FNSPID, all 381 for Benzinga)
       is fully rendered and accounted for.
     - Paginated heatmaps (default 50 stocks/page) provide large, crisp typography and exact
       numerical article counts inside every cell.
     - Complete macro heatmaps render the entire universe on a high-resolution continuous canvas
       with explicit, non-overlapping tick marks for every single ticker.
  2. Strict Logical Ordering:
     - Stocks are ranked from best distributed (active in all available years, 100% continuity,
       zero multi-year gaps, highest news counts) down to sparse / windowed entrants.
  3. Standardized Visual Colormap:
     - Identical logarithmic colormap (YlGnBu, vmin=1, vmax=6000) across all heatmaps.
     - Neutral soft grey (#ECEFF1) highlighting reporting hiatuses (0 news / silent years).
     - Adaptive high-contrast cell typography (white on dark cells, dark navy on light cells,
       and soft grey dashes '-' on zero cells).
  4. Universal Dual-Dataset Support:
     - FNSPID: 2009–2023 (15 calendar years, 343 S&P 500 stocks, 3,954 total stocks).
     - Benzinga: 2009–2020 (12 calendar years, 381 S&P 500 stocks, 6,204 total stocks).

Outputs:
  - fnspid_heatmaps/
      00_complete_sp500_master_heatmap_all_343_stocks.png
      01_page_1_rank_001_to_050_best_distributed.png ... page_7_rank_301_to_343.png
      02_focus_stocks_with_all_15_years_active.png
      03_focus_stocks_with_multi_year_gaps.png
      04_focus_stocks_with_fewest_years_recent_or_sparse.png
      05_full_universe_top500_macro_heatmap.png
  - benzinga_heatmaps/
      00_complete_sp500_master_heatmap_all_381_stocks.png
      01_page_1_rank_001_to_050_best_distributed.png ... page_8_rank_351_to_381.png
      02_focus_stocks_with_all_12_years_active_overview.png
      03_focus_stocks_with_multi_year_gaps.png
      04_focus_stocks_with_fewest_years_recent_or_sparse.png
      05_full_universe_top500_macro_heatmap.png
"""

import os
import sys
import math
import time
import argparse
import numpy as np
import pandas as pd

# Add fallback search paths for Anaconda and user-installed site-packages
for p in [
    r"C:\Users\julia\anaconda3\Lib\site-packages",
    r"C:\Users\julia\AppData\Roaming\Python\Python311\site-packages",
]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns

def safe_savefig(fig, out_path, dpi=200, bbox_inches="tight"):
    """Safely save figure to disk handling transient Windows file locking."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp_path = out_path + f".tmp_{os.getpid()}_{time.time_ns()}.png"
    success = False
    for attempt in range(4):
        try:
            fig.savefig(tmp_path, dpi=dpi, bbox_inches=bbox_inches)
            if os.path.exists(out_path):
                try:
                    os.remove(out_path)
                except OSError:
                    pass
            os.replace(tmp_path, out_path)
            success = True
            break
        except (OSError, PermissionError):
            if attempt < 3:
                time.sleep(0.6 * (attempt + 1))
            else:
                # Direct fallback save
                fig.savefig(out_path, dpi=dpi, bbox_inches=bbox_inches)
                success = True
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
    return success
UNIFIED_CMAP = plt.cm.YlGnBu.copy()
UNIFIED_CMAP.set_bad(color="#ECEFF1")  # Neutral light grey for 0 news / silences
UNIFIED_NORM = mcolors.LogNorm(vmin=1, vmax=6000)
ZERO_COLOR_HEX = "#ECEFF1"


def resolve_excel_path(dataset_name):
    """Locate the Excel file for a given dataset across possible working directories."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        # Relative to script inside ANALISIS DATASETS NOTICIAS/news_coverage_heatmaps
        os.path.join(script_dir, "..", f"{dataset_name.lower()}_stock_analysis", f"{dataset_name.lower()}_stock_analysis.xlsx"),
        # In case folders are in root
        os.path.join(script_dir, f"{dataset_name.lower()}_stock_analysis", f"{dataset_name.lower()}_stock_analysis.xlsx"),
        # Relative to CWD
        os.path.join(os.getcwd(), "ANALISIS DATASETS NOTICIAS", f"{dataset_name.lower()}_stock_analysis", f"{dataset_name.lower()}_stock_analysis.xlsx"),
        os.path.join(os.getcwd(), f"{dataset_name.lower()}_stock_analysis", f"{dataset_name.lower()}_stock_analysis.xlsx"),
        # Hardcoded absolute fallback
        rf"C:\Users\julia\tfm\ANALISIS DATASETS NOTICIAS\{dataset_name.lower()}_stock_analysis\{dataset_name.lower()}_stock_analysis.xlsx",
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    raise FileNotFoundError(f"Could not locate analysis Excel for '{dataset_name}'. Checked:\n" + "\n".join(candidates))


def get_year_columns(df):
    """Extract and sort year-by-year news columns from dataframe."""
    year_cols = [c for c in df.columns if c.startswith("news_") and c[5:].isdigit()]
    year_cols.sort(key=lambda c: int(c[5:]))
    return year_cols


def sort_stocks_by_distribution(df):
    """Sort stocks from best distributed (all years active, high continuity) to fewest years."""
    df_sorted = df.sort_values(
        by=["active_years_count", "continuity_pct", "missing_years_count", "total_news"],
        ascending=[False, False, True, False]
    ).reset_index(drop=True)
    return df_sorted


def render_annotated_heatmap(
    df_subset,
    year_cols,
    title,
    subtitle,
    out_path,
    rank_offset=1,
    dpi=250
):
    """Render an annotated heatmap with exact counts inside every cell and high-contrast styling."""
    n_stocks = len(df_subset)
    if n_stocks == 0:
        print(f"  [Notice] Subset for '{title}' is empty. Skipping plot.")
        return

    # Proportional figure sizing: ~0.35 inches per row ensures crisp cell typography
    fig_height = max(n_stocks * 0.35 + 2.4, 5.0)
    fig_width = 17.0
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

    # Format y-axis labels: [Rank] TICKER | Company Name (Total news | Active yrs | Continuity %)
    labels = []
    for idx, (_, r) in enumerate(df_subset.iterrows()):
        curr_rank = rank_offset + idx
        sym = str(r["ticker"]).strip().upper()
        cname = str(r.get("company_name", ""))[:24].strip()
        tot = int(r.get("total_news", 0))
        act = int(r.get("active_years_count", 0))
        cont = float(r.get("continuity_pct", 0.0))
        labels.append(f"[{curr_rank:03d}] {sym:<6} | {cname:<24} ({tot:>6,} news | {act:>2}y | {cont:>5.1f}%)")

    data_matrix = df_subset[year_cols].copy().astype(float)
    data_matrix.index = labels
    years_labels = [c[5:] for c in year_cols]
    data_matrix.columns = years_labels

    # Replace 0 with NaN so Seaborn uses UNIFIED_CMAP bad_color (#ECEFF1)
    data_nan = data_matrix.replace(0, np.nan)

    # Text annotations: exact count or '-' for 0
    annot = data_matrix.map(lambda v: f"{int(v):,}" if v > 0 else "-")

    cbar_kws = {
        "label": "Annual News Count (Standardized Log Scale)",
        "fraction": 0.025,
        "pad": 0.02,
        "ticks": [1, 5, 20, 100, 500, 2000, 6000],
        "format": "%.0f"
    }

    sns.heatmap(
        data_nan,
        cmap=UNIFIED_CMAP,
        norm=UNIFIED_NORM,
        annot=annot,
        fmt="",
        cbar=True,
        cbar_kws=cbar_kws,
        linewidths=0.6,
        linecolor="#FFFFFF",
        ax=ax
    )

    # Post-process text colors for maximum contrast against background luminance
    for text in ax.texts:
        val_str = text.get_text().replace(",", "")
        if val_str == "-":
            text.set_color("#90A4AE")  # Muted grey dash
            text.set_fontsize(8)
            text.set_fontweight("normal")
        else:
            try:
                v = float(val_str)
                nv = UNIFIED_NORM(min(max(v, 1.0), 6000.0))
                # If dark cell (nv > 0.65), use white; otherwise dark navy
                text.set_color("#FFFFFF" if nv > 0.65 else "#1A237E")
                text.set_fontsize(8)
                text.set_fontweight("medium")
            except ValueError:
                pass

    ax.set_title(f"{title}\n", fontsize=13, fontweight="bold", pad=10, loc="left")
    plt.suptitle(subtitle, fontsize=10, color="#424242", x=0.125, y=0.99, ha="left")

    ax.set_xlabel("Calendar Year", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylabel("Rank. TICKER | Company Name (Total News | Active Years | Continuity)", fontsize=10, fontweight="bold", labelpad=10)
    ax.tick_params(axis="x", labelsize=10, rotation=0)
    ax.set_yticks(np.arange(n_stocks) + 0.5)
    ax.set_yticklabels(labels, fontsize=8, family="monospace")

    fig.text(
        0.125, 0.01,
        "Note: Grey cells '-' indicate 0 news articles (silence / reporting hiatus). Color scale is identical across all FNSPID and Benzinga heatmaps.",
        fontsize=8.5, style="italic", color="#616161"
    )

    plt.tight_layout(rect=[0, 0.02, 1, 0.98])
    safe_savefig(fig, out_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"  -> Generated: {os.path.basename(out_path)} ({n_stocks} stocks)")


def render_macro_heatmap(
    df_full,
    year_cols,
    title,
    subtitle,
    out_path,
    dpi=200
):
    """Render a continuous high-resolution macro heatmap with all stocks labeled on the y-axis."""
    n_stocks = len(df_full)
    if n_stocks == 0:
        print(f"  [Notice] Full dataset for '{title}' is empty. Skipping macro plot.")
        return

    # Proportional height (0.28 inches per row ensures every single tick is explicitly drawn and legible)
    fig_height = max(n_stocks * 0.28 + 3.0, 10.0)
    fig_width = 17.0
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

    labels = []
    for idx, (_, r) in enumerate(df_full.iterrows()):
        curr_rank = idx + 1
        sym = str(r["ticker"]).strip().upper()
        cname = str(r.get("company_name", ""))[:24].strip()
        tot = int(r.get("total_news", 0))
        act = int(r.get("active_years_count", 0))
        cont = float(r.get("continuity_pct", 0.0))
        labels.append(f"[{curr_rank:03d}] {sym:<6} | {cname:<24} ({tot:>6,} | {act:>2}y | {cont:>5.1f}%)")

    data_matrix = df_full[year_cols].copy().astype(float)
    data_matrix.index = labels
    years_labels = [c[5:] for c in year_cols]
    data_matrix.columns = years_labels

    data_nan = data_matrix.replace(0, np.nan)

    cbar_kws = {
        "label": "Annual News Count (Standardized Log Scale)",
        "fraction": 0.02,
        "pad": 0.02,
        "ticks": [1, 5, 20, 100, 500, 2000, 6000],
        "format": "%.0f"
    }

    sns.heatmap(
        data_nan,
        cmap=UNIFIED_CMAP,
        norm=UNIFIED_NORM,
        annot=False,  # Uncluttered for continuous macro poster
        cbar=True,
        cbar_kws=cbar_kws,
        linewidths=0.3,
        linecolor="#E0E0E0",
        ax=ax
    )

    ax.set_title(f"{title}\n", fontsize=14, fontweight="bold", pad=12, loc="left")
    plt.suptitle(subtitle, fontsize=10.5, color="#424242", x=0.125, y=0.992, ha="left")

    ax.set_xlabel("Calendar Year", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylabel("Rank. TICKER | Company Name (Total News | Active Years | Continuity)", fontsize=10, fontweight="bold", labelpad=10)
    ax.tick_params(axis="x", labelsize=10, rotation=0)

    # Explicitly set every tick so matplotlib does not skip any labels
    ax.set_yticks(np.arange(n_stocks) + 0.5)
    ax.set_yticklabels(labels, fontsize=7, family="monospace")

    fig.text(
        0.125, 0.005,
        f"Master Overview: 100% of {n_stocks} stocks rendered with individual y-axis labels. Grey cells indicate 0 news articles.",
        fontsize=9, style="italic", color="#616161"
    )

    plt.tight_layout(rect=[0, 0.01, 1, 0.99])
    safe_savefig(fig, out_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"  -> Generated Master Macro: {os.path.basename(out_path)} (ALL {n_stocks} stocks rendered)")


def process_dataset(dataset_name, excel_path, out_dir, page_size=50):
    """Generate all paginated heatmaps, macro posters, and focus heatmaps for a dataset."""
    print("=" * 85)
    print(f"GENERATING COMPLETE NEWS COVERAGE HEATMAP SUITE FOR: {dataset_name.upper()}")
    print(f"Source Excel:     {excel_path}")
    print(f"Output Directory: {out_dir}")
    print(f"Page Size:        {page_size} stocks per paginated image")
    print("=" * 85)

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Source Excel not found at: {excel_path}")

    # 1. Load S&P 500 Universe sheet
    df_sp = pd.read_excel(excel_path, sheet_name="SP500_Stocks")
    year_cols = get_year_columns(df_sp)
    available_years_str = f"{year_cols[0][5:]} to {year_cols[-1][5:]}"
    total_sp_stocks = len(df_sp)

    print(f"Loaded {total_sp_stocks} S&P 500 stocks across {len(year_cols)} calendar years ({available_years_str}).")

    # Sort all stocks strictly from best distributed to fewest years
    df_sorted = sort_stocks_by_distribution(df_sp)

    # -------------------------------------------------------------------------
    # PART 1: MASTER COMPLETE HEATMAP (ALL STOCKS IN ONE IMAGE)
    # -------------------------------------------------------------------------
    print("\n[Stage 1/4] Generating Complete S&P 500 Universe Master Macro Heatmap...")
    master_path = os.path.join(out_dir, f"00_complete_sp500_master_heatmap_all_{total_sp_stocks}_stocks.png")
    render_macro_heatmap(
        df_sorted,
        year_cols,
        title=f"{dataset_name}: Complete S&P 500 Newsflow Heatmap (All {total_sp_stocks} Stocks)",
        subtitle=f"Every single S&P 500 stock ranked from best distribution (Rank 1) to sparse/windowed coverage (Rank {total_sp_stocks}). Full timeline {available_years_str}.",
        out_path=master_path,
        dpi=200
    )

    # -------------------------------------------------------------------------
    # PART 2: PAGINATED HEATMAPS (100% OF STOCKS WITH CELL ANNOTATIONS)
    # -------------------------------------------------------------------------
    num_pages = math.ceil(total_sp_stocks / page_size)
    print(f"\n[Stage 2/4] Generating Paginated Heatmaps ({num_pages} pages covering 100% of stocks)...")

    for p in range(num_pages):
        start_idx = p * page_size
        end_idx = min(start_idx + page_size, total_sp_stocks)
        df_page = df_sorted.iloc[start_idx:end_idx].copy()

        # Categorize page description based on rank
        if p == 0:
            desc = "best_distributed"
            tier_desc = "Best Distributed Stocks (Full Timeline Continuity)"
        elif end_idx == total_sp_stocks:
            desc = "fewest_active_years"
            tier_desc = "Stocks with Fewest Active Years (Sparse / Recent Entrants)"
        else:
            desc = f"coverage_group_{p+1}"
            tier_desc = f"Continuous & Moderate Coverage (Ranks {start_idx+1}–{end_idx})"

        page_file = f"01_page_{p+1:02d}_rank_{start_idx+1:03d}_to_{end_idx:03d}_{desc}.png"
        page_path = os.path.join(out_dir, page_file)

        render_annotated_heatmap(
            df_page,
            year_cols,
            title=f"{dataset_name} Coverage: Ranks {start_idx+1} to {end_idx} of {total_sp_stocks} (Page {p+1}/{num_pages})",
            subtitle=f"{tier_desc}. Sorted by active years, continuity, and news volume across {available_years_str}.",
            out_path=page_path,
            rank_offset=start_idx + 1,
            dpi=250
        )

    # -------------------------------------------------------------------------
    # PART 3: SPECIALIZED FOCUS HEATMAPS (ALL YEARS ACTIVE, GAPS, FEWEST YEARS)
    # -------------------------------------------------------------------------
    print("\n[Stage 3/4] Generating Specialized Focus Heatmaps...")

    # Focus A: Stocks with ALL available years active (100% years populated)
    all_years_mask = (df_sp[year_cols] > 0).all(axis=1)
    df_all_years = df_sp[all_years_mask].sort_values(by="total_news", ascending=False).copy()
    print(f"  - Stocks with all {len(year_cols)} years active: {len(df_all_years)}")

    if len(df_all_years) <= 60:
        # Fits on one clear annotated heatmap (e.g. FNSPID has 21)
        render_annotated_heatmap(
            df_all_years,
            year_cols,
            title=f"{dataset_name} Focus: Stocks with All {len(year_cols)} Calendar Years Active ({len(df_all_years)} Stocks)",
            subtitle=f"100% timeline coverage ({available_years_str}) with news articles reported every single year. Sorted by total news volume.",
            out_path=os.path.join(out_dir, f"02_focus_stocks_with_all_{len(year_cols)}_years_active.png"),
            rank_offset=1,
            dpi=250
        )
    else:
        # Large group (e.g. Benzinga has 226) -> generate complete overview
        render_macro_heatmap(
            df_all_years,
            year_cols,
            title=f"{dataset_name} Focus: Stocks with All {len(year_cols)} Calendar Years Active ({len(df_all_years)} Stocks)",
            subtitle=f"Complete overview of all {len(df_all_years)} stocks with active newsflow across every single year ({available_years_str}). Sorted by total news.",
            out_path=os.path.join(out_dir, f"02_focus_stocks_with_all_{len(year_cols)}_years_active_overview.png"),
            dpi=200
        )

    # Focus B: Stocks with Multi-Year Hiatuses / Missing Intermediate Years
    gapped_mask = (df_sp["missing_years_count"] > 0) | (df_sp["max_gap_days"] >= 365)
    df_gapped = df_sp[gapped_mask].sort_values(
        by=["missing_years_count", "max_gap_days", "total_news"],
        ascending=[False, False, False]
    ).copy()
    print(f"  - Stocks with multi-year gaps / missing intermediate years: {len(df_gapped)}")

    render_annotated_heatmap(
        df_gapped,
        year_cols,
        title=f"{dataset_name} Focus: Stocks with Multi-Year Reporting Hiatuses ({len(df_gapped)} Stocks)",
        subtitle=f"All stocks exhibiting missing intermediate calendar years or continuous silences >= 365 days. Grey blocks '-' highlight reporting hiatuses.",
        out_path=os.path.join(out_dir, "03_focus_stocks_with_multi_year_gaps.png"),
        rank_offset=1,
        dpi=250
    )

    # Focus C: Stocks with Fewest Active Years (<= 4 years)
    sparse_mask = (df_sp["active_years_count"] <= 4)
    df_sparse = df_sp[sparse_mask].sort_values(
        by=["active_years_count", "total_news"],
        ascending=[True, False]
    ).copy()
    print(f"  - Stocks with <= 4 active years: {len(df_sparse)}")

    render_annotated_heatmap(
        df_sparse,
        year_cols,
        title=f"{dataset_name} Focus: Stocks with Fewest Active Years ({len(df_sparse)} Stocks with <= 4 Years)",
        subtitle=f"Stocks with news presence restricted to <= 4 calendar years (recent IPO entrants, historical cessations, or sparse coverage).",
        out_path=os.path.join(out_dir, "04_focus_stocks_with_fewest_years_recent_or_sparse.png"),
        rank_offset=1,
        dpi=250
    )

    # -------------------------------------------------------------------------
    # PART 4: FULL UNIVERSE MACRO HEATMAP (TOP 500 STOCKS ACROSS FULL MARKET)
    # -------------------------------------------------------------------------
    print("\n[Stage 4/4] Generating Full Universe Macro Heatmap (Top 500 Stocks)...")
    full_sheet_name = f"All_{dataset_name}_Stocks"
    try:
        df_all_univ = pd.read_excel(excel_path, sheet_name=full_sheet_name)
        total_market_stocks = len(df_all_univ)
        df_all_sorted = sort_stocks_by_distribution(df_all_univ)
        df_top500 = df_all_sorted.head(500).copy()

        render_macro_heatmap(
            df_top500,
            year_cols,
            title=f"{dataset_name}: Full Universe Top 500 Stocks Macro Heatmap (Market Universe: {total_market_stocks:,} Stocks)",
            subtitle=f"Top 500 stocks across the entire {total_market_stocks:,}-asset database ranked by timeline continuity and newsflow volume ({available_years_str}).",
            out_path=os.path.join(out_dir, "05_full_universe_top500_macro_heatmap.png"),
            dpi=200
        )
    except Exception as e:
        print(f"  [Warning] Could not generate full universe heatmap from sheet '{full_sheet_name}': {e}")

    print(f"\n[Completed] All heatmaps for {dataset_name} generated successfully in:\n  {out_dir}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive newsflow heatmaps from stock analysis Excels (100% stock coverage)."
    )
    parser.add_argument(
        "--dataset",
        choices=["all", "fnspid", "benzinga"],
        default="all",
        help="Which dataset to process: 'all' (default), 'fnspid', or 'benzinga'."
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=50,
        help="Number of stocks per paginated heatmap (default: 50)."
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    fnspid_out_dir = os.path.join(script_dir, "fnspid_heatmaps")
    benzinga_out_dir = os.path.join(script_dir, "benzinga_heatmaps")

    start_time = time.time()

    if args.dataset in ["all", "fnspid"]:
        excel_fnspid = resolve_excel_path("FNSPID")
        process_dataset("FNSPID", excel_fnspid, fnspid_out_dir, page_size=args.page_size)

    if args.dataset in ["all", "benzinga"]:
        excel_benzinga = resolve_excel_path("Benzinga")
        process_dataset("Benzinga", excel_benzinga, benzinga_out_dir, page_size=args.page_size)

    elapsed = time.time() - start_time
    print("=" * 85)
    print(f"ALL HEATMAP GENERATION COMPLETED IN {elapsed:.1f}s")
    print(f"FNSPID Directory:   {fnspid_out_dir}")
    print(f"Benzinga Directory: {benzinga_out_dir}")
    print("=" * 85)


if __name__ == "__main__":
    main()
