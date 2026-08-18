"""
Unit tests for Before vs After Optimization metrics calculations.
"""

import pytest
from src.rules.before_after import calculate_before_after_metrics


def test_before_after_metrics_benchmark():
    """
    Validates benchmark metrics:
    Baseline: Wasted spend = 25%, ROAS = 3.0x, Margin = 35%
    Optimized: Wasted spend = 8%, ROAS = 4.5x, Margin = 35%
    """
    df_ba = calculate_before_after_metrics(total_budget=100.0)

    # Convert to dictionary keyed by metric name
    metrics_map = df_ba.set_index("metric").to_dict(orient="index")

    # 1. Wasted Spend Rate
    waste_row = metrics_map["Wasted Spend Rate"]
    assert waste_row["baseline_blind_marketing"] == 25.0
    assert waste_row["optimized_data_driven"] == 8.0
    assert pytest.approx(waste_row["percentage_improvement"], 0.1) == 68.0  # (25 - 8) / 25 = 68%

    # 2. ROAS
    roas_row = metrics_map["Return on Ad Spend (ROAS)"]
    assert roas_row["baseline_blind_marketing"] == 3.0
    assert roas_row["optimized_data_driven"] == 4.5
    assert pytest.approx(roas_row["percentage_improvement"], 0.1) == 50.0  # +50%

    # 3. Incremental Profit
    profit_row = metrics_map["Incremental Net Profit"]
    assert pytest.approx(profit_row["baseline_blind_marketing"], 0.1) == 105.0  # 300 * 0.35 = 105
    assert pytest.approx(profit_row["optimized_data_driven"], 0.1) == 157.5   # 450 * 0.35 = 157.5
    assert pytest.approx(profit_row["percentage_improvement"], 0.1) == 50.0
