"""
Schema definitions and column constants for Instacart and processed datasets.
"""

from typing import Dict, List

# Instacart Raw Data Schemas
ORDERS_COLUMNS: List[str] = [
    "order_id",
    "user_id",
    "eval_set",
    "order_number",
    "order_dow",
    "order_hour_of_day",
    "days_since_prior_order",
]

ORDER_PRODUCTS_COLUMNS: List[str] = [
    "order_id",
    "product_id",
    "add_to_cart_order",
    "reordered",
]

PRODUCTS_COLUMNS: List[str] = [
    "product_id",
    "product_name",
    "aisle_id",
    "department_id",
]

DEPARTMENTS_COLUMNS: List[str] = [
    "department_id",
    "department",
]

AISLES_COLUMNS: List[str] = [
    "aisle_id",
    "aisle",
]

# Processed Feature Table Schemas
BASKET_FEATURES_COLUMNS: List[str] = [
    "order_id",
    "product_id",
    "product_name",
    "department_id",
    "department",
    "aisle_id",
    "aisle",
    "add_to_cart_order",
    "reordered",
    "basket_size",
    "checkout_rank",
    "is_in_need_zone",
    "is_pg_product",
    "matched_brand",
    "is_need_department",
    "is_want_department",
    "proxy_period",
]

PG_NEED_SHARE_COLUMNS: List[str] = [
    "segment",
    "proxy_period",
    "total_baskets",
    "total_need_zone_items",
    "pg_need_zone_items",
    "pg_need_share",
    "wilson_ci_lower",
    "wilson_ci_upper",
    "confidence_level_label",
    "is_high_confidence",
]

BUDGET_RECOMMENDATION_COLUMNS: List[str] = [
    "segment",
    "proxy_period",
    "total_baskets",
    "pg_need_share",
    "demand_multiplier",
    "supply_score",
    "supply_multiplier",
    "base_ad_budget",
    "recommended_ad_budget",
    "expected_incremental_revenue",
    "expected_incremental_profit",
    "max_allowed_ad_budget",
    "final_recommended_budget",
    "expected_roas",
    "expected_profit_roi",
    "action_label",
    "confidence_level_label",
]

BEFORE_AFTER_COLUMNS: List[str] = [
    "metric",
    "baseline_blind_marketing",
    "optimized_data_driven",
    "absolute_change",
    "percentage_improvement",
    "unit",
]
