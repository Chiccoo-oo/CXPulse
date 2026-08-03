-- CXPulse Analytical Warehouse Schema (Star Schema for Financial Complaints & Servicing Analytics)
-- Optimized for SQLite & ANSI SQL / PostgreSQL Syntax Compatibility

-- Drop existing tables if re-initialising
DROP TABLE IF EXISTS fact_complaints;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS dim_geography;
DROP TABLE IF EXISTS dim_date;

-- Dimension 1: Customer Dimension
CREATE TABLE dim_customer (
    customer_id VARCHAR(30) PRIMARY KEY,
    customer_segment VARCHAR(50) NOT NULL,
    customer_age INT CHECK (customer_age >= 18),
    account_tenure_months INT CHECK (account_tenure_months >= 0),
    transaction_frequency INT,
    monthly_spend DECIMAL(12, 2)
);

-- Dimension 2: Product Hierarchy Dimension
CREATE TABLE dim_product (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name VARCHAR(50) NOT NULL,
    sub_product_name VARCHAR(100) NOT NULL,
    issue_category VARCHAR(100) NOT NULL,
    sub_issue VARCHAR(150) NOT NULL
);

-- Dimension 3: Servicing Channel Dimension
CREATE TABLE dim_channel (
    channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_name VARCHAR(50) UNIQUE NOT NULL
);

-- Dimension 4: Geography Dimension
CREATE TABLE dim_geography (
    geography_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name VARCHAR(50) UNIQUE NOT NULL
);

-- Dimension 5: Date Dimension
CREATE TABLE dim_date (
    date_key VARCHAR(10) PRIMARY KEY, -- YYYY-MM-DD
    full_date DATE NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(15) NOT NULL,
    day_of_month INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(15) NOT NULL,
    is_weekend INT NOT NULL
);

-- Fact Table: Complaint Servicing Fact
CREATE TABLE fact_complaints (
    complaint_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(30) NOT NULL,
    product_id INT NOT NULL,
    channel_id INT NOT NULL,
    geography_id INT NOT NULL,
    complaint_date TIMESTAMP NOT NULL,
    response_date TIMESTAMP,
    resolution_date TIMESTAMP,
    resolution_time_days DECIMAL(8, 2),
    sla_breach_flag INT NOT NULL CHECK (sla_breach_flag IN (0, 1)),
    resolution_status VARCHAR(50),
    resolution_type VARCHAR(50),
    escalation_flag INT NOT NULL CHECK (escalation_flag IN (0, 1)),
    repeat_complaint_flag INT NOT NULL CHECK (repeat_complaint_flag IN (0, 1)),
    satisfaction_score DECIMAL(3, 1),
    agent_team VARCHAR(50),
    complaint_text TEXT,
    severity_level VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (channel_id) REFERENCES dim_channel(channel_id),
    FOREIGN KEY (geography_id) REFERENCES dim_geography(geography_id)
);

-- Performance Analytical Indexes
CREATE INDEX idx_fact_cust ON fact_complaints(customer_id);
CREATE INDEX idx_fact_date ON fact_complaints(complaint_date);
CREATE INDEX idx_fact_prod ON fact_complaints(product_id);
CREATE INDEX idx_fact_channel ON fact_complaints(channel_id);
CREATE INDEX idx_fact_escalation ON fact_complaints(escalation_flag);
CREATE INDEX idx_fact_sla ON fact_complaints(sla_breach_flag);
