-- ==============================================================================
-- INSIGHTMART BUSINESS SALES & CUSTOMER ANALYTICS SYSTEM
-- File: sql/business_analysis_queries.sql
-- Description: Comprehensive suite of 20 production-grade SQL analytical queries
--              demonstrating CTEs, Window Functions, Complex Joins, Aggregations,
--              Date Functions, and Business Intelligence KPI formulations.
-- Target RDBMS: MySQL 8.0+ / MariaDB 10.5+
-- Database: business_sales_db
-- ==============================================================================

USE business_sales_db;

-- ==============================================================================
-- 1. EXECUTIVE KPI OVERVIEW
-- Business Purpose: Single-row executive summary of total volume, top-line revenue,
--                   cogs, gross profit, average order value, and profit margin.
-- ==============================================================================
SELECT 
    COUNT(DISTINCT s.sale_id) AS total_orders,
    SUM(si.quantity) AS total_units_sold,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS total_revenue,
    ROUND(SUM(si.quantity * p.unit_cost), 2) AS total_cost_of_goods_sold,
    ROUND(SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)), 2) AS total_gross_profit,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount) / COUNT(DISTINCT s.sale_id), 2) AS average_order_value,
    ROUND(
        (SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)) / 
         SUM((si.quantity * si.unit_price) - si.discount)) * 100, 
    2) AS overall_profit_margin_pct
FROM SALES s
INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
INNER JOIN PRODUCTS p ON si.product_id = p.product_id;


-- ==============================================================================
-- 2. MONTH-OVER-MONTH (MoM) REVENUE, PROFIT & GROWTH RATE
-- Business Purpose: Tracks historical momentum and calculates MoM revenue growth %
-- Techniques: CTE, Window Function LAG(), Date Formatting
-- ==============================================================================
WITH MonthlySales AS (
    SELECT 
        DATE_FORMAT(s.sale_date, '%Y-%m') AS sales_month,
        COUNT(DISTINCT s.sale_id) AS order_count,
        SUM(si.quantity) AS units_sold,
        ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS monthly_revenue,
        ROUND(SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)), 2) AS monthly_profit
    FROM SALES s
    INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
    INNER JOIN PRODUCTS p ON si.product_id = p.product_id
    GROUP BY DATE_FORMAT(s.sale_date, '%Y-%m')
)
SELECT 
    sales_month,
    order_count,
    units_sold,
    monthly_revenue,
    monthly_profit,
    ROUND((monthly_profit / monthly_revenue) * 100, 2) AS profit_margin_pct,
    LAG(monthly_revenue, 1) OVER (ORDER BY sales_month) AS previous_month_revenue,
    ROUND(
        ((monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY sales_month)) / 
         LAG(monthly_revenue, 1) OVER (ORDER BY sales_month)) * 100, 
    2) AS mom_growth_pct
FROM MonthlySales
ORDER BY sales_month ASC;


-- ==============================================================================
-- 3. YEAR-OVER-YEAR (YoY) ANNUAL REVENUE COMPARISON
-- Business Purpose: Evaluates macro business growth across fiscal years
-- Techniques: GROUP BY YEAR(), Aggregation, Conditional Metrics
-- ==============================================================================
SELECT 
    YEAR(s.sale_date) AS fiscal_year,
    COUNT(DISTINCT s.sale_id) AS total_orders,
    COUNT(DISTINCT s.customer_id) AS active_customers,
    SUM(si.quantity) AS total_units_sold,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS annual_revenue,
    ROUND(SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)), 2) AS annual_profit,
    ROUND(
        (SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)) / 
         SUM((si.quantity * si.unit_price) - si.discount)) * 100, 
    2) AS annual_margin_pct,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount) / COUNT(DISTINCT s.sale_id), 2) AS annual_aov
FROM SALES s
INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
INNER JOIN PRODUCTS p ON si.product_id = p.product_id
GROUP BY YEAR(s.sale_date)
ORDER BY fiscal_year ASC;


-- ==============================================================================
-- 4. MERCHANDISE CATEGORY PERFORMANCE & MARGIN AUDIT
-- Business Purpose: Evaluates revenue contribution, gross margin, and volume by category
-- Techniques: INNER JOIN, Multi-level Aggregation, Percentage of Total
-- ==============================================================================
SELECT 
    cat.category_id,
    cat.category_name,
    COUNT(DISTINCT s.sale_id) AS order_occurrences,
    SUM(si.quantity) AS total_units_sold,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS category_revenue,
    ROUND(SUM(si.quantity * p.unit_cost), 2) AS category_cogs,
    ROUND(SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)), 2) AS category_profit,
    ROUND(
        (SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)) / 
         SUM((si.quantity * si.unit_price) - si.discount)) * 100, 
    2) AS profit_margin_pct,
    ROUND(
        (SUM((si.quantity * si.unit_price) - si.discount) / 
         (SELECT SUM((si2.quantity * si2.unit_price) - si2.discount) FROM SALE_ITEMS si2)) * 100,
    2) AS revenue_share_pct
FROM CATEGORIES cat
INNER JOIN PRODUCTS p ON cat.category_id = p.category_id
INNER JOIN SALE_ITEMS si ON p.product_id = si.product_id
INNER JOIN SALES s ON si.sale_id = s.sale_id
GROUP BY cat.category_id, cat.category_name
ORDER BY category_revenue DESC;


-- ==============================================================================
-- 5. TOP 10 BEST-SELLING PRODUCTS BY REVENUE (WITH DENSE_RANK)
-- Business Purpose: Identifies hero products driving top-line cash flow
-- Techniques: Window Function DENSE_RANK(), Subquery
-- ==============================================================================
WITH ProductRankings AS (
    SELECT 
        p.product_id,
        p.product_name,
        cat.category_name,
        p.selling_price,
        p.unit_cost,
        SUM(si.quantity) AS units_sold,
        ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS total_revenue,
        ROUND(SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)), 2) AS gross_profit,
        ROUND(
            (SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)) / 
             SUM((si.quantity * si.unit_price) - si.discount)) * 100, 
        2) AS margin_pct,
        DENSE_RANK() OVER (ORDER BY SUM((si.quantity * si.unit_price) - si.discount) DESC) AS revenue_rank
    FROM PRODUCTS p
    INNER JOIN CATEGORIES cat ON p.category_id = cat.category_id
    INNER JOIN SALE_ITEMS si ON p.product_id = si.product_id
    GROUP BY p.product_id, p.product_name, cat.category_name, p.selling_price, p.unit_cost
)
SELECT * 
FROM ProductRankings
WHERE revenue_rank <= 10
ORDER BY revenue_rank ASC;


-- ==============================================================================
-- 6. BOTTOM 10 UNDERPERFORMING PRODUCTS (CANDIDATES FOR CLEARANCE/DELISTING)
-- Business Purpose: Spotlights stagnant inventory tie-up and low profitability
-- Techniques: Aggregations, HAVING clause, Multi-column Ordering
-- ==============================================================================
SELECT 
    p.product_id,
    p.product_name,
    cat.category_name,
    p.stock_quantity AS current_inventory,
    p.unit_cost,
    p.selling_price,
    COALESCE(SUM(si.quantity), 0) AS total_units_sold,
    COALESCE(ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2), 0.00) AS total_revenue,
    COALESCE(ROUND(SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)), 2), 0.00) AS total_profit,
    COALESCE(ROUND(
        (SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)) / 
         SUM((si.quantity * si.unit_price) - si.discount)) * 100, 
    2), 0.00) AS profit_margin_pct
FROM PRODUCTS p
INNER JOIN CATEGORIES cat ON p.category_id = cat.category_id
LEFT JOIN SALE_ITEMS si ON p.product_id = si.product_id
GROUP BY p.product_id, p.product_name, cat.category_name, p.stock_quantity, p.unit_cost, p.selling_price
ORDER BY total_revenue ASC, total_units_sold ASC
LIMIT 10;


-- ==============================================================================
-- 7. STORE PERFORMANCE & PROFITABILITY BENCHMARKING
-- Business Purpose: Compares retail store locations by revenue, margin, and AOV
-- Techniques: Multi-table JOIN, RANK() Window function
-- ==============================================================================
SELECT 
    st.store_id,
    st.store_name,
    st.city,
    st.region,
    COUNT(DISTINCT s.sale_id) AS total_transactions,
    SUM(si.quantity) AS total_items_sold,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS store_revenue,
    ROUND(SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)), 2) AS store_profit,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount) / COUNT(DISTINCT s.sale_id), 2) AS store_aov,
    ROUND(
        (SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)) / 
         SUM((si.quantity * si.unit_price) - si.discount)) * 100, 
    2) AS store_margin_pct,
    RANK() OVER (ORDER BY SUM((si.quantity * si.unit_price) - si.discount) DESC) AS store_revenue_rank
FROM STORES st
INNER JOIN SALES s ON st.store_id = s.store_id
INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
INNER JOIN PRODUCTS p ON si.product_id = p.product_id
GROUP BY st.store_id, st.store_name, st.city, st.region
ORDER BY store_revenue DESC;


-- ==============================================================================
-- 8. REGIONAL SALES CONTRIBUTION WITH WINDOW SUM() OVER()
-- Business Purpose: Computes regional share of total enterprise turnover
-- Techniques: Window Function SUM() OVER() without PARTITION for grand totals
-- ==============================================================================
WITH RegionalMetrics AS (
    SELECT 
        st.region,
        COUNT(DISTINCT st.store_id) AS store_count,
        COUNT(DISTINCT s.sale_id) AS regional_orders,
        ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS regional_revenue,
        ROUND(SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)), 2) AS regional_profit
    FROM STORES st
    INNER JOIN SALES s ON st.store_id = s.store_id
    INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
    INNER JOIN PRODUCTS p ON si.product_id = p.product_id
    GROUP BY st.region
)
SELECT 
    region,
    store_count,
    regional_orders,
    regional_revenue,
    regional_profit,
    ROUND((regional_profit / regional_revenue) * 100, 2) AS regional_margin_pct,
    ROUND((regional_revenue / SUM(regional_revenue) OVER ()) * 100, 2) AS share_of_national_revenue_pct
FROM RegionalMetrics
ORDER BY regional_revenue DESC;


-- ==============================================================================
-- 9. TOP 20 HIGH-VALUE CUSTOMERS (CUSTOMER LIFETIME VALUE / CLV)
-- Business Purpose: Identifies enterprise VIPs for dedicated account retention
-- Techniques: CONCAT, Multiple Aggregates, Filtered Leaderboard
-- ==============================================================================
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS full_name,
    c.customer_segment,
    c.city AS customer_city,
    c.registration_date,
    COUNT(DISTINCT s.sale_id) AS total_orders_placed,
    SUM(si.quantity) AS total_units_bought,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS total_historical_spend,
    ROUND(SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)), 2) AS total_profit_contributed,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount) / COUNT(DISTINCT s.sale_id), 2) AS average_order_value
FROM CUSTOMERS c
INNER JOIN SALES s ON c.customer_id = s.customer_id
INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
INNER JOIN PRODUCTS p ON si.product_id = p.product_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.customer_segment, c.city, c.registration_date
ORDER BY total_historical_spend DESC
LIMIT 20;


-- ==============================================================================
-- 10. REPEAT CUSTOMER ANALYSIS & LOYALTY RATE
-- Business Purpose: Measures customer retention rate (1-time buyers vs repeat shoppers)
-- Techniques: CTE, Conditional CASE Aggregation
-- ==============================================================================
WITH CustomerOrderCounts AS (
    SELECT 
        c.customer_id,
        c.customer_segment,
        COUNT(DISTINCT s.sale_id) AS order_count,
        ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS total_spend
    FROM CUSTOMERS c
    INNER JOIN SALES s ON c.customer_id = s.customer_id
    INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
    GROUP BY c.customer_id, c.customer_segment
)
SELECT 
    customer_segment,
    COUNT(customer_id) AS total_customers,
    SUM(CASE WHEN order_count = 1 THEN 1 ELSE 0 END) AS single_order_customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND((SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(customer_id), 2) AS repeat_purchase_rate_pct,
    ROUND(AVG(order_count), 2) AS avg_orders_per_customer,
    ROUND(AVG(total_spend), 2) AS avg_customer_spend
FROM CustomerOrderCounts
GROUP BY customer_segment
ORDER BY avg_customer_spend DESC;


-- ==============================================================================
-- 11. RFM CUSTOMER SEGMENTATION ENGINE
-- Business Purpose: Classifies customer base into Recency, Frequency, and Monetary tiers
-- Techniques: CTE, NTILE() Window Function, DATEDIFF
-- ==============================================================================
WITH CustomerRFM AS (
    SELECT 
        c.customer_id,
        CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
        c.customer_segment,
        DATEDIFF('2025-12-31', MAX(s.sale_date)) AS recency_days,
        COUNT(DISTINCT s.sale_id) AS frequency,
        ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS monetary_value
    FROM CUSTOMERS c
    INNER JOIN SALES s ON c.customer_id = s.customer_id
    INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
    GROUP BY c.customer_id, c.first_name, c.last_name, c.customer_segment
),
RFM_Scores AS (
    SELECT 
        customer_id,
        customer_name,
        customer_segment,
        recency_days,
        frequency,
        monetary_value,
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM CustomerRFM
)
SELECT 
    customer_id,
    customer_name,
    customer_segment,
    recency_days,
    frequency,
    monetary_value,
    r_score,
    f_score,
    m_score,
    CASE 
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions / VIP'
        WHEN r_score >= 3 AND f_score >= 2 THEN 'Loyal Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk / Churning'
        WHEN r_score >= 3 AND f_score = 1 THEN 'New Promising'
        ELSE 'Needs Attention / Dormant'
    END AS analytical_segment
FROM RFM_Scores
ORDER BY monetary_value DESC
LIMIT 25;


-- ==============================================================================
-- 12. OMNICHANNEL CHANNEL BREAKDOWN: IN-STORE VS ONLINE
-- Business Purpose: Evaluates digital channel efficiency vs brick-and-mortar stores
-- Techniques: Aggregations, Filtered KPIs, Profitability Comparison
-- ==============================================================================
SELECT 
    s.sales_channel,
    COUNT(DISTINCT s.sale_id) AS total_orders,
    SUM(si.quantity) AS total_units_sold,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS total_revenue,
    ROUND(SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)), 2) AS total_profit,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount) / COUNT(DISTINCT s.sale_id), 2) AS average_order_value,
    ROUND(
        (SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)) / 
         SUM((si.quantity * si.unit_price) - si.discount)) * 100, 
    2) AS profit_margin_pct,
    ROUND(
        (SUM((si.quantity * si.unit_price) - si.discount) / 
         (SELECT SUM((si2.quantity * si2.unit_price) - si2.discount) FROM SALE_ITEMS si2)) * 100,
    2) AS channel_revenue_share_pct
FROM SALES s
INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
INNER JOIN PRODUCTS p ON si.product_id = p.product_id
GROUP BY s.sales_channel;


-- ==============================================================================
-- 13. PAYMENT METHOD POPULARITY & BASKET SIZE CORRELATION
-- Business Purpose: Analyzes payment preferences and corresponding average ticket size
-- Techniques: GROUP BY, ORDER BY, Financial Ratios
-- ==============================================================================
SELECT 
    s.payment_method,
    COUNT(DISTINCT s.sale_id) AS transaction_count,
    ROUND((COUNT(DISTINCT s.sale_id) * 100.0) / (SELECT COUNT(*) FROM SALES), 2) AS transaction_share_pct,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS total_processed_revenue,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount) / COUNT(DISTINCT s.sale_id), 2) AS average_order_value
FROM SALES s
INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
GROUP BY s.payment_method
ORDER BY total_processed_revenue DESC;


-- ==============================================================================
-- 14. DAY OF WEEK SALES TRAFFIC & WEEKEND EFFECT
-- Business Purpose: Staffing and operational planning based on customer traffic surges
-- Techniques: DAYNAME(), DAYOFWEEK(), Ordering by Chronological Weekday
-- ==============================================================================
SELECT 
    DAYOFWEEK(s.sale_date) AS day_index,
    DAYNAME(s.sale_date) AS weekday_name,
    COUNT(DISTINCT s.sale_id) AS transaction_volume,
    SUM(si.quantity) AS units_sold,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS gross_revenue,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount) / COUNT(DISTINCT s.sale_id), 2) AS avg_ticket_size
FROM SALES s
INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
GROUP BY DAYOFWEEK(s.sale_date), DAYNAME(s.sale_date)
ORDER BY day_index ASC;


-- ==============================================================================
-- 15. DISCOUNT SENSITIVITY & MARGIN DILUTION ANALYSIS
-- Business Purpose: Determines whether promotional markdowns erode or boost margin
-- Techniques: CASE Expression, Conditional Aggregation
-- ==============================================================================
SELECT 
    CASE 
        WHEN si.discount = 0 THEN 'Full Price (No Discount)'
        WHEN si.discount > 0 AND (si.discount / (si.quantity * si.unit_price)) <= 0.15 THEN 'Standard Promo (<= 15%)'
        ELSE 'Deep Discount / Clearance (> 15%)'
    END AS promotion_tier,
    COUNT(si.sale_item_id) AS line_item_count,
    SUM(si.quantity) AS units_sold,
    ROUND(SUM(si.discount), 2) AS total_discount_given,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS net_realized_revenue,
    ROUND(SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)), 2) AS realized_profit,
    ROUND(
        (SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)) / 
         SUM((si.quantity * si.unit_price) - si.discount)) * 100, 
    2) AS realized_margin_pct
FROM SALE_ITEMS si
INNER JOIN PRODUCTS p ON si.product_id = p.product_id
GROUP BY 
    CASE 
        WHEN si.discount = 0 THEN 'Full Price (No Discount)'
        WHEN si.discount > 0 AND (si.discount / (si.quantity * si.unit_price)) <= 0.15 THEN 'Standard Promo (<= 15%)'
        ELSE 'Deep Discount / Clearance (> 15%)'
    END
ORDER BY net_realized_revenue DESC;


-- ==============================================================================
-- 16. CUMULATIVE RUNNING REVENUE TOTALS (YEAR-TO-DATE / YTD)
-- Business Purpose: Running financial pacing towards annual revenue targets
-- Techniques: CTE, Window Function SUM() OVER (ORDER BY ...)
-- ==============================================================================
WITH MonthlyTotals AS (
    SELECT 
        YEAR(s.sale_date) AS fiscal_year,
        DATE_FORMAT(s.sale_date, '%Y-%m') AS sales_month,
        ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS month_revenue
    FROM SALES s
    INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
    GROUP BY YEAR(s.sale_date), DATE_FORMAT(s.sale_date, '%Y-%m')
)
SELECT 
    fiscal_year,
    sales_month,
    month_revenue,
    SUM(month_revenue) OVER (
        PARTITION BY fiscal_year 
        ORDER BY sales_month ASC
    ) AS running_ytd_revenue
FROM MonthlyTotals
ORDER BY sales_month ASC;


-- ==============================================================================
-- 17. PRODUCT AFFINITY & MULTI-ITEM BASKET PENETRATION
-- Business Purpose: Calculates % of transactions containing multiple distinct items
-- Techniques: CTE, Basket Size Aggregation
-- ==============================================================================
WITH BasketSizes AS (
    SELECT 
        s.sale_id,
        COUNT(si.sale_item_id) AS distinct_items_in_cart,
        SUM(si.quantity) AS total_units_in_cart,
        ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS basket_revenue
    FROM SALES s
    INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
    GROUP BY s.sale_id
)
SELECT 
    CASE 
        WHEN distinct_items_in_cart = 1 THEN '1 Item (Single-Item Basket)'
        WHEN distinct_items_in_cart = 2 THEN '2 Items (Dual-Item Basket)'
        WHEN distinct_items_in_cart = 3 THEN '3 Items (Multi-Item Basket)'
        ELSE '4+ Items (Large Basket)'
    END AS basket_tier,
    COUNT(sale_id) AS transaction_count,
    ROUND((COUNT(sale_id) * 100.0) / (SELECT COUNT(*) FROM BasketSizes), 2) AS percent_of_all_orders,
    ROUND(AVG(basket_revenue), 2) AS average_basket_value
FROM BasketSizes
GROUP BY 
    CASE 
        WHEN distinct_items_in_cart = 1 THEN '1 Item (Single-Item Basket)'
        WHEN distinct_items_in_cart = 2 THEN '2 Items (Dual-Item Basket)'
        WHEN distinct_items_in_cart = 3 THEN '3 Items (Multi-Item Basket)'
        ELSE '4+ Items (Large Basket)'
    END
ORDER BY transaction_count DESC;


-- ==============================================================================
-- 18. SUPPLIER PERFORMANCE & PROCUREMENT SPEND AUDIT
-- Business Purpose: Evaluates vendor revenue and average product profitability
-- Techniques: Multi-table JOIN, Aggregations
-- ==============================================================================
SELECT 
    sup.supplier_id,
    sup.supplier_name,
    sup.city AS supplier_city,
    COUNT(DISTINCT p.product_id) AS active_catalog_skus,
    SUM(si.quantity) AS units_sold,
    ROUND(SUM((si.quantity * si.unit_price) - si.discount), 2) AS total_retail_sales,
    ROUND(SUM(si.quantity * p.unit_cost), 2) AS total_cogs_paid_to_vendor,
    ROUND(SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)), 2) AS total_gross_margin,
    ROUND(
        (SUM(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)) / 
         SUM((si.quantity * si.unit_price) - si.discount)) * 100, 
    2) AS vendor_margin_pct
FROM SUPPLIERS sup
INNER JOIN PRODUCTS p ON sup.supplier_id = p.supplier_id
INNER JOIN SALE_ITEMS si ON p.product_id = si.product_id
GROUP BY sup.supplier_id, sup.supplier_name, sup.city
ORDER BY total_retail_sales DESC;


-- ==============================================================================
-- 19. INVENTORY REORDER ALERT (STOCK VS REORDER LEVEL)
-- Business Purpose: Operations alert for replenishment procurement
-- Techniques: Filtering with WHERE stock_quantity <= reorder_level
-- ==============================================================================
SELECT 
    p.product_id,
    p.product_name,
    cat.category_name,
    sup.supplier_name,
    p.stock_quantity,
    p.reorder_level,
    (p.reorder_level - p.stock_quantity) AS units_deficit,
    p.unit_cost,
    ROUND((p.reorder_level - p.stock_quantity) * p.unit_cost, 2) AS estimated_reorder_cost,
    p.status
FROM PRODUCTS p
INNER JOIN CATEGORIES cat ON p.category_id = cat.category_id
INNER JOIN SUPPLIERS sup ON p.supplier_id = sup.supplier_id
WHERE p.stock_quantity <= p.reorder_level
ORDER BY units_deficit DESC;


-- ==============================================================================
-- 20. STORE GROWTH: Q4 HOLIDAY SURGE VS Q3 BASELINE
-- Business Purpose: Assesses store-level agility in capturing holiday demand surges
-- Techniques: CTE, Conditional Aggregations, Percentage Surge Growth
-- ==============================================================================
WITH QuarterlyStoreSales AS (
    SELECT 
        st.store_id,
        st.store_name,
        ROUND(SUM(CASE WHEN MONTH(s.sale_date) IN (7, 8, 9) THEN (si.quantity * si.unit_price) - si.discount ELSE 0 END), 2) AS q3_revenue,
        ROUND(SUM(CASE WHEN MONTH(s.sale_date) IN (10, 11, 12) THEN (si.quantity * si.unit_price) - si.discount ELSE 0 END), 2) AS q4_holiday_revenue
    FROM STORES st
    INNER JOIN SALES s ON st.store_id = s.store_id
    INNER JOIN SALE_ITEMS si ON s.sale_id = si.sale_id
    WHERE YEAR(s.sale_date) = 2025
    GROUP BY st.store_id, st.store_name
)
SELECT 
    store_id,
    store_name,
    q3_revenue,
    q4_holiday_revenue,
    ROUND(q4_holiday_revenue - q3_revenue, 2) AS net_holiday_surge_dollar,
    ROUND(((q4_holiday_revenue - q3_revenue) / q3_revenue) * 100, 2) AS holiday_surge_pct
FROM QuarterlyStoreSales
ORDER BY holiday_surge_pct DESC;
