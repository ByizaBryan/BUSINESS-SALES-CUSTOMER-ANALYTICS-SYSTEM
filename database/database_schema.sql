-- ==============================================================================
-- INSIGHTMART BUSINESS SALES & CUSTOMER ANALYTICS SYSTEM
-- Relational Database Schema Definition (3NF Normalized)
-- Target RDBMS: MySQL 8.0+ / MariaDB 10.5+
-- Database: business_sales_db
-- ==============================================================================

-- 1. Database Initialization
CREATE DATABASE IF NOT EXISTS business_sales_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE business_sales_db;

-- 2. Drop existing tables in reverse dependency order
DROP TABLE IF EXISTS SALE_ITEMS;
DROP TABLE IF EXISTS SALES;
DROP TABLE IF EXISTS PRODUCTS;
DROP TABLE IF EXISTS CUSTOMERS;
DROP TABLE IF EXISTS STORES;
DROP TABLE IF EXISTS SUPPLIERS;
DROP TABLE IF EXISTS CATEGORIES;

-- ==============================================================================
-- 3. Table Creation with Primary Keys, Foreign Keys, Constraints & Indexes
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Table: CATEGORIES
-- Business Purpose: Groups products into high-level merchandise departments
-- ------------------------------------------------------------------------------
CREATE TABLE CATEGORIES (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- Table: SUPPLIERS
-- Business Purpose: Maintains vendor directory for inventory replenishment & procurement
-- ------------------------------------------------------------------------------
CREATE TABLE SUPPLIERS (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    contact_information VARCHAR(100),
    city VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- Table: PRODUCTS
-- Business Purpose: Central product catalog containing pricing, cost, and stock inventory
-- ------------------------------------------------------------------------------
CREATE TABLE PRODUCTS (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,
    supplier_id INT NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL CHECK (unit_cost >= 0),
    selling_price DECIMAL(10, 2) NOT NULL CHECK (selling_price >= unit_cost),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    reorder_level INT NOT NULL DEFAULT 15 CHECK (reorder_level >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES CATEGORIES (category_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id) REFERENCES SUPPLIERS (supplier_id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_products_category ON PRODUCTS(category_id);
CREATE INDEX idx_products_supplier ON PRODUCTS(supplier_id);
CREATE INDEX idx_products_status ON PRODUCTS(status);

-- ------------------------------------------------------------------------------
-- Table: CUSTOMERS
-- Business Purpose: Customer master records, demographic information, and segmentation
-- ------------------------------------------------------------------------------
CREATE TABLE CUSTOMERS (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    gender VARCHAR(10),
    date_of_birth DATE,
    customer_segment VARCHAR(30) NOT NULL,
    city VARCHAR(50) NOT NULL,
    registration_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE INDEX idx_customers_segment ON CUSTOMERS(customer_segment);
CREATE INDEX idx_customers_city ON CUSTOMERS(city);
CREATE INDEX idx_customers_regdate ON CUSTOMERS(registration_date);

-- ------------------------------------------------------------------------------
-- Table: STORES
-- Business Purpose: InsightMart retail branch locations and geographic regions
-- ------------------------------------------------------------------------------
CREATE TABLE STORES (
    store_id INT AUTO_INCREMENT PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    region VARCHAR(30) NOT NULL,
    opening_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE INDEX idx_stores_region ON STORES(region);
CREATE INDEX idx_stores_city ON STORES(city);

-- ------------------------------------------------------------------------------
-- Table: SALES
-- Business Purpose: Transaction header records representing a checkout order
-- ------------------------------------------------------------------------------
CREATE TABLE SALES (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_date DATE NOT NULL,
    customer_id INT NOT NULL,
    store_id INT NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    sales_channel VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sales_customer FOREIGN KEY (customer_id) REFERENCES CUSTOMERS (customer_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_sales_store FOREIGN KEY (store_id) REFERENCES STORES (store_id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_sales_date ON SALES(sale_date);
CREATE INDEX idx_sales_customer ON SALES(customer_id);
CREATE INDEX idx_sales_store ON SALES(store_id);
CREATE INDEX idx_sales_channel ON SALES(sales_channel);
CREATE INDEX idx_sales_payment ON SALES(payment_method);

-- ------------------------------------------------------------------------------
-- Table: SALE_ITEMS
-- Business Purpose: Line item details for each sale, tracking product, quantity & discount
-- ------------------------------------------------------------------------------
CREATE TABLE SALE_ITEMS (
    sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    discount DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (discount >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sale_items_sale FOREIGN KEY (sale_id) REFERENCES SALES (sale_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_sale_items_product FOREIGN KEY (product_id) REFERENCES PRODUCTS (product_id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_sale_items_sale ON SALE_ITEMS(sale_id);
CREATE INDEX idx_sale_items_product ON SALE_ITEMS(product_id);

-- ==============================================================================
-- 4. Analytical View: VIEW_SALES_PERFORMANCE
-- Denormalized view computing line-item Revenue, Cost, Profit, and Profit Margin
-- ==============================================================================
CREATE OR REPLACE VIEW view_sales_performance AS
SELECT 
    si.sale_item_id,
    s.sale_id,
    s.sale_date,
    s.sales_channel,
    s.payment_method,
    st.store_id,
    st.store_name,
    st.region,
    st.city AS store_city,
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.customer_segment,
    c.city AS customer_city,
    p.product_id,
    p.product_name,
    cat.category_id,
    cat.category_name,
    sup.supplier_name,
    si.quantity,
    si.unit_price,
    si.discount,
    p.unit_cost,
    -- Financial Business Metrics
    ROUND((si.quantity * si.unit_price) - si.discount, 2) AS line_revenue,
    ROUND(si.quantity * p.unit_cost, 2) AS line_cost,
    ROUND(((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost), 2) AS line_profit,
    ROUND(
        CASE 
            WHEN ((si.quantity * si.unit_price) - si.discount) > 0 
            THEN ((((si.quantity * si.unit_price) - si.discount) - (si.quantity * p.unit_cost)) / ((si.quantity * si.unit_price) - si.discount)) * 100 
            ELSE 0 
        END, 
    2) AS profit_margin_pct
FROM SALE_ITEMS si
INNER JOIN SALES s ON si.sale_id = s.sale_id
INNER JOIN PRODUCTS p ON si.product_id = p.product_id
INNER JOIN CATEGORIES cat ON p.category_id = cat.category_id
INNER JOIN SUPPLIERS sup ON p.supplier_id = sup.supplier_id
INNER JOIN CUSTOMERS c ON s.customer_id = c.customer_id
INNER JOIN STORES st ON s.store_id = st.store_id;
