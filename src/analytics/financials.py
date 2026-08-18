"""
Financial modeling and P&G corporate marketing budget estimation.
Calibrated against P&G FY2024 Form 10-K SEC filings.
"""

from typing import Dict
import pandas as pd
from src.config import get_config
from src.logging import get_logger

logger = get_logger("financial_analytics")


def compute_financial_marketing_summary() -> Dict[str, any]:
    """
    Computes corporate financial marketing intensity:
    marketing_intensity = advertising_expense / total_revenue
    And category budget estimates.
    """
    config = get_config()

    rev = config.total_revenue
    ad_spend = config.advertising_expense

    # Marketing intensity
    intensity = (ad_spend / rev) if rev > 0 else 0.0

    # Category allocations
    category_estimates = {}
    for cat, share in config.category_revenue_shares.items():
        category_estimates[cat] = {
            "revenue_share": share,
            "allocated_annual_ad_budget": round(ad_spend * share, 2),
            "allocated_annual_net_sales": round(rev * share, 2),
        }

    summary = {
        "company": config.company_name,
        "fiscal_year": config.fiscal_year,
        "currency": config.currency,
        "total_revenue": rev,
        "advertising_expense": ad_spend,
        "marketing_intensity": round(intensity, 6),
        "marketing_intensity_pct": round(intensity * 100, 2),
        "category_allocations": category_estimates,
        "source": "P&G Form 10-K Annual Report (US SEC EDGAR)",
    }

    logger.info(
        f"P&G Financial Summary: Total Net Sales = ${rev:,.0f}, "
        f"Ad Expense = ${ad_spend:,.0f}, Marketing Intensity = {intensity:.2%}"
    )

    return summary


def get_financial_estimate_df() -> pd.DataFrame:
    """
    Returns category financial allocations as a clean DataFrame.
    """
    config = get_config()
    summary = compute_financial_marketing_summary()

    rows = []
    for cat_name, details in summary["category_allocations"].items():
        clean_cat = cat_name.replace("_", " ").title()
        rows.append({
            "category": clean_cat,
            "revenue_share": details["revenue_share"],
            "allocated_ad_budget_usd": details["allocated_annual_ad_budget"],
            "allocated_sales_usd": details["allocated_annual_net_sales"],
            "marketing_intensity": f"{summary['marketing_intensity_pct']}%",
            "source": summary["source"]
        })

    return pd.DataFrame(rows)
