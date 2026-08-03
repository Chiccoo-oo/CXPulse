import os
import pandas as pd
import numpy as np

def perform_eda(df):
    """
    Executes Exploratory Data Analysis (EDA) on the cleaned complaints dataset.
    Returns key aggregated statistical metrics.
    """
    print("=== Running Exploratory Data Analysis (EDA) ===")

    total_records = len(df)
    unique_customers = df["customer_id"].nunique()
    overall_escalation_rate = float(df["escalation_flag"].mean() * 100)
    avg_resolution_time = float(df["resolution_time_days"].mean())
    median_resolution_time = float(df["resolution_time_days"].median())
    overall_sla_breach_rate = float(df["sla_breach_flag"].mean() * 100)
    overall_csat = float(df["satisfaction_score"].mean())
    repeat_complaint_rate = float(df["repeat_complaint_flag"].mean() * 100)

    # Product breakdown
    prod_summary = df.groupby("product").agg(
        complaints=("complaint_id", "count"),
        escalations=("escalation_flag", "sum"),
        avg_res_days=("resolution_time_days", "mean"),
        avg_csat=("satisfaction_score", "mean")
    ).reset_index()
    prod_summary["escalation_rate_pct"] = (prod_summary["escalations"] / prod_summary["complaints"]) * 100

    # Channel breakdown
    chan_summary = df.groupby("complaint_channel").agg(
        complaints=("complaint_id", "count"),
        escalations=("escalation_flag", "sum"),
        avg_res_days=("resolution_time_days", "mean")
    ).reset_index()
    chan_summary["escalation_rate_pct"] = (chan_summary["escalations"] / chan_summary["complaints"]) * 100

    metrics = {
        "total_records": total_records,
        "unique_customers": unique_customers,
        "overall_escalation_rate_pct": round(overall_escalation_rate, 2),
        "avg_resolution_time_days": round(avg_resolution_time, 2),
        "median_resolution_time_days": round(median_resolution_time, 2),
        "overall_sla_breach_rate_pct": round(overall_sla_breach_rate, 2),
        "overall_csat": round(overall_csat, 2),
        "repeat_complaint_rate_pct": round(repeat_complaint_rate, 2),
        "product_summary": prod_summary.to_dict(orient="records"),
        "channel_summary": chan_summary.to_dict(orient="records")
    }

    print("EDA completed successfully.")
    return metrics

if __name__ == "__main__":
    df_clean = pd.read_csv("data/processed/cleaned_complaints.csv")
    res = perform_eda(df_clean)
    print("EDA Key Metrics Summary:", res)
