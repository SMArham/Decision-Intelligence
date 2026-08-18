"""
Data cleaning and validation module for Instacart raw datasets.
"""

from typing import Dict, Tuple
import pandas as pd
from src.exceptions import MissingColumnError, EmptyDataError
from src.logging import get_logger

logger = get_logger("data_cleaner")


def clean_raw_datasets(datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Cleans raw Instacart DataFrames:
    1. Removes duplicate order-product rows.
    2. Drops rows with missing critical IDs (order_id, product_id, add_to_cart_order).
    3. Validates positive add_to_cart_order.
    4. Converts low-cardinality strings to categorical dtypes for high speed and low memory.
    """
    logger.info("Starting raw dataset sanitation and validation...")

    # 1. Orders
    df_orders = datasets.get("orders")
    if df_orders is None or df_orders.empty:
        raise EmptyDataError("Orders table is missing or empty.")
    
    required_order_cols = ["order_id", "user_id"]
    for col in required_order_cols:
        if col not in df_orders.columns:
            raise MissingColumnError(f"Missing required column '{col}' in orders table.")

    df_orders = df_orders.drop_duplicates(subset=["order_id"])
    df_orders["order_id"] = pd.to_numeric(df_orders["order_id"], errors="coerce").astype("int64")
    df_orders["user_id"] = pd.to_numeric(df_orders["user_id"], errors="coerce").astype("int64")
    if "order_number" in df_orders.columns:
        df_orders["order_number"] = pd.to_numeric(df_orders["order_number"], errors="coerce").fillna(1).astype("int32")

    # 2. Order Products
    df_op = datasets.get("order_products__prior")
    if df_op is None:
        df_op = datasets.get("order_products")
    if df_op is None or df_op.empty:
        raise EmptyDataError("Order products table is missing or empty.")

    required_op_cols = ["order_id", "product_id", "add_to_cart_order"]
    for col in required_op_cols:
        if col not in df_op.columns:
            raise MissingColumnError(f"Missing required column '{col}' in order_products table.")

    df_op = df_op.dropna(subset=required_op_cols)
    df_op = df_op.drop_duplicates(subset=["order_id", "product_id"])

    df_op["order_id"] = pd.to_numeric(df_op["order_id"], errors="coerce").astype("int64")
    df_op["product_id"] = pd.to_numeric(df_op["product_id"], errors="coerce").astype("int64")
    df_op["add_to_cart_order"] = pd.to_numeric(df_op["add_to_cart_order"], errors="coerce").astype("int32")
    
    # Filter out non-positive add_to_cart_order
    df_op = df_op[df_op["add_to_cart_order"] > 0]
    if "reordered" in df_op.columns:
        df_op["reordered"] = pd.to_numeric(df_op["reordered"], errors="coerce").fillna(0).astype("int8")

    # 3. Products
    df_products = datasets.get("products")
    if df_products is None or df_products.empty:
        raise EmptyDataError("Products table is missing or empty.")
    
    df_products = df_products.dropna(subset=["product_id", "product_name"])
    df_products["product_id"] = pd.to_numeric(df_products["product_id"], errors="coerce").astype("int64")
    df_products["product_name"] = df_products["product_name"].astype(str).str.strip()
    if "aisle_id" in df_products.columns:
        df_products["aisle_id"] = pd.to_numeric(df_products["aisle_id"], errors="coerce").fillna(0).astype("int32")
    if "department_id" in df_products.columns:
        df_products["department_id"] = pd.to_numeric(df_products["department_id"], errors="coerce").fillna(0).astype("int32")

    # 4. Departments
    df_dept = datasets.get("departments")
    if df_dept is not None and not df_dept.empty:
        df_dept["department_id"] = pd.to_numeric(df_dept["department_id"], errors="coerce").astype("int32")
        df_dept["department"] = df_dept["department"].astype(str).str.strip().str.lower()
    else:
        df_dept = pd.DataFrame(columns=["department_id", "department"])

    # 5. Aisles
    df_aisles = datasets.get("aisles")
    if df_aisles is not None and not df_aisles.empty:
        df_aisles["aisle_id"] = pd.to_numeric(df_aisles["aisle_id"], errors="coerce").astype("int32")
        df_aisles["aisle"] = df_aisles["aisle"].astype(str).str.strip().str.lower()
    else:
        df_aisles = pd.DataFrame(columns=["aisle_id", "aisle"])

    logger.info(
        f"Data cleaning complete: {len(df_orders)} orders, {len(df_op)} order_items, "
        f"{len(df_products)} products, {len(df_dept)} departments, {len(df_aisles)} aisles."
    )

    return {
        "orders": df_orders,
        "order_products": df_op,
        "products": df_products,
        "departments": df_dept,
        "aisles": df_aisles,
    }
