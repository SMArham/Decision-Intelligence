"""
P&G brand identification and regex matching module.
"""

import re
from typing import Dict, List, Optional, Set, Tuple
import pandas as pd
from src.config import get_config
from src.exceptions import MissingColumnError
from src.logging import get_logger

logger = get_logger("brand_features")


def match_pg_brand(product_name: str, include_patterns: List[re.Pattern], exclude_patterns: List[re.Pattern]) -> Tuple[bool, Optional[str]]:
    """
    Checks if a product_name matches any P&G brand keyword while avoiding false positives.
    Returns (is_pg, matched_brand_name).
    """
    if not isinstance(product_name, str) or not product_name.strip():
        return False, None

    name_lower = product_name.lower().strip()

    # 1. Check exclusions
    for exc in exclude_patterns:
        if exc.search(name_lower):
            return False, None

    # 2. Check inclusions
    for inc in include_patterns:
        match = inc.search(name_lower)
        if match:
            return True, match.group(0).capitalize()

    return False, None


def enrich_with_pg_brands(
    df_products: pd.DataFrame,
    include_keywords: Optional[List[str]] = None,
    exclude_keywords: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Tags products table with `is_pg_product` and `matched_brand`.
    """
    if "product_name" not in df_products.columns:
        raise MissingColumnError("Column 'product_name' missing from products DataFrame.")

    config = get_config()
    inc_words = include_keywords or config.include_brand_keywords
    exc_words = exclude_keywords or config.exclude_brand_keywords

    # Compile regexes with word boundaries for precision
    include_patterns = [
        re.compile(r"\b" + re.escape(k.lower()) + r"\b", re.IGNORECASE)
        for k in inc_words if k.strip()
    ]
    exclude_patterns = [
        re.compile(r"\b" + re.escape(k.lower()) + r"\b", re.IGNORECASE)
        for k in exc_words if k.strip()
    ]

    df = df_products.copy()

    is_pg_list = []
    brand_list = []

    for name in df["product_name"]:
        is_pg, brand = match_pg_brand(name, include_patterns, exclude_patterns)
        is_pg_list.append(is_pg)
        brand_list.append(brand if is_pg else "Non-P&G")

    df["is_pg_product"] = is_pg_list
    df["matched_brand"] = brand_list

    pg_count = df["is_pg_product"].sum()
    logger.info(
        f"P&G Brand Matching completed: {pg_count}/{len(df)} products matched as P&G "
        f"({pg_count/len(df):.1%}). Distinct brands identified: {df[df['is_pg_product']]['matched_brand'].nunique()}"
    )

    return df


def generate_brand_audit_report(df_products: pd.DataFrame) -> pd.DataFrame:
    """
    Generates a diagnostic audit of identified P&G products for verification.
    """
    if "is_pg_product" not in df_products.columns:
        df_products = enrich_with_pg_brands(df_products)

    pg_products = df_products[df_products["is_pg_product"]].copy()
    if pg_products.empty:
        logger.warning("No P&G products identified in dataset!")
        return pd.DataFrame(columns=["product_id", "product_name", "matched_brand"])

    return pg_products[["product_id", "product_name", "matched_brand"]].sort_values("matched_brand")
