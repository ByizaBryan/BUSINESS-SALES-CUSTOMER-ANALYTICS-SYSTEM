"""
InsightMart Business Sales & Customer Analytics System
Module: src/data_generation.py
Description: Generates realistic enterprise synthetic business data for InsightMart.
             Includes retail seasonality, store performance tiers, customer lifetime behaviors,
             product margins, and controlled real-world data noise for data pipeline validation.
"""

import os
import random
import csv
from datetime import datetime, date, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

# Fixed seed for deterministic, reproducible enterprise generation
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
os.makedirs(RAW_DIR, exist_ok=True)


# ==============================================================================
# Master Reference Data
# ==============================================================================

CATEGORIES_DATA = [
    (1, "Electronics", "Consumer electronics, audio equipment, computing accessories, and smart devices"),
    (2, "Apparel", "Men, women, and children casual wear, activewear, outerwear, and accessories"),
    (3, "Home & Kitchen", "Small appliances, cookware, dinnerware, home organization, and decor"),
    (4, "Health & Beauty", "Skincare, cosmetics, personal grooming, oral care, and wellness essentials"),
    (5, "Sports & Outdoors", "Athletic gear, fitness equipment, yoga accessories, and outdoor recreation"),
    (6, "Groceries & Gourmet", "Packaged gourmet foods, artisanal coffees, teas, snacks, and condiments")
]

SUPPLIERS_DATA = [
    (1, "Apex Tech Distribution", "orders@apextech.com | +1-312-555-0101", "Chicago"),
    (2, "Vanguard Global Brands", "b2b@vanguardgb.com | +1-212-555-0102", "New York"),
    (3, "Heritage Home Goods", "supply@heritagehg.com | +1-214-555-0103", "Dallas"),
    (4, "Lumina Care & Wellness", "sales@luminacare.com | +1-213-555-0104", "Los Angeles"),
    (5, "Titan Athletics Inc", "partner@titanathletics.com | +1-206-555-0105", "Seattle"),
    (6, "GreenValley Food Co", "vendor@greenvalleyfood.com | +1-303-555-0106", "Denver"),
    (7, "Metro Sound Innovations", "wholesale@metrosound.com | +1-512-555-0107", "Austin"),
    (8, "Nordic Fabric Works", "info@nordicfabrics.com | +1-617-555-0108", "Boston"),
    (9, "KitchenPro Dynamics", "commercial@kitchenpro.com | +1-404-555-0109", "Atlanta"),
    (10, "Zenith Lifestyle Goods", "inquiries@zenithlife.com | +1-415-555-0110", "San Francisco")
]

STORES_DATA = [
    (1, "InsightMart Downtown Chicago", "Chicago", "Midwest", "2021-03-15", 1.25),      # Tier 1 Flagship
    (2, "InsightMart Manhattan Flagship", "New York", "Northeast", "2020-01-10", 1.45),   # Tier 1 Top Performer
    (3, "InsightMart Dallas Galleria", "Dallas", "South", "2021-07-22", 1.10),
    (4, "InsightMart LA Sunset", "Los Angeles", "West", "2020-05-18", 1.30),             # Tier 1 Flagship
    (5, "InsightMart Seattle Center", "Seattle", "Northwest", "2022-02-01", 1.05),
    (6, "InsightMart Denver Rockies", "Denver", "West", "2022-06-14", 0.85),             # Developing
    (7, "InsightMart Austin Tech Ridge", "Austin", "South", "2021-11-05", 1.08),
    (8, "InsightMart Boston Back Bay", "Boston", "Northeast", "2020-09-30", 1.15),
    (9, "InsightMart Atlanta Midtown", "Atlanta", "Southeast", "2021-04-12", 1.00),
    (10, "InsightMart SF Bay Pavilion", "San Francisco", "West", "2020-11-20", 1.20),
    (11, "InsightMart Miami Biscayne", "Miami", "Southeast", "2022-08-19", 0.90),        # Developing
    (12, "InsightMart Minneapolis Plaza", "Minneapolis", "Midwest", "2023-01-15", 0.75)  # Developing
]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
    "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
    "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra",
    "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Melissa", "George", "Deborah", "Timothy", "Stephanie",
    "Ronald", "Rebecca", "Edward", "Sharon", "Jason", "Laura", "Jeffrey", "Cynthia", "Ryan", "Dorothy",
    "Jacob", "Amy", "Gary", "Kathleen", "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Emma",
    "Stephen", "Brenda", "Larry", "Pamela", "Justin", "Nicole", "Scott", "Anna", "Brandon", "Samantha",
    "Benjamin", "Katherine", "Samuel", "Christine", "Gregory", "Debra", "Alexander", "Rachel", "Frank", "Carolyn"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper"
]

CITIES = ["Chicago", "New York", "Dallas", "Los Angeles", "Seattle", "Denver", "Austin", "Boston", "Atlanta", "San Francisco", "Miami", "Minneapolis"]


# ==============================================================================
# Product Catalog Definitions (120 Realistic Retail SKUs)
# ==============================================================================

PRODUCT_TEMPLATES = [
    # Category 1: Electronics (High Revenue, Lower Margin 22% - 38%)
    (1, 1, "UltraWireless Noise-Cancelling Headphones", 95.00, 189.99),
    (1, 7, "SmartWatch Pro Series 5", 120.00, 239.99),
    (1, 1, "Bluetooth Ergonomic Mechanical Keyboard", 42.00, 79.99),
    (1, 7, "4K UltraHD Streaming Dongle", 17.50, 34.99),
    (1, 1, "True Wireless Earbuds with Wireless Case", 38.00, 69.99),
    (1, 7, "27-Inch 144Hz QHD Gaming Monitor", 175.00, 279.99),
    (1, 1, "USB-C Dual 4K Universal Docking Station", 65.00, 119.99),
    (1, 7, "Portable Waterproof Bluetooth Speaker 20W", 28.00, 54.99),
    (1, 1, "High-Speed MagSafe Wireless Charging Pad", 14.00, 29.99),
    (1, 7, "Smart Security Wi-Fi Camera 2K Indoor", 22.00, 44.99),
    (1, 1, "PowerBank 20000mAh 65W Fast Charge", 26.00, 49.99),
    (1, 7, "Noise-Isolating Studio Over-Ear Headphones", 60.00, 109.99),
    (1, 1, "Smart Home Voice Assistant Speaker", 30.00, 59.99),
    (1, 7, "Ultra-Slim Wireless Numeric Keypad", 15.00, 29.99),
    (1, 1, "Multi-Port 100W GaN Travel Charger", 24.00, 47.99),
    (1, 7, "Digital Drawing Graphics Tablet 10x6", 45.00, 89.99),
    (1, 1, "Dash Cam 4K Front and Rear GPS", 68.00, 129.99),
    (1, 7, "Smart LED Color Ambient Light Bar Duo", 25.00, 49.99),
    (1, 1, "Precision Optical Wireless Mouse", 12.50, 24.99),
    (1, 7, "Noise-Cancelling Conference Microphone", 40.00, 79.99),

    # Category 2: Apparel (Moderate-High Margin 45% - 68%)
    (2, 2, "Premium Merino Wool Crewneck Sweater", 28.00, 74.99),
    (2, 8, "Slim-Fit Stretch Denim Jeans", 21.00, 59.99),
    (2, 2, "Weatherproof All-Season Expedition Parka", 65.00, 169.99),
    (2, 8, "Breathable Athletic Performance Tee", 8.50, 24.99),
    (2, 2, "Organic Pima Cotton Casual Polo Shirt", 14.00, 39.99),
    (2, 8, "Comfort Stretch Chino Trousers", 18.00, 49.99),
    (2, 2, "Water-Resistant Softshell Trail Jacket", 35.00, 89.99),
    (2, 8, "Seamless High-Waist Athletic Leggings", 12.00, 38.00),
    (2, 2, "Brushed Fleece Pullover Hoodie", 16.50, 46.99),
    (2, 8, "Pack of 3 Everyday Crewneck Undershirts", 9.00, 24.50),
    (2, 2, "Tailored Linen Blend Summer Button-Down", 16.00, 44.99),
    (2, 8, "Thermal Base Layer Compression Pants", 11.50, 29.99),
    (2, 2, "Windproof Packable Running Vest", 19.00, 48.00),
    (2, 8, "Classic Knit Ribbed Beanie Cap", 5.00, 18.00),
    (2, 2, "Genuine Leather Minimalist Belt", 12.00, 34.99),
    (2, 8, "Cushioned Merino Wool Hiking Socks 3pk", 8.00, 22.99),
    (2, 2, "Quilted Lightweight Transitional Vest", 24.00, 64.99),
    (2, 8, "Relaxed Fit Cotton Flannel Overshirt", 17.50, 46.00),
    (2, 2, "Moisture-Wicking Training Shorts", 9.50, 27.99),
    (2, 8, "Polar Fleece Full-Zip Loungewear", 20.00, 52.00),

    # Category 3: Home & Kitchen (Margin 38% - 58%)
    (3, 9, "Stainless Steel Compact Espresso Machine", 95.00, 219.99),
    (3, 3, "Tri-Ply Clad Stainless Cookware Set 10pc", 62.00, 149.99),
    (3, 3, "Smart HEPA Air Purifier with PM2.5 Sensor", 48.00, 114.99),
    (3, 9, "Enameled Cast Iron Dutch Oven 6-Quart", 26.00, 68.99),
    (3, 3, "Programmable Precision Electric Kettle 1.7L", 18.00, 44.99),
    (3, 9, "Multi-Function High-Speed Blender 1200W", 42.00, 99.99),
    (3, 3, "Digital Dual-Zone Air Fryer 8-Quart", 50.00, 119.99),
    (3, 9, "Handcrafted Japanese Santoku Chef Knife", 22.00, 54.99),
    (3, 3, "Aromatherapy Ultrasonic Diffuser 500ml", 11.00, 28.99),
    (3, 9, "Bamboo Modular Drawer Organizers 6pc", 9.00, 24.99),
    (3, 3, "Weighted Cooling Blanket 15lb Organic Cotton", 30.00, 69.99),
    (3, 9, "Non-Slip Microfiber Bath Mat Set 2pc", 7.50, 21.99),
    (3, 3, "Vacuum Insulated French Press Coffee Maker", 14.50, 36.99),
    (3, 9, "Ceramic Non-Stick Everyday Fry Pan 12-inch", 15.00, 38.00),
    (3, 3, "Smart Wi-Fi Food Dehydrator 5-Tray", 38.00, 84.99),
    (3, 9, "Under-Cabinet Magnetic Knife Strip", 8.00, 21.99),
    (3, 3, "Stainless Steel Kitchen Scale Precision 0.1g", 7.00, 19.99),
    (3, 9, "Silicone Heat-Resistant Utensil Set 10pc", 10.00, 26.99),
    (3, 3, "Memory Foam Contour Bed Pillow", 14.00, 34.99),
    (3, 9, "Countertop Compost Bin Odorless Stainless", 11.00, 27.99),

    # Category 4: Health & Beauty (High Margin 55% - 75%)
    (4, 4, "Hydrating Vitamin C + Hyaluronic Serum 30ml", 7.50, 28.99),
    (4, 4, "Botanical Gentle Cleansing Facial Oil 150ml", 6.20, 22.50),
    (4, 10, "Sonic Electric Toothbrush with 4 Heads", 22.00, 64.99),
    (4, 4, "Mineral SPF 50 Sheer Sunscreen 100ml", 5.50, 18.99),
    (4, 10, "Collagen Peptide Revitalizing Night Cream", 9.00, 34.99),
    (4, 4, "Nourishing Argan & Keratin Hair Mask", 6.80, 24.00),
    (4, 10, "Ionic Deep Conditioning Hair Dryer 1800W", 25.00, 69.99),
    (4, 4, "Rosewater & Aloe Soothing Facial Toner", 4.20, 16.50),
    (4, 10, "Ultrasonic Skin Scrubber Exfoliator Spatula", 13.00, 36.99),
    (4, 4, "Organic Shea Butter Body Cream 250ml", 5.80, 19.99),
    (4, 10, "Rechargeable Cordless Water Flosser 300ml", 14.00, 38.99),
    (4, 4, "Biotin + Zinc Hair Growth Vitamins 60ct", 6.50, 22.99),
    (4, 10, "Acupressure Mat and Neck Pillow Set", 12.00, 32.99),
    (4, 4, "Gentle Exfoliating AHA/BHA Peeling Solution", 6.00, 21.00),
    (4, 10, "Heated Eye Massager with Air Compression", 24.00, 59.99),
    (4, 4, "Natural Charcoal Teeth Whitening Powder", 3.80, 14.99),
    (4, 10, "Rose Quartz Facial Roller and Gua Sha", 4.50, 17.50),
    (4, 4, "Epsom Salt & Lavender Muscle Soak 2kg", 4.00, 14.99),
    (4, 10, "LED Light Therapy Face Mask 7 Colors", 38.00, 94.99),
    (4, 4, "Tea Tree Clarifying Spot Treatment 15ml", 3.50, 13.99),

    # Category 5: Sports & Outdoors (Margin 42% - 58%)
    (5, 5, "Pro-Grip Eco-Friendly Non-Slip Yoga Mat", 13.00, 34.99),
    (5, 5, "High-Density Foam Roller 36-Inch Deep Tissue", 8.50, 22.99),
    (5, 10, "Insulated Stainless Hydration Flask 32oz", 9.50, 26.99),
    (5, 5, "Adjustable Quick-Select Dumbbell 50lb", 95.00, 199.99),
    (5, 10, "Lightweight Ultralight 2-Person Backpacking Tent", 58.00, 139.99),
    (5, 5, "Resistance Exercise Band Set 5-Resistance", 7.00, 19.99),
    (5, 10, "Trekking Poles Carbon Fiber Collapsible Pair", 18.00, 44.99),
    (5, 5, "Speed Jump Rope Ball-Bearing Steel Cable", 5.00, 15.99),
    (5, 10, "Hydration Running Backpack 2L Water Bladder", 16.00, 39.99),
    (5, 5, "Exercise Ball 65cm Anti-Burst with Pump", 8.00, 21.99),
    (5, 10, "Portable Camping Hammock with Tree Straps", 11.00, 28.99),
    (5, 5, "Deep Tissue Percussion Muscle Massage Gun", 32.00, 79.99),
    (5, 10, "Waterproof Dry Bag 20L with Phone Pouch", 7.50, 19.99),
    (5, 5, "Pull-Up Bar Doorway Trainer Multi-Grip", 14.00, 34.99),
    (5, 10, "Compact Camp Stove Burner Windproof Piezo", 9.00, 24.50),
    (5, 5, "Gym Chalk Ball 2-Pack 100% Magnesium", 4.00, 12.99),
    (5, 10, "Swimming Goggles Polarized Anti-Fog UV", 6.50, 18.99),
    (5, 5, "Agility Ladder & Cones Speed Training Set", 9.50, 23.99),
    (5, 10, "LED Rechargeable Headlamp 1000 Lumens", 8.00, 21.99),
    (5, 5, "Weightlifting Wrist Wraps & Grips Set", 5.50, 16.99),

    # Category 6: Groceries & Gourmet (High Volume, Lower Margin 24% - 40%)
    (6, 6, "Organic Single-Origin Roast Coffee Beans 1lb", 6.20, 14.99),
    (6, 6, "Matcha Green Tea Powder Ceremonial Grade 100g", 9.50, 22.99),
    (6, 6, "Extra Virgin Cold-Pressed Olive Oil 750ml", 7.80, 17.99),
    (6, 6, "Raw Organic Wildflower Honey 500g Glass Jar", 5.20, 12.99),
    (6, 6, "Dark Chocolate Almond Artisanal Bark 250g", 3.50, 8.99),
    (6, 6, "Organic Whole Spelt Granola with Cranberries", 3.80, 8.49),
    (6, 6, "Pure Maple Syrup Grade A Amber 500ml", 6.00, 13.99),
    (6, 6, "Himalayan Pink Rock Salt Grinder 300g", 2.20, 5.99),
    (6, 6, "Aged Balsamic Vinegar of Modena 250ml", 6.50, 15.99),
    (6, 6, "Organic Medjool Dates Jumbo 1lb Box", 4.50, 10.99),
    (6, 6, "Gluten-Free Roasted Nut & Seed Mix 400g", 4.80, 11.49),
    (6, 6, "Artisan Loose Leaf Earl Grey Tea 150g Tin", 4.20, 10.50),
    (6, 6, "Cold-Brew Coffee Pitcher Concentrated Packs", 5.50, 13.49),
    (6, 6, "Crispy Rosemary Sea Salt Flatbread Crackers", 2.10, 5.49),
    (6, 6, "Avocado Oil Cooking Spray Pure Expeller-Pressed", 3.40, 7.99),
    (6, 6, "Organic Rolled Oats Whole Grain 2lb Bag", 2.00, 5.29),
    (6, 6, "Spiced Chai Tea Concentrate Blend 32oz", 3.60, 8.99),
    (6, 6, "Smoked Paprika & Garlic Dry Rub Blend 120g", 2.30, 6.49),
    (6, 6, "Kombucha Starter Probiotic Tea 12pk Cans", 12.00, 24.99),
    (6, 6, "Stone-Ground Organic Almond Butter 16oz", 5.80, 12.99)
]


def generate_categories_and_suppliers():
    """Generates categories.csv and suppliers.csv."""
    categories_df = pd.DataFrame(CATEGORIES_DATA, columns=["category_id", "category_name", "description"])
    categories_df.to_csv(RAW_DIR / "categories.csv", index=False)

    suppliers_df = pd.DataFrame(SUPPLIERS_DATA, columns=["supplier_id", "supplier_name", "contact_information", "city"])
    suppliers_df.to_csv(RAW_DIR / "suppliers.csv", index=False)
    return categories_df, suppliers_df


def generate_stores():
    """Generates stores.csv with retail store details."""
    clean_stores = [(s[0], s[1], s[2], s[3], s[4]) for s in STORES_DATA]
    stores_df = pd.DataFrame(clean_stores, columns=["store_id", "store_name", "city", "region", "opening_date"])
    stores_df.to_csv(RAW_DIR / "stores.csv", index=False)
    return stores_df


def generate_products():
    """Generates products.csv (120 SKUs) with stock quantities and status."""
    products = []
    for idx, template in enumerate(PRODUCT_TEMPLATES, 1):
        cat_id, sup_id, name, unit_cost, selling_price = template
        stock = random.randint(25, 350)
        reorder = random.choice([15, 20, 25, 30, 40])
        # 95% Active, 5% Discontinued or Out of Stock for realistic inventory management
        status_prob = random.random()
        status = "Active" if status_prob < 0.94 else ("Out of Stock" if status_prob < 0.98 else "Discontinued")

        products.append({
            "product_id": idx,
            "product_name": name,
            "category_id": cat_id,
            "supplier_id": sup_id,
            "unit_cost": round(unit_cost, 2),
            "selling_price": round(selling_price, 2),
            "stock_quantity": stock,
            "reorder_level": reorder,
            "status": status
        })

    products_df = pd.DataFrame(products)
    products_df.to_csv(RAW_DIR / "products.csv", index=False)
    return products_df


def generate_customers(num_customers=5000):
    """
    Generates customers.csv with realistic customer profiles, demographics,
    segments, and registration dates.
    Injects realistic minor raw-data noise (trailing whitespace in 2% of records).
    """
    customers = []
    start_reg = date(2022, 1, 1)
    end_reg = date(2025, 6, 30)
    delta_reg_days = (end_reg - start_reg).days

    for cid in range(1, num_customers + 1):
        gender = random.choice(["Male", "Female"])
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)

        # Realistic age distribution (18 to 72 years old)
        birth_year = random.randint(1953, 2006)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        dob = date(birth_year, birth_month, birth_day)

        # City assignment aligned with store footprint
        city = random.choice(CITIES)

        # Realistic segment distribution: 18% High Value, 42% Medium Value, 40% Low Value
        r_seg = random.random()
        if r_seg < 0.18:
            segment = "High Value"
        elif r_seg < 0.60:
            segment = "Medium Value"
        else:
            segment = "Low Value"

        reg_days = random.randint(0, delta_reg_days)
        reg_date = start_reg + timedelta(days=reg_days)

        # Inject realistic data noise: 1% chance of whitespace or lowercase
        first_clean = first
        last_clean = last
        if random.random() < 0.015:
            first_clean = f" {first} "
        if random.random() < 0.01:
            city_val = city.lower()
        else:
            city_val = city

        customers.append({
            "customer_id": cid,
            "first_name": first_clean,
            "last_name": last_clean,
            "gender": gender,
            "date_of_birth": dob.strftime("%Y-%m-%d"),
            "customer_segment": segment,
            "city": city_val,
            "registration_date": reg_date.strftime("%Y-%m-%d")
        })

    customers_df = pd.DataFrame(customers)
    customers_df.to_csv(RAW_DIR / "customers.csv", index=False)
    return customers_df


def generate_sales_and_items(customers_df, products_df, target_sales=32000):
    """
    Generates realistic historical transactions (SALES and SALE_ITEMS) covering 2024 and 2025.
    Applies realistic retail factors:
    - November / December holiday surges
    - Summer volume bump
    - Weekend purchase frequency
    - Customer segment repeat frequency (High Value shoppers buy more frequently)
    - Store performance weighting
    - Basket sizes (1 to 5 items)
    - Promotional discounts (5% to 25%)
    """
    start_date = date(2024, 1, 1)
    end_date = date(2025, 12, 31)
    total_days = (end_date - start_date).days + 1

    # Pre-parse customers by segment for realistic repeat purchasing
    high_val_cids = customers_df[customers_df["customer_segment"] == "High Value"]["customer_id"].tolist()
    med_val_cids = customers_df[customers_df["customer_segment"] == "Medium Value"]["customer_id"].tolist()
    low_val_cids = customers_df[customers_df["customer_segment"] == "Low Value"]["customer_id"].tolist()

    # Pre-compute store IDs and weights based on performance tiers
    store_ids = [s[0] for s in STORES_DATA]
    store_weights = [s[5] for s in STORES_DATA]
    store_weights_norm = np.array(store_weights) / sum(store_weights)

    # Product popularity weighting (80/20 power law rule)
    num_products = len(products_df)
    # Generate Zipfian / power-law popularity distribution
    prod_ranks = np.arange(1, num_products + 1)
    prod_probs = 1.0 / np.power(prod_ranks, 0.75)
    prod_probs /= prod_probs.sum()
    product_records = products_df.to_dict("records")

    # Payment method distributions
    payment_methods_instore = ["Credit Card", "Debit Card", "Digital Wallet", "Cash"]
    payment_weights_instore = [0.48, 0.28, 0.16, 0.08]

    payment_methods_online = ["Credit Card", "Debit Card", "Digital Wallet"]
    payment_weights_online = [0.60, 0.20, 0.20]

    sales_records = []
    sale_item_records = []

    sale_counter = 0
    item_counter = 0

    # Determine daily transaction target distribution across 731 days
    daily_weights = []
    date_list = []
    for d in range(total_days):
        cur_date = start_date + timedelta(days=d)
        date_list.append(cur_date)

        # Baseline weight
        weight = 1.0

        # Day of week seasonality: Friday (4), Saturday (5), Sunday (6)
        dow = cur_date.weekday()
        if dow in (4, 5):
            weight *= 1.35
        elif dow == 6:
            weight *= 1.20
        elif dow == 1:  # Tuesday lull
            weight *= 0.85

        # Monthly / Annual Seasonality
        m = cur_date.month
        day = cur_date.day

        # Q4 Surge: Black Friday / Holiday Season
        if m == 11 and day >= 20:
            weight *= 2.2  # Black Friday week
        elif m == 12 and day <= 24:
            weight *= 2.5  # Holiday peak
        elif m == 12 and day > 24:
            weight *= 1.4  # Post-Christmas sales
        elif m in (6, 7):
            weight *= 1.25  # Summer sales bump
        elif m in (1, 2):
            weight *= 0.82  # Post-holiday slump

        daily_weights.append(weight)

    daily_weights = np.array(daily_weights) / sum(daily_weights)
    daily_sales_counts = np.random.multinomial(target_sales, daily_weights)

    print(f"Generating ~{target_sales} sales transactions across 24 months...")

    for d_idx, cur_date in enumerate(date_list):
        num_sales_today = daily_sales_counts[d_idx]
        cur_date_str = cur_date.strftime("%Y-%m-%d")

        for _ in range(num_sales_today):
            sale_counter += 1

            # Select customer segment with realistic purchase propensity
            # High-value customers purchase much more frequently
            seg_roll = random.random()
            if seg_roll < 0.45:  # 45% of transactions from High Value
                cust_id = random.choice(high_val_cids)
            elif seg_roll < 0.80:  # 35% from Medium Value
                cust_id = random.choice(med_val_cids)
            else:  # 20% from Low Value
                cust_id = random.choice(low_val_cids)

            # Store selection weighted by store tier
            store_id = np.random.choice(store_ids, p=store_weights_norm)

            # Channel: 65% In-Store, 35% Online
            is_online = random.random() < 0.35
            sales_channel = "Online" if is_online else "In-Store"

            if is_online:
                payment_method = np.random.choice(payment_methods_online, p=payment_weights_online)
            else:
                payment_method = np.random.choice(payment_methods_instore, p=payment_weights_instore)

            # Add sale transaction
            sales_records.append({
                "sale_id": sale_counter,
                "sale_date": cur_date_str,
                "customer_id": cust_id,
                "store_id": int(store_id),
                "payment_method": payment_method,
                "sales_channel": sales_channel
            })

            # Line items per transaction: 1 to 5 items (geometric/poisson)
            # Basket size distribution: 1 item (45%), 2 items (30%), 3 items (15%), 4 items (7%), 5 items (3%)
            basket_size = np.random.choice([1, 2, 3, 4, 5], p=[0.45, 0.30, 0.15, 0.07, 0.03])

            # Select distinct products for this transaction based on popularity
            selected_indices = np.random.choice(num_products, size=basket_size, replace=False, p=prod_probs)

            for prod_idx in selected_indices:
                item_counter += 1
                prod = product_records[prod_idx]
                p_id = prod["product_id"]
                unit_price = prod["selling_price"]

                # Quantity: 1 (75%), 2 (18%), 3 (5%), 4 (2%)
                qty = np.random.choice([1, 2, 3, 4], p=[0.75, 0.18, 0.05, 0.02])

                # Discount structure: 70% no discount, 20% promotional (5-15%), 10% holiday/clearance (20-30%)
                disc_roll = random.random()
                subtotal = qty * unit_price

                if cur_date.month == 12 or (cur_date.month == 11 and cur_date.day >= 20):
                    # Holiday season has higher discount frequency
                    if disc_roll < 0.40:
                        discount = 0.0
                    elif disc_roll < 0.75:
                        pct = random.choice([0.05, 0.10, 0.15])
                        discount = round(subtotal * pct, 2)
                    else:
                        pct = random.choice([0.20, 0.25, 0.30])
                        discount = round(subtotal * pct, 2)
                else:
                    if disc_roll < 0.72:
                        discount = 0.0
                    elif disc_roll < 0.92:
                        pct = random.choice([0.05, 0.10, 0.15])
                        discount = round(subtotal * pct, 2)
                    else:
                        pct = random.choice([0.20, 0.25])
                        discount = round(subtotal * pct, 2)

                sale_item_records.append({
                    "sale_item_id": item_counter,
                    "sale_id": sale_counter,
                    "product_id": p_id,
                    "quantity": int(qty),
                    "unit_price": round(unit_price, 2),
                    "discount": discount
                })

    sales_df = pd.DataFrame(sales_records)
    sale_items_df = pd.DataFrame(sale_item_records)

    sales_df.to_csv(RAW_DIR / "sales.csv", index=False)
    sale_items_df.to_csv(RAW_DIR / "sale_items.csv", index=False)

    print(f"Generated {len(sales_df):,} sales transactions and {len(sale_items_df):,} line items.")
    return sales_df, sale_items_df


def run_data_generation():
    """Master orchestrator generating complete synthetic raw enterprise data."""
    print("=================================================================")
    print("InsightMart: Running Enterprise Synthetic Data Generator")
    print("=================================================================")
    print(f"Output directory: {RAW_DIR.resolve()}")

    categories_df, suppliers_df = generate_categories_and_suppliers()
    print(f"-> Generated {len(categories_df)} categories & {len(suppliers_df)} suppliers.")

    stores_df = generate_stores()
    print(f"-> Generated {len(stores_df)} retail stores across 5 regions.")

    products_df = generate_products()
    print(f"-> Generated {len(products_df)} products across 6 categories.")

    customers_df = generate_customers(num_customers=5000)
    print(f"-> Generated {len(customers_df):,} customer master records.")

    sales_df, sale_items_df = generate_sales_and_items(customers_df, products_df, target_sales=32000)

    print("=================================================================")
    print("Data Generation Completed Successfully!")
    print(f"Total Customers:  {len(customers_df):,}")
    print(f"Total Products:   {len(products_df):,}")
    print(f"Total Stores:     {len(stores_df):,}")
    print(f"Total Sales:      {len(sales_df):,}")
    print(f"Total Line Items: {len(sale_items_df):,}")
    print("=================================================================")


if __name__ == "__main__":
    run_data_generation()
