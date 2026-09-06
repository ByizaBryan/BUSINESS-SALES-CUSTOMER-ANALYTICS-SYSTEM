"""
InsightMart Business Sales & Customer Analytics System
Module: app/services/analytics_service.py
Description: Service layer executing parameterized analytical queries against the database,
             enforcing input validation, business logic, pagination, and data formatting.
"""

import logging
from typing import Dict, Any, List, Tuple
from src.database import execute_query

logger = logging.getLogger("AnalyticsService")


class AnalyticsService:

    @staticmethod
    def _build_filter_clauses(filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """
        Constructs safe parameterized WHERE clauses based on user-selected filters.
        Prevents SQL injection by enforcing parameter substitution.
        """
        clauses = ["1=1"]
        params = []

        if not filters:
            return "1=1", []

        if filters.get("start_date"):
            clauses.append("sale_date >= %s")
            params.append(filters["start_date"])

        if filters.get("end_date"):
            clauses.append("sale_date <= %s")
            params.append(filters["end_date"])

        if filters.get("store_id") and str(filters["store_id"]).isdigit():
            clauses.append("store_id = %s")
            params.append(int(filters["store_id"]))

        if filters.get("region"):
            clauses.append("region = %s")
            params.append(filters["region"])

        if filters.get("category_id") and str(filters["category_id"]).isdigit():
            clauses.append("category_id = %s")
            params.append(int(filters["category_id"]))

        if filters.get("sales_channel") in ["In-Store", "Online"]:
            clauses.append("sales_channel = %s")
            params.append(filters["sales_channel"])

        if filters.get("payment_method"):
            clauses.append("payment_method = %s")
            params.append(filters["payment_method"])

        if filters.get("customer_segment"):
            clauses.append("customer_segment = %s")
            params.append(filters["customer_segment"])

        return " AND ".join(clauses), params

    @classmethod
    def get_dashboard_kpis(cls, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculates top-level executive KPIs with applied filters."""
        where_sql, params = cls._build_filter_clauses(filters)

        query = f"""
        SELECT 
            COUNT(DISTINCT sale_id) AS total_orders,
            COALESCE(SUM(quantity), 0) AS total_units_sold,
            COALESCE(ROUND(SUM(line_revenue), 2), 0.0) AS total_revenue,
            COALESCE(ROUND(SUM(line_cost), 2), 0.0) AS total_cost,
            COALESCE(ROUND(SUM(line_profit), 2), 0.0) AS total_profit,
            CASE 
                WHEN COUNT(DISTINCT sale_id) > 0 
                THEN ROUND(SUM(line_revenue) / COUNT(DISTINCT sale_id), 2)
                ELSE 0.0 
            END AS average_order_value,
            CASE 
                WHEN SUM(line_revenue) > 0 
                THEN ROUND((SUM(line_profit) / SUM(line_revenue)) * 100, 2)
                ELSE 0.0 
            END AS profit_margin_pct
        FROM view_sales_performance
        WHERE {where_sql}
        """
        res = execute_query(query, tuple(params) if params else None, fetch_one=True)
        return res or {
            "total_orders": 0,
            "total_units_sold": 0,
            "total_revenue": 0.0,
            "total_cost": 0.0,
            "total_profit": 0.0,
            "average_order_value": 0.0,
            "profit_margin_pct": 0.0
        }

    @classmethod
    def get_revenue_trend(cls, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Returns monthly revenue and profit trend data points."""
        where_sql, params = cls._build_filter_clauses(filters)

        query = f"""
        SELECT 
            SUBSTR(sale_date, 1, 7) AS month_year,
            COUNT(DISTINCT sale_id) AS orders,
            SUM(quantity) AS units,
            ROUND(SUM(line_revenue), 2) AS revenue,
            ROUND(SUM(line_profit), 2) AS profit,
            ROUND((SUM(line_profit) / SUM(line_revenue)) * 100, 2) AS margin_pct
        FROM view_sales_performance
        WHERE {where_sql}
        GROUP BY SUBSTR(sale_date, 1, 7)
        ORDER BY month_year ASC
        """
        return execute_query(query, tuple(params) if params else None)

    @classmethod
    def get_category_performance(cls, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Returns category revenue, profit, units, and margin breakdown."""
        where_sql, params = cls._build_filter_clauses(filters)

        query = f"""
        SELECT 
            category_id,
            category_name,
            COUNT(DISTINCT sale_id) AS orders,
            SUM(quantity) AS units,
            ROUND(SUM(line_revenue), 2) AS revenue,
            ROUND(SUM(line_profit), 2) AS profit,
            ROUND((SUM(line_profit) / SUM(line_revenue)) * 100, 2) AS margin_pct
        FROM view_sales_performance
        WHERE {where_sql}
        GROUP BY category_id, category_name
        ORDER BY revenue DESC
        """
        return execute_query(query, tuple(params) if params else None)

    @classmethod
    def get_store_performance(cls, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Returns store-level benchmarking metrics."""
        where_sql, params = cls._build_filter_clauses(filters)

        query = f"""
        SELECT 
            store_id,
            store_name,
            store_city,
            region,
            COUNT(DISTINCT sale_id) AS orders,
            SUM(quantity) AS units,
            ROUND(SUM(line_revenue), 2) AS revenue,
            ROUND(SUM(line_profit), 2) AS profit,
            ROUND(SUM(line_revenue) / COUNT(DISTINCT sale_id), 2) AS aov,
            ROUND((SUM(line_profit) / SUM(line_revenue)) * 100, 2) AS margin_pct
        FROM view_sales_performance
        WHERE {where_sql}
        GROUP BY store_id, store_name, store_city, region
        ORDER BY revenue DESC
        """
        return execute_query(query, tuple(params) if params else None)

    @classmethod
    def get_sales_channel_breakdown(cls, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Returns sales channel distribution (In-Store vs Online)."""
        where_sql, params = cls._build_filter_clauses(filters)

        query = f"""
        SELECT 
            sales_channel,
            COUNT(DISTINCT sale_id) AS orders,
            ROUND(SUM(line_revenue), 2) AS revenue,
            ROUND(SUM(line_profit), 2) AS profit
        FROM view_sales_performance
        WHERE {where_sql}
        GROUP BY sales_channel
        """
        return execute_query(query, tuple(params) if params else None)

    @classmethod
    def get_payment_methods_breakdown(cls, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Returns payment method distribution."""
        where_sql, params = cls._build_filter_clauses(filters)

        query = f"""
        SELECT 
            payment_method,
            COUNT(DISTINCT sale_id) AS orders,
            ROUND(SUM(line_revenue), 2) AS revenue
        FROM view_sales_performance
        WHERE {where_sql}
        GROUP BY payment_method
        ORDER BY revenue DESC
        """
        return execute_query(query, tuple(params) if params else None)

    @classmethod
    def get_top_products(cls, limit: int = 10, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Returns top products ranked by revenue."""
        where_sql, params = cls._build_filter_clauses(filters)

        query = f"""
        SELECT 
            product_id,
            product_name,
            category_name,
            SUM(quantity) AS units,
            ROUND(SUM(line_revenue), 2) AS revenue,
            ROUND(SUM(line_profit), 2) AS profit,
            ROUND((SUM(line_profit) / SUM(line_revenue)) * 100, 2) AS margin_pct
        FROM view_sales_performance
        WHERE {where_sql}
        GROUP BY product_id, product_name, category_name
        ORDER BY revenue DESC
        LIMIT {limit}
        """
        return execute_query(query, tuple(params) if params else None)

    @classmethod
    def get_underperforming_products(cls, limit: int = 10, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Returns underperforming products by lowest revenue and margins."""
        where_sql, params = cls._build_filter_clauses(filters)

        query = f"""
        SELECT 
            product_id,
            product_name,
            category_name,
            SUM(quantity) AS units,
            ROUND(SUM(line_revenue), 2) AS revenue,
            ROUND(SUM(line_profit), 2) AS profit,
            ROUND((SUM(line_profit) / SUM(line_revenue)) * 100, 2) AS margin_pct
        FROM view_sales_performance
        WHERE {where_sql}
        GROUP BY product_id, product_name, category_name
        HAVING SUM(line_revenue) > 0
        ORDER BY revenue ASC, profit ASC
        LIMIT {limit}
        """
        return execute_query(query, tuple(params) if params else None)

    @classmethod
    def get_all_products_catalog(cls) -> List[Dict[str, Any]]:
        """Returns product catalog with inventory, costs, prices, and status."""
        query = """
        SELECT 
            p.product_id,
            p.product_name,
            c.category_name,
            s.supplier_name,
            p.unit_cost,
            p.selling_price,
            p.stock_quantity,
            p.reorder_level,
            p.status,
            COALESCE(SUM(si.quantity), 0) AS units_sold,
            COALESCE(ROUND(SUM(v.line_revenue), 2), 0.00) AS total_revenue,
            COALESCE(ROUND(SUM(v.line_profit), 2), 0.00) AS total_profit,
            COALESCE(ROUND((SUM(v.line_profit) / SUM(v.line_revenue)) * 100, 2), 0.00) AS margin_pct
        FROM PRODUCTS p
        INNER JOIN CATEGORIES c ON p.category_id = c.category_id
        INNER JOIN SUPPLIERS s ON p.supplier_id = s.supplier_id
        LEFT JOIN SALE_ITEMS si ON p.product_id = si.product_id
        LEFT JOIN view_sales_performance v ON si.sale_item_id = v.sale_item_id
        GROUP BY p.product_id, p.product_name, c.category_name, s.supplier_name,
                 p.unit_cost, p.selling_price, p.stock_quantity, p.reorder_level, p.status
        ORDER BY total_revenue DESC
        """
        return execute_query(query)

    @classmethod
    def get_customer_segments(cls) -> List[Dict[str, Any]]:
        """Returns customer segments analysis."""
        query = """
        SELECT 
            c.customer_segment,
            COUNT(DISTINCT c.customer_id) AS customer_count,
            COUNT(DISTINCT s.sale_id) AS total_orders,
            COALESCE(ROUND(SUM(v.line_revenue), 2), 0.0) AS total_revenue,
            COALESCE(ROUND(SUM(v.line_profit), 2), 0.0) AS total_profit,
            ROUND(SUM(v.line_revenue) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer,
            ROUND(SUM(v.line_revenue) / COUNT(DISTINCT s.sale_id), 2) AS aov
        FROM CUSTOMERS c
        LEFT JOIN SALES s ON c.customer_id = s.customer_id
        LEFT JOIN view_sales_performance v ON s.sale_id = v.sale_id
        GROUP BY c.customer_segment
        ORDER BY total_revenue DESC
        """
        return execute_query(query)

    @classmethod
    def get_top_customers(cls, limit: int = 15) -> List[Dict[str, Any]]:
        """Returns top customers ranked by lifetime spend."""
        query = f"""
        SELECT 
            customer_id,
            customer_name,
            customer_segment,
            customer_city,
            COUNT(DISTINCT sale_id) AS orders,
            SUM(quantity) AS units,
            ROUND(SUM(line_revenue), 2) AS total_spent,
            ROUND(SUM(line_profit), 2) AS profit_contributed,
            ROUND(SUM(line_revenue) / COUNT(DISTINCT sale_id), 2) AS aov
        FROM view_sales_performance
        GROUP BY customer_id, customer_name, customer_segment, customer_city
        ORDER BY total_spent DESC
        LIMIT {limit}
        """
        return execute_query(query)

    @classmethod
    def get_transactions_paginated(cls, page: int = 1, per_page: int = 15, search: str = "", filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Returns a paginated, searchable list of transactions.
        Supports filtering and search across customer name, store name, product name, and sale ID.
        """
        offset = (page - 1) * per_page
        where_sql, params = cls._build_filter_clauses(filters)

        search_clause = ""
        search_params = []
        if search:
            search_clause = " AND (customer_name LIKE %s OR product_name LIKE %s OR store_name LIKE %s OR CAST(sale_id AS CHAR) = %s)"
            search_pattern = f"%{search}%"
            search_params = [search_pattern, search_pattern, search_pattern, search]

        full_where = f"{where_sql} {search_clause}"
        all_params = params + search_params

        # Count total matching records
        count_query = f"""
        SELECT COUNT(*) AS total_count
        FROM view_sales_performance
        WHERE {full_where}
        """
        count_res = execute_query(count_query, tuple(all_params) if all_params else None, fetch_one=True)
        total_records = count_res["total_count"] if count_res else 0
        total_pages = max(1, (total_records + per_page - 1) // per_page)

        # Retrieve page items
        data_query = f"""
        SELECT 
            sale_id,
            sale_date,
            customer_name,
            customer_segment,
            store_name,
            product_name,
            category_name,
            sales_channel,
            payment_method,
            quantity,
            unit_price,
            discount,
            line_revenue,
            line_profit,
            profit_margin_pct
        FROM view_sales_performance
        WHERE {full_where}
        ORDER BY sale_date DESC, sale_id DESC
        LIMIT {per_page} OFFSET {offset}
        """
        records = execute_query(data_query, tuple(all_params) if all_params else None)

        return {
            "records": records,
            "page": page,
            "per_page": per_page,
            "total_records": total_records,
            "total_pages": total_pages
        }

    @classmethod
    def get_filter_options(cls) -> Dict[str, Any]:
        """Populates dynamic dropdown selections for frontend filters."""
        stores = execute_query("SELECT store_id, store_name, region, city FROM STORES ORDER BY store_name")
        categories = execute_query("SELECT category_id, category_name FROM CATEGORIES ORDER BY category_name")
        regions = execute_query("SELECT DISTINCT region FROM STORES ORDER BY region")
        segments = execute_query("SELECT DISTINCT customer_segment FROM CUSTOMERS ORDER BY customer_segment")

        return {
            "stores": stores,
            "categories": categories,
            "regions": [r["region"] for r in regions],
            "segments": [s["customer_segment"] for s in segments],
            "channels": ["In-Store", "Online"],
            "payment_methods": ["Credit Card", "Debit Card", "Digital Wallet", "Cash"]
        }
