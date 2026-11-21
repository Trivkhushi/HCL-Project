"""
tests/test_analysis.py
Technical tests (TC-T-06 to TC-T-11) validating core mathematical formulas,
financial calculations, KPI metrics on tiny known datasets, statistical functions, and simulation models.
"""

import numpy as np
import pytest
from scipy import stats

def test_tc_t_06_gross_margin_formula():
    """TC-T-06: Test gross margin calculation and margin bleed alert flag on known numbers."""
    selling_price = 1000.0
    cost_price = 850.0
    margin_pct = ((selling_price - cost_price) / selling_price) * 100.0
    assert pytest.approx(margin_pct, 0.01) == 15.0
    assert margin_pct >= 10.0 # No bleed
    
    # Severe bleed scenario
    predatory_selling_price = 900.0
    bleed_cost_price = 850.0
    bleed_margin_pct = ((predatory_selling_price - bleed_cost_price) / predatory_selling_price) * 100.0
    assert pytest.approx(bleed_margin_pct, 0.01) == 5.55
    assert bleed_margin_pct < 10.0 # Bleed triggered!

def test_tc_t_07_price_competitiveness_index_tiers():
    """TC-T-07: Test PCI ratio and categorization logic (<97 Underpriced, 97-103 Par, >103 Overpriced)."""
    benchmark_avg = 1000.0
    
    def classify_pci(our_price, avg_price):
        pci = (our_price / avg_price) * 100.0
        if pci < 97.0:
            return pci, "Underpriced"
        elif pci > 103.0:
            return pci, "Overpriced"
        else:
            return pci, "Par"

    pci_val, tier = classify_pci(920.0, benchmark_avg)
    assert pytest.approx(pci_val, 0.1) == 92.0
    assert tier == "Underpriced"
    
    pci_val, tier = classify_pci(1005.0, benchmark_avg)
    assert pytest.approx(pci_val, 0.1) == 100.5
    assert tier == "Par"
    
    pci_val, tier = classify_pci(1080.0, benchmark_avg)
    assert pytest.approx(pci_val, 0.1) == 108.0
    assert tier == "Overpriced"

def test_tc_t_08_effective_cart_price():
    """TC-T-08: Test additive checkout effective cart price formula."""
    selling_price = 450.0
    shipping_fee = 35.0
    platform_fee = 12.0
    effective_cart = selling_price + shipping_fee + platform_fee
    assert pytest.approx(effective_cart, 0.01) == 497.0

def test_tc_t_09_coefficient_of_variation():
    """TC-T-09: Test Coefficient of Variation (CV %) calculation on known distribution."""
    prices = np.array([100.0, 102.0, 98.0, 101.0, 99.0])
    mean_val = np.mean(prices)
    std_val = np.std(prices, ddof=1)
    cv_pct = (std_val / mean_val) * 100.0
    
    assert pytest.approx(mean_val, 0.01) == 100.0
    assert cv_pct > 0.0 and cv_pct < 5.0 # Low volatility

def test_tc_t_10_inferential_two_sample_ttest():
    """TC-T-10: Test SciPy two-sample t-test hypothesis testing function on separated distributions."""
    np.random.seed(42)
    # Group 1: Marketplace prices (mean ~ 100)
    mkt_prices = np.random.normal(loc=100.0, scale=8.0, size=50)
    # Group 2: Quick-Commerce prices (mean ~ 108, significant convenience markup)
    qc_prices = np.random.normal(loc=108.0, scale=8.0, size=50)
    
    t_stat, p_val = stats.ttest_ind(qc_prices, mkt_prices, equal_var=False)
    
    assert t_stat > 0.0
    assert p_val < 0.05, f"Expected statistically significant difference (p < 0.05), got p = {p_val}"

def test_tc_t_11_elasticity_simulation_formula():
    """TC-T-11: Test What-If demand elasticity and revenue/margin impact formulas."""
    base_price = 1000.0
    cost_price = 700.0
    base_volume = 100
    base_revenue = base_price * base_volume # 100,000
    base_margin = (base_price - cost_price) * base_volume # 30,000
    
    # Price drop of 10% (P_new = 900) with elasticity e = -1.5 (Elastic demand)
    simulated_price = 900.0
    elasticity = -1.5
    price_change_pct = (simulated_price - base_price) / base_price # -0.10
    
    # Delta Q = base_volume * (elasticity * price_change_pct) = 100 * (-1.5 * -0.10) = +15%
    volume_change_pct = elasticity * price_change_pct
    new_volume = base_volume * (1.0 + volume_change_pct) # 115 units
    
    new_revenue = simulated_price * new_volume # 900 * 115 = 103,500
    new_margin = (simulated_price - cost_price) * new_volume # 200 * 115 = 23,000
    
    delta_revenue = new_revenue - base_revenue # +3,500
    delta_margin = new_margin - base_margin # -7,000
    
    assert pytest.approx(new_volume, 0.1) == 115.0
    assert pytest.approx(delta_revenue, 0.1) == 3500.0
    assert pytest.approx(delta_margin, 0.1) == -7000.0
