"""
Need vs Want classification module for FMCG departments and aisles.
"""

from typing import Dict, Optional
import pandas as pd
from src.config import get_config
from src.logging import get_logger

logger = get_logger("need_want_features")


def enrich_with_need_want(
    df: pd.DataFrame,
    df_departments: Optional[pd.DataFrame] = None,
    df_aisles: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Enriches dataset with `is_need_department`, `is_want_department`, and `need_want_category`.
    Combines rule-based department and aisle definitions from configuration.
    """
    config = get_config()
    df_out = df.copy()

    # Merge department & aisle names if IDs are present and names are missing
    if "department" not in df_out.columns and df_departments is not None and "department_id" in df_out.columns:
        df_out = df_out.merge(df_departments[["department_id", "department"]], on="department_id", how="left")

    if "aisle" not in df_out.columns and df_aisles is not None and "aisle_id" in df_out.columns:
        df_out = df_out.merge(df_aisles[["aisle_id", "aisle"]], on="aisle_id", how="left")

    # Lowercase for exact comparison
    dept_series = df_out["department"].astype(str).str.lower().fillna("")
    aisle_series = df_out["aisle"].astype(str).str.lower().fillna("") if "aisle" in df_out.columns else pd.Series([""] * len(df_out))

    # Check if department or aisle is in need list
    is_need = dept_series.isin(config.need_departments) | aisle_series.isin(config.need_aisles)
    
    # Check if department or aisle is in want list
    is_want = (dept_series.isin(config.want_departments) | aisle_series.isin(config.want_aisles)) & (~is_need)

    df_out["is_need_department"] = is_need
    df_out["is_want_department"] = is_want
    df_out["need_want_category"] = "Neutral / Other"
    df_out.loc[is_need, "need_want_category"] = "Essential Need"
    df_out.loc[is_want, "need_want_category"] = "Discretionary Want"

    logger.info(
        f"Need/Want categorization: {is_need.sum()} Need items ({is_need.mean():.1%}), "
        f"{is_want.sum()} Want items ({is_want.mean():.1%})."
    )

    return df_out
