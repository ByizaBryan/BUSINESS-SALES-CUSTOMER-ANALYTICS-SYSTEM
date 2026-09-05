-- ==============================================================================
-- INSIGHTMART BUSINESS SALES & CUSTOMER ANALYTICS SYSTEM
-- Sample Seed Data Script for Standalone Testing
-- Target RDBMS: MySQL 8.0+ / MariaDB 10.5+
-- Database: business_sales_db
-- ==============================================================================

USE business_sales_db;

-- ------------------------------------------------------------------------------
-- 1. Seed CATEGORIES
-- ------------------------------------------------------------------------------
INSERT INTO CATEGORIES (category_id, category_name, description) VALUES
(1, 'Electronics', 'Consumer electronics, personal computing, audio and accessories'),
(2, 'Apparel', 'Men, women, and children clothing, footwear, and fashion accessories'),
(3, 'Home & Kitchen', 'Home appliances, cookware, furniture, and interior decor'),
(4, 'Health & Beauty', 'Personal care, skincare, cosmetics, and wellness products'),
(5, 'Sports & Outdoors', 'Athletic gear, fitness equipment, camping, and outdoor recreation'),
(6, 'Groceries & Gourmet', 'Packaged food, beverages, snacks, and gourmet specialty items');

-- ------------------------------------------------------------------------------
-- 2. Seed SUPPLIERS
-- ------------------------------------------------------------------------------
INSERT INTO SUPPLIERS (supplier_id, supplier_name, contact_information, city) VALUES
(1, 'Apex Tech Distribution', 'contact@apextech.com | +1-555-0101', 'Chicago'),
(2, 'Vanguard Global Brands', 'orders@vanguardgb.com | +1-555-0102', 'New York'),
(3, 'Heritage Home Goods', 'support@heritagehg.com | +1-555-0103', 'Dallas'),
(4, 'Lumina Care & Wellness', 'sales@luminacare.com | +1-555-0104', 'Los Angeles'),
(5, 'Titan Athletics Inc', 'b2b@titanathletics.com | +1-555-0105', 'Seattle'),
(6, 'GreenValley Food Co', 'supply@greenvalleyfood.com | +1-555-0106', 'Denver'),
(7, 'Metro Sound Innovations', 'partner@metrosound.com | +1-555-0107', 'Austin'),
(8, 'Nordic Fabric Works', 'service@nordicfabrics.com | +1-555-0108', 'Boston'),
(9, 'KitchenPro Dynamics', 'sales@kitchenpro.com | +1-555-0109', 'Atlanta'),
(10, 'Zenith Lifestyle Goods', 'info@zenithlife.com | +1-555-0110', 'San Francisco');

-- ------------------------------------------------------------------------------
-- 3. Seed STORES
-- ------------------------------------------------------------------------------
INSERT INTO STORES (store_id, store_name, city, region, opening_date) VALUES
(1, 'InsightMart Downtown Chicago', 'Chicago', 'Midwest', '2021-03-15'),
(2, 'InsightMart Manhattan Flagship', 'New York', 'Northeast', '2020-01-10'),
(3, 'InsightMart Dallas Galleria', 'Dallas', 'South', '2021-07-22'),
(4, 'InsightMart LA Sunset', 'Los Angeles', 'West', '2020-05-18'),
(5, 'InsightMart Seattle Center', 'Seattle', 'Northwest', '2022-02-01'),
(6, 'InsightMart Denver Rockies', 'Denver', 'West', '2022-06-14'),
(7, 'InsightMart Austin Tech Ridge', 'Austin', 'South', '2021-11-05'),
(8, 'InsightMart Boston Back Bay', 'Boston', 'Northeast', '2020-09-30'),
(9, 'InsightMart Atlanta Midtown', 'Atlanta', 'Southeast', '2021-04-12'),
(10, 'InsightMart SF Bay Pavilion', 'San Francisco', 'West', '2020-11-20'),
(11, 'InsightMart Miami Biscayne', 'Miami', 'Southeast', '2022-08-19'),
(12, 'InsightMart Minneapolis Plaza', 'Minneapolis', 'Midwest', '2023-01-15');

-- ------------------------------------------------------------------------------
-- 4. Seed PRODUCTS (Subset for immediate verification)
-- ------------------------------------------------------------------------------
INSERT INTO PRODUCTS (product_id, product_name, category_id, supplier_id, unit_cost, selling_price, stock_quantity, reorder_level, status) VALUES
(1, 'UltraWireless Noise-Cancelling Headphones', 1, 1, 95.00, 199.99, 140, 25, 'Active'),
(2, 'SmartWatch Pro Series 5', 1, 7, 120.00, 249.50, 95, 20, 'Active'),
(3, 'Bluetooth Ergonomic Mechanical Keyboard', 1, 1, 45.00, 89.99, 210, 30, 'Active'),
(4, '4K UltraHD Streaming Dongle', 1, 7, 18.50, 39.99, 300, 50, 'Active'),
(5, 'Premium Merino Wool Crewneck', 2, 2, 32.00, 78.00, 180, 25, 'Active'),
(6, 'Slim-Fit Stretch Denim Jeans', 2, 8, 22.50, 59.99, 240, 40, 'Active'),
(7, 'Weatherproof All-Season Parka', 2, 2, 75.00, 165.00, 70, 15, 'Active'),
(8, 'Breathable Athletic Performance Tee', 2, 8, 9.50, 24.99, 450, 60, 'Active'),
(9, 'Stainless Steel Espresso Machine', 3, 9, 110.00, 229.00, 65, 15, 'Active'),
(10, 'Tri-Ply Clad Non-Stick Cookware Set', 3, 3, 68.00, 149.99, 85, 20, 'Active'),
(11, 'Smart Multi-Speed Air Purifier', 3, 3, 55.00, 119.50, 120, 25, 'Active'),
(12, 'Cast Iron Dutch Oven 6-Qt', 3, 9, 28.00, 64.99, 130, 20, 'Active'),
(13, 'Hydrating Vitamin C Facial Serum', 4, 4, 11.00, 28.50, 320, 50, 'Active'),
(14, 'Botanical Cleansing Facial Oil', 4, 4, 8.50, 22.00, 280, 40, 'Active'),
(15, 'Sonic Electric Toothbrush Elite', 4, 10, 26.00, 69.99, 190, 30, 'Active'),
(16, 'Mineral SPF 50 Broad Spectrum Lotion', 4, 4, 7.00, 18.50, 400, 60, 'Active'),
(17, 'Pro-Grip Anti-Slip Yoga Mat', 5, 5, 14.00, 34.99, 220, 35, 'Active'),
(18, 'High-Density Foam Roller 36-Inch', 5, 5, 9.00, 22.50, 160, 25, 'Active'),
(19, 'Insulated Stainless Hydration Flask 32oz', 5, 10, 11.50, 27.99, 310, 40, 'Active'),
(20, 'Organic Single-Origin Roast Coffee Beans', 6, 6, 6.20, 15.99, 500, 75, 'Active');

-- ------------------------------------------------------------------------------
-- 5. Seed CUSTOMERS (Representative sample across segments)
-- ------------------------------------------------------------------------------
INSERT INTO CUSTOMERS (customer_id, first_name, last_name, gender, date_of_birth, customer_segment, city, registration_date) VALUES
(1, 'James', 'Wilson', 'Male', '1985-04-12', 'High Value', 'Chicago', '2023-01-10'),
(2, 'Sarah', 'Jenkins', 'Female', '1992-08-25', 'High Value', 'New York', '2023-02-14'),
(3, 'Michael', 'Chang', 'Male', '1988-11-03', 'Medium Value', 'San Francisco', '2023-03-01'),
(4, 'Emily', 'Rodriguez', 'Female', '1995-02-19', 'Medium Value', 'Dallas', '2023-03-18'),
(5, 'David', 'Kim', 'Male', '1990-07-30', 'Low Value', 'Seattle', '2023-04-05'),
(6, 'Jessica', 'Taylor', 'Female', '1983-09-14', 'High Value', 'Boston', '2023-04-22'),
(7, 'Robert', 'Martinez', 'Male', '1979-12-05', 'Medium Value', 'Austin', '2023-05-11'),
(8, 'Amanda', 'Brown', 'Female', '1994-06-18', 'Low Value', 'Denver', '2023-05-29'),
(9, 'Daniel', 'White', 'Male', '1987-03-22', 'High Value', 'Atlanta', '2023-06-15'),
(10, 'Olivia', 'Harris', 'Female', '1996-10-09', 'Medium Value', 'Los Angeles', '2023-07-01'),
(11, 'William', 'Clark', 'Male', '1982-01-17', 'Low Value', 'Miami', '2023-07-20'),
(12, 'Sophia', 'Lewis', 'Female', '1991-05-27', 'High Value', 'Chicago', '2023-08-08'),
(13, 'Ethan', 'Walker', 'Male', '1989-09-02', 'Medium Value', 'Minneapolis', '2023-08-25'),
(14, 'Isabella', 'Hall', 'Female', '1993-12-14', 'Low Value', 'New York', '2023-09-12'),
(15, 'Alexander', 'Allen', 'Male', '1986-07-08', 'High Value', 'Seattle', '2023-10-03');

-- ------------------------------------------------------------------------------
-- 6. Seed SALES (Representative sample)
-- ------------------------------------------------------------------------------
INSERT INTO SALES (sale_id, sale_date, customer_id, store_id, payment_method, sales_channel) VALUES
(1, '2024-01-05', 1, 1, 'Credit Card', 'In-Store'),
(2, '2024-01-08', 2, 2, 'Credit Card', 'Online'),
(3, '2024-01-15', 3, 10, 'Digital Wallet', 'In-Store'),
(4, '2024-01-20', 4, 3, 'Debit Card', 'In-Store'),
(5, '2024-02-02', 6, 8, 'Credit Card', 'Online'),
(6, '2024-02-14', 1, 1, 'Credit Card', 'In-Store'),
(7, '2024-02-22', 7, 7, 'Digital Wallet', 'In-Store'),
(8, '2024-03-05', 9, 9, 'Credit Card', 'In-Store'),
(9, '2024-03-12', 2, 2, 'Debit Card', 'In-Store'),
(10, '2024-03-25', 12, 1, 'Credit Card', 'Online'),
(11, '2024-04-03', 15, 5, 'Credit Card', 'In-Store'),
(12, '2024-04-18', 3, 10, 'Digital Wallet', 'Online'),
(13, '2024-05-06', 10, 4, 'Credit Card', 'In-Store'),
(14, '2024-05-20', 1, 1, 'Credit Card', 'In-Store'),
(15, '2024-06-01', 6, 8, 'Debit Card', 'In-Store');

-- ------------------------------------------------------------------------------
-- 7. Seed SALE_ITEMS (Line items with quantity, price, discount)
-- ------------------------------------------------------------------------------
INSERT INTO SALE_ITEMS (sale_item_id, sale_id, product_id, quantity, unit_price, discount) VALUES
(1, 1, 1, 1, 199.99, 10.00),
(2, 1, 3, 1, 89.99, 0.00),
(3, 2, 2, 1, 249.50, 20.00),
(4, 2, 8, 2, 24.99, 5.00),
(5, 3, 5, 2, 78.00, 0.00),
(6, 3, 13, 1, 28.50, 0.00),
(7, 4, 9, 1, 229.00, 15.00),
(8, 5, 1, 1, 199.99, 0.00),
(9, 5, 17, 1, 34.99, 0.00),
(10, 6, 7, 1, 165.00, 25.00),
(11, 6, 6, 1, 59.99, 0.00),
(12, 7, 10, 1, 149.99, 10.00),
(13, 8, 15, 2, 69.99, 10.00),
(14, 9, 11, 1, 119.50, 0.00),
(15, 10, 9, 1, 229.00, 20.00),
(16, 10, 20, 3, 15.99, 0.00),
(17, 11, 2, 1, 249.50, 0.00),
(18, 12, 1, 1, 199.99, 15.00),
(19, 13, 13, 2, 28.50, 0.00),
(20, 14, 19, 2, 27.99, 0.00),
(21, 15, 5, 1, 78.00, 0.00);
