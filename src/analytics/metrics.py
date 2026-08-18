"""
P&G Need Share and Basket Metrics aggregation module.
"""

from typing import Optional
import pandas as pd
from src.analytics.statistics import wilson_score_interval
from src.config import get_config
from src.exceptions import EmptyDataError, MissingColumnError
from src.logging import get_logger

logger = get_logger("metrics_analytics")


def calculate_pg_need_share(
    df_features: pd.DataFrame,
    segment_col: str = "department",
    period_col: str = "proxy_period"
) -> pd.DataFrame:
    """
    Aggregates P&G Need Share across segments (departments) and proxy periods:
    P&G Need Share = P&G items in last 10 scanned items / total items in last 10 scanned items.
    Also calculates Wilson score confidence bounds and confidence tags.
    """
    if df_features.empty:
        raise EmptyDataError("Input features DataFrame is empty.")

    required_cols = ["order_id", "is_in_need_zone", "is_pg_product"]
    for col in required_cols:
        if col not in df_features.columns:
            raise MissingColumnError(f"Missing column '{col}' required for need share calculation.")

    config = get_config()
    min_orders = config.minimum_orders_for_confidence

    # Ensure grouping columns exist
    group_cols = []
    if segment_col in df_features.columns:
        group_cols.append(segment_col)
    if period_col in df_features.columns:
        group_cols.append(period_col)

    if not group_cols:
        group_cols = ["segment"]
        df_features["segment"] = "All_Categories"

    # Filter to need zone items for calculating share
    need_zone_df = df_features[df_features["is_in_need_zone"]].copy()

    records = []
    grouped = df_features.groupby(group_cols)

    for group_keys, group_data in grouped:
        if not isinstance(group_keys, tuple):
            group_keys = (group_keys,)

        seg_val = group_keys[0] if len(group_keys) >= 1 else "All"
        period_val = group_keys[1] if len(group_keys) >= 2 else "All_Periods"

        # Group data in need zone
        nz_group = group_data[group_data["is_in_need_zone"]]

        total_baskets = int(group_data["order_id"].nunique())
        total_need_items = int(len(nz_group))
        pg_need_items = int(nz_group["is_pg_product"].sum())

        # Safe division
        pg_need_share = (pg_need_items / total_need_items) if total_need_items > 0 else 0.0

        # Wilson Confidence Interval
        ci_lower, ci_upper = wilson_score_interval(pg_need_items, total_need_items, confidence=0.95)

        # Confidence Level Tag
        if total_baskets >= min_orders and total_need_items >= 50:
            conf_label = "HIGH"
            is_high_conf = True
        elif total_baskets >= (min_orders // 2):
            conf_label = "MEDIUM"
            is_high_conf = False
        else:
            conf_label = "LOW"
            is_high_conf = False

        records.append({
            "segment": seg_val,
            "proxy_period": period_val,
            "total_baskets": total_baskets,
            "total_need_zone_items": total_need_items,
            "pg_need_zone_items": pg_need_items,
            "pg_need_share": round(pg_need_share, 4),
            "wilson_ci_lower": round(ci_lower, 4),
            "wilson_ci_upper": round(ci_upper, 4),
            "confidence_level_label": conf_label,
            "is_high_confidence": is_high_conf,
        })

    df_result = pd.DataFrame(records)
    logger.info(
        f"Computed P&G Need Share for {len(df_result)} segment-period combinations. "
        f"Overall average P&G Need Share: {df_result['pg_need_share'].mean():.2%}"
    )

    return df_result
