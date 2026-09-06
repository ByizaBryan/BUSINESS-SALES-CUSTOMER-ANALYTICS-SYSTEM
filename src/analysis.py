"""
InsightMart Business Sales & Customer Analytics System
Module: src/analysis.py
Description: Centralized Business Intelligence and Analytics Engine. Computes core KPIs,
             trends, category breakdowns, customer segments, product matrices, and store benchmarks
             using optimized database queries.
"""

import logging
from typing import Dict, List, Any
from src.database import execute_query

logger = logging.getLogger("AnalyticsEngine")


def get_executive_kpis(filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Calculates executive-level KPIs: Total Revenue, Total Profit, Total Orders,
    Units Sold, Average Order Value (AOV), and Profit Margin %.
    Supports optional dynamic filtering by store, category, date range, channel, segment.
    """
    where_clauses = ["1=1"]
    params = []

    if filters:
        if filters.get("start_date"):
            where_clauses.append("sale_date >= %s")
            params.append(filters["start_date"])
        if filters.get("end_date"):
            where_clauses.append("sale_date <= %s")
            params.append(filters["end_date"])
        if filters.get("store_id"):
            where_clauses.append("store_id = %s")
            params.append(int(filters["store_id"]))
        if filters.get("category_id"):
            where_clauses.append("category_id = %s")
            params.append(int(filters["category_id"]))
        if filters.get("sales_channel"):
            where_clauses.append("sales_channel = %s")
            params.append(filters["sales_channel"])
        if filters.get("customer_segment"):
            where_clauses.append("customer_segment = %s")
            params.append(filters["customer_segment"])
        if filters.get("region"):
            where_clauses.append("region = %s")
            params.append(filters["region"])

    where_sql = " AND ".join(where_clauses)

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
    result = execute_query(query, tuple(params) if params else None, fetch_one=True)
    return result or {
        "total_orders": 0,
        "total_units_sold": 0,
        "total_revenue": 0.0,
        "total_cost": 0.0,
        "total_profit": 0.0,
        "average_order_value": 0.0,
        "profit_margin_pct": 0.0
    }


def get_monthly_revenue_trend(filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Retrieves month-over-month revenue, profit, and order trends.
    Uses SUBSTR(sale_date, 1, 7) for portable cross-database date formatting.
    """
    where_clauses = ["1=1"]
    params = []

    if filters:
        if filters.get("store_id"):
            where_clauses.append("store_id = %s")
            params.append(int(filters["store_id"]))
        if filters.get("category_id"):
            where_clauses.append("category_id = %s")
            params.append(int(filters["category_id"]))
        if filters.get("sales_channel"):
            where_clauses.append("sales_channel = %s")
            params.append(filters["sales_channel"])

    where_sql = " AND ".join(where_clauses)

    query = f"""
    SELECT 
        SUBSTR(sale_date, 1, 7) AS month_year,
        COUNT(DISTINCT sale_id) AS order_count,
        SUM(quantity) AS units_sold,
        ROUND(SUM(line_revenue), 2) AS monthly_revenue,
        ROUND(SUM(line_profit), 2) AS monthly_profit,
        ROUND((SUM(line_profit) / SUM(line_revenue)) * 100, 2) AS profit_margin_pct
    FROM view_sales_performance
    WHERE {where_sql}
    GROUP BY SUBSTR(sale_date, 1, 7)
    ORDER BY month_year ASC
    """
    return execute_query(query, tuple(params) if params else None)


def get_category_performance(filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Returns revenue, profit, units sold, and profit margin aggregated by product category.
    """
    where_clauses = ["1=1"]
    params = []

    if filters and filters.get("store_id"):
        where_clauses.append("store_id = %s")
        params.append(int(filters["store_id"]))
    if filters and filters.get("sales_channel"):
        where_clauses.append("sales_channel = %s")
        params.append(filters["sales_channel"])

    where_sql = " AND ".join(where_clauses)

    query = f"""
    SELECT 
        category_id,
        category_name,
        COUNT(DISTINCT sale_id) AS total_orders,
        SUM(quantity) AS total_units,
        ROUND(SUM(line_revenue), 2) AS total_revenue,
        ROUND(SUM(line_profit), 2) AS total_profit,
        ROUND((SUM(line_profit) / SUM(line_revenue)) * 100, 2) AS profit_margin_pct
    FROM view_sales_performance
    WHERE {where_sql}
    GROUP BY category_id, category_name
    ORDER BY total_revenue DESC
    """
    return execute_query(query, tuple(params) if params else None)


def get_store_performance() -> List[Dict[str, Any]]:
    """
    Returns financial and operational performance metrics by store branch and geographic region.
    """
    query = """
    SELECT 
        store_id,
        store_name,
        store_city,
        region,
        COUNT(DISTINCT sale_id) AS total_orders,
        SUM(quantity) AS units_sold,
        ROUND(SUM(line_revenue), 2) AS total_revenue,
        ROUND(SUM(line_profit), 2) AS total_profit,
        ROUND(SUM(line_revenue) / COUNT(DISTINCT sale_id), 2) AS average_order_value,
        ROUND((SUM(line_profit) / SUM(line_revenue)) * 100, 2) AS profit_margin_pct
    FROM view_sales_performance
    GROUP BY store_id, store_name, store_city, region
    ORDER BY total_revenue DESC
    """
    return execute_query(query)


def get_top_products(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieves the top performing products ranked by total revenue.
    """
    query = f"""
    SELECT 
        product_id,
        product_name,
        category_name,
        SUM(quantity) AS units_sold,
        ROUND(SUM(line_revenue), 2) AS total_revenue,
        ROUND(SUM(line_profit), 2) AS total_profit,
        ROUND((SUM(line_profit) / SUM(line_revenue)) * 100, 2) AS profit_margin_pct
    FROM view_sales_performance
    GROUP BY product_id, product_name, category_name
    ORDER BY total_revenue DESC
    LIMIT {limit}
    """
    return execute_query(query)


def get_underperforming_products(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Identifies bottom performing products by sales volume, profit, or lowest margin.
    """
    query = f"""
    SELECT 
        product_id,
        product_name,
        category_name,
        SUM(quantity) AS units_sold,
        ROUND(SUM(line_revenue), 2) AS total_revenue,
        ROUND(SUM(line_profit), 2) AS total_profit,
        ROUND((SUM(line_profit) / SUM(line_revenue)) * 100, 2) AS profit_margin_pct
    FROM view_sales_performance
    GROUP BY product_id, product_name, category_name
    HAVING SUM(line_revenue) > 0
    ORDER BY total_revenue ASC, total_profit ASC
    LIMIT {limit}
    """
    return execute_query(query)


def get_customer_segments_summary() -> List[Dict[str, Any]]:
    """
    Aggregates customer counts, total revenue, average spend per customer,
    and total orders across customer segments.
    """
    query = """
    SELECT 
        c.customer_segment,
        COUNT(DISTINCT c.customer_id) AS customer_count,
        COUNT(DISTINCT s.sale_id) AS total_orders,
        COALESCE(ROUND(SUM(v.line_revenue), 2), 0.0) AS total_revenue,
        COALESCE(ROUND(SUM(v.line_profit), 2), 0.0) AS total_profit,
        ROUND(SUM(v.line_revenue) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer,
        ROUND(SUM(v.line_revenue) / COUNT(DISTINCT s.sale_id), 2) AS average_order_value
    FROM CUSTOMERS c
    LEFT JOIN SALES s ON c.customer_id = s.customer_id
    LEFT JOIN view_sales_performance v ON s.sale_id = v.sale_id
    GROUP BY c.customer_segment
    ORDER BY total_revenue DESC
    """
    return execute_query(query)


def get_top_customers(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieves the highest lifetime value customers by total spend.
    """
    query = f"""
    SELECT 
        customer_id,
        customer_name,
        customer_segment,
        customer_city,
        COUNT(DISTINCT sale_id) AS order_count,
        SUM(quantity) AS total_units_purchased,
        ROUND(SUM(line_revenue), 2) AS total_spent,
        ROUND(SUM(line_profit), 2) AS profit_contribution,
        ROUND(SUM(line_revenue) / COUNT(DISTINCT sale_id), 2) AS avg_order_value
    FROM view_sales_performance
    GROUP BY customer_id, customer_name, customer_segment, customer_city
    ORDER BY total_spent DESC
    LIMIT {limit}
    """
    return execute_query(query)


def get_channel_and_payment_breakdown() -> Dict[str, Any]:
    """
    Retrieves distributions of sales channels (Online vs In-Store) and payment methods.
    """
    channel_query = """
    SELECT 
        sales_channel,
        COUNT(DISTINCT sale_id) AS order_count,
        ROUND(SUM(line_revenue), 2) AS total_revenue,
        ROUND((SUM(line_revenue) / (SELECT SUM(line_revenue) FROM view_sales_performance)) * 100, 2) AS revenue_share_pct
    FROM view_sales_performance
    GROUP BY sales_channel
    """
    payment_query = """
    SELECT 
        payment_method,
        COUNT(DISTINCT sale_id) AS transaction_count,
        ROUND(SUM(line_revenue), 2) AS total_revenue,
        ROUND((SUM(line_revenue) / (SELECT SUM(line_revenue) FROM view_sales_performance)) * 100, 2) AS revenue_share_pct
    FROM view_sales_performance
    GROUP BY payment_method
    ORDER BY total_revenue DESC
    """
    channels = execute_query(channel_query)
    payments = execute_query(payment_query)
    return {"channels": channels, "payments": payments}


def generate_automated_business_insights() -> List[Dict[str, str]]:
    """
    Generates data-driven executive insights and recommendations based on real numbers
    calculated from the database.
    """
    kpis = get_executive_kpis()
    categories = get_category_performance()
    stores = get_store_performance()
    channels = get_channel_and_payment_breakdown()["channels"]
    segments = get_customer_segments_summary()

    insights = []

    # 1. Top Category Insight
    if categories:
        top_cat = categories[0]
        insights.append({
            "id": 1,
            "category": "Merchandise & Profitability",
            "title": f"{top_cat['category_name']} Leads Revenue Generation",
            "observation": f"{top_cat['category_name']} is the #1 revenue-generating category, accounting for ${top_cat['total_revenue']:,.2f} with an overall gross margin of {top_cat['profit_margin_pct']}%.",
            "business_meaning": "This category acts as InsightMart's core volume and traffic driver. Sustaining product availability and vendor relationships here is essential to baseline revenue stability.",
            "recommendation": "Negotiate tiered volume discounts with suppliers to improve gross margin percentages and bundle high-margin accessories with core bestsellers.",
            "type": "positive"
        })

    # 2. Store Disparity Insight
    if len(stores) >= 2:
        best_store = stores[0]
        bottom_store = stores[-1]
        ratio = round(best_store['total_revenue'] / bottom_store['total_revenue'], 1) if bottom_store['total_revenue'] > 0 else 1
        insights.append({
            "id": 2,
            "category": "Retail Operations",
            "title": f"Regional Revenue Variance ({best_store['store_name']} vs {bottom_store['store_name']})",
            "observation": f"The top-performing branch ({best_store['store_name']}) generated ${best_store['total_revenue']:,.2f}, which is {ratio}x higher than the lowest-performing branch ({bottom_store['store_name']} at ${bottom_store['total_revenue']:,.2f}).",
            "business_meaning": "Significant performance variance indicates either divergent foot traffic, demographic mismatch, local marketing discrepancies, or under-trained branch staff.",
            "recommendation": "Conduct a localized merchandising audit for lower-tier locations and replicate the promotional scheduling and product mix of top flagship stores.",
            "type": "warning"
        })

    # 3. Customer Segmentation & 80/20 Rule
    if segments:
        high_val = next((s for s in segments if "High" in s["customer_segment"]), None)
        if high_val and kpis["total_revenue"] > 0:
            share = round((high_val["total_revenue"] / kpis["total_revenue"]) * 100, 1)
            insights.append({
                "id": 3,
                "category": "Customer Analytics",
                "title": f"High Value Customers Drive {share}% of Total Revenue",
                "observation": f"High Value customers represent {high_val['customer_count']:,} customers with an average spend of ${high_val['revenue_per_customer']:,.2f}, contributing {share}% of overall enterprise sales.",
                "business_meaning": "Customer lifetime value is heavily concentrated. A small churn in this segment would disproportionately impact profitability.",
                "recommendation": "Deploy a dedicated VIP loyalty rewards program with early access to sales, free expedited delivery, and personalized marketing to protect and expand this segment.",
                "type": "info"
            })

    # 4. Omnichannel Sales Channel Performance
    if channels:
        online_ch = next((c for c in channels if c["sales_channel"] == "Online"), None)
        instore_ch = next((c for c in channels if c["sales_channel"] == "In-Store"), None)
        if online_ch and instore_ch:
            insights.append({
                "id": 4,
                "category": "Channel Strategy",
                "title": "Digital Omnichannel Expansion Opportunity",
                "observation": f"In-Store sales represent {instore_ch['revenue_share_pct']}% of revenue (${instore_ch['total_revenue']:,.2f}), while Online channels contribute {online_ch['revenue_share_pct']}% (${online_ch['total_revenue']:,.2f}).",
                "business_meaning": "While brick-and-mortar stores remain the foundation of customer trust, online sales offer a lower cost of acquisition and higher reach.",
                "recommendation": "Implement 'Buy Online, Pick Up In-Store' (BOPIS) to drive online shoppers into physical stores, stimulating incremental add-on purchases.",
                "type": "positive"
            })

    # 5. Margin Health
    insights.append({
        "id": 5,
        "category": "Financial Strategy",
        "title": f"Healthy Overall Gross Margin of {kpis['profit_margin_pct']}%",
        "observation": f"InsightMart generated ${kpis['total_profit']:,.2f} in gross profit on ${kpis['total_revenue']:,.2f} revenue, maintaining a blended margin of {kpis['profit_margin_pct']}%.",
        "business_meaning": "The company's product pricing model and discount management are fundamentally sound and exceed typical retail discount benchmarks.",
        "recommendation": "Maintain promotional discipline; cap clearance discounts at 25% and establish minimum order thresholds to protect Average Order Value ($" + f"{kpis['average_order_value']:.2f}).",
        "type": "positive"
    })

    return insights
