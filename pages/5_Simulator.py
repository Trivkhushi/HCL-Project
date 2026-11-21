"""
pages/5_Simulator.py
UI-05: What-If Pricing Strategy Simulator
Features: F-11
User Stories: US-11
"""

import streamlit as st
import pandas as pd
from src.data_loader import load_pricing_view
from src.simulator import simulate_price_matching
from src.ui import render_tailwind_header, render_kpi_card, render_alert_box

st.set_page_config(
    page_title="What-If Pricing Simulator | PriceIntel Pro",
    page_icon="🔮",
    layout="wide"
)

# Load data
df = load_pricing_view()

# Header
render_tailwind_header(
    title="What-If Pricing Simulation & Demand Elasticity",
    subtitle="Microeconomic price elasticity modeling, volume projections, and gross margin optimization (UI-05)",
    badge_text="F-11"
)

st.markdown("<br>", unsafe_allow_html=True)

# 1. Interactive Control Form
st.markdown("### ⚙️ Simulation Parameters & SKU Selection")

sku_options = {
    f"{row['sku_code']} - {row['product_name']} (Cur: ₹{row['selling_price']:,.2f} | Cost: ₹{row['cost_price']:,.2f})": row
    for _, row in df.drop_duplicates(subset=["sku_code"]).iterrows()
}

selected_label = st.selectbox("Select Target Product to Simulate", options=list(sku_options.keys()), index=0)
selected_row = sku_options[selected_label]

base_price = float(selected_row["selling_price"])
cost_price = float(selected_row["cost_price"])
base_mrp = float(selected_row["mrp"])

col_param1, col_param2, col_param3 = st.columns(3)

with col_param1:
    target_price = st.slider(
        "Proposed Reprice Target (₹)",
        min_value=round(cost_price * 0.9, 1),
        max_value=round(base_mrp * 1.1, 1),
        value=round(base_price * 0.95, 1),
        step=5.0,
        help="Simulate matching a lower competitor price or executing a strategic price increase."
    )

with col_param2:
    elasticity = st.slider(
        "Price Elasticity of Demand (e)",
        min_value=-3.5,
        max_value=-0.2,
        value=-1.5,
        step=0.1,
        help="Percentage change in quantity demanded per 1% price change (typically -1.0 to -2.5 in retail e-commerce)."
    )

with col_param3:
    base_volume = st.number_input(
        "Baseline Monthly Unit Volume",
        min_value=50,
        max_value=10000,
        value=500,
        step=50,
        help="Estimated baseline monthly sales volume for this product."
    )

# Run simulation
sim_res = simulate_price_matching(
    base_price=base_price,
    cost_price=cost_price,
    base_volume=base_volume,
    target_price=target_price,
    elasticity=elasticity
)

st.markdown("<br>", unsafe_allow_html=True)

# 2. Strategic Verdict Banner
render_alert_box(
    title=f"TACTICAL PRICING DIRECTIVE: {sim_res['rec_type'].upper()}",
    message=sim_res["recommendation"],
    alert_type=sim_res["rec_type"]
)

st.markdown("<br>", unsafe_allow_html=True)

# 3. Dynamic KPI Comparison Ribbon
st.markdown("### 📊 Projected Commercial Impact")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    vol_delta = f"{sim_res['volume_growth_pct']:+.1f}% ({sim_res['new_volume'] - sim_res['base_volume']:+d} units)"
    render_kpi_card(
        "Projected Volume",
        f"{sim_res['new_volume']:,} units",
        vol_delta,
        "positive" if sim_res["new_volume"] >= sim_res["base_volume"] else "negative"
    )

with kpi2:
    rev_delta = f"{sim_res['revenue_growth_pct']:+.1f}%"
    render_kpi_card(
        "Projected Revenue",
        f"₹{sim_res['new_revenue']:,.2f}",
        f"Delta: ₹{sim_res['delta_revenue']:+,.2f} ({rev_delta})",
        "positive" if sim_res["delta_revenue"] >= 0 else "negative"
    )

with kpi3:
    margin_delta = f"{sim_res['margin_growth_pct']:+.1f}%"
    render_kpi_card(
        "Projected Gross Profit",
        f"₹{sim_res['new_margin_val']:,.2f}",
        f"Delta: ₹{sim_res['delta_margin_val']:+,.2f} ({margin_delta})",
        "positive" if sim_res["delta_margin_val"] >= 0 else "negative"
    )

with kpi4:
    m_pct_delta = f"{sim_res['new_margin_pct'] - sim_res['current_margin_pct']:+.1f}% pts"
    render_kpi_card(
        "New Gross Margin %",
        f"{sim_res['new_margin_pct']:.1f}%",
        f"Base: {sim_res['current_margin_pct']:.1f}% ({m_pct_delta})",
        "positive" if sim_res["new_margin_pct"] >= 10.0 else "negative"
    )

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# 4. Detailed Economic Breakdown
st.markdown("### 📐 Microeconomic Simulation Breakdown")
breakdown_df = pd.DataFrame([
    {"Metric": "Selling Price (₹)", "Current Baseline": f"₹{sim_res['base_price']:,.2f}", "Simulated Scenario": f"₹{sim_res['target_price']:,.2f}", "Net Variance": f"{sim_res['price_change_pct']:+.2f}%"},
    {"Metric": "Unit Demand Volume", "Current Baseline": f"{sim_res['base_volume']:,} units", "Simulated Scenario": f"{sim_res['new_volume']:,} units", "Net Variance": f"{sim_res['volume_growth_pct']:+.2f}%"},
    {"Metric": "Monthly Gross Revenue (₹)", "Current Baseline": f"₹{sim_res['current_revenue']:,.2f}", "Simulated Scenario": f"₹{sim_res['new_revenue']:,.2f}", "Net Variance": f"₹{sim_res['delta_revenue']:+,.2f}"},
    {"Metric": "Monthly Gross Profit (₹)", "Current Baseline": f"₹{sim_res['current_margin_val']:,.2f}", "Simulated Scenario": f"₹{sim_res['new_margin_val']:,.2f}", "Net Variance": f"₹{sim_res['delta_margin_val']:+,.2f}"},
    {"Metric": "Gross Profit Margin (%)", "Current Baseline": f"{sim_res['current_margin_pct']:.2f}%", "Simulated Scenario": f"{sim_res['new_margin_pct']:.2f}%", "Net Variance": f"{sim_res['new_margin_pct'] - sim_res['current_margin_pct']:+.2f}% pts"}
])
st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
