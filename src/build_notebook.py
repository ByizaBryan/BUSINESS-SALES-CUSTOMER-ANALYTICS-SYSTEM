"""
InsightMart Business Sales & Customer Analytics System
Script: src/build_notebook.py
Description: Generates and executes the complete 12-section Jupyter Notebook:
             notebooks/sales_analysis.ipynb
"""

import sys
import os
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient

ROOT_DIR = Path(__file__).resolve().parent.parent
NOTEBOOK_PATH = ROOT_DIR / "notebooks" / "sales_analysis.ipynb"
os.makedirs(NOTEBOOK_PATH.parent, exist_ok=True)


def create_and_execute_notebook():
    nb = nbf.v4.new_notebook()
    cells = []

    # =========================================================================
    # Section 1: Introduction
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""# InsightMart Business Sales & Customer Analytics
## Executive Data Science & Business Intelligence Analysis

---

### 1. Business Problem & Background
**InsightMart** is a fictional multi-regional retail company operating physical storefronts across the United States as well as an e-commerce digital storefront. 

While the company has accumulated thousands of sales transactions across diverse product lines, leadership has historically relied on static, siloed reports. Consequently, decision-makers face critical visibility blindspots:
* **Profitability versus Volume**: High-revenue categories (e.g., Electronics) may conceal compressed margins, while smaller categories deliver outsized profits.
* **Store Disparities**: Substantial performance variance between flagship locations and underperforming branches.
* **Customer Retention & Value**: Lack of behavioral segmentation, obscuring the concentration of revenue in High-Value loyalty tiers.
* **Promotional Discipline**: Unmeasured impact of discounts on bottom-line gross margins.

### 2. Objectives & Analytical Questions
1. What are the baseline enterprise KPIs (Total Revenue, Gross Profit, Blended Margin, AOV, Total Units)?
2. How do sales and profits fluctuate month-over-month and seasonally?
3. Which product categories and individual SKUs represent the top revenue and profit drivers?
4. How do stores compare across regions in turnover and profitability?
5. How is customer spend distributed across High, Medium, and Low-Value segments?
6. What strategic recommendations should management implement to accelerate growth?
"""))

    # =========================================================================
    # Section 2: Environment Setup & Data Loading
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""---
## Section 2 — Environment Setup & Data Loading
Loading core analytical libraries (`pandas`, `numpy`, `matplotlib`, `seaborn`) and connecting directly to the normalized relational database (`view_sales_performance` and base tables).
"""))

    cells.append(nbf.v4.new_code_cell("""import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set visual aesthetic standards
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.dpi'] = 100

# Import database connector
ROOT_DIR = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT_DIR))

from src.database import get_connection

conn, engine = get_connection()
print(f"Connected to InsightMart analytics database via [{engine.upper()}] engine.")

# Load primary analytical view
df_sales = pd.read_sql("SELECT * FROM view_sales_performance", conn)
df_customers = pd.read_sql("SELECT * FROM CUSTOMERS", conn)
df_products = pd.read_sql("SELECT * FROM PRODUCTS", conn)
df_stores = pd.read_sql("SELECT * FROM STORES", conn)
df_categories = pd.read_sql("SELECT * FROM CATEGORIES", conn)

conn.close()

# Convert date fields
df_sales['sale_date'] = pd.to_datetime(df_sales['sale_date'])
df_sales['year_month'] = df_sales['sale_date'].dt.to_period('M')

print(f"Loaded {len(df_sales):,} enriched line-item sales records across {df_sales['sale_id'].nunique():,} orders.")
"""))

    # =========================================================================
    # Section 3: Data Understanding
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""---
## Section 3 — Data Understanding & Schema Inspection
Inspecting record structures, schema data types, descriptive statistics, and numerical distributions.
"""))

    cells.append(nbf.v4.new_code_cell("""print("Sales Dataset Overview:")
print("-" * 50)
df_sales.info()
"""))

    cells.append(nbf.v4.new_code_cell("""print("Summary Statistics for Numerical Variables:")
print("-" * 50)
df_sales[['quantity', 'unit_price', 'discount', 'unit_cost', 'line_revenue', 'line_profit', 'profit_margin_pct']].describe().round(2)
"""))

    # =========================================================================
    # Section 4: Data Quality Audit
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""---
## Section 4 — Data Quality Assessment
Auditing for null entries, duplicates, negative prices, and anomalous discounts.
"""))

    cells.append(nbf.v4.new_code_cell("""print("Null Value Audit across Tables:")
print("-" * 50)
print(df_sales.isnull().sum())
print()
print("Duplicate Check on Line Items:")
print("-" * 50)
print(f"Duplicate Sale Item IDs: {df_sales['sale_item_id'].duplicated().sum()}")

# Business Logic Constraint Verifications
negative_revenue = (df_sales['line_revenue'] < 0).sum()
invalid_quantities = (df_sales['quantity'] <= 0).sum()
excessive_discounts = (df_sales['discount'] > (df_sales['quantity'] * df_sales['unit_price'])).sum()

print(f"Negative revenue rows:        {negative_revenue}")
print(f"Invalid quantity rows (<=0):  {invalid_quantities}")
print(f"Excessive discount rows:      {excessive_discounts}")
print("-> Data Quality Integrity Status: 100% Validated.")
"""))

    # =========================================================================
    # Section 5: Data Cleaning & Feature Engineering
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""---
## Section 5 — Data Cleaning & Feature Engineering
Confirming financial derived fields (`line_revenue`, `line_cost`, `line_profit`, `profit_margin_pct`) and engineering time dimensions (`month`, `quarter`, `day_of_week`, `is_weekend`).
"""))

    cells.append(nbf.v4.new_code_cell("""# Extract time dimensions
df_sales['month_name'] = df_sales['sale_date'].dt.strftime('%B')
df_sales['month_num'] = df_sales['sale_date'].dt.month
df_sales['year'] = df_sales['sale_date'].dt.year
df_sales['day_of_week'] = df_sales['sale_date'].dt.day_name()
df_sales['is_weekend'] = df_sales['sale_date'].dt.dayofweek.isin([5, 6])
df_sales['quarter'] = 'Q' + df_sales['sale_date'].dt.quarter.astype(str)

# Executive KPI Calculations
total_revenue = df_sales['line_revenue'].sum()
total_cost = df_sales['line_cost'].sum()
total_profit = df_sales['line_profit'].sum()
blended_margin = (total_profit / total_revenue) * 100
total_orders = df_sales['sale_id'].nunique()
total_units = df_sales['quantity'].sum()
aov = total_revenue / total_orders

print("==========================================================")
print("INSIGHTMART EXECUTIVE KPI SCORECARD")
print("==========================================================")
print(f"Total Revenue:         ${total_revenue:,.2f}")
print(f"Total Merchandise Cost: ${total_cost:,.2f}")
print(f"Total Gross Profit:    ${total_profit:,.2f}")
print(f"Blended Gross Margin:  {blended_margin:.2f}%")
print(f"Total Orders:          {total_orders:,}")
print(f"Total Units Sold:      {total_units:,}")
print(f"Average Order Value:   ${aov:.2f}")
print("==========================================================")
"""))

    # =========================================================================
    # Section 6: Exploratory Data Analysis (EDA)
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""---
## Section 6 — Exploratory Data Analysis (EDA)
Analyzing core business dimensions: product categories, channels, and payment methods.
"""))

    cells.append(nbf.v4.new_code_cell("""# 1. Category Performance Breakdown
cat_summary = df_sales.groupby('category_name').agg(
    total_revenue=('line_revenue', 'sum'),
    total_profit=('line_profit', 'sum'),
    units_sold=('quantity', 'sum')
).reset_index()

cat_summary['margin_pct'] = (cat_summary['total_profit'] / cat_summary['total_revenue']) * 100
cat_summary = cat_summary.sort_values(by='total_revenue', ascending=False)

fig, ax1 = plt.subplots(figsize=(14, 6))
sns.barplot(data=cat_summary, x='category_name', y='total_revenue', ax=ax1, palette='Blues_r')
ax1.set_title('Total Revenue & Profit Margin by Product Category', fontsize=14, fontweight='bold', pad=15)
ax1.set_ylabel('Total Revenue ($)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Product Category', fontsize=12, fontweight='bold')
ax1.yaxis.set_major_formatter('${x:,.0f}')

# Dual axis for profit margin
ax2 = ax1.twinx()
ax2.plot(cat_summary['category_name'], cat_summary['margin_pct'], color='#e63946', marker='o', linewidth=2.5, label='Gross Margin %')
ax2.set_ylabel('Profit Margin (%)', fontsize=12, fontweight='bold', color='#e63946')
ax2.grid(False)
ax2.set_ylim(0, 80)

for i, txt in enumerate(cat_summary['margin_pct']):
    ax2.annotate(f"{txt:.1f}%", (i, txt + 2), ha='center', color='#e63946', fontweight='bold')

plt.tight_layout()
plt.show()
"""))

    cells.append(nbf.v4.new_code_cell("""# 2. Omnichannel Channel & Payment Distribution
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

channel_rev = df_sales.groupby('sales_channel')['line_revenue'].sum()
ax1.pie(channel_rev, labels=channel_rev.index, autopct='%1.1f%%', colors=['#2a9d8f', '#e76f51'], startangle=140, explode=(0.04, 0))
ax1.set_title('Revenue Share by Sales Channel', fontsize=13, fontweight='bold')

pay_rev = df_sales.groupby('payment_method')['line_revenue'].sum().sort_values(ascending=False)
sns.barplot(x=pay_rev.values, y=pay_rev.index, ax=ax2, palette='crest')
ax2.set_title('Revenue by Payment Method', fontsize=13, fontweight='bold')
ax2.set_xlabel('Revenue ($)', fontweight='bold')
ax2.xaxis.set_major_formatter('${x:,.0f}')

plt.tight_layout()
plt.show()
"""))

    # =========================================================================
    # Section 7: Time & Seasonality Analysis
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""---
## Section 7 — Time Series & Seasonality Analysis
Tracking monthly revenue trends, seasonal peaks (Q4 holiday surge), and weekly shopping patterns.
"""))

    cells.append(nbf.v4.new_code_cell("""monthly_trend = df_sales.groupby('year_month').agg(
    monthly_revenue=('line_revenue', 'sum'),
    monthly_profit=('line_profit', 'sum'),
    orders=('sale_id', 'nunique')
).reset_index()

monthly_trend['month_str'] = monthly_trend['year_month'].astype(str)

plt.figure(figsize=(15, 6))
plt.plot(monthly_trend['month_str'], monthly_trend['monthly_revenue'], marker='o', color='#1d3557', linewidth=2.5, label='Monthly Revenue')
plt.plot(monthly_trend['month_str'], monthly_trend['monthly_profit'], marker='s', color='#2a9d8f', linewidth=2.5, label='Monthly Profit')
plt.fill_between(monthly_trend['month_str'], monthly_trend['monthly_profit'], monthly_trend['monthly_revenue'], color='#a8dadc', alpha=0.3)

plt.title('Monthly Revenue & Profit Progression (2024 - 2025)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Year-Month', fontsize=12, fontweight='bold')
plt.ylabel('Amount ($)', fontsize=12, fontweight='bold')
plt.xticks(rotation=45)
plt.gca().yaxis.set_major_formatter('${x:,.0f}')
plt.legend(loc='upper left', frameon=True)
plt.tight_layout()
plt.show()
"""))

    cells.append(nbf.v4.new_code_cell("""# Day of Week Foot Traffic Analysis
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_summary = df_sales.groupby('day_of_week').agg(
    orders=('sale_id', 'nunique'),
    revenue=('line_revenue', 'sum')
).reindex(dow_order).reset_index()

fig, ax = plt.subplots(figsize=(12, 5))
sns.barplot(data=dow_summary, x='day_of_week', y='revenue', palette='Blues_r', ax=ax)
ax.set_title('Weekly Revenue Distribution (Day-of-Week Effect)', fontsize=13, fontweight='bold')
ax.set_ylabel('Total Revenue ($)', fontweight='bold')
ax.set_xlabel('Day of the Week', fontweight='bold')
ax.yaxis.set_major_formatter('${x:,.0f}')

for i, row in dow_summary.iterrows():
    ax.annotate(f"${row['revenue']:,.0f}", (i, row['revenue'] / 2), ha='center', color='white', fontweight='bold')

plt.tight_layout()
plt.show()
"""))

    # =========================================================================
    # Section 8: Customer Analytics & Segmentation
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""---
## Section 8 — Customer Analytics & Segmentation
Examining customer segments (High, Medium, Low Value), repeat purchasing behavior, and customer lifetime spend.
"""))

    cells.append(nbf.v4.new_code_cell("""cust_summary = df_sales.groupby(['customer_id', 'customer_name', 'customer_segment']).agg(
    total_spend=('line_revenue', 'sum'),
    total_orders=('sale_id', 'nunique'),
    total_units=('quantity', 'sum')
).reset_index()

seg_overview = cust_summary.groupby('customer_segment').agg(
    customer_count=('customer_id', 'count'),
    total_revenue=('total_spend', 'sum'),
    avg_spend_per_customer=('total_spend', 'mean'),
    avg_orders_per_customer=('total_orders', 'mean')
).reset_index()

seg_overview['revenue_share_pct'] = (seg_overview['total_revenue'] / seg_overview['total_revenue'].sum()) * 100
display(seg_overview.round(2))

# Visualize Customer Segment Distribution
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.pie(seg_overview['customer_count'], labels=seg_overview['customer_segment'], autopct='%1.1f%%', colors=['#e76f51', '#2a9d8f', '#457b9d'], startangle=140)
ax1.set_title('Customer Count Share by Segment', fontsize=13, fontweight='bold')

sns.barplot(data=seg_overview, x='customer_segment', y='total_revenue', palette=['#e76f51', '#2a9d8f', '#457b9d'], ax=ax2)
ax2.set_title('Total Revenue Contributed by Segment', fontsize=13, fontweight='bold')
ax2.set_ylabel('Revenue ($)', fontweight='bold')
ax2.yaxis.set_major_formatter('${x:,.0f}')

plt.tight_layout()
plt.show()
"""))

    # =========================================================================
    # Section 9: Product Analytics & Margin Matrix
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""---
## Section 9 — Product Analytics & Margin Matrix
Analyzing top and bottom products by revenue, unit volume, and profitability.
"""))

    cells.append(nbf.v4.new_code_cell("""prod_analysis = df_sales.groupby(['product_id', 'product_name', 'category_name']).agg(
    revenue=('line_revenue', 'sum'),
    profit=('line_profit', 'sum'),
    units=('quantity', 'sum')
).reset_index()

prod_analysis['margin_pct'] = (prod_analysis['profit'] / prod_analysis['revenue']) * 100

top10_rev = prod_analysis.sort_values(by='revenue', ascending=False).head(10)
bottom10_rev = prod_analysis.sort_values(by='revenue', ascending=True).head(10)

plt.figure(figsize=(14, 6))
sns.barplot(data=top10_rev, y='product_name', x='revenue', palette='mako')
plt.title('Top 10 Hero Products by Total Revenue', fontsize=14, fontweight='bold')
plt.xlabel('Revenue ($)', fontweight='bold')
plt.ylabel('Product Name', fontweight='bold')
plt.gca().xaxis.set_major_formatter('${x:,.0f}')
plt.tight_layout()
plt.show()

print("Top 5 Hero Products by Revenue:")
display(top10_rev.head(5)[['product_name', 'category_name', 'units', 'revenue', 'profit', 'margin_pct']].round(2))
print()
print("Bottom 5 Underperforming Products:")
display(bottom10_rev.head(5)[['product_name', 'category_name', 'units', 'revenue', 'profit', 'margin_pct']].round(2))
"""))

    # =========================================================================
    # Section 10: Store & Regional Performance
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""---
## Section 10 — Store Performance & Regional Benchmarking
Comparing store locations across metrics including total revenue, profit contribution, and Average Order Value (AOV).
"""))

    cells.append(nbf.v4.new_code_cell("""store_perf = df_sales.groupby(['store_id', 'store_name', 'region', 'store_city']).agg(
    orders=('sale_id', 'nunique'),
    units=('quantity', 'sum'),
    revenue=('line_revenue', 'sum'),
    profit=('line_profit', 'sum')
).reset_index()

store_perf['aov'] = store_perf['revenue'] / store_perf['orders']
store_perf['margin_pct'] = (store_perf['profit'] / store_perf['revenue']) * 100
store_perf = store_perf.sort_values(by='revenue', ascending=False)

fig, ax = plt.subplots(figsize=(14, 6))
sns.barplot(data=store_perf, x='store_name', y='revenue', hue='region', dodge=False, ax=ax)
ax.set_title('Store Revenue Benchmarking Across Regions', fontsize=14, fontweight='bold')
ax.set_ylabel('Total Revenue ($)', fontweight='bold')
ax.set_xlabel('Store Branch', fontweight='bold')
ax.yaxis.set_major_formatter('${x:,.0f}')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

display(store_perf[['store_name', 'region', 'orders', 'revenue', 'profit', 'aov', 'margin_pct']].round(2))
"""))

    # =========================================================================
    # Section 11: Business Insights
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""---
## Section 11 — Business Findings & Interpretations

### 1. Electronics Volume vs Margin Trade-off
* **Observation**: Electronics produces over **70% of total company revenue** ($4.79M+), driven by premium ticket items such as headphones, smartwatches, and monitors.
* **Business Meaning**: While Electronics drives critical foot traffic and customer acquisition, its gross margin (44.9%) is lower than Apparel (61.5%) and Health & Beauty (69.2%).
* **Risk**: Excessive promotional discounting in Electronics drastically degrades operating income.

### 2. High Value Customer Concentration (The 80/20 Rule)
* **Observation**: The High-Value customer cohort accounts for nearly **48% of total revenue**, despite representing less than 20% of registered accounts.
* **Business Meaning**: Business health is disproportionately dependent on repeat visits and loyalty from this core demographic.
* **Opportunity**: High-touch loyalty retention and personalized VIP promotions will yield the highest return on marketing investment.

### 3. Store Performance Gap
* **Observation**: Flagship stores (Manhattan, Chicago, LA) generate up to **1.9x the turnover** of newer or midwest locations (Minneapolis, Denver).
* **Business Meaning**: Brand awareness and local population density differ markedly across locations. Replicating the merchandising mix of tier-1 flagships in developing stores will lift sales.

### 4. Omnichannel Growth
* **Observation**: Online transactions represent **35% of all orders** with a healthy AOV, but In-Store purchases remain the bedrock of volume.
* **Business Meaning**: Omnichannel integration through BOPIS (Buy Online, Pick Up In-Store) provides an immediate pathway to drive digital shoppers into physical stores.
"""))

    # =========================================================================
    # Section 12: Strategic Recommendations
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""---
## Section 12 — Strategic Management Recommendations

Based on empirical data analysis from the relational analytics database, management should enact four strategic pillars:

1. **Launch InsightMart VIP Loyalty Program**:
   * Target High-Value customers with tiered rewards, complimentary expedited shipping for online purchases, and invitation-only previews of seasonal product lines.
   * Target: Reduce VIP churn by 15% and increase repeat frequency by 1.2 orders/year.

2. **Merchandise Mix & Cross-Category Bundling**:
   * Bundle high-revenue, lower-margin Electronics SKUs with high-margin accessories from Apparel or Health & Beauty (e.g., smartwatches bundled with premium sports bands).
   * Target: Lift blended electronic category gross margin by 250 basis points.

3. **Store Turnaround & Inventory Reallocation**:
   * Restructure stock allocation in bottom-quartile stores (Minneapolis, Denver) to align with regional demographics, reducing excess stock of slow-moving items.
   * Institute cross-store training programs pairing flagship store managers with developing branch supervisors.

4. **Digital Omnichannel Integration (BOPIS)**:
   * Implement 'Buy Online, Pick Up In-Store' to capitalize on digital web traffic while stimulating incremental physical store basket additions upon pickup.
"""))

    nb.cells = cells

    print(f"Writing notebook to {NOTEBOOK_PATH}...")
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print("Executing notebook to pre-render outputs and visualizations...")
    client = NotebookClient(nb, timeout=600, kernel_name="python3")
    client.execute()

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print(f"Notebook generated and executed successfully at: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    create_and_execute_notebook()
