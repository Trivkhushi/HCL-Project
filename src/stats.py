"""
src/stats.py
Inferential statistical testing and correlation modeling for Pricing Comparison Analytics.
Implements two-sample t-tests, Mann-Whitney U fallback, Pearson/Spearman correlation, and one-way ANOVA.
"""

import pandas as pd
import numpy as np
from scipy import stats

def run_quickcomm_vs_market_ttest(df: pd.DataFrame, category: str = "FMCG", alpha: float = 0.05) -> dict:
    """
    Executes an inferential hypothesis test comparing Quick-Commerce vs Marketplace FMCG prices.
    H0: mu_quick = mu_mkt (No significant difference in average price)
    H1: mu_quick != mu_mkt (Significant price difference exists)
    """
    cat_df = df[df["category_name"] == category].copy()
    
    qc_prices = cat_df[cat_df["platform_type"] == "Quick-Commerce"]["selling_price"].dropna().values
    mkt_prices = cat_df[cat_df["platform_type"] == "Marketplace"]["selling_price"].dropna().values
    
    if len(qc_prices) < 3 or len(mkt_prices) < 3:
        return {
            "test_name": "Insufficient Sample Size",
            "stat": 0.0,
            "p_value": 1.0,
            "mean_qc": 0.0,
            "mean_mkt": 0.0,
            "premium_pct": 0.0,
            "reject_h0": False,
            "conclusion": "Insufficient sample data in selected category to conduct a reliable statistical test."
        }
        
    # Check normality using Shapiro-Wilk test
    _, p_norm_qc = stats.shapiro(qc_prices) if len(qc_prices) <= 50 else (0, 0.5)
    _, p_norm_mkt = stats.shapiro(mkt_prices) if len(mkt_prices) <= 50 else (0, 0.5)
    
    mean_qc = float(np.mean(qc_prices))
    mean_mkt = float(np.mean(mkt_prices))
    premium_pct = round(((mean_qc - mean_mkt) / mean_mkt) * 100.0, 2)
    
    # If both normal (p > 0.05), use Welch's t-test; else fallback to Mann-Whitney U test
    if p_norm_qc > 0.05 and p_norm_mkt > 0.05:
        test_name = "Two-Sample Welch's t-Test (Parametric)"
        t_stat, p_val = stats.ttest_ind(qc_prices, mkt_prices, equal_var=False)
    else:
        test_name = "Mann-Whitney U Test (Non-Parametric Fallback)"
        u_stat, p_val = stats.mannwhitneyu(qc_prices, mkt_prices, alternative='two-sided')
        t_stat = u_stat

    reject_h0 = bool(p_val < alpha)
    
    if reject_h0:
        conclusion = (
            f"Statistically Significant (p = {p_val:.6f} < {alpha}). We formally REJECT the null hypothesis. "
            f"Quick-Commerce platforms command an average convenience markup of +{premium_pct}% over traditional marketplaces."
        )
    else:
        conclusion = (
            f"Not Statistically Significant (p = {p_val:.4f} >= {alpha}). We FAIL TO REJECT the null hypothesis. "
            f"Observed price difference ({premium_pct}%) is within expected random sampling variation."
        )

    return {
        "test_name": test_name,
        "stat": round(float(t_stat), 4),
        "p_value": float(p_val),
        "mean_qc": round(mean_qc, 2),
        "mean_mkt": round(mean_mkt, 2),
        "premium_pct": premium_pct,
        "reject_h0": reject_h0,
        "conclusion": conclusion
    }

def calculate_discount_review_correlation(df: pd.DataFrame) -> dict:
    """
    Computes Pearson r and Spearman rho correlations between discount_pct and review_count.
    Fits an OLS regression trendline.
    """
    valid_data = df.dropna(subset=["discount_pct", "review_count"]).copy()
    valid_data = valid_data[valid_data["review_count"] > 0]
    
    if len(valid_data) < 5:
        return {"r": 0.0, "p_val": 1.0, "rho": 0.0, "slope": 0.0, "intercept": 0.0, "r_squared": 0.0}
        
    x = valid_data["discount_pct"].values
    y = valid_data["review_count"].values
    
    r_val, p_val = stats.pearsonr(x, y)
    rho_val, rho_p = stats.spearmanr(x, y)
    slope, intercept, _, _, _ = stats.linregress(x, y)
    
    return {
        "r": round(float(r_val), 3),
        "p_value": float(p_val),
        "rho": round(float(rho_val), 3),
        "rho_p_value": float(rho_p),
        "slope": round(float(slope), 2),
        "intercept": round(float(intercept), 2),
        "r_squared": round(float(r_val ** 2), 3)
    }

def run_platform_anova(df: pd.DataFrame) -> dict:
    """
    Executes a one-way ANOVA evaluating whether selling prices differ significantly across competitor platforms.
    """
    groups = [group["selling_price"].dropna().values for _, group in df.groupby("competitor_name", observed=True)]
    groups = [g for g in groups if len(g) >= 5]
    
    if len(groups) < 2:
        return {"f_stat": 0.0, "p_value": 1.0, "reject_h0": False}
        
    f_stat, p_val = stats.f_oneway(*groups)
    return {
        "f_stat": round(float(f_stat), 3),
        "p_value": float(p_val),
        "reject_h0": bool(p_val < 0.05)
    }
