"""
Budget recommendation rules engine and action label assignment.
"""

from typing import Dict, Optional, Tuple
import pandas as pd
from src.config import get_config
from src.exceptions import BudgetCalculationError
from src.logging import get_logger

logger = get_logger("budget_rules")


def get_demand_multiplier(need_share: float) -> float:
    """
    Calculates demand multiplier based on P&G Need Share:
    - 0% to 10%   -> 1.5 (Awareness push)
    - 10% to 30%  -> 1.3 (Growth opportunity)
    - 30% to 50%  -> 1.0 (Baseline demand)
    - 50% to 80%  -> 1.3 (Expansion)
    - 80% to 100% -> 0.8 (Maintain/saturation)
    """
    share = max(0.0, min(1.0, float(need_share)))
    if share <= 0.10:
        return 1.5
    elif share <= 0.30:
        return 1.3
    elif share <= 0.50:
        return 1.0
    elif share <= 0.80:
        return 1.3
    else:
        return 0.8


def get_supply_multiplier(supply_score: float) -> float:
    """
    Calculates supply multiplier based on supply availability proxy:
    - supply_score < 0.6       -> 0.0 (Stockout protection: Halt ads)
    - 0.6 <= supply_score < 0.8 -> 0.5 (Low stock: Throttle budget)
    - 0.8 <= supply_score <= 1.0-> 1.0 (Adequate inventory: Full budget)
    - supply_score > 1.0       -> 1.1 (Surplus inventory: Aggressive push)
    """
    score = float(supply_score)
    if score < 0.60:
        return 0.0
    elif score < 0.80:
        return 0.5
    elif score <= 1.00:
        return 1.0
    else:
        return 1.1


def assign_action_label(need_share: float, supply_score: float) -> str:
    """
    Assigns strategic decision action label based on demand need share and supply health:
    - ADVERTISE: High demand / good opportunity + Adequate supply
    - RESTOCK_FIRST: Strong demand / need share + Depleted supply (< 0.8)
    - TEST: Low demand + High supply (Test promotional response)
    - MAINTAIN: Very high need share (>= 80%) + Good supply (Maintain presence)
    - STOP: Low demand + Low supply, or critical stockout (< 0.6)
    """
    if supply_score < 0.60:
        return "RESTOCK_FIRST" if need_share >= 0.30 else "STOP"

    if supply_score < 0.80:
        return "RESTOCK_FIRST" if need_share >= 0.10 else "STOP"

    # Adequate or high supply (>= 0.80)
    if need_share >= 0.80:
        return "MAINTAIN"
    elif need_share >= 0.10:
        return "ADVERTISE"
    else:
        return "TEST"


def generate_budget_recommendations(
    df_need_share: pd.DataFrame,
    df_supply: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Generates budget recommendations, ROI bounds, and action labels for each segment/period.
    """
    config = get_config()
    base_budget = config.base_ad_budget
    target_roi = config.target_roi
    margin_pct = config.average_margin_percentage
    target_roas = config.target_roas

    df = df_need_share.copy()

    # Merge supply score if provided
    if df_supply is not None and not df_supply.empty:
        # Check merge key
        merge_col = "segment" if "segment" in df_supply.columns else "department"
        df = df.merge(df_supply.rename(columns={merge_col: "segment"}), on="segment", how="left")
        df["supply_score"] = df["supply_score"].fillna(0.95)
    else:
        df["supply_score"] = 0.95

    demand_mults = []
    supply_mults = []
    recommended_budgets = []
    inc_revenues = []
    inc_profits = []
    max_allowed_budgets = []
    final_budgets = []
    expected_roas_list = []
    expected_profit_roi_list = []
    actions = []

    for _, row in df.iterrows():
        share = float(row["pg_need_share"])
        supply_s = float(row["supply_score"])

        # Multipliers
        d_mult = get_demand_multiplier(share)
        s_mult = get_supply_multiplier(supply_s)
        action = assign_action_label(share, supply_s)

        # Unconstrained budget recommendation
        rec_budget = round(base_budget * d_mult * s_mult, 2)

        # Projected ROAS & Incremental Revenue
        # Effective ROAS scales with demand strength and supply completeness
        effective_roas = target_roas * (0.85 + 0.35 * min(share * 2.0, 1.0)) if s_mult > 0 else 0.0
        exp_revenue = round(rec_budget * effective_roas, 2)
        exp_profit = round(exp_revenue * margin_pct, 2)

        # Maximum allowed budget to guarantee target ROI hurdle
        # Profit ROI = Profit / Budget >= target_roi  =>  Budget <= Profit / target_roi
        if exp_profit > 0 and target_roi > 0:
            max_allowed = round(exp_profit / target_roi, 2)
        else:
            max_allowed = 0.0

        # If s_mult == 0 (stockout), budget must be 0
        if s_mult == 0.0:
            final_budget = 0.0
            profit_roi = 0.0
        else:
            final_budget = min(rec_budget, max_allowed if max_allowed > 0 else rec_budget)
            profit_roi = round(exp_profit / final_budget, 2) if final_budget > 0 else 0.0

        demand_mults.append(d_mult)
        supply_mults.append(s_mult)
        recommended_budgets.append(rec_budget)
        inc_revenues.append(exp_revenue)
        inc_profits.append(exp_profit)
        max_allowed_budgets.append(max_allowed)
        final_budgets.append(final_budget)
        expected_roas_list.append(round(effective_roas, 2))
        expected_profit_roi_list.append(profit_roi)
        actions.append(action)

    df["demand_multiplier"] = demand_mults
    df["supply_multiplier"] = supply_mults
    df["base_ad_budget"] = base_budget
    df["recommended_ad_budget"] = recommended_budgets
    df["expected_incremental_revenue"] = inc_revenues
    df["expected_incremental_profit"] = inc_profits
    df["max_allowed_ad_budget"] = max_allowed_budgets
    df["final_recommended_budget"] = final_budgets
    df["expected_roas"] = expected_roas_list
    df["expected_profit_roi"] = expected_profit_roi_list
    df["action_label"] = actions

    logger.info(
        f"Budget recommendations generated for {len(df)} segments. "
        f"Total Recommended Budget: ${df['final_recommended_budget'].sum():,.2f} "
        f"(vs Base Total: ${base_budget * len(df):,.2f})"
    )

    return df
