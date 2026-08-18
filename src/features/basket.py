"""
Basket feature engineering: FILO checkout sequence, basket size, and need zone demarcation.
"""

from typing import Optional
import numpy as np
import pandas as pd
from src.config import get_config
from src.exceptions import MissingColumnError, EmptyDataError
from src.logging import get_logger

logger = get_logger("basket_features")


def calculate_basket_features(
    df_order_products: pd.DataFrame,
    df_orders: Optional[pd.DataFrame] = None,
    need_zone_limit: int = 10
) -> pd.DataFrame:
    """
    Computes core basket sequence features:
    1. basket_size: Total items in order.
    2. checkout_rank: FILO checkout sequence proxy = basket_size - add_to_cart_order + 1.
    3. is_in_need_zone: True if checkout_rank is among the last N scanned items (first N added).
    4. confidence_flag: 'HIGH' if basket_size >= need_zone_limit, else 'LOW'.
    5. proxy_period: Discrete period bin for trend analytics.
    """
    if df_order_products.empty:
        raise EmptyDataError("Order products dataframe is empty.")

    required_cols = ["order_id", "product_id", "add_to_cart_order"]
    for col in required_cols:
        if col not in df_order_products.columns:
            raise MissingColumnError(f"Missing required column '{col}' in order_products.")

    df = df_order_products.copy()

    # 1. Compute basket_size per order
    basket_sizes = df.groupby("order_id")["add_to_cart_order"].transform("max")
    df["basket_size"] = basket_sizes.astype("int32")

    # 2. FILO Checkout Rank: First in trolley = Last scanned by cashier
    # Item added 1st in basket of size 20 -> checkout_rank = 20 - 1 + 1 = 20 (scanned last)
    # Item added 20th in basket of size 20 -> checkout_rank = 20 - 20 + 1 = 1 (scanned first)
    df["checkout_rank"] = (df["basket_size"] - df["add_to_cart_order"] + 1).astype("int32")

    # 3. Need Zone: Last 10 scanned items
    # For basket_size >= 10: checkout_rank > basket_size - 10  (i.e. add_to_cart_order <= 10)
    # For basket_size < 10: all items are considered need zone, but flagged as LOW confidence
    df["is_in_need_zone"] = np.where(
        df["basket_size"] >= need_zone_limit,
        df["checkout_rank"] > (df["basket_size"] - need_zone_limit),
        True
    )

    df["basket_confidence_flag"] = np.where(
        df["basket_size"] >= need_zone_limit,
        "HIGH",
        "LOW"
    )

    # 4. Proxy Period: Assign orders to sequential proxy periods (e.g. Proxy_Period_1..4)
    # Allows trend analysis without pretending to have real calendar dates
    if df_orders is not None and not df_orders.empty and "order_number" in df_orders.columns:
        df = df.merge(df_orders[["order_id", "order_number"]], on="order_id", how="left")
        # Bin order_number into 4 proxy periods
        bins = [0, 10, 20, 30, 999]
        labels = ["Proxy_Period_1", "Proxy_Period_2", "Proxy_Period_3", "Proxy_Period_4"]
        df["proxy_period"] = pd.cut(df["order_number"].fillna(1), bins=bins, labels=labels).astype(str)
        df.drop(columns=["order_number"], inplace=True)
    else:
        # Bin by order_id quantiles
        try:
            df["proxy_period"] = pd.qcut(
                df["order_id"],
                q=4,
                labels=["Proxy_Period_1", "Proxy_Period_2", "Proxy_Period_3", "Proxy_Period_4"]
            ).astype(str)
        except Exception:
            df["proxy_period"] = "Proxy_Period_1"

    logger.info(
        f"Calculated basket features for {len(df)} items across {df['order_id'].nunique()} orders. "
        f"Need zone items: {df['is_in_need_zone'].sum()}/{len(df)} ({df['is_in_need_zone'].mean():.1%})."
    )

    return df
