"""
InsightMart Business Sales & Customer Analytics System
Module: tests/test_system.py
Description: Comprehensive automated test suite verifying database layer,
             all 7 web portal routes, and all 15 REST API endpoints.
"""

import sys
from pathlib import Path
import unittest

# Ensure root directory in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.app import create_app
from src.database import execute_query


class SystemTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Sets up Flask test client and verifies database state."""
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    def test_01_database_connectivity_and_records(self):
        """Verifies database tables are populated with expected records."""
        count_sales = execute_query("SELECT COUNT(*) AS total FROM SALES", fetch_one=True)
        self.assertIsNotNone(count_sales)
        self.assertGreaterEqual(count_sales["total"], 30000, "Sales table should have >= 30,000 transactions.")

        count_items = execute_query("SELECT COUNT(*) AS total FROM SALE_ITEMS", fetch_one=True)
        self.assertGreaterEqual(count_items["total"], 60000, "Sale items table should have >= 60,000 records.")

        count_cust = execute_query("SELECT COUNT(*) AS total FROM CUSTOMERS", fetch_one=True)
        self.assertEqual(count_cust["total"], 5000, "Customers table should have 5,000 records.")

        count_prods = execute_query("SELECT COUNT(*) AS total FROM PRODUCTS", fetch_one=True)
        self.assertEqual(count_prods["total"], 120, "Products table should have 120 SKUs.")

    def test_02_web_views_status_200(self):
        """Verifies all 7 HTML views render successfully."""
        routes = [
            "/",
            "/dashboard",
            "/sales",
            "/products",
            "/customers",
            "/stores",
            "/insights",
            "/about"
        ]
        for r in routes:
            response = self.client.get(r)
            self.assertEqual(response.status_code, 200, f"Route {r} failed with status {response.status_code}")
            self.assertIn(b"InsightMart", response.data)

    def test_03_dashboard_kpis_api(self):
        """Tests /api/dashboard/kpis returns accurate metrics."""
        res = self.client.get("/api/dashboard/kpis")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        d = json_data["data"]
        self.assertGreater(d["total_revenue"], 1000000)
        self.assertGreater(d["total_profit"], 500000)
        self.assertGreater(d["total_orders"], 25000)
        self.assertGreater(d["profit_margin_pct"], 20.0)

    def test_04_revenue_trend_api(self):
        """Tests /api/dashboard/revenue-trend returns monthly progression."""
        res = self.client.get("/api/dashboard/revenue-trend")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertGreaterEqual(len(json_data["data"]), 12)

    def test_05_category_performance_api(self):
        """Tests /api/dashboard/category-performance."""
        res = self.client.get("/api/dashboard/category-performance")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(len(json_data["data"]), 6)

    def test_06_store_performance_api(self):
        """Tests /api/dashboard/store-performance."""
        res = self.client.get("/api/dashboard/store-performance")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(len(json_data["data"]), 12)

    def test_07_products_top_and_underperforming(self):
        """Tests top and bottom product analytical endpoints."""
        top_res = self.client.get("/api/products/top?limit=5")
        self.assertEqual(top_res.status_code, 200)
        top_json = top_res.get_json()
        self.assertTrue(top_json["success"])
        self.assertEqual(len(top_json["data"]), 5)

        under_res = self.client.get("/api/products/underperforming?limit=5")
        self.assertEqual(under_res.status_code, 200)
        under_json = under_res.get_json()
        self.assertTrue(under_json["success"])
        self.assertEqual(len(under_json["data"]), 5)

    def test_08_customer_segments_api(self):
        """Tests customer segments aggregation."""
        res = self.client.get("/api/customers/segments")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertGreaterEqual(len(json_data["data"]), 3)

    def test_09_paginated_transactions_api(self):
        """Tests pagination and search functionality on transaction ledger."""
        res = self.client.get("/api/sales/transactions?page=1&per_page=10")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        d = json_data["data"]
        self.assertEqual(len(d["records"]), 10)
        self.assertEqual(d["page"], 1)
        self.assertGreater(d["total_records"], 50000)

        # Test search
        res_search = self.client.get("/api/sales/transactions?page=1&per_page=10&search=Chicago")
        self.assertEqual(res_search.status_code, 200)
        self.assertTrue(res_search.get_json()["success"])

    def test_10_automated_insights_api(self):
        """Tests automated business intelligence insights endpoint."""
        res = self.client.get("/api/insights")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertGreaterEqual(len(json_data["data"]), 4)
        for insight in json_data["data"]:
            self.assertIn("observation", insight)
            self.assertIn("business_meaning", insight)
            self.assertIn("recommendation", insight)

    def test_11_filter_options_api(self):
        """Tests filter options dropdown metadata endpoint."""
        res = self.client.get("/api/filters/options")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        d = json_data["data"]
        self.assertEqual(len(d["stores"]), 12)
        self.assertEqual(len(d["categories"]), 6)

    def test_12_security_headers_and_error_handling(self):
        """Verifies security headers and safe 404 JSON handling."""
        res = self.client.get("/")
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("X-Frame-Options"), "SAMEORIGIN")

        # Test API 404 returns JSON without revealing server internals
        res_404 = self.client.get("/api/nonexistent-endpoint")
        self.assertEqual(res_404.status_code, 404)
        self.assertFalse(res_404.get_json()["success"])


if __name__ == "__main__":
    unittest.main()
