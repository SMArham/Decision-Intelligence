"""
Unit tests for AI enhancements: K-Means Basket Clustering and Fuzzy Logic Inference.
"""

import pytest
import pandas as pd
from src.models.clustering import perform_basket_clustering
from src.models.fuzzy_engine import FuzzyBudgetInferenceSystem
from tests.fixtures.sample_data import create_fixture_order_20_items
from src.features.basket import calculate_basket_features
from src.features.brand import enrich_with_pg_brands


def test_fuzzy_inference_stockout_protection():
    """Validates that critical stockout in fuzzy logic reduces multiplier toward 0.0."""
    fuzzy_sys = FuzzyBudgetInferenceSystem()
    # High demand (0.60) but critical stockout (0.30)
    mult = fuzzy_sys.evaluate_fuzzy_multiplier(need_share=0.60, supply_score=0.30)
    assert mult < 0.15


def test_fuzzy_inference_healthy_expansion():
    """Validates that healthy supply with strong demand yields an expansion multiplier > 1.2."""
    fuzzy_sys = FuzzyBudgetInferenceSystem()
    mult = fuzzy_sys.evaluate_fuzzy_multiplier(need_share=0.65, supply_score=0.95)
    assert 1.20 <= mult <= 1.45


def test_kmeans_basket_clustering():
    """Validates that K-Means clusters baskets into valid archetypes."""
    fixture = create_fixture_order_20_items()
    df_products = enrich_with_pg_brands(fixture["products"])
    df_feat = calculate_basket_features(fixture["order_products"], fixture["orders"])
    df_feat = df_feat.merge(df_products[["product_id", "is_pg_product"]], on="product_id", how="left")

    baskets, summary, model = perform_basket_clustering(df_feat, n_clusters=1)
    assert not baskets.empty
    assert "cluster" in baskets.columns
    assert "cluster_archetype" in baskets.columns
