"""
pages/2_Compare.py
UI-02: Price Comparison & Margin Bleed Desk
Features: F-02, F-03, F-07
User Stories: US-02, US-03, US-07
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_loader import load_pricing_view, apply_global_filters
from src.analytics import (
    get_margin_bleed_skus,
    calculate_effective_cart_gap,
    get_stock_out_opportunities
)
from src.ui import render_tailwind_header, render_alert_box, render_kpi_card

st.set_page_config(
    page_title="Price Comparison & Bleed Desk | PriceIntel Pro",
    page_icon="⚖️",
    layout="wide"
)

# Load data
df_raw = load_pricing_view()

# Sidebar filters
with st.sidebar:
    st.markdown("### 🔍 Filters")
    all_categories = sorted(df_raw["category_name"].unique().tolist())
    all_competitors = sorted(df_raw["competitor_name"].unique().tolist())
    
    sel_categories = st.multiselect(
        "Categories",
        options=all_categories,
        default=st.session_state.get("global_filter_categories", all_categories),
        key="compare_categories"
    )
    sel_competitors = st.multiselect(
        "Competitor Platforms",
        options=all_competitors,
        default=st.session_state.get("global_filter_competitors", all_competitors),
        key="compare_competitors"
    )

df = apply_global_filters(df_raw, sel_categories, sel_competitors)

if df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# Header
render_tailwind_header(
    title="Price Comparison & Margin Bleed Desk",
    subtitle="Active gross margin protection, effective cart fee decomposition, and stock-out surge monitor (UI-02)",
    badge_text="F-02 | F-03 | F-07"
)

st.markdown("<br>", unsafe_allow_html=True)

# 1. Margin Bleed Desk (F-02)
st.markdown("### 🚨 Margin Bleed Protection Desk (F-02)")

ctrl_col1, ctrl_col2 = st.columns([1, 3])
with ctrl_col1:
    margin_threshold = st.slider(
        "Gross Margin Floor (%)",
        min_value=5.0,
        max_value=25.0,
        value=10.0,
        step=1.0,
        help="Flag SKUs with gross profit margin below this governance threshold."
    )

bleed_df = get_margin_bleed_skus(df, min_margin_threshold=margin_threshold / 100.0)

with ctrl_col2:
    if len(bleed_df) > 0:
        render_alert_box(
            title=f"CRITICAL ALERT: {len(bleed_df)} SKUs VIOLATING MARGIN FLOOR (< {margin_threshold}%)",
            message=f"Discovered {len(bleed_df)} SKUs priced below the mandated gross margin threshold. Selling these items at current price levels induces commercial margin erosion.",
            alert_type="danger"
        )
    else:
        render_alert_box(
            title="PORTFOLIO COMPLIANT: ZERO MARGIN BLEED",
            message=f"All current SKUs satisfy the minimum {margin_threshold}% gross margin governance floor.",
            alert_type="success"
        )

if not bleed_df.empty:
    display_bleed = bleed_df[[
        "sku_code", "product_name", "category_name", "competitor_name",
        "selling_price", "cost_price", "gross_margin_pct", "margin_risk_severity"
    ]].rename(columns={
        "sku_code": "SKU Code",
        "product_name": "Product Name",
        "category_name": "Category",
        "competitor_name": "Competitor",
        "selling_price": "Selling Price (₹)",
        "cost_price": "Cost Price (₹)",
        "gross_margin_pct": "Gross Margin %",
        "margin_risk_severity": "Risk Severity"
    })
    st.dataframe(display_bleed, use_container_width=True, hide_index=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# 2. Effective Cart Fee Breakdown (F-03)
st.markdown("### 🛒 Effective Cart Price Decomposition (F-03)")
st.markdown("Compares Base Listed Price against True Checkout Price by incorporating hidden Shipping and Platform Convenience Fees.")

cart_df = calculate_effective_cart_gap(df)

# Melt for stacked bar
cart_melted = cart_df.melt(
    id_vars=["competitor_name", "platform_type"],
    value_vars=["avg_selling_price", "avg_shipping_fee", "avg_platform_fee"],
    var_name="Fee Component",
    value_name="Amount (₹)"
)
cart_melted["Fee Component"] = cart_melted["Fee Component"].map({
    "avg_selling_price": "Base Selling Price",
    "avg_shipping_fee": "Delivery / Shipping Fee",
    "avg_platform_fee": "Platform Fee"
})

fig_cart = px.bar(
    cart_melted,
    x="competitor_name",
    y="Amount (₹)",
    color="Fee Component",
    barmode="stack",
    color_discrete_sequence=["#1E3A8A", "#F59E0B", "#EF4444"],
    title="Average Checkout Cart Price Decomposition by Competitor Platform",
    labels={"competitor_name": "Competitor Platform", "Amount (₹)": "Mean Amount (₹)"}
)
fig_cart.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    height=380,
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_cart, use_container_width=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# 3. Competitor Stock-Out Tactical Surge Monitor (F-07)
st.markdown("### ⚡ Competitor Stock-Out Tactical Surge Monitor (F-07)")
st.markdown("Products currently tagged as **Out of Stock** on competing platforms represent immediate demand capture opportunities without competitive price retaliation.")

stockouts = get_stock_out_opportunities(df)

if stockouts.empty:
    st.info("No competitor stock-out anomalies detected in the currently filtered segment.")
else:
    st.dataframe(
        stockouts.rename(columns={
            "sku_code": "SKU Code",
            "product_name": "Product Name",
            "category_name": "Category",
            "competitor_name": "Stocked-Out Competitor",
            "selling_price": "Our Price (₹)",
            "market_avg_price": "Market Benchmark (₹)",
            "rating_value": "Customer Rating"
        }),
        use_container_width=True,
        hide_index=True
    )
