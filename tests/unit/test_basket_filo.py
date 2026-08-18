"""
Unit tests for Stack checkout rank, basket sizing, and need zone identification.
"""

import pytest
import pandas as pd
from src.features.basket import calculate_basket_features
from tests.fixtures.sample_data import create_fixture_order_20_items


def test_basket_size_calculation():
    fixture = create_fixture_order_20_items()
    df_feat = calculate_basket_features(fixture["order_products"], fixture["orders"])

    assert len(df_feat) == 20
    assert (df_feat["basket_size"] == 20).all()


def test_checkout_rank_filo_logic():
    """
    Validates Stack (LIFO) checkout sequence:
    Item added 1st should have checkout_rank = 20 (scanned last).
    Item added 20th should have checkout_rank = 1 (scanned first).
    """
    fixture = create_fixture_order_20_items()
    df_feat = calculate_basket_features(fixture["order_products"], fixture["orders"])

    item_1 = df_feat[df_feat["add_to_cart_order"] == 1].iloc[0]
    item_20 = df_feat[df_feat["add_to_cart_order"] == 20].iloc[0]

    assert item_1["checkout_rank"] == 20
    assert item_20["checkout_rank"] == 1


def test_last_10_scanned_need_zone():
    """
    In a basket of size 20:
    Need zone = last 10 scanned items (checkout_rank 11 to 20),
    which corresponds to add_to_cart_order 1 to 10.
    """
    fixture = create_fixture_order_20_items()
    df_feat = calculate_basket_features(fixture["order_products"], fixture["orders"])

    need_zone_items = df_feat[df_feat["is_in_need_zone"]]
    assert len(need_zone_items) == 10
    assert set(need_zone_items["add_to_cart_order"]) == set(range(1, 11))
    assert set(need_zone_items["checkout_rank"]) == set(range(11, 21))


def test_small_basket_fallback():
    """
    For baskets with size < 10, all items are included in need zone with LOW confidence.
    """
    df_small = pd.DataFrame([
        {"order_id": 1, "product_id": 101, "add_to_cart_order": 1},
        {"order_id": 1, "product_id": 102, "add_to_cart_order": 2},
        {"order_id": 1, "product_id": 103, "add_to_cart_order": 3},
    ])
    df_feat = calculate_basket_features(df_small)

    assert len(df_feat) == 3
    assert df_feat["is_in_need_zone"].all()
    assert (df_feat["basket_confidence_flag"] == "LOW").all()
