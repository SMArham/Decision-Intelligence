"""
Unit tests for budget formulas, action labels, and ROI constraints.
"""

import pytest
import pandas as pd
from src.rules.budget import generate_budget_recommendations, assign_action_label


def test_budget_calculation_formula():
    """
    Test case from requirements:
    base_budget = 100000
    demand_multiplier = 1.3 (for need share 0.20)
    supply_multiplier = 1.0 (for supply score 0.90)
    expected recommended_ad_budget = 130000
    """
    df_share = pd.DataFrame([{
        "segment": "household",
        "proxy_period": "Proxy_Period_1",
        "total_baskets": 100,
        "total_need_zone_items": 500,
        "pg_need_zone_items": 100,
        "pg_need_share": 0.20,
        "wilson_ci_lower": 0.16,
        "wilson_ci_upper": 0.24,
        "confidence_level_label": "HIGH",
        "is_high_confidence": True
    }])

    df_supply = pd.DataFrame([{
        "segment": "household",
        "supply_score": 0.90
    }])

    df_rec = generate_budget_recommendations(df_share, df_supply)
    row = df_rec.iloc[0]

    assert row["demand_multiplier"] == 1.3
    assert row["supply_multiplier"] == 1.0
    assert row["recommended_ad_budget"] == 130000.0
    assert row["final_recommended_budget"] == 130000.0


def test_supply_zero_halts_budget():
    """
    Validates that when supply_score = 0.5, recommended budget MUST be 0.
    """
    df_share = pd.DataFrame([{
        "segment": "babies",
        "proxy_period": "Proxy_Period_1",
        "total_baskets": 100,
        "total_need_zone_items": 500,
        "pg_need_zone_items": 200,
        "pg_need_share": 0.40,
        "wilson_ci_lower": 0.35,
        "wilson_ci_upper": 0.45,
        "confidence_level_label": "HIGH",
        "is_high_confidence": True
    }])

    df_supply = pd.DataFrame([{
        "segment": "babies",
        "supply_score": 0.50  # Critical stockout
    }])

    df_rec = generate_budget_recommendations(df_share, df_supply)
    row = df_rec.iloc[0]

    assert row["supply_multiplier"] == 0.0
    assert row["final_recommended_budget"] == 0.0
    assert row["action_label"] == "RESTOCK_FIRST"


def test_action_label_assignments():
    """Tests action label logic under diverse operational conditions."""
    assert assign_action_label(need_share=0.40, supply_score=0.90) == "ADVERTISE"
    assert assign_action_label(need_share=0.50, supply_score=0.50) == "RESTOCK_FIRST"
    assert assign_action_label(need_share=0.05, supply_score=0.95) == "TEST"
    assert assign_action_label(need_share=0.85, supply_score=0.90) == "MAINTAIN"
    assert assign_action_label(need_share=0.05, supply_score=0.50) == "STOP"
