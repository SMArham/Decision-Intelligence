"""
Unit tests for data quality audit and validation checks.
"""

import pytest
import pandas as pd
from src.validation.checks import run_data_quality_checks


def test_data_quality_audit_clean_data():
    """Validates that clean data produces all PASS checks."""
    df_features = pd.DataFrame([{
        "order_id": 1,
        "product_id": 101,
        "add_to_cart_order": 1,
        "basket_size": 15,
        "is_in_need_zone": True,
        "is_pg_product": True,
    }])

    df_need_share = pd.DataFrame([{
        "segment": "household",
        "proxy_period": "Proxy_Period_1",
        "pg_need_share": 0.35,
    }])

    df_recommendations = pd.DataFrame([{
        "segment": "household",
        "supply_score": 0.95,
        "final_recommended_budget": 100000.0,
        "expected_profit_roi": 1.58,
    }])

    df_report = run_data_quality_checks(df_features, df_need_share, df_recommendations)

    assert not df_report.empty
    critical_failures = df_report[(df_report["status"] == "FAIL") & (df_report["severity"] == "CRITICAL")]
    assert len(critical_failures) == 0


def test_data_quality_audit_detects_corrupt_data():
    """Validates that data quality checks catch nulls, negative values, and out of bounds metrics."""
    # Corrupt feature table with null order_id and negative add_to_cart_order
    df_features_corrupt = pd.DataFrame([{
        "order_id": None,
        "product_id": 101,
        "add_to_cart_order": -5,
        "basket_size": 0,
        "is_in_need_zone": True,
        "is_pg_product": False,
    }])

    # Corrupt need share (> 1.0)
    df_share_corrupt = pd.DataFrame([{
        "segment": "household",
        "proxy_period": "Proxy_Period_1",
        "pg_need_share": 1.45,  # Invalid
    }])

    # Corrupt budget (< 0)
    df_rec_corrupt = pd.DataFrame([{
        "segment": "household",
        "supply_score": -0.2,
        "final_recommended_budget": -5000.0,
        "expected_profit_roi": float("inf"),
    }])

    df_report = run_data_quality_checks(df_features_corrupt, df_share_corrupt, df_rec_corrupt)
    failures = df_report[df_report["status"] == "FAIL"]

    assert len(failures) >= 4
