"""
Realistic Instacart Sample Dataset Generator.
Used as test fixtures, offline demos, and automated fallback when Kaggle terms are pending.
"""

import random
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from src.config import get_config
from src.logging import get_logger

logger = get_logger("sample_generator")


def generate_instacart_sample(
    num_orders: int = 1200,
    num_users: int = 150,
    seed: int = 42,
    save_dir: Path = None
) -> Dict[str, pd.DataFrame]:
    """
    Generates realistic Instacart dataset tables mirroring the exact schema,
    including authentic P&G brand items across household, personal care, and babies departments.
    """
    np.random.seed(seed)
    random.seed(seed)
    config = get_config()

    # 1. Departments
    departments_data = [
        {"department_id": 1, "department": "frozen"},
        {"department_id": 2, "department": "other"},
        {"department_id": 3, "department": "bakery"},
        {"department_id": 4, "department": "produce"},
        {"department_id": 5, "department": "alcohol"},
        {"department_id": 6, "department": "international"},
        {"department_id": 7, "department": "beverages"},
        {"department_id": 8, "department": "pets"},
        {"department_id": 9, "department": "dry goods pasta"},
        {"department_id": 10, "department": "bulk"},
        {"department_id": 11, "department": "personal care"},
        {"department_id": 12, "department": "meat seafood"},
        {"department_id": 13, "department": "pantry"},
        {"department_id": 14, "department": "breakfast"},
        {"department_id": 15, "department": "canned goods"},
        {"department_id": 16, "department": "dairy eggs"},
        {"department_id": 17, "department": "household"},
        {"department_id": 18, "department": "babies"},
        {"department_id": 19, "department": "snacks"},
        {"department_id": 20, "department": "deli"},
        {"department_id": 21, "department": "missing"},
    ]
    df_departments = pd.DataFrame(departments_data)

    # 2. Aisles
    aisles_data = [
        {"aisle_id": 1, "aisle": "prepared soups salads"},
        {"aisle_id": 2, "aisle": "specialty cheeses"},
        {"aisle_id": 3, "aisle": "energy granola bars"},
        {"aisle_id": 4, "aisle": "instant foods"},
        {"aisle_id": 20, "aisle": "oral hygiene"},
        {"aisle_id": 22, "aisle": "hair care"},
        {"aisle_id": 25, "aisle": "soap"},
        {"aisle_id": 30, "aisle": "body lotions soap"},
        {"aisle_id": 54, "aisle": "paper goods"},
        {"aisle_id": 56, "aisle": "diapers wipes"},
        {"aisle_id": 74, "aisle": "dish detergents"},
        {"aisle_id": 75, "aisle": "laundry"},
        {"aisle_id": 77, "aisle": "soft drinks"},
        {"aisle_id": 80, "aisle": "shave needs"},
        {"aisle_id": 84, "aisle": "cleaning products"},
        {"aisle_id": 92, "aisle": "baby food formula"},
        {"aisle_id": 100, "aisle": "chips pretzels"},
        {"aisle_id": 107, "aisle": "chips pretzels"},
        {"aisle_id": 126, "aisle": "feminine care"},
    ]
    df_aisles = pd.DataFrame(aisles_data)

    # 3. Products (Authentic P&G Items + Non-P&G competitors & groceries)
    products_catalog = [
        # P&G Items - Household & Laundry
        (101, "Tide PODS Free & Gentle Liquid Laundry Detergent", 75, 17),
        (102, "Tide Original Liquid Laundry Detergent 64 Loads", 75, 17),
        (103, "Ariel Concentrated Power Liquid Detergent", 75, 17),
        (104, "Dawn Ultra Original Liquid Dish Soap", 74, 17),
        (105, "Dawn Platinum Dishwashing Foam", 74, 17),
        (106, "Downy Ultra Liquid Fabric Conditioner Clean Breeze", 75, 17),
        (107, "Febreze Air Freshener Spray Linen & Sky", 84, 17),
        (108, "Swiffer Sweeper Dry Sweeping Cloth Refills", 84, 17),
        (109, "Cascade Complete Dishwasher Detergent Pods", 74, 17),
        (110, "Bounty Select-a-Size Paper Towels White", 54, 17),
        (111, "Charmin Ultra Soft Toilet Paper 12 Rolls", 54, 17),
        (112, "Gain Flings Original Liquid Laundry Pods", 75, 17),

        # P&G Items - Personal Care & Grooming
        (201, "Pampers Swaddlers Diapers Size 3", 56, 18),
        (202, "Pampers Sensitive Baby Wipes 6-Pack", 56, 18),
        (203, "Whisper Ultra Clean Sanitary Napkins Wings", 126, 11),
        (204, "Always Ultra Thin Size 1 Pads with Wings", 126, 11),
        (205, "Pantene Pro-V Daily Moisture Renewal Shampoo", 22, 11),
        (206, "Head & Shoulders Classic Clean Anti-Dandruff Shampoo", 22, 11),
        (207, "Gillette Fusion5 Men's Razor Blade Refills", 80, 11),
        (208, "Gillette Venus ComfortGlide Women's Razor", 80, 11),
        (209, "Oral-B CrossAction All In One Toothbrush", 20, 11),
        (210, "Crest 3D White Radiant Mint Whitening Toothpaste", 20, 11),
        (211, "Safeguard Antibacterial Liquid Hand Soap", 25, 11),
        (212, "Old Spice High Endurance Pure Sport Deodorant", 30, 11),
        (213, "Olay Regenerist Micro-Sculpting Face Cream", 30, 11),
        (214, "Braun Series 7 Replacement Foil Head", 80, 11),
        (215, "Ambi Pur Car Air Freshener Clip", 84, 17),

        # Non-P&G Generic / Competitor Groceries & Want Items
        (301, "Organic Whole Milk 1 Gallon", 84, 16),
        (302, "Large Grade A Brown Eggs 12 Count", 84, 16),
        (303, "Organic Hass Avocado Single", 24, 4),
        (304, "Organic Bananas Bundle", 24, 4),
        (305, "Boneless Skinless Chicken Breasts", 35, 12),
        (306, "Colgate Total Clean Mint Toothpaste", 20, 11),
        (307, "Seventh Generation Natural Dish Liquid", 74, 17),
        (308, "Huggies Little Snugglers Diapers Size 3", 56, 18),
        (309, "Dove Deep Moisture Nourishing Body Wash", 25, 11),
        (310, "Lay's Classic Potato Chips Party Size", 107, 19),
        (311, "Doritos Nacho Cheese Tortilla Chips", 107, 19),
        (312, "Coca-Cola Classic Soda 12-Pack Cans", 77, 7),
        (313, "Pepsi Wild Cherry Soda 12-Pack", 77, 7),
        (314, "Oreo Double Stuf Chocolate Sandwich Cookies", 61, 19),
        (315, "Ben & Jerry's Half Baked Ice Cream Pint", 37, 1),
        (316, "Snickers Chocolate Candy Bar King Size", 45, 19),
        (317, "Organic Strawberries 1 lb Clamshell", 24, 4),
        (318, "Artisan Sourdough Bread Loaf", 112, 3),
        (319, "Sparkling Water Lime Essence 8-Pack", 77, 7),
        (320, "Heinz Tomato Ketchup 32 oz Bottle", 72, 13),
        (321, "Kraft Natural Extra Sharp Cheddar Cheese", 21, 16),
        (322, "Starbucks Pike Place Medium Roast Ground Coffee", 26, 7),
        (323, "Nature Valley Crunchy Oats 'n Honey Granola Bars", 3, 19),
        (324, "Kleenex Ultra Soft Facial Tissues 3-Pack", 54, 17),
        (325, "Persil ProClean Liquid Laundry Detergent", 75, 17),
    ]

    df_products = pd.DataFrame(
        products_catalog,
        columns=["product_id", "product_name", "aisle_id", "department_id"]
    )

    # 4. Generate Orders & Order Products
    orders_records = []
    order_products_records = []

    need_product_ids = [p[0] for p in products_catalog if p[3] in [11, 17, 18, 16, 4, 12, 13]]
    want_product_ids = [p[0] for p in products_catalog if p[3] in [19, 7, 1, 3, 5]]
    all_product_ids = [p[0] for p in products_catalog]

    for order_id in range(1, num_orders + 1):
        user_id = random.randint(1, num_users)
        order_number = random.randint(1, 40)
        order_dow = random.randint(0, 6)
        order_hour_of_day = random.randint(7, 21)
        days_since_prior = random.choice([3, 5, 7, 10, 14, 21, 30, None])

        orders_records.append({
            "order_id": order_id,
            "user_id": user_id,
            "eval_set": "prior",
            "order_number": order_number,
            "order_dow": order_dow,
            "order_hour_of_day": order_hour_of_day,
            "days_since_prior_order": days_since_prior,
        })

        # Basket size: 6 to 24 items
        basket_size = random.randint(6, 24)

        # Realistic FMCG Shopping Behaviour:
        # Customers select staple Need items first (first in cart, early add_to_cart_order)
        # and discretionary/impulse items later in the shopping trip.
        num_need_items = min(basket_size, random.randint(4, max(4, basket_size - 2)))
        num_want_items = basket_size - num_need_items

        chosen_needs = list(np.random.choice(need_product_ids, size=num_need_items, replace=(num_need_items > len(need_product_ids))))
        chosen_wants = list(np.random.choice(want_product_ids, size=num_want_items, replace=(num_want_items > len(want_product_ids)))) if num_want_items > 0 else []

        ordered_items = chosen_needs + chosen_wants

        for rank, p_id in enumerate(ordered_items, start=1):
            reordered = 1 if random.random() > 0.4 else 0
            order_products_records.append({
                "order_id": order_id,
                "product_id": p_id,
                "add_to_cart_order": rank,
                "reordered": reordered,
            })

    df_orders = pd.DataFrame(orders_records)
    df_order_products = pd.DataFrame(order_products_records)

    logger.info(
        f"Generated sample Instacart dataset: {len(df_orders)} orders, "
        f"{len(df_order_products)} basket items, {len(df_products)} catalog products."
    )

    dataset_dict = {
        "orders": df_orders,
        "order_products__prior": df_order_products,
        "products": df_products,
        "departments": df_departments,
        "aisles": df_aisles,
    }

    if save_dir:
        save_p = Path(save_dir)
        save_p.mkdir(parents=True, exist_ok=True)
        for name, df in dataset_dict.items():
            csv_file = save_p / f"{name}.csv"
            df.to_csv(csv_file, index=False)
        logger.info(f"Saved sample CSVs to {save_p}")

    return dataset_dict
