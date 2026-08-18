"""
Supply availability proxy and inventory scoring module.
"""

from typing import Dict, Optional
import numpy as np
import pandas as pd
from src.config import get_config
from src.logging import get_logger

logger = get_logger("supply_features")


def calculate_supply_score(
    df: pd.DataFrame,
    overrides: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """
    Computes a transparent Supply Availability Proxy Score (0.0 to 1.2) for each segment.
    Factors:
    1. Reorder regularity proxy (higher reorder rate indicates steady supply chain).
    2. Basket frequency presence.
    3. Manual department overrides from config/supply.yaml.
    """
    config = get_config()
    supply_cfg = config.supply
    dept_overrides = overrides or supply_cfg.get("department_supply_overrides", {})
    default_score = float(supply_cfg.get("default_supply_score", 0.95))

    # Segment by department if available, else overall
    segment_col = "department" if "department" in df.columns else "segment"

    if segment_col in df.columns:
        # Group metrics
        grouped = df.groupby(segment_col).agg(
            reorder_rate=("reordered", "mean") if "reordered" in df.columns else ("product_id", "count"),
            item_count=("product_id", "count")
        ).reset_index()

        # Score formulation: Baseline from config override or computed proxy
        scores = []
        for _, row in grouped.iterrows():
            seg_name = str(row[segment_col]).lower().strip()
            if seg_name in dept_overrides:
                score = float(dept_overrides[seg_name])
            else:
                # Proxy formula: base around default_score + slight variation based on reorder stability
                if "reordered" in df.columns:
                    reorder_val = float(row["reorder_rate"])
                    score = default_score * (0.85 + 0.3 * reorder_val)
                else:
                    score = default_score
            scores.append(round(min(max(score, 0.0), 1.2), 3))

        grouped["supply_score"] = scores
        return grouped[[segment_col, "supply_score"]]

    # Fallback single row
    return pd.DataFrame([{segment_col: "All_Categories", "supply_score": default_score}])
