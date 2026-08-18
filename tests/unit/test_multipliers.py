"""
Unit tests for demand multiplier and supply multiplier rules.
"""

import pytest
from src.rules.budget import get_demand_multiplier, get_supply_multiplier


def test_demand_multiplier_tiers():
    """
    Validates Demand Multiplier thresholds:
    - 0% to 10% -> 1.5
    - 10% to 30% -> 1.3
    - 30% to 50% -> 1.0
    - 50% to 80% -> 1.3
    - 80% to 100% -> 0.8
    """
    assert get_demand_multiplier(0.05) == 1.5
    assert get_demand_multiplier(0.20) == 1.3
    assert get_demand_multiplier(0.40) == 1.0
    assert get_demand_multiplier(0.65) == 1.3
    assert get_demand_multiplier(0.90) == 0.8


def test_supply_multiplier_tiers():
    """
    Validates Supply Multiplier rules:
    - supply_score < 0.6 -> 0.0
    - supply_score 0.6 to 0.8 -> 0.5
    - supply_score 0.8 to 1.0 -> 1.0
    - supply_score > 1.0 -> 1.1
    """
    assert get_supply_multiplier(0.40) == 0.0
    assert get_supply_multiplier(0.59) == 0.0
    assert get_supply_multiplier(0.70) == 0.5
    assert get_supply_multiplier(0.90) == 1.0
    assert get_supply_multiplier(1.00) == 1.0
    assert get_supply_multiplier(1.15) == 1.1


def test_supply_critical_zero_budget():
    """Validates that a supply score of 0.5 results in multiplier 0.0."""
    assert get_supply_multiplier(0.50) == 0.0
