"""
app.py
Main entrypoint for PriceIntel Pro - Pricing Comparison Analytics.
ABES Engineering College - MCA Final Year Capstone Project
Learner: Khushi Trivedi (Roll No: 2500320140080)
Guide: Mrs. Kalpana Diwedi
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_loader import load_pricing_view, apply_global_filters
from src.analytics import get_margin_bleed_skus
from src.ui import render_tailwind_header, render_kpi_card, render_alert_box

# 1. Page Configuration
st.set_page_config(
    page_title="PriceIntel Pro | Pricing Analytics",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Global Styling Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #F8FAFC;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
    }
    
    /* Clean Cards */
    .dashboard-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 0.75rem;
        padding: 1.25rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #CBD5E1;
    }
    
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# 3. Data Loading
try:
    df_raw = load_pricing_view()
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

# 4. Sidebar Controls & Global State Management
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid #334155;">
        <h2 style="color: #60A5FA; margin: 0; font-size: 1.4rem; font-weight: 800;">🏷️ PriceIntel Pro</h2>
        <p style="color: #94A3B8; font-size: 0.8rem; margin: 4px 0 0 0;">Pricing Comparison & Margin Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔍 Global Filters")

    # Categories
    all_categories = sorted(df_raw["category_name"].unique().tolist())
    selected_categories = st.multiselect(
        "Select Categories",
        options=all_categories,
        default=all_categories,
        key="global_filter_categories"
    )

    # Competitors
    all_competitors = sorted(df_raw["competitor_name"].unique().tolist())
    selected_competitors = st.multiselect(
        "Select Competitor Platforms",
        options=all_competitors,
        default=all_competitors,
        key="global_filter_competitors"
    )

    if st.button("Reset Global Filters", use_container_width=True):
        st.session_state["global_filter_categories"] = all_categories
        st.session_state["global_filter_competitors"] = all_competitors
        st.rerun()

    st.markdown("<br><hr style='border-color: #334155;'><br>", unsafe_allow_html=True)
    
    # Academic & Guide Badge
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid #475569; border-radius: 0.5rem; padding: 0.85rem; font-size: 0.75rem;">
        <p style="color: #38BDF8; font-weight: 700; margin: 0 0 4px 0; text-transform: uppercase; letter-spacing: 0.05em;">Academic Metadata</p>
        <p style="color: #E2E8F0; margin: 2px 0;"><strong>Learner:</strong> Khushi Trivedi</p>
        <p style="color: #94A3B8; margin: 2px 0;">Roll No: 2500320140080</p>
        <p style="color: #94A3B8; margin: 2px 0;">MCA 2nd Year (Data Analytics)</p>
        <p style="color: #E2E8F0; margin: 6px 0 2px 0;"><strong>Guide:</strong> Mrs. Kalpana Diwedi</p>
        <p style="color: #94A3B8; margin: 2px 0;">ABES Engineering College</p>
    </div>
    """, unsafe_allow_html=True)

# 5. Apply Global Filters
df_filtered = apply_global_filters(df_raw, selected_categories, selected_competitors)

if df_filtered.empty:
    st.warning("No records match the current filter selection. Please broaden your category or competitor filter.")
    st.stop()

# 6. Hero Header
render_tailwind_header(
    title="PriceIntel Pro Enterprise",
    subtitle="Continuous competitive benchmarking, gross margin protection, and microeconomic simulation",
    badge_text="ABES MCA Capstone 2026"
)

st.markdown("<br>", unsafe_allow_html=True)

# 7. Executive KPI Metric Ribbon
col1, col2, col3, col4 = st.columns(4)

total_skus = len(df_filtered)
active_competitors = df_filtered["competitor_name"].nunique()
avg_price = df_filtered["selling_price"].mean()
margin_bleed_count = len(get_margin_bleed_skus(df_filtered, min_margin_threshold=0.10))

with col1:
    render_kpi_card(
        title="Active Monitored SKUs",
        value=f"{total_skus:,}",
        delta=f"{len(df_raw)} Total in Catalog",
        delta_type="neutral"
    )

with col2:
    render_kpi_card(
        title="Benchmarked Competitors",
        value=str(active_competitors),
        delta="Marketplace + Quick-Comm",
        delta_type="neutral"
    )

with col3:
    render_kpi_card(
        title="Average Selling Price",
        value=f"₹{avg_price:,.2f}",
        delta="Across Filtered SKUs",
        delta_type="neutral"
    )

with col4:
    render_kpi_card(
        title="Margin Bleed SKUs (<10%)",
        value=str(margin_bleed_count),
        delta="Requires Intervention" if margin_bleed_count > 0 else "Catalog Healthy",
        delta_type="negative" if margin_bleed_count > 0 else "positive"
    )

st.markdown("<br>", unsafe_allow_html=True)

# 8. Visual Summary Section
col_chart_left, col_chart_right = st.columns([3, 2])

with col_chart_left:
    st.markdown("### 📊 Category Pricing Landscape")
    cat_summary = df_filtered.groupby("category_name", observed=True).agg(
        avg_price=("selling_price", "mean"),
        sku_count=("product_id", "nunique")
    ).reset_index()
    
    fig_cat = px.bar(
        cat_summary,
        x="category_name",
        y="avg_price",
        text=cat_summary["avg_price"].apply(lambda v: f"₹{v:,.1f}"),
        color="category_name",
        color_discrete_sequence=px.colors.qualitative.Prism,
        labels={"category_name": "Product Category", "avg_price": "Mean Selling Price (₹)"},
        title="Mean Selling Price by Product Category"
    )
    fig_cat.update_traces(textposition="outside", cliponaxis=False)
    fig_cat.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        showlegend=False,
        height=340,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col_chart_right:
    st.markdown("### 🏢 Platform Distribution")
    platform_summary = df_filtered.groupby("platform_type", observed=True)["product_id"].count().reset_index()
    platform_summary.columns = ["Platform Type", "SKU Records"]
    
    fig_plat = px.pie(
        platform_summary,
        names="Platform Type",
        values="SKU Records",
        hole=0.55,
        color_discrete_sequence=["#1E3A8A", "#0D9488"],
        title="Marketplace vs Quick-Commerce Share"
    )
    fig_plat.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=340,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_plat, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# 9. Dashboard Modules Navigation Desk
st.markdown("### 🚀 Analytical Modules & System Capabilities")
st.markdown("Navigate using the sidebar to explore deep-dive analytics designed for retail strategy and data engineering.")

grid_col1, grid_col2, grid_col3 = st.columns(3)

with grid_col1:
    st.markdown("""
    <div class="dashboard-card">
        <h4 style="color: #1E3A8A; margin: 0 0 8px 0;">1. Executive Overview (UI-01)</h4>
        <p style="color: #475569; font-size: 0.85rem; margin: 0 0 10px 0;">
            Comprehensive KPI summary, category variance benchmark against market averages, and top overpriced SKUs prone to sales leakage.
        </p>
        <span style="color: #0284C7; font-size: 0.8rem; font-weight: 600;">Features: F-01, F-04, F-06</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="dashboard-card">
        <h4 style="color: #1E3A8A; margin: 0 0 8px 0;">2. Price Comparison & Bleed (UI-02)</h4>
        <p style="color: #475569; font-size: 0.85rem; margin: 0 0 10px 0;">
            Real-time margin bleed desk flagging SKUs below 10% floor, hidden delivery/platform fees, and competitor out-of-stock surge monitors.
        </p>
        <span style="color: #0284C7; font-size: 0.8rem; font-weight: 600;">Features: F-02, F-03, F-07</span>
    </div>
    """, unsafe_allow_html=True)

with grid_col2:
    st.markdown("""
    <div class="dashboard-card">
        <h4 style="color: #1E3A8A; margin: 0 0 8px 0;">3. Temporal Trends (UI-03)</h4>
        <p style="color: #475569; font-size: 0.85rem; margin: 0 0 10px 0;">
            30-day temporal price series tracking weekend dynamic repricing spikes and ranking competitor Coefficient of Variation (CV %).
        </p>
        <span style="color: #0284C7; font-size: 0.8rem; font-weight: 600;">Features: F-05, F-08</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="dashboard-card">
        <h4 style="color: #1E3A8A; margin: 0 0 8px 0;">4. Inferential Statistics (UI-04)</h4>
        <p style="color: #475569; font-size: 0.85rem; margin: 0 0 10px 0;">
            Rigorous statistical tests: Welch's t-test / Mann-Whitney U for quick-commerce markups, OLS regression, and one-way ANOVA.
        </p>
        <span style="color: #0284C7; font-size: 0.8rem; font-weight: 600;">Features: F-09, F-10</span>
    </div>
    """, unsafe_allow_html=True)

with grid_col3:
    st.markdown("""
    <div class="dashboard-card">
        <h4 style="color: #1E3A8A; margin: 0 0 8px 0;">5. What-If Simulator (UI-05)</h4>
        <p style="color: #475569; font-size: 0.85rem; margin: 0 0 10px 0;">
            Interactive microeconomic pricing simulator modeling unit volume elasticity, revenue expansion, and gross margin delta.
        </p>
        <span style="color: #0284C7; font-size: 0.8rem; font-weight: 600;">Features: F-11</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="dashboard-card">
        <h4 style="color: #1E3A8A; margin: 0 0 8px 0;">6. Diagnostics & About (UI-06 & 07)</h4>
        <p style="color: #475569; font-size: 0.85rem; margin: 0 0 10px 0;">
            Automated Z-score outlier detection, data quality health checks, star schema documentation, and academic project metadata.
        </p>
        <span style="color: #0284C7; font-size: 0.8rem; font-weight: 600;">Features: F-12, UI-07</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.8rem;">
    <strong>ABES Engineering College</strong> | Department of Computer Applications | MCA Final Year Project<br>
    Developed by <strong>Khushi Trivedi</strong> (Roll No: <code>2500320140080</code>) | Guided by <strong>Mrs. Kalpana Diwedi</strong>
</div>
""", unsafe_allow_html=True)
