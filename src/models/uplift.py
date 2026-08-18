"""
Ad Spend Elasticity and Diminishing Returns Response Curve Modeling.
"""

from typing import Dict, List
import numpy as np
import pandas as pd
from src.logging import get_logger

logger = get_logger("uplift_model")


def calculate_diminishing_returns_curve(
    recommended_budget: float,
    expected_roas: float = 4.5,
    margin_pct: float = 0.35,
    steps: int = 10
) -> pd.DataFrame:
    """
    Simulates a Hill/Logarithmic diminishing return response curve for budget sensitivity analysis.
    Formula:
      Revenue(Spend) = MaxRevenue * (Spend^alpha) / (Spend^alpha + K^alpha)
    """
    if recommended_budget <= 0:
        recommended_budget = 100000.0

    spend_levels = np.linspace(recommended_budget * 0.1, recommended_budget * 2.0, steps)

    # Saturation parameters
    max_multiplier = expected_roas * 1.3
    k = recommended_budget * 0.8
    alpha = 1.1

    records = []
    for spend in spend_levels:
        # Hill equation for incremental sales
        sales_lift_factor = (spend ** alpha) / (spend ** alpha + k ** alpha)
        inc_revenue = recommended_budget * max_multiplier * sales_lift_factor
        inc_profit = inc_revenue * margin_pct
        roas = inc_revenue / spend if spend > 0 else 0.0
        profit_roi = inc_profit / spend if spend > 0 else 0.0

        records.append({
            "spend": round(float(spend), 2),
            "projected_revenue": round(float(inc_revenue), 2),
            "projected_profit": round(float(inc_profit), 2),
            "effective_roas": round(float(roas), 2),
            "effective_profit_roi": round(float(profit_roi), 2),
            "is_optimal_point": bool(abs(spend - recommended_budget) < (recommended_budget * 0.1)),
        })

    return pd.DataFrame(records)
