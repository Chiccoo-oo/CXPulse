import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def perform_customer_segmentation(df, n_clusters=4, random_state=42):
    """
    Executes K-Means Clustering on customer-level aggregated features.
    Features: monthly_spend, tenure, transaction_frequency, complaint_count, avg_res_time, escalation_rate.
    """
    print("=== Running K-Means Customer Segmentation ===")

    # Customer-level aggregation
    cust_df = df.groupby("customer_id").agg(
        segment=("customer_segment", "first"),
        monthly_spend=("monthly_spend", "first"),
        tenure_months=("account_tenure_months", "first"),
        transaction_freq=("transaction_frequency", "first"),
        complaint_count=("complaint_id", "count"),
        avg_res_time=("resolution_time_days", "mean"),
        escalation_count=("escalation_flag", "sum"),
        avg_csat=("satisfaction_score", "mean")
    ).reset_index()

    cust_df["escalation_rate"] = cust_df["escalation_count"] / cust_df["complaint_count"]

    feature_cols = ["monthly_spend", "tenure_months", "transaction_freq", "complaint_count", "avg_res_time", "escalation_rate"]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(cust_df[feature_cols])

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    cust_df["cluster_id"] = kmeans.fit_predict(X_scaled)

    # Name clusters based on centroid characteristics
    cluster_means = cust_df.groupby("cluster_id")[feature_cols + ["avg_csat"]].mean()

    cluster_name_map = {}
    for cid in range(n_clusters):
        row = cluster_means.loc[cid]
        if row["monthly_spend"] > cust_df["monthly_spend"].median() and row["avg_csat"] < 3.0:
            cluster_name_map[cid] = "High-Value Dissatisfied (Priority At-Risk)"
        elif row["complaint_count"] > 1.3:
            cluster_name_map[cid] = "Frequent Complainants (High Touch)"
        elif row["tenure_months"] < 24:
            cluster_name_map[cid] = "New Customer Onboarding Issues"
        else:
            cluster_name_map[cid] = "Standard Low-Risk Complainant"

    # Handle duplicates if naming overlap occurs
    seen = {}
    final_names = {}
    for cid, name in cluster_name_map.items():
        if name in seen:
            seen[name] += 1
            final_names[cid] = f"{name} Tier {seen[name]}"
        else:
            seen[name] = 1
            final_names[cid] = name

    cust_df["cluster_name"] = cust_df["cluster_id"].map(final_names)

    # Merge cluster names back into main complaint dataset
    df_segmented = df.merge(cust_df[["customer_id", "cluster_id", "cluster_name"]], on="customer_id", how="left")

    summary_df = cust_df.groupby("cluster_name").agg(
        customer_count=("customer_id", "count"),
        avg_spend=("monthly_spend", "mean"),
        avg_tenure=("tenure_months", "mean"),
        avg_complaints=("complaint_count", "mean"),
        avg_resolution_days=("avg_res_time", "mean"),
        avg_csat=("avg_csat", "mean")
    ).reset_index()

    print("Customer Segmentation completed.")
    return df_segmented, summary_df

if __name__ == "__main__":
    df_clean = pd.read_csv("data/processed/cleaned_complaints.csv")
    df_seg, summary = perform_customer_segmentation(df_clean)
    print("Cluster Summary:\n", summary)
