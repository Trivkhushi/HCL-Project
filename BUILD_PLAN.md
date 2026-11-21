# BUILD PLAN: Pricing Comparison Analytics

## 1. Project Summary & Artifact Inventory
**Pricing Comparison Analytics** is an enterprise-grade retail intelligence platform engineered in Python 3.12, SQLite, and Streamlit. The application tracks multi-channel price movements across 300+ standardized SKUs in 4 categories (Electronics, FMCG, Personal Care, Fashion) spanning 6 platforms (ApexRetail, Amazon India, Flipkart, Blinkit, Zepto, Croma). Designed for commercial leaders and category pricing managers, it calculates cross-channel price variances, enforces gross margin floors (< 10% alert), conducts inferential hypothesis testing ($t$-tests / ANOVA) comparing quick-commerce against standard marketplaces, and simulates gross revenue/margin trade-offs under dynamic price matching elasticity. The platform features responsive Tailwind CSS styled KPI cards embedded via isolated iframes and delivers sub-second analytical query performance.

### Project Document Inventory (Traceable Steps 1–13):
1. **Step 1 (Project Understanding):** [`docs/01_Project_Understanding.docx`](docs/01_Project_Understanding.docx)
2. **Step 2 (HMW Statements):** [`docs/02_HMW_Statements.docx`](docs/02_HMW_Statements.docx)
3. **Step 3 (Needs Analysis):** [`docs/03_Needs_Analysis.docx`](docs/03_Needs_Analysis.docx)
4. **Step 4 (Traceability Matrix):** [`docs/04_Traceability_Matrix.xlsx`](docs/04_Traceability_Matrix.xlsx)
5. **Step 5 (BRD):** [`docs/05_BRD.docx`](docs/05_BRD.docx)
6. **Step 6 (PRD):** [`docs/06_PRD.docx`](docs/06_PRD.docx)
7. **Step 7 (TRD):** [`docs/07_TRD.docx`](docs/07_TRD.docx)
8. **Step 8 (Database Design):** [`docs/08_Database_Design.xlsx`](docs/08_Database_Design.xlsx)
9. **Step 9 (ER Diagram):** [`docs/09_ER_Diagram.docx`](docs/09_ER_Diagram.docx) & [`docs/09_ER_Diagram.png`](docs/09_ER_Diagram.png)
10. **Step 10 (Dataset Generation):** [`src/generate_data.py`](src/generate_data.py), [`data/app.db`](data/app.db), [`data/pricing_data.xlsx`](data/pricing_data.xlsx), [`docs/10_Dataset_Generation.docx`](docs/10_Dataset_Generation.docx)
11. **Step 11 (User Stories):** [`docs/11_User_Stories.docx`](docs/11_User_Stories.docx)
12. **Step 12 (UI Framework):** [`.streamlit/config.toml`](.streamlit/config.toml), [`src/ui.py`](src/ui.py), [`docs/12_UI_Framework.docx`](docs/12_UI_Framework.docx)
13. **Step 13 (Test Cases):** [`tests/`](tests/), [`docs/13_Test_Cases.docx`](docs/13_Test_Cases.docx), [`docs/04_Traceability_Matrix.xlsx` (FINAL RTM)](docs/04_Traceability_Matrix.xlsx)

---

## 2. Final Repository Architecture

```text
pricing-comparison-analytics/
├── .streamlit/
│   └── config.toml               # Streamlit theme colors, fonts, and server flags
├── data/
│   ├── app.db                    # Primary SQLite relational database (committed)
│   ├── pricing_data.xlsx         # Multi-sheet Excel workbook export of raw tables
│   └── *.csv                     # Individual table CSV backups for portability
├── docs/
│   ├── 01_Project_Understanding.docx
│   ├── 02_HMW_Statements.docx
│   ├── 03_Needs_Analysis.docx
│   ├── 04_Traceability_Matrix.xlsx
│   ├── 05_BRD.docx
│   ├── 06_PRD.docx
│   ├── 07_TRD.docx
│   ├── 08_Database_Design.xlsx
│   ├── 09_ER_Diagram.docx
│   ├── 09_ER_Diagram.png
│   ├── 10_Dataset_Generation.docx
│   ├── 11_User_Stories.docx
│   ├── 12_UI_Framework.docx
│   ├── 13_Test_Cases.docx
│   └── 14_BUILD_PLAN.docx
├── pages/
│   ├── 1_Overview.py             # Macro KPI cards, category variance, PCI donut
│   ├── 2_Compare.py              # SKU-level comparison, margin bleed, effective cart
│   ├── 3_Trends.py               # 30-day price cadence & competitor volatility CV %
│   ├── 4_Statistics.py           # t-Test (Quick-Comm vs Mkt), ANOVA, correlation
│   ├── 5_Simulator.py            # What-If dynamic price matching simulation
│   ├── 6_Data_Quality.py         # Schema checks, nulls, duplicates, outlier diagnostics
│   └── 7_About.py                # Academic credentials, mentorship, and architecture
├── src/
│   ├── __init__.py
│   ├── data_loader.py            # SQLite connection, st.cache_data, SQL queries
│   ├── cleaner.py                # Data cleaning, type casts, Z-score outlier engine
│   ├── analytics.py              # Variance %, margin %, effective cart, PCI formulas
│   ├── stats.py                  # SciPy/statsmodels t-tests, ANOVA, Pearson/Spearman
│   ├── simulator.py              # Demand elasticity and revenue/margin simulation
│   └── ui.py                     # Tailwind CSS iframe KPI card and header renderers
├── tests/
│   ├── __init__.py
│   ├── test_data.py              # Database integrity, schema validation, foreign keys
│   ├── test_analysis.py          # Math formulas (margin, PCI, CV %, simulation)
│   └── test_app.py               # Streamlit AppTest execution and page rendering
├── app.py                        # Main entrypoint, global filters, landing overview
├── requirements.txt              # Pinned Python package dependencies
├── BUILD_PLAN.md                 # Step-by-step engineering build roadmap
└── README.md                     # Deployment, setup, and architectural guide
```

---

## 3. Step-by-Step Build Tasks (BUILD-01 to BUILD-18)

### [BUILD-01] Environment Setup & Configuration
- **Goal:** Establish virtual environment, dependencies, and Streamlit theme configuration.
- **Files Touched:** `requirements.txt`, `.streamlit/config.toml`
- **Linked Stories / Features:** Foundation / NFR-03
- **Prompt:** "Configure `requirements.txt` with pinned versions (`streamlit`, `pandas`, `numpy`, `scipy`, `statsmodels`, `plotly`, `pytest`, `openpyxl`, `python-docx`) and `.streamlit/config.toml` with Navy `#1E3A8A` theme."
- **Check:** Run `pip check` and verify `.streamlit/config.toml` exists.
- **Tests Passing:** Environment executes Python 3.12 cleanly.

### [BUILD-02] Data Layer & Caching Engine
- **Goal:** Implement `src/data_loader.py` providing cached database connections and SQL data access.
- **Files Touched:** `src/data_loader.py`
- **Linked Stories / Features:** US-11, US-13 / F-11, F-12
- **Prompt:** "Write `src/data_loader.py` with `@st.cache_data(ttl=3600)` to query `v_pricing_analysis`, `price_history`, and raw master tables from `data/app.db` with relative paths."
- **Check:** In Python: `from src.data_loader import load_pricing_view; df = load_pricing_view(); assert len(df) >= 300`
- **Tests Passing:** `tests/test_data.py` (all 5 tests pass).

### [BUILD-03] Data Cleaning & Outlier Engine
- **Goal:** Implement `src/cleaner.py` for type casting, null handling, and $Z$-score outlier detection.
- **Files Touched:** `src/cleaner.py`
- **Linked Stories / Features:** US-13 / F-12 / BR-12
- **Prompt:** "Write `src/cleaner.py` containing `detect_outliers(df, threshold=3.0)` and `get_data_quality_report(df)` calculating null counts, duplicates, and extreme prices."
- **Check:** Run `cleaner.get_data_quality_report(df)` and verify it flags 3 simulated outliers and 5 missing ratings.
- **Tests Passing:** `tests/test_data.py::test_tc_t_05_analytical_view_columns`.

### [BUILD-04] Analytical Pricing Engine
- **Goal:** Implement `src/analytics.py` for financial calculations and metric aggregation.
- **Files Touched:** `src/analytics.py`
- **Linked Stories / Features:** US-01, US-02, US-05, US-06, US-08 / F-01, F-02, F-05, F-06, F-08
- **Prompt:** "Write `src/analytics.py` containing vectorized functions for `calculate_category_variance()`, `get_margin_bleed_skus()`, `calculate_pci_distribution()`, `calculate_effective_cart_gap()`, and `calculate_cv_volatility()`."
- **Check:** Assert margin bleed flags trigger on budget electronics SKUs with margin < 10%.
- **Tests Passing:** `tests/test_analysis.py::test_tc_t_06_gross_margin_formula`, `test_tc_t_07_price_competitiveness_index_tiers`, `test_tc_t_08_effective_cart_price`, `test_tc_t_09_coefficient_of_variation`.

### [BUILD-05] Inferential Statistics Engine
- **Goal:** Implement `src/stats.py` for parametric and non-parametric hypothesis testing and correlation.
- **Files Touched:** `src/stats.py`
- **Linked Stories / Features:** US-04, US-07 / F-04, F-07 / BR-04, BR-07
- **Prompt:** "Write `src/stats.py` implementing `run_quickcomm_vs_market_ttest(df)` (checking normality via Shapiro-Wilk and fallback to Mann-Whitney U) and `calculate_discount_review_correlation(df)`."
- **Check:** Verify $p < 0.05$ on Quick-Commerce vs Marketplace FMCG subset.
- **Tests Passing:** `tests/test_analysis.py::test_tc_t_10_inferential_two_sample_ttest`.

### [BUILD-06] What-If Pricing Simulation Model
- **Goal:** Implement `src/simulator.py` for dynamic price elasticity and revenue/margin trade-off forecasting.
- **Files Touched:** `src/simulator.py`
- **Linked Stories / Features:** US-10 / F-10 / BR-10
- **Prompt:** "Write `src/simulator.py` implementing `simulate_price_matching(base_price, cost_price, base_volume, target_price, elasticity)`."
- **Check:** Verify that dropping price by 10% with $e = -1.5$ yields $+15\%$ volume uplift.
- **Tests Passing:** `tests/test_analysis.py::test_tc_t_11_elasticity_simulation_formula`.

### [BUILD-07] Tailwind UI Component Framework
- **Goal:** Refine `src/ui.py` providing iframe containers for modern Tailwind styled headers, KPI cards, and banners.
- **Files Touched:** `src/ui.py`
- **Linked Stories / Features:** All / UI-01..06 / NFR-03
- **Prompt:** "Refine `src/ui.py` with responsive styling for `render_tailwind_header()`, `render_kpi_card()`, and `render_alert_box()`."
- **Check:** Execute `pytest tests/test_app.py::test_tc_t_12_ui_components_importable`.
- **Tests Passing:** `tests/test_app.py::test_tc_t_12_ui_components_importable`.

### [BUILD-08] Main Entrypoint & Global Filters (`app.py`)
- **Goal:** Build the main application landing page with shared sidebar filters using `st.session_state`.
- **Files Touched:** `app.py`
- **Linked Stories / Features:** US-11, US-12 / F-11 / UI-01
- **Prompt:** "Build `app.py` initializing session state filters (Category, Competitor, Date range), rendering Tailwind header, and displaying executive KPI summary."
- **Check:** Run `streamlit run app.py` and verify sidebar filters slice data without errors.
- **Tests Passing:** `tests/test_app.py::test_tc_t_13_query_latency_under_one_second`.

### [BUILD-09] Page 1: Overview & Executive KPIs
- **Goal:** Implement `pages/1_Overview.py` with category price variance grouped bar chart and PCI donut chart.
- **Files Touched:** `pages/1_Overview.py`
- **Linked Stories / Features:** US-01, US-05 / F-01, F-05 / UI-01
- **Prompt:** "Build `pages/1_Overview.py` with 4 Tailwind KPI cards, `px.bar` for category price variance %, `px.pie(hole=0.5)` for PCI tiers, and Top 5 Overpriced SKUs table."
- **Check:** Verify bar chart displays red bars for categories > 3% above market average.
- **Tests Passing:** `TC-F-01`, `TC-F-05`.

### [BUILD-10] Page 2: Price Comparison & Margin Bleed Desk
- **Goal:** Implement `pages/2_Compare.py` with margin bleed violation table and effective cart price stacked bar chart.
- **Files Touched:** `pages/2_Compare.py`
- **Linked Stories / Features:** US-02, US-06, US-09 / F-02, F-06, F-09 / UI-02
- **Prompt:** "Build `pages/2_Compare.py` featuring a red alert banner for margin bleed SKUs (<10%), full SKU comparison table with risk pills, and stacked bar chart showing Base + Shipping + Platform fee."
- **Check:** Verify stacked bar exposes quick-commerce convenience and shipping charges.
- **Tests Passing:** `TC-F-02`, `TC-F-06`, `TC-F-09`.

### [BUILD-11] Page 3: Temporal Trends & Volatility
- **Goal:** Implement `pages/3_Trends.py` with 30-day repricing cadence line chart and CV % volatility ranker.
- **Files Touched:** `pages/3_Trends.py`
- **Linked Stories / Features:** US-03, US-08 / F-03, F-08 / UI-03
- **Prompt:** "Build `pages/3_Trends.py` querying `price_history` to display a 30-day temporal line chart with weekend repricing annotations and horizontal bar chart ranking competitor CV %."
- **Check:** Verify Friday/Saturday repricing frequency spikes are visible on the line chart.
- **Tests Passing:** `TC-F-03`, `TC-F-08`.

### [BUILD-12] Page 4: Inferential EDA & Statistics
- **Goal:** Implement `pages/4_Statistics.py` with two-sample t-test hypothesis card and correlation scatter plot.
- **Files Touched:** `pages/4_Statistics.py`
- **Linked Stories / Features:** US-04, US-07 / F-04, F-07 / UI-04
- **Prompt:** "Build `pages/4_Statistics.py` displaying the two-sample t-test hypothesis card (rejecting H0 at p < 0.001) and Plotly scatter plot with OLS trendline showing discount vs review velocity."
- **Check:** Verify test card displays $t$-statistic, exact $p$-value, and verbal statistical decision.
- **Tests Passing:** `TC-F-04`, `TC-F-07`.

### [BUILD-13] Page 5: What-If Pricing Simulator
- **Goal:** Implement `pages/5_Simulator.py` providing interactive elasticity sliders and revenue/margin delta forecasting.
- **Files Touched:** `pages/5_Simulator.py`
- **Linked Stories / Features:** US-10 / F-10 / UI-05
- **Prompt:** "Build `pages/5_Simulator.py` with category/SKU selector, target benchmark selector, price elasticity slider (-0.5 to -2.5), and dynamic delta KPI metric cards."
- **Check:** Test slider movement and verify Delta Revenue and Delta Margin cards update in real time.
- **Tests Passing:** `TC-F-10`.

### [BUILD-14] Page 6: Data Quality Diagnostics & Raw Data
- **Goal:** Implement `pages/6_Data_Quality.py` tabulating schema checks, nullness, duplicates, outliers, and CSV export.
- **Files Touched:** `pages/6_Data_Quality.py`
- **Linked Stories / Features:** US-13, US-14 / F-12 / UI-06
- **Prompt:** "Build `pages/6_Data_Quality.py` displaying a diagnostic summary table (0 duplicate PKs, 0 orphan FKs, 5 missing ratings), outlier table (|Z| > 3.0), and a 'Download CSV' button."
- **Check:** Click download button and verify browser downloads valid CSV.
- **Tests Passing:** `TC-F-12`, `TC-T-03`, `TC-T-04`.

### [BUILD-15] Page 7: About & Academic Reference
- **Goal:** Implement `pages/7_About.py` detailing student credentials, guide, ABES institution, and architecture reference.
- **Files Touched:** `pages/7_About.py`
- **Linked Stories / Features:** Documentation / UI-07
- **Prompt:** "Build `pages/7_About.py` with cards detailing Khushi Trivedi (Roll: 2500320140080), Mentor Mrs. Kalpana Diwedi, tech stack badges, and ER diagram reference."
- **Check:** Verify all student and mentor details match Step 0 metadata.
- **Tests Passing:** All pages render cleanly without navigation errors.

### [BUILD-16] Automated Test Suite Execution
- **Goal:** Execute full pytest regression suite and verify 100% pass rate.
- **Files Touched:** `tests/test_data.py`, `tests/test_analysis.py`, `tests/test_app.py`
- **Linked Stories / Features:** NFR-05 / All Tests
- **Prompt:** "Execute `pytest -v` across all test files and confirm zero failures."
- **Check:** Output displays `14 passed in < 20s`.
- **Tests Passing:** 100% test pass rate.

### [BUILD-17] Project Documentation & README Compilation
- **Goal:** Write a production-grade `README.md` detailing project overview, architecture, installation, test execution, and deployment instructions.
- **Files Touched:** `README.md`
- **Linked Stories / Features:** NFR-05
- **Prompt:** "Create `README.md` with project badge, architecture diagram, feature matrix, local setup instructions, pytest guide, and Streamlit Community Cloud deployment steps."
- **Check:** Verify markdown formatting and relative file links.
- **Tests Passing:** Documentation complete.

### [BUILD-18] Git Repository Preparation & Deployment Verification
- **Goal:** Verify relative paths, ensure `.gitignore` excludes `.venv/` and cache files, commit code, and prepare Streamlit Cloud deployment.
- **Files Touched:** `.gitignore`, Git commits
- **Linked Stories / Features:** NFR-01..06
- **Prompt:** "Audit repository to ensure `data/app.db` is tracked, `app.py` is at root, and relative paths resolve cleanly."
- **Check:** Run `git status` to ensure clean working directory ready for cloud push.
- **Tests Passing:** Ready for Step 16 deployment.

---

## 4. Definition of Done (DoD)
A build task or the overall project is declared **DONE** if and only if:
1. **100% Must-Have Requirements Implemented:** All 8 Must BRs and MVP features (F-01, F-02, F-04, F-05, F-06, F-10, F-11, F-12) are fully functional.
2. **100% Pytest Pass Rate:** All unit and technical test cases in `tests/` pass with zero failures or errors.
3. **Sub-2.5s Latency SLA:** Initial page load is < 2.5s and filter re-render is < 1.0s.
4. **Data Hygiene & Schema Integrity:** Database exhibits 0 orphaned foreign keys and 0 duplicate primary keys.
5. **Full Traceability:** The Requirements Traceability Matrix (`docs/04_Traceability_Matrix.xlsx`) is 100% populated from OQ to Test Cases.
6. **Academic Conformance:** Fully aligned with ABES Engineering College MCA evaluation rubrics.

---

## 5. Standard Terminal Commands

```bash
# 1. Activate Virtual Environment
.venv\Scripts\activate

# 2. Install Pinned Dependencies
pip install -r requirements.txt

# 3. Generate Synthetic Data (if regenerating)
python src/generate_data.py

# 4. Run Automated Pytest Suite
pytest -v

# 5. Launch Streamlit Application Locally
streamlit run app.py
```

---

## 6. Viva Preparation Notes (10 Likely Questions & High-Impact Answers)

1. **Q: What is the core business problem this project addresses?**
   *A:* Multi-channel digital retailers face extreme pricing opacity and unmonitored margin erosion due to competitors' dynamic algorithmic repricing. This platform provides transparent competitive price indexing, gross margin protection, and statistical verification.
2. **Q: How does this project differ from a typical descriptive dashboard?**
   *A:* Typical dashboards only display static bar charts of prices. Our platform integrates inferential hypothesis testing (two-sample $t$-tests at $\alpha = 0.05$ to statistically prove channel markups), gross margin floor alerting, and predictive what-if price elasticity simulation modeling.
3. **Q: Why was SQLite selected over cloud databases like PostgreSQL or Snowflake?**
   *A:* SQLite is a serverless, zero-configuration relational database embedded directly in the repository (`data/app.db`). This enables deterministic academic reproducibility, instant cold-start execution on Streamlit Community Cloud, and eliminates external database subscription costs or network connection dropouts.
4. **Q: Explain the Price Competitiveness Index (PCI) formula and how categories are binned.**
   *A:* $PCI = \left(\frac{P_{our}}{\bar{P}_{comp}}\right) \times 100$. A PCI of 100 indicates exact market parity. We classify catalog SKUs into Underpriced ($PCI < 97$), Par ($97 \le PCI \le 103$), and Overpriced ($PCI > 103$), providing actionable posture buckets for commercial executives.
5. **Q: What is the statistical rationale for conducting a Two-Sample Independent t-test on FMCG prices?**
   *A:* It tests the null hypothesis $H_0: \mu_{quick} = \mu_{mkt}$ against $H_1: \mu_{quick} \ne \mu_{mkt}$. Finding $p < 0.001$ proves with $> 99.9\%$ confidence that quick-commerce platforms command a statistically significant convenience premium (+6.4%), proving it is not random sampling noise.
6. **Q: How does the "Effective Cart Price" metric prevent misleading pricing decisions?**
   *A:* Competitors frequently advertise low base sticker prices to attract clicks but add steep delivery fees (₹25–₹45) and platform convenience surcharges (₹5–₹15) at checkout. Calculating $\text{Effective Cart Price} = \text{Selling Price} + \text{Shipping} + \text{Platform Fee}$ reveals true out-of-pocket consumer parity.
7. **Q: How does the What-If Pricing Simulator work mathematically?**
   *A:* It uses economic price elasticity of demand: $\Delta Q = Q_0 \times e \times \left(\frac{\Delta P}{P_0}\right)$. When matching a lower competitor price ($\Delta P < 0$), demand volume expands. The simulator computes the net revenue delta and margin delta, warning users if volume expansion fails to offset margin sacrifice.
8. **Q: How did you ensure data hygiene and prevent regression errors?**
   *A:* By enforcing database engine constraints (`PRAGMA foreign_keys = ON;`, `CHECK`, `UNIQUE`), compiling a pre-joined analytical view (`v_pricing_analysis`), and executing automated pytest suites covering 100% of mathematical formulas and schema constraints.
9. **Q: Why did you embed Tailwind CSS via `st.components.v1.html` iframe?**
   *A:* Streamlit's default components lack modern flexbox layouts, gradient borders, and responsive badges. Injecting Tailwind CSS via an isolated iframe achieves production-grade design-system fidelity without needing Node.js or risking global CSS conflicts.
10. **Q: How does the Requirements Traceability Matrix (RTM) demonstrate professional engineering discipline?**
    *A:* The RTM provides complete bidirectional traceability from initial stakeholder business questions (OQs) through HMW statements, business requirements (BRs), product features, database columns, user stories, UI screens, and pytest test cases, proving zero orphaned requirements and zero unverified code.
