"""
ROI, ROAS, and unit economics calculation module.
"""

from typing import Dict
from src.config import get_config
from src.logging import get_logger

logger = get_logger("roi_rules")


def calculate_campaign_roi(
    ad_spend: float,
    incremental_revenue: float,
    margin_percentage: float = 0.35
) -> Dict[str, float]:
    """
    Calculates campaign ROAS, Incremental Profit, and Profit ROI.
    Formula:
      ROAS = incremental_revenue / ad_spend
      incremental_profit = incremental_revenue * margin_percentage
      Profit ROI = incremental_profit / ad_spend
    """
    if ad_spend <= 0:
        return {
            "ad_spend": 0.0,
            "incremental_revenue": 0.0,
            "incremental_profit": 0.0,
            "roas": 0.0,
            "profit_roi": 0.0,
        }

    profit = incremental_revenue * margin_percentage
    roas = incremental_revenue / ad_spend
    profit_roi = profit / ad_spend

    return {
        "ad_spend": round(ad_spend, 2),
        "incremental_revenue": round(incremental_revenue, 2),
        "incremental_profit": round(profit, 2),
        "roas": round(roas, 2),
        "profit_roi": round(profit_roi, 2),
    }
