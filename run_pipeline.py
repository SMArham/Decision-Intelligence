"""
Master Command-Line Interface and Pipeline Orchestrator for pg_ad_optimizer.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.analytics.financials import compute_financial_marketing_summary, get_financial_estimate_df
from src.analytics.metrics import calculate_pg_need_share
from src.config import get_config
from src.data.ingest import ingest_data
from src.data.load import persist_data_mart
from src.features.basket import calculate_basket_features
from src.features.brand import enrich_with_pg_brands, generate_brand_audit_report
from src.features.need_want import enrich_with_need_want
from src.features.supply import calculate_supply_score
from src.logging import get_logger
from src.models.classifier import NeedPropensityClassifier
from src.rules.before_after import calculate_before_after_metrics
from src.rules.budget import generate_budget_recommendations
from src.utils.io import save_csv, save_parquet
from src.validation.checks import run_data_quality_checks

logger = get_logger("pipeline_runner")


def run_full_pipeline(force_sample: bool = False) -> None:
    """
    Executes the complete end-to-end P&G Ad Budget Optimizer pipeline:
    1. Ingestion & Sanitation (Kaggle or sample fallback)
    2. FILO Basket Feature Engineering
    3. P&G Brand Matching & Need/Want Categorization
    4. Supply Scoring Proxy
    5. P&G Need Share Aggregation & Confidence Intervals
    6. Machine Learning Classifier Training
    7. Rules Engine Budget & ROI Recommendations
    8. Before vs After Optimization Model
    9. Data Quality & Audit Report Generation
    10. Export to CSV, Parquet, and SQLite Data Mart
    """
    logger.info("==================================================")
    logger.info("  P&G ADVERTISEMENT BUDGET OPTIMIZER PIPELINE    ")
    logger.info("==================================================")

    config = get_config()

    # Step 1: Ingestion
    logger.info("[1/8] Ingesting and sanitizing dataset...")
    tables = ingest_data(force_sample=force_sample)

    # Step 2: Brand Tagging
    logger.info("[2/8] Enriching products with P&G brand regex...")
    df_products = enrich_with_pg_brands(tables["products"])

    # Step 3: Basket FILO Features
    logger.info("[3/8] Computing FILO checkout sequence & need zones...")
    df_features = calculate_basket_features(tables["order_products"], tables["orders"])

    # Merge product details
    df_features = df_features.merge(
        df_products[["product_id", "product_name", "department_id", "aisle_id", "is_pg_product", "matched_brand"]],
        on="product_id",
        how="left"
    )
    df_features = enrich_with_need_want(df_features, tables["departments"], tables["aisles"])

    # Step 4: Supply Proxy
    logger.info("[4/8] Estimating supply availability proxy scores...")
    df_supply = calculate_supply_score(df_features)

    # Step 5: P&G Need Share Analytics
    logger.info("[5/8] Aggregating P&G Need Share & Wilson Confidence Intervals...")
    df_need_share = calculate_pg_need_share(df_features, segment_col="department", period_col="proxy_period")

    # Step 6: ML Propensity Classifier
    logger.info("[6/8] Training Need Propensity ML Classifier...")
    clf = NeedPropensityClassifier()
    clf.train(df_features)

    # Step 7: Budget Optimization & ROI
    logger.info("[7/8] Generating budget recommendations and decision labels...")
    df_recommendations = generate_budget_recommendations(df_need_share, df_supply)
    df_before_after = calculate_before_after_metrics(total_budget=config.base_ad_budget)
    df_financials = get_financial_estimate_df()

    # Step 8: Data Quality Audit
    logger.info("[8/8] Executing data quality audit & compliance checks...")
    df_dq_report = run_data_quality_checks(df_features, df_need_share, df_recommendations)

    # Persist all output artifacts
    out_dir = config.output_dir
    cache_dir = config.raw_cache_dir

    save_csv(df_need_share, out_dir / "pg_need_share.csv")
    save_parquet(df_need_share, out_dir / "pg_need_share.parquet")

    save_csv(df_recommendations, out_dir / "budget_recommendations.csv")
    save_parquet(df_recommendations, out_dir / "budget_recommendations.parquet")

    save_csv(df_before_after, out_dir / "before_after_metrics.csv")
    save_csv(df_financials, out_dir / "financial_estimate.csv")
    save_csv(df_dq_report, out_dir / "data_quality_report.csv")

    # Save feature store
    save_parquet(df_features, cache_dir / "basket_features.parquet")

    # Update SQLite data mart
    persist_data_mart({
        "basket_features": df_features,
        "pg_need_share": df_need_share,
        "budget_recommendations": df_recommendations,
        "before_after_metrics": df_before_after,
        "financial_estimate": df_financials,
        "data_quality_report": df_dq_report,
    })

    logger.info("==================================================")
    logger.info("  PIPELINE EXECUTION COMPLETED SUCCESSFULLY!      ")
    logger.info(f"  All outputs generated in: {out_dir}           ")
    logger.info("==================================================")


def launch_dashboard() -> None:
    """Launches the interactive Streamlit decision dashboard."""
    app_path = root_dir / "src" / "dashboard" / "app.py"
    logger.info(f"Launching Streamlit dashboard at {app_path}...")
    subprocess.run(["streamlit", "run", str(app_path)], check=True)


def main():
    parser = argparse.ArgumentParser(description="P&G Ad Budget Optimizer Orchestrator")
    parser.add_argument("--all", action="store_true", help="Run entire pipeline from ingestion to output generation")
    parser.add_argument("--sample", action="store_true", help="Force sample dataset generator mode")
    parser.add_argument("--dashboard", action="store_true", help="Launch Streamlit dashboard")
    args = parser.parse_args()

    if args.dashboard:
        launch_dashboard()
    else:
        # Default action is running full pipeline
        run_full_pipeline(force_sample=args.sample)


if __name__ == "__main__":
    main()
