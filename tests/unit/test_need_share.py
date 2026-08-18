"""
Unit tests for P&G Need Share calculations and Wilson confidence intervals.
"""

import pytest
import pandas as pd
from src.analytics.metrics import calculate_pg_need_share
from src.analytics.statistics import wilson_score_interval
from src.features.basket import calculate_basket_features
from src.features.brand import enrich_with_pg_brands
from tests.fixtures.sample_data import create_fixture_order_20_items


def test_pg_need_share_fixture_20_items():
    """
    Validates example test case:
    Order with 20 products, first 10 items contain 5 P&G products.
    Expected pg_need_share = 5 / 10 = 0.50 (50%).
    """
    fixture = create_fixture_order_20_items()
    df_products = enrich_with_pg_brands(fixture["products"])
    df_feat = calculate_basket_features(fixture["order_products"], fixture["orders"])
    df_feat = df_feat.merge(df_products[["product_id", "department_id", "is_pg_product"]], on="product_id", how="left")
    df_feat["segment"] = "All"
    df_feat["proxy_period"] = "Proxy_Period_1"

    df_share = calculate_pg_need_share(df_feat, segment_col="segment", period_col="proxy_period")

    assert len(df_share) == 1
    row = df_share.iloc[0]
    assert row["total_need_zone_items"] == 10
    assert row["pg_need_zone_items"] == 5
    assert pytest.approx(row["pg_need_share"], 0.001) == 0.50


def test_wilson_confidence_interval_bounds():
    """Validates that Wilson confidence interval is within [0, 1] and contains sample proportion."""
    lower, upper = wilson_score_interval(successes=50, total=100, confidence=0.95)
    assert 0.0 <= lower <= 0.50 <= upper <= 1.0
    assert lower < upper

    # Edge cases
    assert wilson_score_interval(0, 0) == (0.0, 0.0)
    l_zero, u_zero = wilson_score_interval(0, 100)
    assert l_zero == 0.0 and u_zero > 0.0
