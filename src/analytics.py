"""
src/analytics.py
Analytical calculation engine for Pricing Comparison Analytics.
Computes price variances, gross margin floors, Price Competitiveness Index (PCI),
effective cart fee gaps, and platform price volatility (CV %).
"""

import pandas as pd
import numpy as np

def calculate_category_variance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes mean percentage price variance per product category against market benchmarks.
    """
    variance_df = df.groupby("category_name", observed=True).agg(
        avg_selling_price=("selling_price", "mean"),
        avg_market_price=("market_avg_price", "mean"),
        sku_count=("product_id", "nunique")
    ).reset_index()
    
    variance_df["price_variance_pct"] = (
        (variance_df["avg_selling_price"] - variance_df["avg_market_price"]) / variance_df["avg_market_price"]
    ) * 100.0
    
    variance_df["variance_status"] = np.where(
        variance_df["price_variance_pct"] > 3.0, "Overpriced (>3%)",
        np.where(variance_df["price_variance_pct"] < -3.0, "Underpriced (<-3%)", "Par (Competitive)")
    )
    return variance_df.round(2)

def get_margin_bleed_skus(df: pd.DataFrame, min_margin_threshold: float = 0.10) -> pd.DataFrame:
    """
    Filters and flags all SKUs where gross profit margin is below the specified margin floor.
    """
    threshold_pct = min_margin_threshold * 100.0
    bleed_df = df[df["gross_margin_pct"] < threshold_pct].copy()
    
    bleed_df["margin_risk_severity"] = np.where(
        bleed_df["gross_margin_pct"] < 5.0, "Critical Bleed (<5%)", "Moderate Risk (5-10%)"
    )
    return bleed_df.sort_values("gross_margin_pct", ascending=True)

def calculate_pci_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes distribution counts and percentage shares across Price Competitiveness Index (PCI) tiers.
    """
    total = len(df)
    if total == 0:
        return pd.DataFrame()
        
    pci_counts = df["pci_tier"].value_counts().reset_index()
    pci_counts.columns = ["pci_tier", "sku_count"]
    pci_counts["percentage_share"] = ((pci_counts["sku_count"] / total) * 100.0).round(1)
    
    # Custom sort: Underpriced, Par, Overpriced
    tier_order = {"Underpriced": 0, "Par": 1, "Overpriced": 2}
    pci_counts["order"] = pci_counts["pci_tier"].map(tier_order)
    return pci_counts.sort_values("order").drop(columns=["order"])

def calculate_effective_cart_gap(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates Base Selling Price, Delivery Charges, and Platform Fees per competitor platform.
    """
    cart_df = df.groupby(["competitor_name", "platform_type"], observed=True).agg(
        avg_selling_price=("selling_price", "mean"),
        avg_shipping_fee=("shipping_fee", "mean"),
        avg_platform_fee=("platform_fee", "mean"),
        avg_effective_cart_price=("effective_cart_price", "mean")
    ).reset_index()
    return cart_df.round(2).sort_values("avg_effective_cart_price", ascending=True)

def calculate_cv_volatility(df_history: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the Coefficient of Variation (CV % = std / mean * 100) per competitor platform over 30 days.
    """
    vol_df = df_history.groupby(["competitor_name", "platform_type"], observed=True)["recorded_price"].agg(
        mean_price="mean",
        std_price="std",
        revisions_count="count"
    ).reset_index()
    
    vol_df["cv_pct"] = ((vol_df["std_price"] / vol_df["mean_price"]) * 100.0).round(2)
    vol_df["volatility_rating"] = np.where(
        vol_df["cv_pct"] > 6.0, "High Volatility",
        np.where(vol_df["cv_pct"] > 3.0, "Moderate Volatility", "Stable Pricing")
    )
    return vol_df.sort_values("cv_pct", ascending=False)

def get_top_overpriced_skus(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Returns top N SKUs with highest Price Competitiveness Index (potential sales leakage).
    """
    return df.sort_values("price_competitiveness_index", ascending=False).head(n)[
        ["sku_code", "product_name", "category_name", "competitor_name", "selling_price", "market_avg_price", "price_competitiveness_index"]
    ]

def get_stock_out_opportunities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters in-stock SKUs where competitors are currently 'Out of Stock' (tactical surge opportunity).
    """
    return df[df["stock_status"] == "Out of Stock"][
        ["sku_code", "product_name", "category_name", "competitor_name", "selling_price", "market_avg_price", "rating_value"]
    ]
