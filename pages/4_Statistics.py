"""
pages/4_Statistics.py
UI-04: Inferential Statistical Analysis
Features: F-09, F-10
User Stories: US-09, US-10
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_loader import load_pricing_view
from src.stats import (
    run_quickcomm_vs_market_ttest,
    calculate_discount_review_correlation,
    run_platform_anova
)
from src.ui import render_tailwind_header, render_kpi_card, render_alert_box

st.set_page_config(
    page_title="Inferential Statistics | PriceIntel Pro",
    page_icon="🔬",
    layout="wide"
)

# Load data
df = load_pricing_view()

# Header
render_tailwind_header(
    title="Inferential Statistics & Hypothesis Testing",
    subtitle="Parametric Welch's t-test, Mann-Whitney U, OLS regression, and One-Way ANOVA (UI-04)",
    badge_text="F-09 | F-10"
)

st.markdown("<br>", unsafe_allow_html=True)

# 1. Inferential Hypothesis Testing: Quick-Commerce Convenience Markup (F-09)
st.markdown("### 🧪 Hypothesis Test: Quick-Commerce Convenience Markup (F-09)")
st.markdown("""
- **Null Hypothesis ($H_0$):** $\\mu_{\\text{Quick-Commerce}} = \\mu_{\\text{Marketplace}}$ (No significant difference in average price for identical products).
- **Alternative Hypothesis ($H_1$):** $\\mu_{\\text{Quick-Commerce}} \\neq \\mu_{\\text{Marketplace}}$ (Quick-Commerce platforms command a statistically significant convenience premium).
- **Decision Rule:** Reject $H_0$ if $p < 0.05$.
""")

test_cat = st.selectbox("Select Target Category for Hypothesis Testing", ["FMCG", "Electronics", "Fashion", "Beauty & Care"], index=0)
ttest_res = run_quickcomm_vs_market_ttest(df, category=test_cat, alpha=0.05)

t_col1, t_col2, t_col3, t_col4 = st.columns(4)
with t_col1:
    render_kpi_card("Statistical Test", ttest_res["test_name"].split(" ")[0] + " Test", "Normality Checked", "neutral")
with t_col2:
    render_kpi_card("p-value", f"{ttest_res['p_value']:.6f}", "Alpha = 0.05", "positive" if ttest_res["reject_h0"] else "neutral")
with t_col3:
    render_kpi_card("Convenience Premium", f"{ttest_res['premium_pct']:+.2f}%", f"QC ₹{ttest_res['mean_qc']} vs Mkt ₹{ttest_res['mean_mkt']}", "positive" if ttest_res["reject_h0"] else "neutral")
with t_col4:
    render_kpi_card("Decision", "REJECT H0" if ttest_res["reject_h0"] else "FAIL TO REJECT", "Statistically Significant" if ttest_res["reject_h0"] else "Not Significant", "positive" if ttest_res["reject_h0"] else "negative")

st.markdown("<br>", unsafe_allow_html=True)
render_alert_box(
    title=f"FORMAL STATISTICAL VERDICT ({test_cat})",
    message=ttest_res["conclusion"],
    alert_type="success" if ttest_res["reject_h0"] else "warning"
)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# 2. OLS Regression & Correlation Engine (F-10)
st.markdown("### 📈 Correlation & OLS Regression: Discount Depth vs Review Velocity (F-10)")
st.markdown("Evaluates whether price markdown aggressiveness ($X = \\text{discount\\_pct}$) drives higher consumer purchase and review engagement ($Y = \\text{review\\_count}$).")

corr_res = calculate_discount_review_correlation(df)

col_corr_left, col_corr_right = st.columns([3, 1])

with col_corr_left:
    fig_scatter = px.scatter(
        df[df["review_count"] > 0],
        x="discount_pct",
        y="review_count",
        color="category_name",
        trendline="ols",
        labels={"discount_pct": "Discount Depth (%)", "review_count": "Review Count"},
        title=f"OLS Regression Fit: Review Count = {corr_res['slope']} * Discount% + {corr_res['intercept']} (R² = {corr_res['r_squared']})",
        hover_data=["product_name", "competitor_name", "selling_price"]
    )
    fig_scatter.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=380,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_corr_right:
    st.markdown("#### Regression Metrics")
    render_kpi_card("Pearson r", str(corr_res["r"]), "Linear Strength", "positive")
    render_kpi_card("R-Squared (R²)", str(corr_res["r_squared"]), "Explained Variance", "neutral")
    render_kpi_card("Spearman rho", str(corr_res["rho"]), "Monotonic Rank", "neutral")
    render_kpi_card("p-value", f"{corr_res['p_value']:.4e}", "Significance", "positive")

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# 3. Platform ANOVA (Cross-Competitor Variance)
st.markdown("### 🏛️ One-Way ANOVA: Cross-Competitor Price Variance")
st.markdown("Evaluates whether mean selling prices differ significantly across the 6 competitor platforms.")

anova_res = run_platform_anova(df)
a_col1, a_col2, a_col3 = st.columns(3)
with a_col1:
    render_kpi_card("F-Statistic", str(anova_res["f_stat"]), "Across 6 Platforms", "neutral")
with a_col2:
    render_kpi_card("ANOVA p-value", f"{anova_res['p_value']:.4e}", "Alpha = 0.05", "positive" if anova_res["reject_h0"] else "neutral")
with a_col3:
    verdict_text = "Significant Cross-Platform Pricing Variations Exist" if anova_res["reject_h0"] else "Homogeneous Cross-Platform Pricing"
    render_kpi_card("Omnibus Conclusion", verdict_text, "Reject H0" if anova_res["reject_h0"] else "Fail to Reject", "positive" if anova_res["reject_h0"] else "neutral")
