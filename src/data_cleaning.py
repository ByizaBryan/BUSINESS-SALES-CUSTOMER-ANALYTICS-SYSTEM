"""
InsightMart Business Sales & Customer Analytics System
Module: src/data_cleaning.py
Description: Enterprise ETL Data Pipeline. Ingests raw business data from data/raw/,
             performs rigorous data validation, identifies and fixes anomalies/inconsistencies,
             corrects types, calculates financial derived fields (revenue, cost, profit, margin),
             exports cleaned datasets to data/processed/, and bulk-loads into the relational database.
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database import get_db_cursor, initialize_schema, execute_non_query, get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("DataCleaningPipeline")

RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)


class DataCleaningPipeline:
    def __init__(self):
        self.quality_report = {
            "missing_values_handled": 0,
            "duplicate_records_removed": 0,
            "strings_trimmed_standardized": 0,
            "anomalies_corrected": 0
        }

    def clean_categories(self) -> pd.DataFrame:
        """Validates and cleans categories master data."""
        logger.info("Processing categories master data...")
        df = pd.read_csv(RAW_DIR / "categories.csv")

        # Validation
        assert not df["category_id"].duplicated().any(), "Duplicate category_id detected!"
        df["category_name"] = df["category_name"].str.strip()
        df["description"] = df["description"].str.strip()

        df.to_csv(PROCESSED_DIR / "categories_clean.csv", index=False)
        return df

    def clean_suppliers(self) -> pd.DataFrame:
        """Validates and cleans suppliers master data."""
        logger.info("Processing suppliers master data...")
        df = pd.read_csv(RAW_DIR / "suppliers.csv")

        # Validation
        assert not df["supplier_id"].duplicated().any(), "Duplicate supplier_id detected!"
        df["supplier_name"] = df["supplier_name"].str.strip()
        df["city"] = df["city"].str.strip().str.title()
        df["contact_information"] = df["contact_information"].str.strip()

        df.to_csv(PROCESSED_DIR / "suppliers_clean.csv", index=False)
        return df

    def clean_stores(self) -> pd.DataFrame:
        """Validates and cleans stores master data."""
        logger.info("Processing stores master data...")
        df = pd.read_csv(RAW_DIR / "stores.csv")

        assert not df["store_id"].duplicated().any(), "Duplicate store_id detected!"
        df["store_name"] = df["store_name"].str.strip()
        df["city"] = df["city"].str.strip().str.title()
        df["region"] = df["region"].str.strip().str.title()
        df["opening_date"] = pd.to_datetime(df["opening_date"]).dt.strftime("%Y-%m-%d")

        df.to_csv(PROCESSED_DIR / "stores_clean.csv", index=False)
        return df

    def clean_products(self, categories_df: pd.DataFrame, suppliers_df: pd.DataFrame) -> pd.DataFrame:
        """Validates products, checks referential integrity and price/cost constraints."""
        logger.info("Processing products master data...")
        df = pd.read_csv(RAW_DIR / "products.csv")

        # Check duplicates
        dups = df.duplicated(subset=["product_id"]).sum()
        if dups > 0:
            df = df.drop_duplicates(subset=["product_id"])
            self.quality_report["duplicate_records_removed"] += dups

        # Referential checks
        valid_cats = set(categories_df["category_id"])
        valid_sups = set(suppliers_df["supplier_id"])
        assert df["category_id"].isin(valid_cats).all(), "Invalid category_id foreign key!"
        assert df["supplier_id"].isin(valid_sups).all(), "Invalid supplier_id foreign key!"

        # Price and cost validation: selling_price >= unit_cost
        invalid_prices = (df["selling_price"] < df["unit_cost"]).sum()
        if invalid_prices > 0:
            logger.warning(f"Found {invalid_prices} products where selling_price < unit_cost. Correcting...")
            df.loc[df["selling_price"] < df["unit_cost"], "selling_price"] = df["unit_cost"] * 1.25
            self.quality_report["anomalies_corrected"] += invalid_prices

        # Format types
        df["product_name"] = df["product_name"].str.strip()
        df["unit_cost"] = df["unit_cost"].round(2)
        df["selling_price"] = df["selling_price"].round(2)
        df["stock_quantity"] = df["stock_quantity"].astype(int)
        df["reorder_level"] = df["reorder_level"].astype(int)
        df["status"] = df["status"].str.strip().str.title()

        df.to_csv(PROCESSED_DIR / "products_clean.csv", index=False)
        return df

    def clean_customers(self) -> pd.DataFrame:
        """
        Cleans customers dataset: strips whitespace noise, normalizes city casing,
        validates date strings, and verifies customer segments.
        """
        logger.info("Processing customers master data...")
        df = pd.read_csv(RAW_DIR / "customers.csv")

        # Check duplicates
        dups = df.duplicated(subset=["customer_id"]).sum()
        if dups > 0:
            df = df.drop_duplicates(subset=["customer_id"])
            self.quality_report["duplicate_records_removed"] += dups

        # Check and handle whitespace and casing noise
        initial_first = df["first_name"].copy()
        df["first_name"] = df["first_name"].astype(str).str.strip().str.title()
        df["last_name"] = df["last_name"].astype(str).str.strip().str.title()
        df["city"] = df["city"].astype(str).str.strip().str.title()
        df["customer_segment"] = df["customer_segment"].astype(str).str.strip().str.title()
        df["gender"] = df["gender"].astype(str).str.strip().str.title()

        # Count noisy strings cleaned
        cleaned_count = (initial_first != df["first_name"]).sum()
        self.quality_report["strings_trimmed_standardized"] += cleaned_count

        # Validate dates
        df["date_of_birth"] = pd.to_datetime(df["date_of_birth"]).dt.strftime("%Y-%m-%d")
        df["registration_date"] = pd.to_datetime(df["registration_date"]).dt.strftime("%Y-%m-%d")

        df.to_csv(PROCESSED_DIR / "customers_clean.csv", index=False)
        return df

    def clean_sales(self, customers_df: pd.DataFrame, stores_df: pd.DataFrame) -> pd.DataFrame:
        """Cleans sales headers and ensures referential integrity."""
        logger.info("Processing sales transactions header data...")
        df = pd.read_csv(RAW_DIR / "sales.csv")

        # Duplicates check
        dups = df.duplicated(subset=["sale_id"]).sum()
        if dups > 0:
            df = df.drop_duplicates(subset=["sale_id"])
            self.quality_report["duplicate_records_removed"] += dups

        # Foreign key integrity
        valid_cids = set(customers_df["customer_id"])
        valid_sids = set(stores_df["store_id"])
        assert df["customer_id"].isin(valid_cids).all(), "Invalid customer_id foreign key in sales!"
        assert df["store_id"].isin(valid_sids).all(), "Invalid store_id foreign key in sales!"

        df["sale_date"] = pd.to_datetime(df["sale_date"]).dt.strftime("%Y-%m-%d")
        df["payment_method"] = df["payment_method"].astype(str).str.strip().str.title()
        df["sales_channel"] = df["sales_channel"].astype(str).str.strip()

        df.to_csv(PROCESSED_DIR / "sales_clean.csv", index=False)
        return df

    def clean_sale_items(self, sales_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans line items, calculates financial derived columns:
        - revenue = (quantity * unit_price) - discount
        - cost = quantity * unit_cost
        - profit = revenue - cost
        - profit_margin_pct = (profit / revenue) * 100
        """
        logger.info("Processing sale items detail data and deriving financial metrics...")
        df = pd.read_csv(RAW_DIR / "sale_items.csv")

        # Duplicates check
        dups = df.duplicated(subset=["sale_item_id"]).sum()
        if dups > 0:
            df = df.drop_duplicates(subset=["sale_item_id"])
            self.quality_report["duplicate_records_removed"] += dups

        # Referential checks
        valid_sales = set(sales_df["sale_id"])
        valid_prods = set(products_df["product_id"])
        assert df["sale_id"].isin(valid_sales).all(), "Invalid sale_id foreign key in sale_items!"
        assert df["product_id"].isin(valid_prods).all(), "Invalid product_id foreign key in sale_items!"

        # Sanitize negative or zero quantities
        invalid_qty = (df["quantity"] <= 0).sum()
        if invalid_qty > 0:
            df.loc[df["quantity"] <= 0, "quantity"] = 1
            self.quality_report["anomalies_corrected"] += invalid_qty

        # Verify discount does not exceed subtotal (quantity * unit_price)
        subtotal = df["quantity"] * df["unit_price"]
        excess_discount = (df["discount"] > subtotal).sum()
        if excess_discount > 0:
            df.loc[df["discount"] > subtotal, "discount"] = subtotal * 0.25
            self.quality_report["anomalies_corrected"] += excess_discount

        # Merge with product cost for derived financial computations
        prod_costs = products_df[["product_id", "unit_cost"]].copy()
        df_merged = df.merge(prod_costs, on="product_id", how="left")

        # Calculate financial metrics as defined in Section 8
        # Revenue = quantity * unit_price - discount
        df_merged["line_revenue"] = ((df_merged["quantity"] * df_merged["unit_price"]) - df_merged["discount"]).round(2)

        # Cost = quantity * unit_cost
        df_merged["line_cost"] = (df_merged["quantity"] * df_merged["unit_cost"]).round(2)

        # Profit = Revenue - Cost
        df_merged["line_profit"] = (df_merged["line_revenue"] - df_merged["line_cost"]).round(2)

        # Profit Margin = (Profit / Revenue) * 100
        df_merged["profit_margin_pct"] = np.where(
            df_merged["line_revenue"] > 0,
            ((df_merged["line_profit"] / df_merged["line_revenue"]) * 100).round(2),
            0.0
        )

        # Output cleaned sale_items
        export_items = df_merged[["sale_item_id", "sale_id", "product_id", "quantity", "unit_price", "discount"]]
        export_items.to_csv(PROCESSED_DIR / "sale_items_clean.csv", index=False)

        # Also save the fully enriched line items for instant analytics
        df_merged.to_csv(PROCESSED_DIR / "sale_items_enriched.csv", index=False)
        return df_merged

    def load_clean_data_to_database(self, categories_df, suppliers_df, stores_df, products_df, customers_df, sales_df, sale_items_df):
        """
        Loads all cleaned data into the relational database using high-performance batch operations.
        Ensures foreign key constraint order:
        CATEGORIES, SUPPLIERS, STORES, PRODUCTS, CUSTOMERS, SALES, SALE_ITEMS
        """
        logger.info("Initializing relational database schema...")
        initialize_schema()

        conn, engine = get_connection()
        logger.info(f"Bulk loading cleaned data into {engine.upper()} database...")

        # Batch insert helper using cursor
        cursor = conn.cursor()
        try:
            # 1. CATEGORIES
            logger.info(f"Loading {len(categories_df)} categories...")
            cat_records = categories_df[["category_id", "category_name", "description"]].values.tolist()
            placeholder = "%s, %s, %s" if engine == "mysql" else "?, ?, ?"
            cursor.executemany(f"INSERT INTO CATEGORIES (category_id, category_name, description) VALUES ({placeholder})", cat_records)

            # 2. SUPPLIERS
            logger.info(f"Loading {len(suppliers_df)} suppliers...")
            sup_records = suppliers_df[["supplier_id", "supplier_name", "contact_information", "city"]].values.tolist()
            placeholder = "%s, %s, %s, %s" if engine == "mysql" else "?, ?, ?, ?"
            cursor.executemany(f"INSERT INTO SUPPLIERS (supplier_id, supplier_name, contact_information, city) VALUES ({placeholder})", sup_records)

            # 3. STORES
            logger.info(f"Loading {len(stores_df)} stores...")
            store_records = stores_df[["store_id", "store_name", "city", "region", "opening_date"]].values.tolist()
            placeholder = "%s, %s, %s, %s, %s" if engine == "mysql" else "?, ?, ?, ?, ?"
            cursor.executemany(f"INSERT INTO STORES (store_id, store_name, city, region, opening_date) VALUES ({placeholder})", store_records)

            # 4. PRODUCTS
            logger.info(f"Loading {len(products_df)} products...")
            prod_records = products_df[["product_id", "product_name", "category_id", "supplier_id", "unit_cost", "selling_price", "stock_quantity", "reorder_level", "status"]].values.tolist()
            placeholder = "%s, %s, %s, %s, %s, %s, %s, %s, %s" if engine == "mysql" else "?, ?, ?, ?, ?, ?, ?, ?, ?"
            cursor.executemany(f"INSERT INTO PRODUCTS (product_id, product_name, category_id, supplier_id, unit_cost, selling_price, stock_quantity, reorder_level, status) VALUES ({placeholder})", prod_records)

            # 5. CUSTOMERS
            logger.info(f"Loading {len(customers_df)} customers...")
            cust_records = customers_df[["customer_id", "first_name", "last_name", "gender", "date_of_birth", "customer_segment", "city", "registration_date"]].values.tolist()
            placeholder = "%s, %s, %s, %s, %s, %s, %s, %s" if engine == "mysql" else "?, ?, ?, ?, ?, ?, ?, ?"
            cursor.executemany(f"INSERT INTO CUSTOMERS (customer_id, first_name, last_name, gender, date_of_birth, customer_segment, city, registration_date) VALUES ({placeholder})", cust_records)

            # 6. SALES
            logger.info(f"Loading {len(sales_df):,} sales headers...")
            sales_records = sales_df[["sale_id", "sale_date", "customer_id", "store_id", "payment_method", "sales_channel"]].values.tolist()
            placeholder = "%s, %s, %s, %s, %s, %s" if engine == "mysql" else "?, ?, ?, ?, ?, ?"
            # Batch in chunks of 5000 for efficiency
            chunk_size = 5000
            for i in range(0, len(sales_records), chunk_size):
                chunk = sales_records[i:i + chunk_size]
                cursor.executemany(f"INSERT INTO SALES (sale_id, sale_date, customer_id, store_id, payment_method, sales_channel) VALUES ({placeholder})", chunk)

            # 7. SALE_ITEMS
            logger.info(f"Loading {len(sale_items_df):,} sale items...")
            item_records = sale_items_df[["sale_item_id", "sale_id", "product_id", "quantity", "unit_price", "discount"]].values.tolist()
            placeholder = "%s, %s, %s, %s, %s, %s" if engine == "mysql" else "?, ?, ?, ?, ?, ?"
            for i in range(0, len(item_records), chunk_size):
                chunk = item_records[i:i + chunk_size]
                cursor.executemany(f"INSERT INTO SALE_ITEMS (sale_item_id, sale_id, product_id, quantity, unit_price, discount) VALUES ({placeholder})", chunk)

            conn.commit()
            logger.info("All records successfully committed to database!")
        except Exception as e:
            conn.rollback()
            logger.error(f"Error loading data into database: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def run_pipeline(self):
        """Orchestrates the end-to-end data cleaning, derivation, and loading pipeline."""
        logger.info("=================================================================")
        logger.info("Starting InsightMart Data Cleaning & Transformation Pipeline")
        logger.info("=================================================================")

        cats = self.clean_categories()
        sups = self.clean_suppliers()
        stores = self.clean_stores()
        prods = self.clean_products(cats, sups)
        custs = self.clean_customers()
        sales = self.clean_sales(custs, stores)
        items = self.clean_sale_items(sales, prods)

        # Print Data Quality Assessment Report
        logger.info("-----------------------------------------------------------------")
        logger.info("DATA QUALITY AUDIT REPORT")
        logger.info(f"Duplicate records removed:           {self.quality_report['duplicate_records_removed']}")
        logger.info(f"Strings trimmed / standardized:     {self.quality_report['strings_trimmed_standardized']}")
        logger.info(f"Anomalies / constraints corrected:   {self.quality_report['anomalies_corrected']}")
        logger.info("-----------------------------------------------------------------")

        # Load into database
        self.load_clean_data_to_database(cats, sups, stores, prods, custs, sales, items)

        # Financial Summary
        total_rev = items["line_revenue"].sum()
        total_cost = items["line_cost"].sum()
        total_profit = items["line_profit"].sum()
        overall_margin = (total_profit / total_rev) * 100 if total_rev > 0 else 0

        logger.info("=================================================================")
        logger.info("DATA PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"Total Revenue Generated:   ${total_rev:,.2f}")
        logger.info(f"Total Merchandise Cost:    ${total_cost:,.2f}")
        logger.info(f"Total Gross Profit:        ${total_profit:,.2f}")
        logger.info(f"Overall Profit Margin:     {overall_margin:.2f}%")
        logger.info(f"Average Order Value (AOV): ${(total_rev / len(sales)):,.2f}")
        logger.info("=================================================================")


if __name__ == "__main__":
    pipeline = DataCleaningPipeline()
    pipeline.run_pipeline()
