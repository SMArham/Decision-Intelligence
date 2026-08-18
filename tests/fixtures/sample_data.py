"""
Standard test fixtures for pg_ad_optimizer test suite.
"""

from typing import Dict
import pandas as pd


def create_fixture_order_20_items() -> Dict[str, pd.DataFrame]:
    """
    Creates a standardized fixture order with exactly 20 products.
    First 10 items added to cart contain exactly 5 P&G products.
    Items 11-20 contain only Non-P&G products.
    """
    df_orders = pd.DataFrame([{
        "order_id": 9999,
        "user_id": 101,
        "eval_set": "prior",
        "order_number": 5,
        "order_dow": 2,
        "order_hour_of_day": 14,
        "days_since_prior_order": 7,
    }])

    # 20 items in order
    op_records = []
    prod_records = []

    # First 10 items (Need Zone) - 5 P&G items and 5 Non-P&G items
    need_zone_products = [
        (1, "Tide Liquid Laundry Detergent", 17, "household", True),
        (2, "Pampers Baby Dry Diapers", 18, "babies", True),
        (3, "Organic Whole Milk", 16, "dairy eggs", False),
        (4, "Gillette Fusion Men's Razor", 11, "personal care", True),
        (5, "Fresh Hass Avocado", 4, "produce", False),
        (6, "Crest 3D White Toothpaste", 11, "personal care", True),
        (7, "Bananas Bunch", 4, "produce", False),
        (8, "Dawn Ultra Dish Soap", 17, "household", True),
        (9, "Grade A Brown Eggs", 16, "dairy eggs", False),
        (10, "Artisan Sourdough Loaf", 3, "bakery", False),
    ]

    for rank, (pid, name, dept_id, dept, is_pg) in enumerate(need_zone_products, start=1):
        op_records.append({
            "order_id": 9999,
            "product_id": pid,
            "add_to_cart_order": rank,
            "reordered": 1,
        })
        prod_records.append({
            "product_id": pid,
            "product_name": name,
            "department_id": dept_id,
            "department": dept,
            "aisle_id": 1,
        })

    # Next 10 items (Discretionary Want Zone, items 11 to 20) - All Non-P&G
    want_zone_products = [
        (11, "Lay's Potato Chips", 19, "snacks", False),
        (12, "Doritos Nacho Cheese", 19, "snacks", False),
        (13, "Coca-Cola 12 Pack", 7, "beverages", False),
        (14, "Pepsi Wild Cherry", 7, "beverages", False),
        (15, "Oreo Sandwich Cookies", 19, "snacks", False),
        (16, "Ben & Jerry's Ice Cream", 1, "frozen", False),
        (17, "Snickers King Size Bar", 19, "snacks", False),
        (18, "Sparkling Lime Water", 7, "beverages", False),
        (19, "Pretzel Crisps", 19, "snacks", False),
        (20, "Gourmet Dark Chocolate", 19, "snacks", False),
    ]

    for rank, (pid, name, dept_id, dept, is_pg) in enumerate(want_zone_products, start=11):
        op_records.append({
            "order_id": 9999,
            "product_id": pid,
            "add_to_cart_order": rank,
            "reordered": 0,
        })
        prod_records.append({
            "product_id": pid,
            "product_name": name,
            "department_id": dept_id,
            "department": dept,
            "aisle_id": 2,
        })

    df_order_products = pd.DataFrame(op_records)
    df_products = pd.DataFrame(prod_records)
    df_departments = pd.DataFrame([
        {"department_id": 1, "department": "frozen"},
        {"department_id": 3, "department": "bakery"},
        {"department_id": 4, "department": "produce"},
        {"department_id": 7, "department": "beverages"},
        {"department_id": 11, "department": "personal care"},
        {"department_id": 16, "department": "dairy eggs"},
        {"department_id": 17, "department": "household"},
        {"department_id": 18, "department": "babies"},
        {"department_id": 19, "department": "snacks"},
    ])

    return {
        "orders": df_orders,
        "order_products": df_order_products,
        "products": df_products,
        "departments": df_departments,
    }
