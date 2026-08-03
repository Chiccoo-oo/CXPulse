import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from src.data_generator import generate_synthetic_complaints

def run_data_pipeline(raw_csv_path="data/raw/raw_complaints.csv", db_path="data/processed/cxpulse.db"):
    """
    Validates, cleans, transforms raw complaint data and loads into SQLite analytical warehouse.
    Idempotent execution support for existing tables.
    """
    print("=== Starting CXPulse Data Pipeline ===")
    
    # Step 1: Check or Generate Raw Data
    if not os.path.exists(raw_csv_path):
        print(f"Raw data file not found at {raw_csv_path}. Generating dataset...")
        df_raw = generate_synthetic_complaints(num_records=50000)
    else:
        print(f"Loading raw data from {raw_csv_path}...")
        df_raw = pd.read_csv(raw_csv_path)

    print(f"Loaded raw records: {len(df_raw)}")

    # Step 2: Data Cleaning & Standardisation
    df_clean = df_raw.copy()

    # Normalize casing in categorical fields
    df_clean["complaint_channel"] = df_clean["complaint_channel"].str.strip().str.title()
    df_clean["product"] = df_clean["product"].str.strip()
    df_clean["issue"] = df_clean["issue"].str.strip()

    # Fill missing values
    df_clean["complaint_text"] = df_clean["complaint_text"].fillna("No complaint narrative provided.")
    
    # Impute missing satisfaction scores with median by resolution status
    sat_medians = df_clean.groupby("resolution_status")["satisfaction_score"].transform("median")
    df_clean["satisfaction_score"] = df_clean["satisfaction_score"].fillna(sat_medians).fillna(3.0)

    # Date parsing and transformation
    df_clean["complaint_date"] = pd.to_datetime(df_clean["complaint_date"])
    df_clean["resolution_date"] = pd.to_datetime(df_clean["resolution_date"])
    df_clean["response_date"] = pd.to_datetime(df_clean["response_date"])

    # Calculate SLA metrics: resolution_time_days
    res_time = (df_clean["resolution_date"] - df_clean["complaint_date"]).dt.total_seconds() / 86400.0
    df_clean["resolution_time_days"] = np.round(res_time, 2)

    # Standard SLA limit = 5 business days
    df_clean["sla_breach_flag"] = (df_clean["resolution_time_days"] > 5.0).astype(int)

    # Detect Repeat Complaints per Customer (if customer filed > 1 complaint within 90 days)
    df_clean = df_clean.sort_values(by=["customer_id", "complaint_date"])
    df_clean["prev_complaint_date"] = df_clean.groupby("customer_id")["complaint_date"].shift(1)
    days_since_prev = (df_clean["complaint_date"] - df_clean["prev_complaint_date"]).dt.days
    df_clean["repeat_complaint_flag"] = ((days_since_prev.notna()) & (days_since_prev <= 90)).astype(int)
    df_clean.drop(columns=["prev_complaint_date"], inplace=True)

    # Severity Level Business Logic
    def assign_severity(row):
        if row["escalation_flag"] == 1 and row["sla_breach_flag"] == 1:
            return "CRITICAL"
        elif row["escalation_flag"] == 1 or row["repeat_complaint_flag"] == 1 or row["issue"] == "Fraud & Unauthorized Transaction":
            return "HIGH"
        elif row["resolution_time_days"] > 4.0:
            return "MEDIUM"
        else:
            return "LOW"

    df_clean["severity_level"] = df_clean.apply(assign_severity, axis=1)

    # Save cleaned dataset
    processed_dir = os.path.dirname(db_path)
    os.makedirs(processed_dir, exist_ok=True)
    cleaned_csv = os.path.join(processed_dir, "cleaned_complaints.csv")
    df_clean.to_csv(cleaned_csv, index=False)
    print(f"Cleaned dataset saved to {cleaned_csv} ({len(df_clean)} records).")

    # Step 3: Populate SQLite Star Schema Database
    print(f"Initializing SQLite database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Load DDL schema
    schema_file = os.path.join("sql", "schema.sql")
    with open(schema_file, "r") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    # Insert Dimension: dim_customer
    dim_cust = df_clean[["customer_id", "customer_segment", "customer_age", "account_tenure_months", "transaction_frequency", "monthly_spend"]].drop_duplicates(subset=["customer_id"])
    dim_cust.to_sql("dim_customer", conn, if_exists="append", index=False)

    # Insert Dimension: dim_product
    dim_prod = df_clean[["product", "sub_product", "issue", "sub_issue"]].drop_duplicates()
    dim_prod.columns = ["product_name", "sub_product_name", "issue_category", "sub_issue"]
    dim_prod.to_sql("dim_product", conn, if_exists="append", index=False)

    # Fetch dim_product auto-assigned IDs
    dim_prod_db = pd.read_sql("SELECT product_id, product_name, sub_product_name, issue_category, sub_issue FROM dim_product", conn)

    # Insert Dimension: dim_channel
    dim_chan = pd.DataFrame({"channel_name": df_clean["complaint_channel"].unique()})
    dim_chan.to_sql("dim_channel", conn, if_exists="append", index=False)
    dim_chan_db = pd.read_sql("SELECT channel_id, channel_name FROM dim_channel", conn)

    # Insert Dimension: dim_geography
    dim_geo = pd.DataFrame({"region_name": df_clean["geography"].unique()})
    dim_geo.to_sql("dim_geography", conn, if_exists="append", index=False)
    dim_geo_db = pd.read_sql("SELECT geography_id, region_name FROM dim_geography", conn)

    # Insert Dimension: dim_date
    df_clean["date_key"] = df_clean["complaint_date"].dt.strftime("%Y-%m-%d")
    unique_dates = df_clean["complaint_date"].dt.normalize().drop_duplicates().sort_values()
    
    date_rows = []
    for d in unique_dates:
        date_rows.append({
            "date_key": d.strftime("%Y-%m-%d"),
            "full_date": d.strftime("%Y-%m-%d"),
            "year": d.year,
            "quarter": d.quarter,
            "month": d.month,
            "month_name": d.strftime("%B"),
            "day_of_month": d.day,
            "day_of_week": d.dayofweek + 1,
            "day_name": d.strftime("%A"),
            "is_weekend": 1 if d.dayofweek >= 5 else 0
        })
    dim_date_df = pd.DataFrame(date_rows)
    dim_date_df.to_sql("dim_date", conn, if_exists="append", index=False)

    # Map surrogate keys onto Fact table
    df_fact = df_clean.merge(dim_prod_db, left_on=["product", "sub_product", "issue", "sub_issue"], right_on=["product_name", "sub_product_name", "issue_category", "sub_issue"])
    df_fact = df_fact.merge(dim_chan_db, left_on="complaint_channel", right_on="channel_name")
    df_fact = df_fact.merge(dim_geo_db, left_on="geography", right_on="region_name")

    fact_cols = [
        "complaint_id", "customer_id", "product_id", "channel_id", "geography_id",
        "complaint_date", "response_date", "resolution_date", "resolution_time_days",
        "sla_breach_flag", "resolution_status", "resolution_type", "escalation_flag",
        "repeat_complaint_flag", "satisfaction_score", "agent_team", "complaint_text", "severity_level"
    ]
    df_fact_insert = df_fact[fact_cols].copy()
    
    # Convert datetime objects to string for SQLite insertion
    df_fact_insert["complaint_date"] = df_fact_insert["complaint_date"].astype(str)
    df_fact_insert["response_date"] = df_fact_insert["response_date"].astype(str)
    df_fact_insert["resolution_date"] = df_fact_insert["resolution_date"].astype(str)

    df_fact_insert.to_sql("fact_complaints", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

    print(f"Data Pipeline completed successfully! Database populated with {len(df_fact_insert)} fact rows.")
    return df_clean

if __name__ == "__main__":
    run_data_pipeline()
