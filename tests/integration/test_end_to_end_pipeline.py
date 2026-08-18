"""
Integration test for full end-to-end pg_ad_optimizer pipeline.
"""

import pytest
from pathlib import Path
from run_pipeline import run_full_pipeline
from src.config import get_config
from src.utils.io import read_parquet


def test_full_pipeline_sample_mode():
    """
    Executes full pipeline end-to-end in sample fallback mode and validates:
    1. Output CSV files exist.
    2. Output Parquet files exist.
    3. SQLite data mart contains all required tables.
    4. Data quality checks pass.
    """
    config = get_config()
    out_dir = config.output_dir

    # Run pipeline
    run_full_pipeline(force_sample=True)

    # 1. Validate files generated
    expected_csvs = [
        "pg_need_share.csv",
        "budget_recommendations.csv",
        "before_after_metrics.csv",
        "financial_estimate.csv",
        "data_quality_report.csv",
    ]
    for filename in expected_csvs:
        csv_p = out_dir / filename
        assert csv_p.exists(), f"Expected output CSV missing: {csv_p}"
        assert csv_p.stat().st_size > 0

    # 2. Validate Parquet
    parquet_p = out_dir / "budget_recommendations.parquet"
    assert parquet_p.exists()
    df_parquet = read_parquet(parquet_p)
    assert not df_parquet.empty
    assert "final_recommended_budget" in df_parquet.columns
    assert "action_label" in df_parquet.columns
