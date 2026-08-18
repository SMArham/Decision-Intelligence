"""
Before vs After Optimization Evaluation Module.
Quantifies efficiency gains from switching from traditional blind ad spend
to need-basket & supply-aware decision intelligence.
"""

from typing import Dict, List
import pandas as pd
from src.logging import get_logger

logger = get_logger("before_after_analytics")


def calculate_before_after_metrics(
    total_budget: float = 100000.0,
    baseline_waste_rate: float = 0.25,
    optimized_waste_rate: float = 0.08,
    baseline_roas: float = 3.0,
    optimized_roas: float = 4.5,
    margin_pct: float = 0.35
) -> pd.DataFrame:
    """
    Computes comparative side-by-side metrics between:
    1. Baseline (Blind / Traditional Marketing)
    2. Optimized (Data-Driven Need + Supply Model)
    """
    # 1. Baseline Calculations
    base_ad_spend = total_budget
    base_wasted_spend = base_ad_spend * baseline_waste_rate
    base_effective_spend = base_ad_spend * (1.0 - baseline_waste_rate)
    base_inc_revenue = base_ad_spend * baseline_roas
    base_inc_profit = base_inc_revenue * margin_pct
    base_profit_roi = (base_inc_profit / base_ad_spend) if base_ad_spend > 0 else 0.0

    # 2. Optimized Calculations
    opt_ad_spend = total_budget
    opt_wasted_spend = opt_ad_spend * optimized_waste_rate
    opt_effective_spend = opt_ad_spend * (1.0 - optimized_waste_rate)
    opt_inc_revenue = opt_ad_spend * optimized_roas
    opt_inc_profit = opt_inc_revenue * margin_pct
    opt_profit_roi = (opt_inc_profit / opt_ad_spend) if opt_ad_spend > 0 else 0.0

    # 3. Deltas & Improvements
    metrics_data = [
        {
            "metric": "Total Ad Spend Deployed",
            "baseline_blind_marketing": base_ad_spend,
            "optimized_data_driven": opt_ad_spend,
            "absolute_change": 0.0,
            "percentage_improvement": 0.0,
            "unit": "Currency ($/₹)",
        },
        {
            "metric": "Wasted Spend Rate",
            "baseline_blind_marketing": baseline_waste_rate * 100,
            "optimized_data_driven": optimized_waste_rate * 100,
            "absolute_change": round((optimized_waste_rate - baseline_waste_rate) * 100, 2),
            "percentage_improvement": round(((baseline_waste_rate - optimized_waste_rate) / baseline_waste_rate) * 100, 2),
            "unit": "% (Lower is Better)",
        },
        {
            "metric": "Wasted Media Spend",
            "baseline_blind_marketing": base_wasted_spend,
            "optimized_data_driven": opt_wasted_spend,
            "absolute_change": round(opt_wasted_spend - base_wasted_spend, 2),
            "percentage_improvement": round(((base_wasted_spend - opt_wasted_spend) / base_wasted_spend) * 100, 2),
            "unit": "Currency ($/₹)",
        },
        {
            "metric": "Effective Media Spend",
            "baseline_blind_marketing": base_effective_spend,
            "optimized_data_driven": opt_effective_spend,
            "absolute_change": round(opt_effective_spend - base_effective_spend, 2),
            "percentage_improvement": round(((opt_effective_spend - base_effective_spend) / base_effective_spend) * 100, 2),
            "unit": "Currency ($/₹)",
        },
        {
            "metric": "Return on Ad Spend (ROAS)",
            "baseline_blind_marketing": baseline_roas,
            "optimized_data_driven": optimized_roas,
            "absolute_change": round(optimized_roas - baseline_roas, 2),
            "percentage_improvement": round(((optimized_roas - baseline_roas) / baseline_roas) * 100, 2),
            "unit": "x Multiplier",
        },
        {
            "metric": "Incremental Gross Revenue",
            "baseline_blind_marketing": base_inc_revenue,
            "optimized_data_driven": opt_inc_revenue,
            "absolute_change": round(opt_inc_revenue - base_inc_revenue, 2),
            "percentage_improvement": round(((opt_inc_revenue - base_inc_revenue) / base_inc_revenue) * 100, 2),
            "unit": "Currency ($/₹)",
        },
        {
            "metric": "Incremental Net Profit",
            "baseline_blind_marketing": base_inc_profit,
            "optimized_data_driven": opt_inc_profit,
            "absolute_change": round(opt_inc_profit - base_inc_profit, 2),
            "percentage_improvement": round(((opt_inc_profit - base_inc_profit) / base_inc_profit) * 100, 2),
            "unit": "Currency ($/₹)",
        },
        {
            "metric": "Profit ROI Hurdle",
            "baseline_blind_marketing": round(base_profit_roi, 2),
            "optimized_data_driven": round(opt_profit_roi, 2),
            "absolute_change": round(opt_profit_roi - base_profit_roi, 2),
            "percentage_improvement": round(((opt_profit_roi - base_profit_roi) / base_profit_roi) * 100, 2),
            "unit": "x Multiplier",
        },
    ]

    df_metrics = pd.DataFrame(metrics_data)
    logger.info("Computed before/after marketing optimization benchmarks.")
    return df_metrics
