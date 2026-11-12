# Multimodal Stock Return Forecasting via LLMs & Accounting Factors

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2+-ee4c2c.svg)](https://pytorch.org/)

## Master's Thesis (TFM) — UPC MERIT

**Title:** Forecasting Cross-Sectional Stock Returns via Multimodal Fusion of Financial Newsflow (LLMs) and SEC Accounting Factors  
**Academic Supervisor:** Cristian Rodríguez Rivero  
**Reference Literature:** RAM Active Investments (*Tian Guo & Emmanuel Hauptmann*, EMNLP 2024 & arXiv Nov 2025)

---

## 1. Executive Summary & Research Hypothesis

This project investigates whether large language models fine-tuned on financial newsflow, when fused with quantitative accounting and momentum factors from SEC EDGAR filings, can forecast cross-sectional US equity returns out-of-sample.

```
Financial Newsflow (LLM Qwen 9B)  ───► Bottleneck Latent x_n (R^4096) ──┐
                                                                         ├─► Multimodal Fusion ──► Return Forecast (ret_20d)
SEC Accounting Factors + Momentum ───► Standardized Factor x_f (R^14)  ──┘
```

### Key Empirical Findings
- **Resolution of 1-Day Horizon Failure:** Daily 1-day returns are dominated by market microstructure noise (Hit Ratio ~50.67%, Rank IC -0.025). Moving to a **20-trading-day horizon (1-month forward)** aligned with Post-Earnings Announcement Drift (PEAD) produces a **76.00% Hit Ratio in Validation** and **63.00% in blind Test**.
- **Champion Architecture:** Replicating RAM AI's North American findings, the **Fusion Combination** model (bottleneck projection concatenated with normalized accounting factors) achieves superior out-of-sample stability over pure gating networks.
- **Decile Monotonicity:** Realized test returns increase monotonically across predicted deciles ($D_0 = -3.26\%$ vs. $D_9 = +3.42\%$, spread = $+6.68\%$).

---

## 2. Repository Structure

```
├── src/                          # Production neural network architectures and dataset pipelines
│   ├── multimodal_models.py      # All 6 multimodal fusion heads (FusionCombination, MixtureDecoupled, etc.)
│   ├── model.py                  # Qwen3.5-9B QLoRA backbone regressor with Masked Mean Pooling
│   ├── dataset.py                # Multimodal tokenization & tensor collation
│   ├── financial_context.py      # SEC financial ratios & momentum feature engineering
│   ├── metrics.py                # Cross-sectional Rank IC, Pearson IC, Hit Ratio, Decile spreads
│   ├── train.py                  # PyTorch training loops with early stopping
│   └── config.py                 # Hyperparameter configuration
│
├── scripts/                      # Empirical evaluation and data forensic scripts
│   ├── extract_multimodal_features.py   # Feature bundle extraction (frozen LLM inference)
│   ├── evaluate_option_a_horizons.py    # Multi-horizon comparison (1d, 5d, 20d)
│   ├── evaluate_20d_best_model.py       # Out-of-sample test evaluation
│   ├── fetch_all_sp500_windows.py       # High-speed HTTP Range downloader for raw news dumps
│   ├── analisis_fnspid.py               # Complete audit of FNSPID (3,954 companies)
│   ├── analisis_benzinga.py             # Complete audit of Benzinga (6,204 companies)
│   └── analisis_duplicados_noticias.py  # News syndication & duplicate analysis
│
├── ANALISIS DATASETS NOTICIAS/   # S&P 500 news coverage deliverables & ranking matrices
│   ├── sp500_noticias_ordenadas_train_val_test.xlsx # 70/10/20 train/val/test optimal ranking
│   └── top150_heatmap_y_estudio_25_companias.xlsx   # Top 150 conditional heatmaps & 25-firm audit
│
├── analisis_noticias_tfm/        # Standalone newsflow analytics & presentations
│   ├── 1_cobertura_noticias_todas_las_acciones.xlsx # Full universe audit (207 companies)
│   ├── 2_mejores_acciones_seleccionadas_entrenamiento.xlsx # Continuous Tier 1 candidates
│   ├── presentacion_noticias_tfm.pptx               # Complete 8-slide presentation
│   ├── presentation_news_and_stock_selection.pptx   # Executive 5-slide English deck
│   └── INFORME_METODOLOGICO_Y_SELECCION_ACCIONES.md # Detailed methodology guide
│
├── seleccion_noticias_sp500/     # Standalone S&P 500 news matrix generation suite
│   ├── matriz_noticias_tickers_anos.xlsx # 8,552 tickers x 15 years matrix
│   ├── matriz_noticias_sp500.xlsx        # 503 S&P 500 constituents by sector
│   └── README.md                         # Pipeline documentation
│
├── checkpoints/                  # Evaluation logs, test predictions, and publication charts
│   ├── llm_return_regressor/charts/     # Training loss convergence & decile plots
│   └── multimodal/val_20d_results/      # Predictions CSVs and validation vs. test figures
│
├── latex_proposal/               # UPC EPSEM-compliant Master's Thesis proposal package
└── latex_slides/                 # Beamer presentation slide deck for supervisor review
```

---

## 3. Data Governance & Newsflow Datasets

| Dataset | Period | Coverage | Licensing | Role in TFM |
| :--- | :---: | :---: | :---: | :--- |
| **FNSPID** | 2009–2023 | 3,954 Tickers (1.15M news) | `CC BY-NC-4.0` | Primary raw newsflow for LLM fine-tuning & feature extraction |
| **Benzinga** | 2009–2020 | 6,204 Tickers (1.39M news) | Research Use | Complementary sentiment & analyst ratings validation |
| **SEC EDGAR** | 2009–2023 | S&P 500 universe | Public Domain | Audited 10-Q / 10-K quarterly fundamentals & balance sheet ratios |
| **CRSP / Yahoo** | 2009–2023 | S&P 500 universe | Educational | Daily adjusted close prices, returns, and backward momentum |

---

## 4. Setup & Quickstart

```bash
# Clone the repository
git clone https://github.com/rapuncel53/tfm-trading-bot.git
cd tfm-trading-bot

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run main entrypoint
python src/main.py
```

---

## 5. Verification & Quality Assurance

All engineering milestones, model checkpoints, and backtest results are continuously verified against observable metrics in [`checks.md`](checks.md), and project development state is tracked in [`progress.md`](progress.md).

## 6. License

This project is licensed under the MIT License - see the LICENSE file for details.
