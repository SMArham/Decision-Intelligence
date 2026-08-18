"""
Data validation checks and automated quality reporting.
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from src.logging import get_logger

logger = get_logger("data_quality")


def run_data_quality_checks(
    df_features: pd.DataFrame,
    df_need_share: pd.DataFrame,
    df_recommendations: pd.DataFrame
) -> pd.DataFrame:
    """
    Runs comprehensive data quality checks across feature and recommendation tables:
    1. Check presence of non-null order_id, product_id, add_to_cart_order.
    2. Check that add_to_cart_order is strictly positive (> 0).
    3. Check that basket_size is strictly positive (> 0).
    4. Check that pg_need_share is within [0.0, 1.0].
    5. Check that supply_score is non-negative (>= 0.0).
    6. Check that recommended_budget is non-negative (>= 0.0).
    7. Check that expected ROI / ROAS values are finite and valid numbers.
    8. Check P&G brand identification match rate.
    """
    logger.info("Executing comprehensive data quality audit...")

    checks: List[Dict[str, any]] = []

    # 1. Feature Table Checks
    if not df_features.empty:
        # Check order_id
        null_orders = int(df_features["order_id"].isnull().sum())
        checks.append({
            "table": "basket_features",
            "check_name": "order_id_not_null",
            "status": "PASS" if null_orders == 0 else "FAIL",
            "details": f"Null count: {null_orders}/{len(df_features)}",
            "severity": "CRITICAL"
        })

        # Check product_id
        null_products = int(df_features["product_id"].isnull().sum())
        checks.append({
            "table": "basket_features",
            "check_name": "product_id_not_null",
            "status": "PASS" if null_products == 0 else "FAIL",
            "details": f"Null count: {null_products}/{len(df_features)}",
            "severity": "CRITICAL"
        })

        # Check add_to_cart_order positive
        invalid_cart_order = int((df_features["add_to_cart_order"] <= 0).sum())
        checks.append({
            "table": "basket_features",
            "check_name": "positive_add_to_cart_order",
            "status": "PASS" if invalid_cart_order == 0 else "FAIL",
            "details": f"Non-positive rows: {invalid_cart_order}/{len(df_features)}",
            "severity": "HIGH"
        })

        # Check basket_size positive
        invalid_basket = int((df_features["basket_size"] <= 0).sum())
        checks.append({
            "table": "basket_features",
            "check_name": "positive_basket_size",
            "status": "PASS" if invalid_basket == 0 else "FAIL",
            "details": f"Non-positive baskets: {invalid_basket}/{len(df_features)}",
            "severity": "HIGH"
        })

        # Check P&G match rate
        pg_match_rate = df_features["is_pg_product"].mean()
        pg_status = "PASS" if (0.01 <= pg_match_rate <= 0.85) else "WARNING"
        checks.append({
            "table": "basket_features",
            "check_name": "pg_brand_match_rate_valid",
            "status": pg_status,
            "details": f"P&G match rate: {pg_match_rate:.2%} ({df_features['is_pg_product'].sum()} items)",
            "severity": "MEDIUM"
        })

    # 2. Need Share Table Checks
    if not df_need_share.empty:
        # Check pg_need_share bounds
        out_of_bounds_share = int(((df_need_share["pg_need_share"] < 0.0) | (df_need_share["pg_need_share"] > 1.0)).sum())
        checks.append({
            "table": "pg_need_share",
            "check_name": "need_share_range_valid_0_to_1",
            "status": "PASS" if out_of_bounds_share == 0 else "FAIL",
            "details": f"Out-of-bounds rows: {out_of_bounds_share}/{len(df_need_share)}",
            "severity": "CRITICAL"
        })

    # 3. Budget Recommendation Checks
    if not df_recommendations.empty:
        # Check supply score non-negative
        invalid_supply = int((df_recommendations["supply_score"] < 0.0).sum())
        checks.append({
            "table": "budget_recommendations",
            "check_name": "supply_score_non_negative",
            "status": "PASS" if invalid_supply == 0 else "FAIL",
            "details": f"Negative supply score count: {invalid_supply}/{len(df_recommendations)}",
            "severity": "HIGH"
        })

        # Check budget non-negative
        invalid_budget = int((df_recommendations["final_recommended_budget"] < 0.0).sum())
        checks.append({
            "table": "budget_recommendations",
            "check_name": "budget_non_negative",
            "status": "PASS" if invalid_budget == 0 else "FAIL",
            "details": f"Negative budget count: {invalid_budget}/{len(df_recommendations)}",
            "severity": "CRITICAL"
        })

        # Check finite ROI
        infinite_roi = int((~np.isfinite(df_recommendations["expected_profit_roi"])).sum())
        checks.append({
            "table": "budget_recommendations",
            "check_name": "finite_roi_metrics",
            "status": "PASS" if infinite_roi == 0 else "FAIL",
            "details": f"Non-finite ROI count: {infinite_roi}/{len(df_recommendations)}",
            "severity": "HIGH"
        })

    df_report = pd.DataFrame(checks)
    passed_count = (df_report["status"] == "PASS").sum()
    logger.info(f"Data Quality Report completed: {passed_count}/{len(df_report)} checks passed.")
    return df_report
