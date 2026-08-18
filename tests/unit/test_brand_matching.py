"""
Unit tests for P&G brand regex pattern matching and false positive filtering.
"""

import pytest
import pandas as pd
from src.features.brand import enrich_with_pg_brands


def test_pg_brand_identifications():
    """Tests positive detection of standard P&G flagship brands."""
    test_products = pd.DataFrame([
        {"product_id": 1, "product_name": "Tide PODS Ultra Oxi Laundry Detergent"},
        {"product_id": 2, "product_name": "Pampers Swaddlers Diapers Size 4"},
        {"product_id": 3, "product_name": "Gillette Fusion5 Men's Razor Blade Refills"},
        {"product_id": 4, "product_name": "Crest 3D White Radiant Mint Toothpaste"},
        {"product_id": 5, "product_name": "Dawn Platinum Dishwashing Liquid"},
        {"product_id": 6, "product_name": "Head & Shoulders Classic Clean Shampoo"},
        {"product_id": 7, "product_name": "Pantene Pro-V Moisture Conditioner"},
        {"product_id": 8, "product_name": "Febreze Air Freshener Spray"},
        {"product_id": 9, "product_name": "Oral-B CrossAction Pro Toothbrush"},
        {"product_id": 10, "product_name": "Whisper Ultra Clean Sanitary Pads"},
        {"product_id": 11, "product_name": "Downy Liquid Fabric Softener"},
        {"product_id": 12, "product_name": "Safeguard Bar Soap 4 Pack"},
        {"product_id": 13, "product_name": "Old Spice High Endurance Deodorant"},
        {"product_id": 14, "product_name": "Ambi Pur Car Vent Clip Freshener"},
    ])

    enriched = enrich_with_pg_brands(test_products)
    assert enriched["is_pg_product"].all()
    assert enriched["matched_brand"].nunique() >= 10


def test_non_pg_and_false_positive_exclusions():
    """Tests that competitor products and exclusion terms are not tagged as P&G."""
    test_products = pd.DataFrame([
        {"product_id": 201, "product_name": "Colgate Total Whitening Toothpaste"},
        {"product_id": 202, "product_name": "Huggies Snug & Dry Diapers"},
        {"product_id": 203, "product_name": "Persil ProClean Liquid Detergent"},
        {"product_id": 204, "product_name": "Dove Sensitive Skin Beauty Bar"},
        {"product_id": 205, "product_name": "High Tide Organic Whole Wheat Bread"},
        {"product_id": 206, "product_name": "Mountain Crest Spring Water"},
        {"product_id": 207, "product_name": "Lay's Classic Potato Chips"},
    ])

    enriched = enrich_with_pg_brands(test_products)
    assert not enriched["is_pg_product"].any()
    assert (enriched["matched_brand"] == "Non-P&G").all()
