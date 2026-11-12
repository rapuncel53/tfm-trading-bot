# TFM Progress & State Handoff (`progress.md`)

## 1. Active Task & Scope
- **Project:** Master's Thesis (TFM) — Forecasting Cross-Sectional Stock Returns via Multimodal Fusion of Financial Newsflow (LLMs) and SEC Accounting Factors.
- **Reference Literature:** RAM Active Investments (Tian Guo & Emmanuel Hauptmann: EMNLP 2024 & arXiv Nov 2025).
- **Current Objective:** Prepare the thesis defense meeting with the academic supervisor and structure the manuscript chapters.

---

## 2. Outputs & Deliverable Paths
- **Trained LLM Checkpoint:** [`checkpoints/llm_return_regressor/best_model.pt`](file:///c:/Users/julia/tfm/checkpoints/llm_return_regressor/best_model.pt) (205.4 MB, Step 700, Val RMSE 0.1280).
- **Cached Multimodal Feature Bundle:** [`checkpoints/multimodal/features.pt`](file:///c:/Users/julia/tfm/checkpoints/multimodal/features.pt) (1,200 instances: $x_f \in \mathbb{R}^{14}$, $x_n \in \mathbb{R}^{4096}$).
- **Evaluation Predictions:**
  - 1-Month Horizon Val & Test: [`checkpoints/multimodal/val_20d_results/val_predictions_20d.csv`](file:///c:/Users/julia/tfm/checkpoints/multimodal/val_20d_results/val_predictions_20d.csv) and [`test_predictions_20d.csv`](file:///c:/Users/julia/tfm/checkpoints/multimodal/val_20d_results/test_predictions_20d.csv).
  - Horizon Comparison: [`checkpoints/multimodal/option_a_experiments/comparativa_horizontes_y_perdida.csv`](file:///c:/Users/julia/tfm/checkpoints/multimodal/option_a_experiments/comparativa_horizontes_y_perdida.csv).
- **Publication Figures:**
  - Val vs. Test 20d: [`checkpoints/multimodal/val_20d_results/val_vs_test_20d_comparison.png`](file:///c:/Users/julia/tfm/checkpoints/multimodal/val_20d_results/val_vs_test_20d_comparison.png).
  - Horizon Diagnostic: [`checkpoints/multimodal/option_a_experiments/comparativa_horizontes_hit_ratio_ic.png`](file:///c:/Users/julia/tfm/checkpoints/multimodal/option_a_experiments/comparativa_horizontes_hit_ratio_ic.png).
  - Decile Monotonicity: [`checkpoints/multimodal/multimodal_decile_returns_comparison.png`](file:///c:/Users/julia/tfm/checkpoints/multimodal/multimodal_decile_returns_comparison.png).
- **Core Methodology Documentation:**
  - Technical TFM Dossier for Supervisor Review: [`dossier_tecnico_tfm_multimodal.md`](file:///C:/Users/julia/.gemini/antigravity/brain/cfd936f4-2d39-41fb-916d-a6f983ac394f/dossier_tecnico_tfm_multimodal.md).
  - Master Multimodal Report: [`replica_estudio_multimodal_ram_ai.md`](file:///C:/Users/julia/.gemini/antigravity/brain/9f7a61e6-afb4-4584-a3e5-1f6d74df8639/replica_estudio_multimodal_ram_ai.md).
  - TFM Proposal Package (UPC EPSEM Layout): [`latex_proposal/propuesta_tfm_latex.zip`](file:///c:/Users/julia/tfm/latex_proposal/propuesta_tfm_latex.zip).
  - Data Architecture & Newsflow Slide Deck (Overleaf Beamer): [`latex_slides/presentacion_dataset_tfm.zip`](file:///c:/Users/julia/tfm/latex_slides/presentacion_dataset_tfm.zip).
  - Exclusive Newsflow Study & Company Timeline: [`data/estudio_flujos_noticias_benzinga_fnspid.md`](file:///c:/Users/julia/tfm/data/estudio_flujos_noticias_benzinga_fnspid.md).
  - Dedicated Newsflow Folder & Complete Deliverable Package: [`analisis_noticias_tfm/`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/).
  - Dedicated FNSPID Stock Analysis Engine & Excel/CSV Outputs: [`fnspid_stock_analysis/`](file:///c:/Users/julia/tfm/fnspid_stock_analysis/).
    - Analysis Script: [`fnspid_stock_analysis/analyze_fnspid_stocks.py`](file:///c:/Users/julia/tfm/fnspid_stock_analysis/analyze_fnspid_stocks.py).
    - Multi-Tab Formatted Excel: [`fnspid_stock_analysis/fnspid_stock_analysis.xlsx`](file:///c:/Users/julia/tfm/fnspid_stock_analysis/fnspid_stock_analysis.xlsx) (3 sheets, 35 columns, S&P 500, full 3,954 universe, sector summary).
    - Full Universe CSV: [`fnspid_stock_analysis/fnspid_stock_analysis.csv`](file:///c:/Users/julia/tfm/fnspid_stock_analysis/fnspid_stock_analysis.csv) (3,954 stocks).
    - S&P 500 Universe CSV: [`fnspid_stock_analysis/fnspid_sp500_stocks.csv`](file:///c:/Users/julia/tfm/fnspid_stock_analysis/fnspid_sp500_stocks.csv) (343 stocks).
    - Documentation & Metric Definitions: [`fnspid_stock_analysis/README.md`](file:///c:/Users/julia/tfm/fnspid_stock_analysis/README.md).
  - Dedicated Benzinga Stock Analysis Engine & Excel/CSV Outputs: [`benzinga_stock_analysis/`](file:///c:/Users/julia/tfm/benzinga_stock_analysis/).
    - Analysis Script: [`benzinga_stock_analysis/analyze_benzinga_stocks.py`](file:///c:/Users/julia/tfm/benzinga_stock_analysis/analyze_benzinga_stocks.py).
    - Multi-Tab Formatted Excel: [`benzinga_stock_analysis/benzinga_stock_analysis.xlsx`](file:///c:/Users/julia/tfm/benzinga_stock_analysis/benzinga_stock_analysis.xlsx) (3 sheets, 32 columns, S&P 500, full 6,204 universe, sector summary).
    - Full Universe CSV: [`benzinga_stock_analysis/benzinga_stock_analysis.csv`](file:///c:/Users/julia/tfm/benzinga_stock_analysis/benzinga_stock_analysis.csv) (6,204 stocks).
    - S&P 500 Universe CSV: [`benzinga_stock_analysis/benzinga_sp500_stocks.csv`](file:///c:/Users/julia/tfm/benzinga_stock_analysis/benzinga_sp500_stocks.csv) (381 stocks).
    - Documentation & Metric Definitions: [`benzinga_stock_analysis/README.md`](file:///c:/Users/julia/tfm/benzinga_stock_analysis/README.md).
  - Standardized Multi-Dataset News Coverage Heatmaps Engine: [`news_coverage_heatmaps/`](file:///c:/Users/julia/tfm/news_coverage_heatmaps/).
    - Unified Heatmaps Generator Script: [`news_coverage_heatmaps/generate_news_heatmaps.py`](file:///c:/Users/julia/tfm/news_coverage_heatmaps/generate_news_heatmaps.py).
    - Documentation & Colormap Definitions: [`news_coverage_heatmaps/README.md`](file:///c:/Users/julia/tfm/news_coverage_heatmaps/README.md).
    - FNSPID Heatmaps Directory (2009–2023, 15 Years): [`news_coverage_heatmaps/fnspid_heatmaps/`](file:///c:/Users/julia/tfm/news_coverage_heatmaps/fnspid_heatmaps/) (12 high-res PNGs: 1 master panorama of all 343 S&P 500 stocks with individual y-labels, 7 paginated annotated heatmaps covering 100% of ranks 1–343, 3 focus heatmaps, and 1 full universe top-500 macro).
    - Benzinga Heatmaps Directory (2009–2020, 12 Years): [`news_coverage_heatmaps/benzinga_heatmaps/`](file:///c:/Users/julia/tfm/news_coverage_heatmaps/benzinga_heatmaps/) (13 high-res PNGs: 1 master panorama of all 381 S&P 500 stocks with individual y-labels, 8 paginated annotated heatmaps covering 100% of ranks 1–381, 3 focus heatmaps, and 1 full universe top-500 macro).
    - Documento 1 (Acción por Acción, 207 Empresas): [`analisis_noticias_tfm/1_cobertura_noticias_todas_las_acciones.xlsx`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/1_cobertura_noticias_todas_las_acciones.xlsx) y [`.csv`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/1_cobertura_noticias_todas_las_acciones.csv).
    - Documento 2 (Mejores Acciones Selección Re-entrenamiento): [`analisis_noticias_tfm/2_mejores_acciones_seleccionadas_entrenamiento.xlsx`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/2_mejores_acciones_seleccionadas_entrenamiento.xlsx) y [`.csv`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/2_mejores_acciones_seleccionadas_entrenamiento.csv).
    - Guía Metodológica: [`analisis_noticias_tfm/INFORME_METODOLOGICO_Y_SELECCION_ACCIONES.md`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/INFORME_METODOLOGICO_Y_SELECCION_ACCIONES.md).
    - Scripts Generadores: [`analisis_noticias_tfm/scripts/`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/scripts/) (`01_generar_excel_todas_las_acciones.py`, `02_generar_excel_mejores_acciones.py`, `03_auditoria_fnspid.py`, `04_auditoria_benzinga.py`, `05_auditoria_duplicados_y_solape.py`).
    - PowerPoint Deck Completo: [`analisis_noticias_tfm/presentacion_noticias_tfm.pptx`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/presentacion_noticias_tfm.pptx).
    - PowerPoint Deck Resumido en Inglés (5 Diapositivas, Puntos Clave): [`analisis_noticias_tfm/presentation_news_and_stock_selection.pptx`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/presentation_news_and_stock_selection.pptx).
    - Gráfico Gantt Temporal en Inglés: [`analisis_noticias_tfm/mapa_temporal_noticias_por_compania_en.png`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/mapa_temporal_noticias_por_compania_en.png).
    - Gráfico Reparto 70/10/20 en Inglés: [`analisis_noticias_tfm/distribucion_optimizada_70_10_20_en.png`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/distribucion_optimizada_70_10_20_en.png).
    - Timeline Gantt Plot: [`analisis_noticias_tfm/mapa_temporal_noticias_por_compania.png`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/mapa_temporal_noticias_por_compania.png).
    - Optimized 70/10/20 Distribution Plot: [`analisis_noticias_tfm/distribucion_optimizada_70_10_20.png`](file:///c:/Users/julia/tfm/analisis_noticias_tfm/distribucion_optimizada_70_10_20.png).
  - Company Timeline Coverage Plot: [`data/grafico_cobertura_temporal_companias.png`](file:///c:/Users/julia/tfm/data/grafico_cobertura_temporal_companias.png).
  - Standalone Forensic Audit Scripts:
    - FNSPID Auditor: [`scripts/analisis_fnspid.py`](file:///c:/Users/julia/tfm/scripts/analisis_fnspid.py) $\to$ [`data/analisis_fnspid_companias.csv`](file:///c:/Users/julia/tfm/data/analisis_fnspid_companias.csv).
    - Benzinga Auditor: [`scripts/analisis_benzinga.py`](file:///c:/Users/julia/tfm/scripts/analisis_benzinga.py) $\to$ [`data/analisis_benzinga_companias.csv`](file:///c:/Users/julia/tfm/data/analisis_benzinga_companias.csv).
    - Duplicates & Syndication Auditor: [`scripts/analisis_duplicados_noticias.py`](file:///c:/Users/julia/tfm/scripts/analisis_duplicados_noticias.py) $\to$ [`data/analisis_duplicados_resumen.json`](file:///c:/Users/julia/tfm/data/analisis_duplicados_resumen.json).
  - S&P 500 Train/Val/Test Optimization Deliverables:
    - Master S&P 500 Split Ranking Excel: [`ANALISIS DATASETS NOTICIAS/sp500_noticias_ordenadas_train_val_test.xlsx`](file:///c:/Users/julia/tfm/ANALISIS DATASETS NOTICIAS/sp500_noticias_ordenadas_train_val_test.xlsx).
    - Top 150 Heatmap & 25-Company Forensic Quality Study Excel: [`ANALISIS DATASETS NOTICIAS/top150_heatmap_y_estudio_25_companias.xlsx`](file:///c:/Users/julia/tfm/ANALISIS DATASETS NOTICIAS/top150_heatmap_y_estudio_25_companias.xlsx).
  - Dedicated Consolidated S&P 500 News Selection Package: [`seleccion_noticias_sp500/`](file:///c:/Users/julia/tfm/seleccion_noticias_sp500/).
    - Complete User Guide & Methodology: [`seleccion_noticias_sp500/README.md`](file:///c:/Users/julia/tfm/seleccion_noticias_sp500/README.md).
    - [Excel 1] Universal News Matrix (8,552 tickers, 2009–2024): [`seleccion_noticias_sp500/matriz_noticias_tickers_anos.xlsx`](file:///c:/Users/julia/tfm/seleccion_noticias_sp500/matriz_noticias_tickers_anos.xlsx).
    - [Excel 2] S&P 500 News Matrix (503 stocks, GICS sector, 4 sheets): [`seleccion_noticias_sp500/matriz_noticias_sp500.xlsx`](file:///c:/Users/julia/tfm/seleccion_noticias_sp500/matriz_noticias_sp500.xlsx).
    - [Excel 3] S&P 500 70/10/20 Optimal Split Ranking (Continuous Top 343 & Elite 100): [`seleccion_noticias_sp500/sp500_noticias_ordenadas_train_val_test.xlsx`](file:///c:/Users/julia/tfm/seleccion_noticias_sp500/sp500_noticias_ordenadas_train_val_test.xlsx).
    - [Excel 4] Top 150 In-Cell Heatmap & 25-Company Quality Forensic Study: [`seleccion_noticias_sp500/top150_heatmap_y_estudio_25_companias.xlsx`](file:///c:/Users/julia/tfm/seleccion_noticias_sp500/top150_heatmap_y_estudio_25_companias.xlsx).
    - Generator Scripts: [`01_generar_matriz_tickers_anos.py`](file:///c:/Users/julia/tfm/seleccion_noticias_sp500/01_generar_matriz_tickers_anos.py), [`02_filtrar_matriz_sp500.py`](file:///c:/Users/julia/tfm/seleccion_noticias_sp500/02_filtrar_matriz_sp500.py), [`03_ordenar_train_val_test.py`](file:///c:/Users/julia/tfm/seleccion_noticias_sp500/03_ordenar_train_val_test.py), [`04_generar_top150_y_estudio_25_companias.py`](file:///c:/Users/julia/tfm/seleccion_noticias_sp500/04_generar_top150_y_estudio_25_companias.py), [`05_descargar_noticias_top150_nasdaq.py`](file:///c:/Users/julia/tfm/seleccion_noticias_sp500/05_descargar_noticias_top150_nasdaq.py).
    - 100% Cached Top 150 FNSPID News Dumps: [`data/windows/`](file:///c:/Users/julia/tfm/data/windows/) (150 / 150 companies, 319,751 real articles, 2.77 GB).

---

## 3. Completed Stages & Verified Results
1. **Data Ingestion & Alignment:** Cleaned SEC EDGAR 10-Q/10-K fundamentals and merged with Benzinga news and CRSP/Yahoo prices into `daily_aligned.parquet` (Train: 2011–2018, Val: 2019–2020, Test: 2021–2023).
2. **LLM Backbone Fine-Tuning (EMNLP 2024):** Fine-tuned `Qwen/Qwen3.5-9B` using 4-bit QLoRA ($r=16, \alpha=32$) and Masked Mean Pooling (Eq. 5) up to step 700 with full loss convergence (0.235 $\to$ 0.019).
3. **Diagnosis of the 1-Day Horizon Failure:** Demonstrated that 1-day daily forward returns are dominated by market microstructure noise (Hit Ratio ~50.67%, Rank IC -0.025).
4. **Resolution via 1-Month Horizon (RAM AI 2025):** Shifted target to 20 trading sessions (`ret_20d`) to align with Post-Earnings Announcement Drift (PEAD), producing a jump to **76.00% Hit Ratio in Validation** and **63.00% in blind Test**.
5. **Multimodal Benchmarking:** Implemented and compared `FactorsAlone`, `NewsAlone`, `FusionCombination` (Eq. 3), and `MixtureDecoupled` (Eq. 12–15). Confirmed `FusionCombination` as the champion model.
6. **Technical Dossier Creation:** Compiled the comprehensive technical specification document covering data forensics, multimodal architectures, empirical proofs, and peer review talking points for the academic supervisor.
7. **100% Granular Row-Level FNSPID Newsflow Profiling:** Downloaded and cached all remaining 64 boundary-probe S&P 500 news blocks into `data/windows/*.bin` via HTTP Range streaming. Recomputed the FNSPID analysis engine (1,157,842 deduplicated news articles across 3,954 tickers) achieving 100% `Full Stream (Row-Level Dates)` coverage (0 estimated companies) across all 343 S&P 500 constituents. Updated CSVs, Excel, and regenerated all heatmaps in `news_coverage_heatmaps/fnspid_heatmaps/` showing exact year-by-year counts without averages.
8. **Top 150 Heatmap & 25-Company Forensic Quality Study:** Selected the top 150 continuous S&P 500 companies ranked by optimal 70/10/20 train/val/test balance. Generated `ANALISIS DATASETS NOTICIAS/top150_heatmap_y_estudio_25_companias.xlsx` with in-cell 3-color conditional formatting (darker = higher news count). Performed an empirical study on 25 randomly sampled companies across 58,400+ articles: measured word count distributions (headlines: 9.3 words, bodies: 735 words), classified quality levels (53% High Fundamental, 41% Mid Market Context, 6% Low Boilerplate/Bots), and compiled 75 verbatim article examples with full excerpts.

---

## 4. Architectural Decisions & Empirical Evidence
- **Champion Architecture:** Selected `FusionCombination` (Equation 3) as the production proposed model.
  * *Evidence:* Replicated RAM AI's North American finding that concatenating factors with bottleneck-compressed news representations yields superior out-of-sample stability compared to complex gating mechanisms.
- **Pooling Mechanism:** Selected Masked Mean Pooling over EOS bottleneck to prevent representation collapse in decoder LLMs.
- **Factor Hygiene:** Removed look-ahead target contamination by using strictly past momentum (`mom_5d_past`, `mom_20d_past`, `dist_sma20`) and lagged fundamental ratios.

---

## 5. Expert Review & Advisor Guidance (Oct 2026)
- **Evaluation:** Feedback received from top-tier quantitative finance / deep learning expert (thesis advisor level). Work evaluated as exceeding Master's thesis standards, with a roadmap to achieve Q1 / NeurIPS-ICAIF workshop publication quality.
- **Identified Vulnerabilities & Directives:**
  1. *Fragility of $N=25$ Deciles:* Expand from 25 pilot tickers to the full 199 Tier 1 Gold universe (~20 stocks/decile).
  2. *Temporal Overlap & Train/Val Leakage:* Introduce a 20-trading-day purge embargo at the end of Train (`2018-12-01` to `2018-12-31`) to ensure zero $ret_{20d}$ look-ahead into Val (`2019-01-01`). Use Newey-West HAC ($lag=20$) for standard errors.
  3. *Factor Hygiene:* Eliminate scale identifiers (`log_close`, raw `eps_diluted`). Replace with stationary ratios (distance to 52-week high, $E/P$ Earnings Yield) and apply cross-sectional Z-scoring per date $t$: $\tilde{x}_{f,i,t} = \frac{x_{f,i,t} - \mu_{f,t}}{\sigma_{f,t}}$ with winsorization.
  4. *Prompt Disentanglement:* Document SEC data in prompts as qualitative market context conditioning, contrasting with continuous quantitative factors in $x_f$.
  5. *Institutional Frictions:* Add turnover tracking ($\tau_t$) and Break-Even Transaction Cost (BETC) across $\{0, 5, 10, 15, 25\}$ bps.
  6. *Hybrid Ranking Loss:* Implement $\mathcal{L}_{\text{hybrid}} = (1-\lambda)\text{MSE} + \lambda(1 - \text{Pearson\_IC})$ on Level 3 fusion heads.
  7. *Adversarial Robustness Chapter:* Original contribution demonstrating how audited SEC fundamentals protect portfolios against fake news and prompt injections.

---

## 6. Supervisor Meeting Directives & 2-Week Roadmap (Meeting Deadline: Mid-Nov 2026)
Feedback and requirements received from TFM Supervisor (Cristian Rodriguez Rivero):
1. **Target Redefinition & Evaluation Horizons:**
   - Multi-horizon comparison: 1-day, 1-week, and 1-month horizons.
   - Dual evaluation objective: Directional prediction (up / down) and price variation / volatility magnitude.
2. **Core Research Hypothesis (LLM as a Financial Analyst):**
   - Train an LLM to reason over multimodal company data (newsflow + SEC accounting fundamentals + price trends) to evaluate if it can understand why and how stocks move, acting like a financial analyst.
3. **Modality Ablation Study:**
   - Systematic ablation: News-only vs. SEC accounting-only vs. Multimodal combination.
4. **Benchmarking Strategy & Literature Action Item:**
   - Tabular benchmark: LightGBM on financial/momentum metrics.
   - Financial NLP benchmark: FinBERT on newsflow.
   - *Active Action Item (User Note):* Survey literature to identify top-tier multimodal financial benchmark models (e.g., existing multimodal fusion architectures in quantitative finance) for comprehensive comparison.
5. **Data Governance & Legal Compliance (GDPR & Licenses):**
   - Document licensing and academic suitability: FNSPID (`CC BY-NC-4.0`), SEC EDGAR (US public domain), Benzinga.
6. **UPC Administration:**
   - Identify and confirm a UPC co-supervisor for the MERIT Master program.
7. **Deliverable in 2 Weeks (Slides):**
   - Presentation deck adhering to `Tips for creating SLIDES` (UPC format): datasets description, methodology, AI models/architectures, baselines, and ablation protocol.

---

## 7. Execution Roadmap (4 Sequential Sprints)
- [ ] **Sprint 1 (Factor Hygiene & Embargo Purging):** Update factor definitions (distance to 52w high, $E/P$ earnings yield, cross-sectional Z-score) and enforce 20d purge between Train and Val.
- [ ] **Sprint 2 (Universe Scaling to 199 Tickers):** Run batch inference with frozen `best_model.pt` (`torch.no_grad()`) to extract $x_n \in \mathbb{R}^{4096}$ and $x_f \in \mathbb{R}^{14}$ into `features_tier1_199.pt`.
- [ ] **Sprint 3 (Hybrid Loss & Institutional Backtesting):** Ablate MSE vs $\mathcal{L}_{\text{hybrid}}$ / ListNet; compute Newey-West HAC ($lag=20$), turnover $\tau_t$, and net Sharpe degradation across 0–25 bps.
- [ ] **Sprint 4 (Adversarial Robustness Experiment):** Implement `scripts/evaluate_adversarial_robustness.py` to test fake news spoofing vs SEC fundamentals and verify gating resistance.

---

## 8. Immediate Action for Upcoming Meeting
- Prepare the 2-week deliverables: Thesis proposal dossier, Benchmark definition, Data Governance / License sheet, and Slides deck for supervisor review.


