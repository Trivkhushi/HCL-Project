"""
pages/3_Trends.py
UI-03: Temporal Trends & Volatility Tracker
Features: F-05, F-08
User Stories: US-05, US-08
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_loader import load_price_history, load_pricing_view
from src.analytics import calculate_cv_volatility
from src.ui import render_tailwind_header, render_kpi_card

st.set_page_config(
    page_title="Temporal Trends & Volatility | PriceIntel Pro",
    page_icon="📈",
    layout="wide"
)

# Load data
df_history = load_price_history()
df_view = load_pricing_view()

# Header
render_tailwind_header(
    title="Temporal Trends & Volatility Tracker",
    subtitle="30-day multi-platform price histories, weekend repricing surges, and Coefficient of Variation (CV %) (UI-03)",
    badge_text="F-05 | F-08"
)

st.markdown("<br>", unsafe_allow_html=True)

# 1. 30-Day Multi-Platform Price Trajectory (F-05)
st.markdown("### 📅 30-Day Longitudinal Price Trajectory (F-05)")

# SKU Selection
sku_list = df_history[["sku_code", "product_name", "category_name"]].drop_duplicates()
sku_options = {f"{row['sku_code']} - {row['product_name']} ({row['category_name']})": row['sku_code'] for _, row in sku_list.iterrows()}

selected_sku_label = st.selectbox(
    "Select Target SKU for Longitudinal Analysis",
    options=list(sku_options.keys()),
    index=0
)
selected_sku_code = sku_options[selected_sku_label]

# Filter history for selected SKU
sku_hist = df_history[df_history["sku_code"] == selected_sku_code].sort_values("effective_date")

if sku_hist.empty:
    st.info("No historical snapshots available for the selected SKU.")
else:
    fig_hist = px.line(
        sku_hist,
        x="effective_date",
        y="recorded_price",
        color="competitor_name",
        markers=True,
        labels={"effective_date": "Snapshot Date", "recorded_price": "Price (₹)", "competitor_name": "Platform"},
        title=f"30-Day Price Cadence: {selected_sku_label}",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_hist.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=380,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# 2. Competitor Price Volatility Ranker (CV %) (F-08)
st.markdown("### 🌪️ Competitor Price Volatility Ranking (CV %) (F-08)")
st.markdown("""
The **Coefficient of Variation** ($CV\\% = \\frac{\\sigma}{\\mu} \\times 100$) quantifies dynamic repricing intensity independent of absolute price scales.
Platforms with $CV > 6\\%$ actively employ algorithmic dynamic repricing (frequent weekend surges and flash discounts).
""")

vol_df = calculate_cv_volatility(df_history)

col_chart, col_table = st.columns([3, 2])

with col_chart:
    fig_vol = px.bar(
        vol_df,
        y="competitor_name",
        x="cv_pct",
        orientation="h",
        color="volatility_rating",
        color_discrete_map={
            "High Volatility": "#EF4444",
            "Moderate Volatility": "#F59E0B",
            "Stable Pricing": "#10B981"
        },
        text=vol_df["cv_pct"].apply(lambda v: f"{v:.2f}%"),
        labels={"cv_pct": "Coefficient of Variation (CV %)", "competitor_name": "Competitor"},
        title="Dynamic Repricing Intensity Ranking (CV %)"
    )
    fig_vol.update_traces(textposition="outside", cliponaxis=False)
    fig_vol.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=340,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig_vol, use_container_width=True)

with col_table:
    st.markdown("#### Volatility Metrics Table")
    st.dataframe(
        vol_df.rename(columns={
            "competitor_name": "Platform",
            "platform_type": "Type",
            "mean_price": "Mean Price (₹)",
            "std_price": "Std Dev (₹)",
            "cv_pct": "CV %",
            "revisions_count": "Revisions",
            "volatility_rating": "Rating"
        }),
        use_container_width=True,
        hide_index=True
    )
