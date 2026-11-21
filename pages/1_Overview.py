"""
pages/1_Overview.py
UI-01: Executive Overview & KPI Dashboard
Features: F-01, F-04, F-06
User Stories: US-01, US-04, US-06
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_loader import load_pricing_view, apply_global_filters
from src.analytics import (
    calculate_category_variance,
    calculate_pci_distribution,
    get_top_overpriced_skus,
    get_margin_bleed_skus
)
from src.ui import render_tailwind_header, render_kpi_card

st.set_page_config(
    page_title="Executive Overview | PriceIntel Pro",
    page_icon="📊",
    layout="wide"
)

# Load data
df_raw = load_pricing_view()

# Sidebar filters inherited or standalone
with st.sidebar:
    st.markdown("### 🔍 Filters")
    all_categories = sorted(df_raw["category_name"].unique().tolist())
    all_competitors = sorted(df_raw["competitor_name"].unique().tolist())
    
    sel_categories = st.multiselect(
        "Categories",
        options=all_categories,
        default=st.session_state.get("global_filter_categories", all_categories),
        key="overview_categories"
    )
    sel_competitors = st.multiselect(
        "Competitor Platforms",
        options=all_competitors,
        default=st.session_state.get("global_filter_competitors", all_competitors),
        key="overview_competitors"
    )

df = apply_global_filters(df_raw, sel_categories, sel_competitors)

if df.empty:
    st.warning("No records match the selected filters. Please adjust your criteria.")
    st.stop()

# Header
render_tailwind_header(
    title="Executive Overview & Market KPIs",
    subtitle="Continuous competitive benchmarking, price variance, and competitiveness tiers (UI-01)",
    badge_text="F-01 | F-04 | F-06"
)

st.markdown("<br>", unsafe_allow_html=True)

# 1. Executive Metric Ribbon (F-01)
col1, col2, col3, col4 = st.columns(4)

total_skus = len(df)
mean_var_pct = ((df["selling_price"] - df["market_avg_price"]) / df["market_avg_price"] * 100.0).mean()
pci_dist = calculate_pci_distribution(df)
underpriced_pct = pci_dist[pci_dist["pci_tier"] == "Underpriced"]["percentage_share"].sum() if not pci_dist.empty else 0.0
bleed_skus = len(get_margin_bleed_skus(df, min_margin_threshold=0.10))

with col1:
    render_kpi_card("Monitored SKUs", f"{total_skus:,}", f"{len(df_raw)} In Catalog", "neutral")
with col2:
    var_label = f"{mean_var_pct:+.2f}%"
    delta_type = "positive" if abs(mean_var_pct) <= 2.0 else ("negative" if mean_var_pct > 2.0 else "neutral")
    render_kpi_card("Mean Price Variance", var_label, "vs Market Benchmark", delta_type)
with col3:
    render_kpi_card("Underpriced Share", f"{underpriced_pct:.1f}%", "Highly Competitive", "positive")
with col4:
    render_kpi_card("Margin Bleed SKUs", str(bleed_skus), "Margin < 10%", "negative" if bleed_skus > 0 else "positive")

st.markdown("<br>", unsafe_allow_html=True)

# 2. Charts Section (F-01, F-04)
chart_col1, chart_col2 = st.columns([3, 2])

with chart_col1:
    st.markdown("### 🏷️ Category Price Variance % (F-01)")
    var_df = calculate_category_variance(df)
    
    # Color map: red if overpriced, green if underpriced, blue if par
    color_map = {
        "Overpriced (>3%)": "#EF4444",
        "Underpriced (<-3%)": "#10B981",
        "Par (Competitive)": "#3B82F6"
    }
    
    fig_var = px.bar(
        var_df,
        x="category_name",
        y="price_variance_pct",
        color="variance_status",
        color_discrete_map=color_map,
        text=var_df["price_variance_pct"].apply(lambda v: f"{v:+.1f}%"),
        labels={"category_name": "Category", "price_variance_pct": "Price Variance % vs Market"},
        title="Price Variance % Relative to Market Benchmark"
    )
    fig_var.add_hline(y=0, line_dash="dash", line_color="#64748B")
    fig_var.update_traces(textposition="outside", cliponaxis=False)
    fig_var.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=360,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_var, use_container_width=True)

with chart_col2:
    st.markdown("### 🎯 Price Competitiveness (PCI) (F-04)")
    if not pci_dist.empty:
        fig_pci = px.pie(
            pci_dist,
            names="pci_tier",
            values="sku_count",
            hole=0.55,
            color="pci_tier",
            color_discrete_map={"Underpriced": "#10B981", "Par": "#3B82F6", "Overpriced": "#EF4444"},
            title="Distribution by PCI Tiers"
        )
        fig_pci.update_layout(
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            height=360,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_pci, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# 3. Top 5 Overpriced SKUs Table (F-06)
st.markdown("### ⚠️ Top 5 Overpriced SKUs (Potential Sales Leakage) (F-06)")
st.markdown("These products command the highest price premium relative to market benchmarks, exposing the catalog to conversion loss.")

top_overpriced = get_top_overpriced_skus(df, n=5)
st.dataframe(
    top_overpriced.rename(columns={
        "sku_code": "SKU Code",
        "product_name": "Product Name",
        "category_name": "Category",
        "competitor_name": "Competitor Platform",
        "selling_price": "Our Price (₹)",
        "market_avg_price": "Market Avg (₹)",
        "price_competitiveness_index": "PCI Index"
    }),
    use_container_width=True,
    hide_index=True
)
