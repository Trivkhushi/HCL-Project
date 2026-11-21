# PriceIntel Pro: Enterprise Pricing Comparison Analytics & Margin Governance

[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42+-FF4B4B.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Star%20Schema-003B57.svg)](https://sqlite.org/)
[![Tests](https://img.shields.io/badge/pytest-14%2F14%20Passed%20(100%25)-brightgreen.svg)](https://docs.pytest.org/)
[![Academic Attribution](https://img.shields.io/badge/ABES%20Engineering%20College-MCA%20Capstone-1E3A8A.svg)](https://abes.ac.in/)

---

## 🎓 Academic Attribution & Credentials
- **Learner / Candidate:** Khushi Trivedi
- **University Roll Number:** `2500320140080`
- **Program:** Master of Computer Applications (MCA) – 2nd Year
- **Specialization:** Data Analytics
- **Department:** Department of Computer Applications
- **Institution:** ABES Engineering College, Ghaziabad, Uttar Pradesh, India
- **Faculty Guide / Mentor:** Mrs. Kalpana Diwedi, Assistant Professor

---

## 📌 Executive Summary & Project Overview
**PriceIntel Pro** is an end-to-end enterprise data analytics and competitive intelligence platform tailored for modern retail and e-commerce ecosystems. Rapidly evolving competitive dynamics across traditional marketplaces (Amazon, Flipkart, Myntra, Nykaa) and hyper-local quick-commerce platforms (Blinkit, Zepto) necessitate real-time price monitoring, automated margin protection, hidden fee decomposition, and microeconomic scenario simulation.

The system ingests multi-platform pricing snapshots into an enterprise **Star Schema SQLite database**, transforms raw pricing attributes via a 30-column analytical view (`v_pricing_analysis`), evaluates price elasticity and statistical hypotheses using **SciPy**, and serves interactive dashboards via **Streamlit** styled with **Tailwind CSS**.

---

## 🏗️ System Architecture & Data Model

```
                    ┌─────────────────────────────────────────┐
                    │      Synthetic Data Pipeline            │
                    │      (src/generate_data.py)             │
                    └────────────────────┬────────────────────┘
                                         │ Ingests Relational Data
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │       SQLite Relational DB              │
                    │          (data/app.db)                  │
                    │   Star Schema: 3 Dims, 2 Fact Tables    │
                    │   View: v_pricing_analysis (30 cols)    │
                    └────────────────────┬────────────────────┘
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
      ┌─────────────────────────┐                 ┌─────────────────────────┐
      │  Core Analytics Engine  │                 │  Inferential Statistics │
      │  (src/analytics.py,     │                 │  & Microeconomic Model  │
      │   src/cleaner.py)       │                 │  (src/stats.py,         │
      │  - Margin Bleed (<10%)  │                 │   src/simulator.py)     │
      │  - PCI Distribution     │                 │  - Welch's t-test / U   │
      │  - Effective Cart Fee   │                 │  - OLS Regression       │
      │  - Dynamic CV % Ranker  │                 │  - Demand Elasticity    │
      └────────────┬────────────┘                 └────────────┬────────────┘
                   │                                           │
                   └─────────────────────┬─────────────────────┘
                                         │ In-Memory Dataframes
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │  Streamlit Multi-Page UI Engine         │
                    │  (Tailwind CSS CDN + Plotly Express)    │
                    │  - app.py (Landing & Global Filters)    │
                    │  - pages/1_Overview.py (UI-01)          │
                    │  - pages/2_Compare.py (UI-02)           │
                    │  - pages/3_Trends.py (UI-03)            │
                    │  - pages/4_Statistics.py (UI-04)        │
                    │  - pages/5_Simulator.py (UI-05)         │
                    │  - pages/6_Data_Quality.py (UI-06)      │
                    │  - pages/7_About.py (UI-07)             │
                    └─────────────────────────────────────────┘
```

### Relational Star Schema (SQLite)
1. **Dimension Tables:**
   - `categories` (`category_id`, `category_name`, `margin_floor_pct`, `created_at`)
   - `competitors` (`competitor_id`, `competitor_name`, `platform_type`, `shipping_flat_fee`, `platform_convenience_fee`)
   - `products` (`product_id`, `sku_code`, `product_name`, `category_id`, `brand_name`, `mrp`, `cost_price`)
2. **Fact Tables:**
   - `price_snapshots` (`snapshot_id`, `product_id`, `competitor_id`, `snapshot_date`, `selling_price`, `stock_status`, `discount_pct`, `rating_value`, `review_count`)
   - `price_history` (`history_id`, `product_id`, `competitor_id`, `recorded_price`, `effective_date`)
3. **Analytical View:**
   - `v_pricing_analysis`: Pre-joins all dimensions with computed columns: `market_avg_price`, `price_variance_pct`, `gross_margin_pct`, `price_competitiveness_index` (PCI), `pci_tier`, and `effective_cart_price`.

---

## ⚡ Key Modules & Features Matrix

| Screen ID | Module / Page | Features Tracked | Primary Business Purpose |
|:---|:---|:---|:---|
| **Home** | `app.py` | Global Filter Desk | Multi-dimensional category & platform filtering, KPI overview cards. |
| **UI-01** | `pages/1_Overview.py` | `F-01, F-04, F-06` | Category price variance % vs market, PCI tier donut, Top 5 overpriced SKUs. |
| **UI-02** | `pages/2_Compare.py` | `F-02, F-03, F-07` | Margin bleed alert banner (<10%), hidden delivery fee decomposition, stock-outs. |
| **UI-03** | `pages/3_Trends.py` | `F-05, F-08` | 30-day temporal price cadences, dynamic repricing spikes, CV % volatility ranker. |
| **UI-04** | `pages/4_Statistics.py` | `F-09, F-10` | Welch's t-test (QC FMCG markup), OLS regression (Discount vs Reviews), ANOVA. |
| **UI-05** | `pages/5_Simulator.py` | `F-11` | Interactive microeconomic price elasticity simulator ($\Delta Q = Q_0 \cdot e \cdot \frac{\Delta P}{P_0}$). |
| **UI-06** | `pages/6_Data_Quality.py`| `F-12` | Z-score anomaly detector ($|Z| > 3.0$), schema health audits, clean CSV export. |
| **UI-07** | `pages/7_About.py` | Documentation | Academic metadata, ABES credentials, mentor attribution, RTM traceability table. |

---

## 🔬 Mathematical & Econometric Formulations

### 1. Price Competitiveness Index (PCI)
$$\text{PCI}_i = \frac{P_{\text{selling}, i}}{\overline{P}_{\text{market}, i}}$$
- $\text{PCI} < 0.97$: **Underpriced** (Aggressively competitive)
- $0.97 \le \text{PCI} \le 1.03$: **Par** (Market competitive parity)
- $\text{PCI} > 1.03$: **Overpriced** (Vulnerable to conversion leakage)

### 2. Effective Checkout Cart Price
$$\text{Effective Cart Price} = P_{\text{selling}} + \text{Shipping Fee} + \text{Platform Convenience Fee}$$

### 3. Price Volatility (Coefficient of Variation)
$$\text{CV}\% = \left( \frac{\sigma_{\text{price}}}{\mu_{\text{price}}} \right) \times 100$$

### 4. Microeconomic Demand Elasticity Simulation
$$\Delta Q = Q_0 \times e \times \left( \frac{P_{\text{target}} - P_0}{P_0} \right)$$
$$\text{Gross Profit}_{\text{new}} = (P_{\text{target}} - C) \times (Q_0 + \Delta Q)$$

### 5. Inferential Hypothesis Testing (Quick-Commerce Convenience Premium)
- **Null Hypothesis ($H_0$):** $\mu_{\text{Quick-Commerce}} = \mu_{\text{Marketplace}}$
- **Alternative Hypothesis ($H_1$):** $\mu_{\text{Quick-Commerce}} \ne \mu_{\text{Marketplace}}$
- **Evaluation:** Normality tested via Shapiro-Wilk. Evaluated via Welch's two-sample $t$-test (or Mann-Whitney $U$ test if non-normal) at $\alpha = 0.05$.

---

## 🛠️ Installation & Execution Guide

### Prerequisites
- Python 3.12 or 3.13
- Git

### 1. Clone & Set Up Virtual Environment
```bash
git clone <repository-url>
cd "c:/HCL Project"

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Relational Database & Seed Data
```bash
python src/generate_data.py
```
*Generates `data/app.db` (SQLite relational database with Star Schema and analytical view `v_pricing_analysis`), along with backup `data/pricing_data.xlsx` and CSV files.*

### 4. Execute Automated Test Suite
```bash
pytest -v
```
*Executes all 14 unit and integration tests across data integrity, analytics logic, and performance budgets with 100% pass rate.*

### 5. Launch Interactive Dashboard
```bash
streamlit run app.py
```
*Access the enterprise dashboard at `http://localhost:8501` in your browser.*

---

## 🧪 Automated Verification & Quality Assurance Suite

All 14 tests in the test suite pass with zero errors:

```
tests/test_analysis.py::test_tc_t_06_gross_margin_formula PASSED         [  7%]
tests/test_analysis.py::test_tc_t_07_price_competitiveness_index_tiers PASSED [ 14%]
tests/test_analysis.py::test_tc_t_08_effective_cart_price PASSED         [ 21%]
tests/test_analysis.py::test_tc_t_09_coefficient_of_variation PASSED     [ 28%]
tests/test_analysis.py::test_tc_t_10_inferential_two_sample_ttest PASSED [ 35%]
tests/test_analysis.py::test_tc_t_11_elasticity_simulation_formula PASSED [ 42%]
tests/test_app.py::test_tc_t_12_ui_components_importable PASSED          [ 50%]
tests/test_app.py::test_tc_t_13_query_latency_under_one_second PASSED    [ 57%]
tests/test_app.py::test_tc_t_14_memory_footprint_compact PASSED          [ 64%]
tests/test_data.py::test_tc_t_01_database_exists PASSED                  [ 71%]
tests/test_data.py::test_tc_t_02_table_row_counts PASSED                 [ 78%]
tests/test_data.py::test_tc_t_03_primary_key_uniqueness PASSED           [ 85%]
tests/test_data.py::test_tc_t_04_foreign_key_integrity PASSED            [ 92%]
tests/test_data.py::test_tc_t_05_analytical_view_columns PASSED          [100%]
======================== 14 passed in 3.78s ========================
```

---

## 🏛️ Institutional Accreditation
Department of Computer Applications  
**ABES Engineering College**, Campus 19th KM Stone, NH-09, Ghaziabad, Uttar Pradesh 201009  
Affiliated to Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow  
**Session:** 2025–2026
