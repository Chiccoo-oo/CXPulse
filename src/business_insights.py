import pandas as pd
import numpy as np

def generate_business_insights(df):
    """
    Programmatically calculates quantitative business insights & actionable recommendations
    from empirical complaints data.
    """
    total = len(df)
    
    # 1. Product disparity insight
    prod_counts = df["product"].value_counts(normalize=True) * 100
    top_prod = prod_counts.index[0]
    top_prod_pct = prod_counts.iloc[0]

    # 2. Escalation driver insight
    esc_by_issue = df.groupby("issue")["escalation_flag"].mean() * 100
    top_esc_issue = esc_by_issue.idxmax()
    top_esc_val = esc_by_issue.max()

    # 3. SLA breach driver insight
    sla_by_channel = df.groupby("complaint_channel")["sla_breach_flag"].mean() * 100
    worst_channel = sla_by_channel.idxmax()
    worst_channel_sla = sla_by_channel.max()

    # 4. CSAT impact insight
    csat_esc = df[df["escalation_flag"] == 1]["satisfaction_score"].mean()
    csat_non_esc = df[df["escalation_flag"] == 0]["satisfaction_score"].mean()
    csat_drop = csat_non_esc - csat_esc

    insights = [
        f"Product Concentration: '{top_prod}' accounts for {top_prod_pct:.1f}% of total complaint volume across servicing channels.",
        f"Escalation Risk Driver: Issue category '{top_esc_issue}' exhibits the highest escalation rate at {top_esc_val:.1f}%.",
        f"Servicing SLA Bottleneck: Channel '{worst_channel}' has the highest SLA breach rate at {worst_channel_sla:.1f}%, indicating operational workflow friction.",
        f"Customer Satisfaction Impact: Escalated complaints suffer a {csat_drop:.2f}-point drop in CSAT (Average CSAT: {csat_esc:.2f} vs {csat_non_esc:.2f} for non-escalated)."
    ]

    recommendations = [
        f"Prioritize Tier-2 Escalation Intervention for '{top_esc_issue}': Implement real-time routing to specialized servicing teams to prevent escalation.",
        f"Streamline Channel Fulfillment for '{worst_channel}': Conduct workflow audit and increase staffing during peak hours to reduce SLA breach rate below target 5%.",
        f"Proactive Outreach for Repeat Complainants: Deploy dedicated resolution managers for customers with >= 2 complaints within 90 days to protect customer lifetime value.",
        f"Digital Dispute Tool Optimization: Enhance self-service dispute resolution capabilities in the Mobile App to intercept billing disputes before phone escalation."
    ]

    return {
        "key_insights": insights,
        "recommended_actions": recommendations
    }

if __name__ == "__main__":
    df_clean = pd.read_csv("data/processed/cleaned_complaints.csv")
    res = generate_business_insights(df_clean)
    print("Insights:", res["key_insights"])
    print("\nRecommendations:", res["recommended_actions"])
