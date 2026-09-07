# Business Sales & Customer Analytics System (InsightMart)

[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/Flask-3.1.3-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Portfolio%20Ready-success.svg)](#)

An enterprise-grade, end-to-end **Business Intelligence & Decision Support System** developed for **InsightMart**, a multi-channel retail company with physical storefronts across the United States and an e-commerce digital storefront.

This project was built to demonstrate practical, professional competencies across:
* **Information Systems & Business Analysis**
* **Relational Database Design (3NF) & MySQL Administration**
* **Advanced SQL Analytics (CTEs, Window Functions, Aggregations)**
* **Python Data Pipeline (ETL, Validation, Cleaning & Derivations)**
* **Exploratory Data Analysis (EDA) & Data Visualization (Pandas, Matplotlib, Seaborn)**
* **RESTful API Backend Architecture (Flask)**
* **Interactive Executive Web Dashboards (HTML5, Bootstrap 5, Chart.js)**
* **Application Security & Dual-Environment Cloud Deployment**

---

## Table of Contents
1. [Business Scenario & Problem](#business-scenario--problem)
2. [Project Objectives & Business Questions](#project-objectives--business-questions)
3. [System Architecture](#system-architecture)
4. [Relational Database Design & Schema](#relational-database-design--schema)
5. [Data Pipeline & ETL Architecture](#data-pipeline--etl-architecture)
6. [Business KPI Formulations](#business-kpi-formulations)
7. [SQL & Python Analytics](#sql--python-analytics)
8. [Interactive Web Dashboard Features](#interactive-web-dashboard-features)
9. [Key Business Findings & Management Recommendations](#key-business-findings--management-recommendations)
10. [Installation & Setup Guide](#installation--setup-guide)
11. [Environment Configuration (.env)](#environment-configuration-env)
12. [API Reference](#api-reference)
13. [Deployment Architecture](#deployment-architecture)
14. [Future Enhancements](#future-enhancements)

---

## Business Scenario & Problem

**InsightMart** is a national retailer operating 12 retail branches across 5 geographic regions, alongside an e-commerce digital channel. InsightMart processes tens of thousands of sales transactions across 120 SKUs in 6 merchandise departments:
* Electronics
* Apparel
* Home & Kitchen
* Health & Beauty
* Sports & Outdoors
* Groceries & Gourmet

### The Problem
Management previously operated in organizational silos relying on manually prepared, disjointed spreadsheets. Consequently, decision-makers faced severe operational challenges:
* **Invisible Profit Margins**: High-volume departments (e.g., Electronics) generated substantial top-line revenue but masked lower margin percentages compared to smaller categories.
* **Store Performance Disparities**: Substantial performance variances between flagship urban locations and developing regional branches went unmeasured.
* **Customer Retention Blindspots**: Lack of RFM (Recency, Frequency, Monetary) segmentation obscured the fact that a small VIP cohort generated almost half of all sales.
* **Discount Inefficiencies**: Inability to quantify how promotional markdowns affected bottom-line gross margins.

---

## Project Objectives & Business Questions

This system transforms raw transactional sales data into a centralized, interactive analytics platform answering critical management questions:
1. **Financial Health**: What is InsightMart's total revenue, merchandise cost, gross profit, and blended margin?
2. **Sales Trajectory**: How do sales volume, revenue, and margin fluctuate month-over-month and seasonally?
3. **Merchandise Mix**: Which products are the top hero revenue generators, and which products are low-margin/stagnant items needing clearance?
4. **Regional Benchmarks**: Which retail branches and geographic regions outperform company averages?
5. **Customer Lifetime Value**: Who are the company's highest-value VIP customers, and what is their repeat purchase rate?
6. **Channel Dynamics**: How does physical in-store performance compare to digital e-commerce?

---

## System Architecture

The project adheres to a clean, modular, multi-tier architecture:

```
[Retail Sales / POS / Online Checkout]
                  │
                  ▼
         [Raw CSV Datasets]
                  │
                  ▼
     [Python ETL Pipeline (Pandas)]
   (Validation, Cleaning, Derivations)
                  │
                  ▼
    [Relational Database (MySQL 8.0)]
  (3NF Tables, Foreign Keys, Indexes, View)
                  │
                  ▼
    [Flask REST API Service Layer]
   (Parameterized Queries & Analytics)
                  │
                  ▼
[Interactive Web Dashboard (HTML5/Chart.js)]
   (Executive KPIs, Cross-Filtering, Charts)
                  │
                  ▼
[Executive Decision Support & Recommendations]
```

---

## Relational Database Design & Schema

The database (`business_sales_db`) is normalized to **Third Normal Form (3NF)** to ensure referential integrity, eliminate data redundancy, and maximize query efficiency.

```
                    ┌─────────────────┐
                    │   CATEGORIES    │
                    ├─────────────────┤
                    │ PK  category_id │
                    │     category_name
                    │     description │
                    └────────┬────────┘
                             │ 1
                             │ has many
                             │ N
┌─────────────────┐ 1      N ┌────────┴────────┐
│    SUPPLIERS    ├──────────┤    PRODUCTS     │
├─────────────────┤ supplies ├─────────────────┤
│ PK  supplier_id │          │ PK  product_id  │
│     supplier_name          │ FK  category_id │
│     city        │          │ FK  supplier_id │
└─────────────────┘          │     unit_cost   │
                             │     selling_price
                             │     stock_quantity
                             │     status      │
                             └────────┬────────┘
                                      │ 1
                                      │ ordered in
                                      │ N
┌─────────────────┐ 1      N ┌────────┴────────┐
│     STORES      ├──────────┤   SALE_ITEMS    │
├─────────────────┤ hosts    ├─────────────────┤
│ PK  store_id    │          │ PK  sale_item_id│
│     store_name  │          │ FK  sale_id     │
│     city        │          │ FK  product_id  │
│     region      │          │     quantity    │
└────────┬────────┘          │     unit_price  │
         │ 1                 │     discount    │
         │ records           └────────┬────────┘
         │ N                          │ N
┌────────┴────────┐                   │ belongs to
│      SALES      ├───────────────────┘ 1
├─────────────────┤
│ PK  sale_id     │
│     sale_date   │
│ FK  customer_id │
│ FK  store_id    │
│     sales_channel
│     payment_method
└────────┬────────┘
         │ N
         │ placed by
         │ 1
┌────────┴────────┐
│    CUSTOMERS    │
├─────────────────┤
│ PK  customer_id │
│     first_name  │
│     last_name   │
│     gender      │
│     date_of_birth
│     customer_segment
│     city        │
│     registration_date
└─────────────────┘
```

### Analytical View: `view_sales_performance`
A denormalized analytical view joins the normalized entities, computing line-item financial metrics dynamically:
* `line_revenue = (quantity * unit_price) - discount`
* `line_cost = quantity * unit_cost`
* `line_profit = line_revenue - line_cost`
* `profit_margin_pct = (line_profit / line_revenue) * 100`

---

## Data Pipeline & ETL Architecture

The data pipeline (`src/data_generation.py` and `src/data_cleaning.py`) processes raw business transactions into clean analytical records:
1. **Raw Ingestion**: Ingests master tables and transaction records from `data/raw/`.
2. **Data Quality Audit**: Identifies missing values, duplicate primary keys, and anomalies.
3. **Data Cleaning & Standardization**:
   * Trims whitespace and enforces Title Casing on names, cities, and tender methods.
   * Enforces business constraints: `selling_price >= unit_cost`, `quantity > 0`, `discount <= subtotal`.
   * Standardizes ISO date formats (`YYYY-MM-DD`).
4. **Derived Metrics Generation**: Computes financial metrics (revenue, cost, gross profit, margin percentage).
5. **Database Bulk Loading**: Loads cleaned data into MySQL using chunked transactions.

---

## Business KPI Formulations

All calculations adhere to standard managerial accounting definitions:

$$\text{Line Revenue} = (\text{Quantity} \times \text{Unit Price}) - \text{Discount}$$

$$\text{Line Cost (COGS)} = \text{Quantity} \times \text{Unit Cost}$$

$$\text{Gross Operating Profit} = \text{Revenue} - \text{Cost}$$

$$\text{Profit Margin Percentage} = \left(\frac{\text{Gross Profit}}{\text{Revenue}}\right) \times 100$$

$$\text{Average Order Value (AOV)} = \frac{\text{Total Revenue}}{\text{Total Completed Orders}}$$

$$\text{Customer Lifetime Value (CLV)} = \sum_{i=1}^{n} \text{Order Revenue}_i$$

$$\text{Month-over-Month Growth (MoM \%)} = \left(\frac{\text{Revenue}_t - \text{Revenue}_{t-1}}{\text{Revenue}_{t-1}}\right) \times 100$$

---

## SQL & Python Analytics

### Advanced SQL Analytics (`sql/business_analysis_queries.sql`)
The repository includes 20 production-ready analytical SQL queries demonstrating mastery of:
* **Common Table Expressions (CTEs)**: Multi-step data isolation for MoM calculations and customer RFM scoring.
* **Window Functions**: `LAG()`, `LEAD()`, `DENSE_RANK()`, `RANK()`, `NTILE()`, and `SUM() OVER ()`.
* **Complex Joins**: Multi-table inner and left outer joins preserving unmatched master records.
* **Case Logic & Aggregations**: Conditional aggregation for promotional tiers and segment summaries.

### Jupyter Notebook (`notebooks/sales_analysis.ipynb`)
A 12-section data science notebook featuring pre-rendered visualizations and business interpretations:
1. Introduction & Objectives
2. Environment Setup & Data Loading
3. Data Understanding & Summary Statistics
4. Data Quality Audit
5. Data Cleaning & Feature Engineering
6. Exploratory Data Analysis (EDA)
7. Time Series & Seasonality Analysis
8. Customer Analytics & RFM Segmentation
9. Product Analytics & Margin Matrix
10. Store & Regional Benchmarks
11. Empirical Business Findings
12. Strategic Management Recommendations

---

## Interactive Web Dashboard Features

The web portal provides a business interface with 7 integrated views:
1. **Executive Dashboard (`/dashboard`)**:
   * 6 Dynamic KPI cards with trend indicators.
   * Monthly Revenue & Profit progression line/area chart.
   * Merchandise Category revenue mix doughnut chart.
   * Top 10 Hero Products horizontal bar chart.
   * Store Branch revenue benchmarking bar chart.
   * Omnichannel (In-Store vs Online) and Payment Method distribution charts.
   * Top customer spenders quick summary table.
2. **Sales Analytics (`/sales`)**:
   * Order volume vs ticket size dual-axis chart.
   * Paginated, searchable sales ledger with live search by customer, store, SKU, or sale ID.
   * One-click CSV table export.
3. **Product Intelligence (`/products`)**:
   * Hero vs Underperforming products bar charts.
   * Full inventory catalog matrix with reorder level alerts and margin badges.
   * Multi-column client-side sorting (Revenue, Margin, Profit, Units, Stock).
4. **Customer Segmentation (`/customers`)**:
   * RFM segmentation distributions (High, Medium, Low Value).
   * Revenue concentration analysis.
   * Top 15 Customer Lifetime Value (CLV) leaderboard.
5. **Store Benchmarking (`/stores`)**:
   * Branch comparison bar chart and regional share donut.
   * Complete store ranking matrix (Tier 1 Flagship, Tier 2 Core, Tier 3 Developing).
6. **Business Insights (`/insights`)**:
   * Automated decision support cards (Observation → Business Meaning → Recommendation).
7. **Architecture & Portfolio (`/about`)**:
   * Information Systems capstone documentation, ERD reference, and KPI glossary.

---

## Key Business Findings & Management Recommendations

### Major Empirical Findings:
* **The 80/20 Rule in Action**: High-Value customers represent **18.0% of accounts** ($900$ customers) but generate **$3.17M (48.0%) of total sales**.
* **Electronics Volume vs Margin Trade-off**: Electronics accounts for **72.6% of revenue** ($4.79M) but operates at a lower gross margin (**44.97%**) than Health & Beauty (**69.21%**) or Apparel (**61.50%**).
* **Flagship Foot Traffic Gap**: Manhattan Flagship ($731k) generates **1.9x the turnover** of developing locations (Minneapolis Plaza at $382k), primarily due to local foot traffic differences rather than basket conversion.

### Strategic Recommendations:
1. **VIP Loyalty Program**: Deploy a structured rewards program to protect the 18% High-Value customer cohort and lift annual purchase frequency.
2. **Margin-Accretive Bundling**: Package lower-margin Electronics SKUs with high-margin Apparel and Beauty accessories to elevate blended category margins by 200–300 bps.
3. **Omnichannel Store Pick-up (BOPIS)**: Implement Buy Online, Pick Up In-Store to drive digital e-commerce shoppers into brick-and-mortar storefronts, stimulating incremental in-store basket additions.
4. **Targeted Branch Assortment**: Reallocate regional inventory and direct localized digital advertising to close the foot-traffic gap in developing Midwest branches.

---

## Installation & Setup Guide

### Prerequisites
* Python 3.10+ (tested on Python 3.14)
* MySQL 8.0+ (optional: local SQLite mode supported out of the box)
* Git

### Step-by-Step Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/ByizaBryan/BUSINESS-SALES-CUSTOMER-ANALYTICS-SYSTEM.git
   cd BUSINESS-SALES-CUSTOMER-ANALYTICS-SYSTEM
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   ```
   *For live MySQL*: Enter your `DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` in `.env`.  
   *For instant local testing*: Set `DB_TYPE=sqlite` in `.env`.

5. **Run the Data Pipeline (Generates Data, Cleans & Initializes Database):**
   ```bash
   # Step A: Generate raw retail data (~5,000 customers, 32,000 orders)
   python src/data_generation.py

   # Step B: Run ETL pipeline (cleans data, derives metrics, loads database)
   python src/data_cleaning.py
   ```

6. **Launch the Web Analytics Portal:**
   ```bash
   python app/app.py
   ```
   Open your browser and navigate to: **`http://127.0.0.1:5000`**

7. **Run the Automated Test Suite:**
   ```bash
   python tests/test_system.py
   ```

---

## Environment Configuration (.env)

The application utilizes environment variables to isolate credentials:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DB_TYPE` | `mysql` (or `sqlite`) | Active database engine |
| `DB_HOST` | `localhost` | MySQL database host address |
| `DB_PORT` | `3306` | MySQL database port |
| `DB_NAME` | `business_sales_db` | Relational database name |
| `DB_USER` | `root` | Database username |
| `DB_PASSWORD` | *(empty)* | Database user password |
| `SQLITE_PATH` | `data/processed/business_sales.db` | Path for local SQLite fallback |
| `SECRET_KEY` | *(configured)* | Flask session encryption key |
| `PORT` | `5000` | Web server listening port |

---

## API Reference

The Flask backend exposes clean REST API endpoints returning structured JSON:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/dashboard/kpis` | Executive KPI scorecard (Revenue, Profit, Orders, AOV, Margin) |
| `GET` | `/api/dashboard/revenue-trend` | Monthly revenue, profit, and volume time series |
| `GET` | `/api/dashboard/category-performance` | Department revenue, profit, units, and margin |
| `GET` | `/api/dashboard/store-performance` | Retail branch benchmarking metrics |
| `GET` | `/api/dashboard/sales-channels` | In-Store vs Online digital fulfillment breakdown |
| `GET` | `/api/dashboard/payment-methods` | Payment tender distribution (Cards, Wallets, Cash) |
| `GET` | `/api/products/top?limit=10` | Top performing products ranked by revenue |
| `GET` | `/api/products/underperforming?limit=10` | Bottom products requiring promotional action |
| `GET` | `/api/products/catalog` | Complete product matrix with inventory and margin details |
| `GET` | `/api/customers/segments` | RFM customer segment profile (High, Medium, Low Value) |
| `GET` | `/api/customers/top?limit=15` | Customer Lifetime Value (CLV) leaderboard |
| `GET` | `/api/stores/performance` | Store ranking table and regional share |
| `GET` | `/api/sales/transactions` | Paginated, searchable sales ledger (`page`, `per_page`, `search`) |
| `GET` | `/api/insights` | Empirically calculated business insights and recommendations |
| `GET` | `/api/filters/options` | Dynamic options for frontend dropdown filters |

---

## Deployment Architecture

The application is engineered to deploy across cloud environments without code modification:

### Development Environment
```
Local Browser  ──>  Flask Web App (Local)  ──>  Local MySQL (or SQLite)
```

### Production Cloud Environment
```
End User (Internet)  ──>  Cloud Host (Render / Railway / Docker)
                               │
                               ▼
                    Hosted Flask WSGI Server (Gunicorn)
                               │
                               ▼
                 Remote Cloud MySQL Database
            (Aiven / PlanetScale / Railway / AWS RDS)
```

To switch from development to production:
1. Deploy the Flask code to your preferred cloud host (e.g., Render, Railway, AWS EC2, or Azure App Service).
2. Provision a cloud MySQL instance (e.g., Aiven MySQL or Railway MySQL).
3. Set the environment variables `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, and `SECRET_KEY` in your cloud host's settings.
4. Run `python src/data_cleaning.py` once to initialize the cloud schema and seed records.

---

## Future Enhancements

* **Role-Based Access Control (RBAC)**: User authentication with Admin, Analyst, and Store Manager privilege tiers.
* **Predictive Machine Learning Models**:
  * Random Forest / XGBoost model for 90-day Customer Churn Prediction.
  * ARIMA / Prophet time series models for automated store sales forecasting.
* **Real-Time POS Streaming**: Webhook / Apache Kafka ingestion pipeline for live transaction streaming.
* **Automated PDF / Email Reporting**: Scheduled executive summaries dispatched via SendGrid.

---

## Author & Portfolio Contact

* **Developer**: Byiza Bryan
* **Specialization**: Information Systems, Business Analytics & Data Engineering
* **Repository**: [https://github.com/ByizaBryan/BUSINESS-SALES-CUSTOMER-ANALYTICS-SYSTEM](https://github.com/ByizaBryan/BUSINESS-SALES-CUSTOMER-ANALYTICS-SYSTEM)
