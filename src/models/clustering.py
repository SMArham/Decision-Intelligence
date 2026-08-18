"""
K-Means Customer Basket Behavioral Clustering.
Segments shopping baskets into distinct behavioral archetypes:
1. Staple Family Shoppers (High need share, large baskets)
2. Quick Convenience / Impulse Buyers (Small baskets, want-heavy)
3. Essential Hygiene & Baby Care Focused (High P&G brand loyalty)
"""

from typing import Dict, Tuple
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from src.config import get_config
from src.logging import get_logger

logger = get_logger("basket_clustering")


def perform_basket_clustering(
    df_features: pd.DataFrame,
    n_clusters: int = 3
) -> Tuple[pd.DataFrame, pd.DataFrame, KMeans]:
    """
    Performs K-Means clustering on basket-level behavioral metrics:
    - basket_size: Total items in basket
    - need_zone_item_count: Count of items in need zone
    - pg_item_count: Total P&G branded items in basket
    - pg_need_share: P&G share within need zone
    - reorder_rate: Proportion of items reordered
    """
    config = get_config()

    if df_features.empty or "order_id" not in df_features.columns:
        logger.warning("Empty features table provided for clustering.")
        return pd.DataFrame(), pd.DataFrame(), None

    # Aggregate to basket level
    basket_df = df_features.groupby("order_id").agg(
        basket_size=("basket_size", "first"),
        need_items=("is_in_need_zone", "sum"),
        pg_items=("is_pg_product", "sum"),
        pg_need_items=("is_pg_product", lambda x: (x & df_features.loc[x.index, "is_in_need_zone"]).sum()),
        reorder_rate=("reordered", "mean") if "reordered" in df_features.columns else ("basket_size", "count")
    ).reset_index()

    basket_df["pg_need_share"] = np.where(
        basket_df["need_items"] > 0,
        basket_df["pg_need_items"] / basket_df["need_items"],
        0.0
    )

    feature_cols = ["basket_size", "need_items", "pg_items", "pg_need_share", "reorder_rate"]
    X = basket_df[feature_cols].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=config.random_seed, n_init=10)
    basket_df["cluster"] = kmeans.fit_predict(X_scaled)

    # Assign meaningful archetype names based on cluster centroids
    cluster_summary = basket_df.groupby("cluster").agg(
        total_orders=("order_id", "count"),
        avg_basket_size=("basket_size", "mean"),
        avg_need_items=("need_items", "mean"),
        avg_pg_items=("pg_items", "mean"),
        avg_pg_need_share=("pg_need_share", "mean"),
        avg_reorder_rate=("reorder_rate", "mean")
    ).reset_index()

    # Determine labels dynamically
    cluster_labels = {}
    for idx, row in cluster_summary.iterrows():
        if row["avg_pg_need_share"] >= 0.35 and row["avg_basket_size"] >= 12:
            label = "Staple Family Shoppers"
        elif row["avg_pg_need_share"] >= 0.25:
            label = "Hygiene & Care Focused"
        else:
            label = "Quick / Impulse Buyers"
        cluster_labels[row["cluster"]] = label

    basket_df["cluster_archetype"] = basket_df["cluster"].map(cluster_labels)
    cluster_summary["archetype_name"] = cluster_summary["cluster"].map(cluster_labels)

    logger.info(f"K-Means clustering completed into {n_clusters} customer shopping archetypes.")
    return basket_df, cluster_summary, kmeans
