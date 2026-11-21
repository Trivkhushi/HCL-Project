"""
src/simulator.py
Interactive what-if pricing simulation and demand elasticity modeling for Pricing Comparison Analytics.
Forecasts unit sales volume shift, revenue delta, and gross profit margin trade-offs.
"""

def simulate_price_matching(
    base_price: float,
    cost_price: float,
    base_volume: int,
    target_price: float,
    elasticity: float = -1.5
) -> dict:
    """
    Simulates commercial outcome of dynamic repricing based on microeconomic price elasticity of demand.
    Formula: Delta_Q = Q_0 * e * (Delta_P / P_0)
    """
    if base_price <= 0 or base_volume <= 0:
        return {}
        
    price_change_pct = (target_price - base_price) / base_price
    volume_change_pct = elasticity * price_change_pct
    
    # New demand volume bounded at non-negative
    new_volume = max(0, int(round(base_volume * (1.0 + volume_change_pct))))
    
    # Financial calculations
    current_revenue = base_price * base_volume
    new_revenue = target_price * new_volume
    delta_revenue = new_revenue - current_revenue
    revenue_growth_pct = (delta_revenue / current_revenue) * 100.0 if current_revenue > 0 else 0.0
    
    current_margin_val = (base_price - cost_price) * base_volume
    new_margin_val = (target_price - cost_price) * new_volume
    delta_margin_val = new_margin_val - current_margin_val
    margin_growth_pct = (delta_margin_val / current_margin_val) * 100.0 if current_margin_val > 0 else 0.0
    
    current_margin_pct = ((base_price - cost_price) / base_price) * 100.0
    new_margin_pct = ((target_price - cost_price) / target_price) * 100.0 if target_price > 0 else 0.0
    
    # Strategy evaluation
    if delta_margin_val > 0 and delta_revenue > 0:
        recommendation = "ACCELERATE PRICE MATCH: Strong volume expansion exceeds price concession, boosting both revenue and net gross profit."
        rec_type = "success"
    elif delta_revenue > 0 and delta_margin_val <= 0:
        recommendation = "CAUTION (VOLUME OVER PROFIT): Generates top-line revenue growth (+{:.1f}%), but unit gross profit contracts by INR {:,.2f}. Consider partial match.".format(revenue_growth_pct, abs(delta_margin_val))
        rec_type = "warning"
    else:
        recommendation = "DO NOT MATCH (MARGIN BLEED): Inelastic demand fails to compensate for price cut, triggering both revenue and margin destruction."
        rec_type = "danger"

    return {
        "base_price": round(base_price, 2),
        "target_price": round(target_price, 2),
        "cost_price": round(cost_price, 2),
        "price_change_pct": round(price_change_pct * 100.0, 2),
        "base_volume": base_volume,
        "new_volume": new_volume,
        "volume_growth_pct": round(volume_change_pct * 100.0, 2),
        "current_revenue": round(current_revenue, 2),
        "new_revenue": round(new_revenue, 2),
        "delta_revenue": round(delta_revenue, 2),
        "revenue_growth_pct": round(revenue_growth_pct, 2),
        "current_margin_val": round(current_margin_val, 2),
        "new_margin_val": round(new_margin_val, 2),
        "delta_margin_val": round(delta_margin_val, 2),
        "margin_growth_pct": round(margin_growth_pct, 2),
        "current_margin_pct": round(current_margin_pct, 2),
        "new_margin_pct": round(new_margin_pct, 2),
        "recommendation": recommendation,
        "rec_type": rec_type
    }
