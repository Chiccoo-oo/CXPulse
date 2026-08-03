import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_synthetic_complaints(num_records=50000, seed=42):
    """
    Generates a realistic synthetic customer complaints and servicing dataset for CXPulse.
    50,000 complaint records spanning 24 months with realistic business relationships.
    """
    np.random.seed(seed)
    random.seed(seed)

    print(f"Generating {num_records} synthetic complaint records...")

    # Unique customers (some submit multiple complaints to simulate repeat complainants)
    num_customers = int(num_records * 0.65) # ~32,500 unique customers
    customer_ids = [f"CUST-{10000 + i}" for i in range(num_customers)]
    
    # Pre-assign customer demography
    customer_segments = ["Mass Market", "Emerging Wealth", "High Net Worth", "Premium Cardholder", "Small Business"]
    segment_weights = [0.45, 0.25, 0.10, 0.15, 0.05]
    
    geographies = ["Northeast", "Southeast", "Midwest", "Southwest", "West Coast"]
    geo_weights = [0.25, 0.30, 0.15, 0.15, 0.15]
    
    customer_pool = {}
    for cid in customer_ids:
        seg = np.random.choice(customer_segments, p=segment_weights)
        geo = np.random.choice(geographies, p=geo_weights)
        age = int(np.random.normal(42, 14))
        age = max(18, min(85, age))
        tenure = int(np.random.exponential(48)) + 1
        tenure = min(360, tenure)
        
        # Monthly spend varies by segment
        if seg == "High Net Worth":
            spend = np.random.normal(12000, 3500)
        elif seg == "Premium Cardholder":
            spend = np.random.normal(6500, 2000)
        elif seg == "Small Business":
            spend = np.random.normal(8500, 3000)
        elif seg == "Emerging Wealth":
            spend = np.random.normal(3500, 1000)
        else:
            spend = np.random.normal(1800, 600)
        spend = max(200.0, round(float(spend), 2))
        
        txn_freq = int(max(3, np.random.poisson(spend / 150)))
        
        customer_pool[cid] = {
            "segment": seg,
            "geography": geo,
            "age": age,
            "tenure": tenure,
            "monthly_spend": spend,
            "transaction_frequency": txn_freq
        }

    # Products & Issues hierarchy
    product_issues = {
        "Credit Card": {
            "sub_products": ["Platinum Rewards Card", "Cash Back Preferred", "Travel Elite Card", "Basic Credit Card"],
            "issues": [
                ("Billing & Fee Dispute", ["Annual fee charged unexpectedly", "Late fee charged despite on-time payment", "Autopay processing error"]),
                ("Fraud & Unauthorized Transaction", ["Unrecognized charge at foreign merchant", "Card cloned at gas station", "Phishing transaction alert"]),
                ("Rewards Redemption Failure", ["Points failed to credit after promotion", "Travel portal booking error", "Cashback balance calculation error"]),
                ("Interest Rate Dispute", ["APR increased without prior notification", "Interest charged during promotional 0% period", "Balance transfer fee dispute"]),
                ("Credit Line Decrease", ["Credit limit reduced without clear reason", "Requested limit increase denied", "Credit score drop notification error"])
            ]
        },
        "Personal Loans": {
            "sub_products": ["Unsecured Fixed Loan", "Debt Consolidation Loan", "Emergency Express Loan"],
            "issues": [
                ("Interest Rate Dispute", ["APR miscalculated on installment schedule", "Prepayment penalty charged unfairly", "Variable rate increase dispute"]),
                ("Billing & Fee Dispute", ["Origination fee incorrectly applied", "Direct debit pulled twice", "Payment processing delay causing late status"]),
                ("Loan Payoff & Closing", ["Payoff quote expired early", "Title release delayed post payment", "Overpayment refund check not received"])
            ]
        },
        "Savings Account": {
            "sub_products": ["High Yield Savings", "Certificate of Deposit (CD)", "Money Market Account"],
            "issues": [
                ("Interest Rate Dispute", ["Promotional APY rate dropped early", "Interest payout missing for month", "Tiered balance APY threshold issue"]),
                ("Transfer & Withdrawal Limits", ["Wire transfer held for security review", "ACH transfer failed without notification", "CD early withdrawal penalty error"]),
                ("Account Maintenance", ["Monthly maintenance fee assessed despite minimum balance", "Joint owner addition delayed", "Paper statement fee dispute"])
            ]
        },
        "Digital Banking": {
            "sub_products": ["Mobile App iOS", "Mobile App Android", "Web Online Portal"],
            "issues": [
                ("Mobile App Access/Outage", ["App crashing upon biometric login", "Two-factor authentication SMS delayed", "Session timeout during transfer"]),
                ("Digital Dispute Tool Error", ["Dispute submission button unresponsive", "Document upload failing for chargeback", "Status tracker not updating"]),
                ("Security & Credentials", ["Account locked after password reset", "Device registration loop error", "Unrecognized login security alert"])
            ]
        }
    }

    product_weights = [0.50, 0.15, 0.15, 0.20] # Credit Card is 50%
    products_list = list(product_issues.keys())
    
    channels = ["Mobile App", "Web Portal", "Phone / Contact Center", "Branch", "Written / Mail"]
    channel_weights = [0.35, 0.30, 0.25, 0.06, 0.04]
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range_days = (end_date - start_date).days

    teams = ["Tier 1 General", "Tier 2 Escalations", "Fraud Ops", "Billing Services", "Digital Tech Support"]

    rows = []
    # Create customer assignment sequence with repeat complaints
    # Select customer IDs with replacement (some customers get multiple complaints)
    chosen_customer_ids = np.random.choice(customer_ids, size=num_records, replace=True)

    for i in range(num_records):
        cid = chosen_customer_ids[i]
        c_info = customer_pool[cid]
        
        comp_id = f"CXP-2024-{i+1:05d}"
        
        # Complaint Date with some seasonality (peaks in Q4 holidays & Jan billing)
        day_offset = int(np.random.uniform(0, date_range_days))
        comp_date = start_date + timedelta(days=day_offset, hours=random.randint(8, 20), minutes=random.randint(0, 59))
        
        prod = np.random.choice(products_list, p=product_weights)
        prod_data = product_issues[prod]
        sub_prod = random.choice(prod_data["sub_products"])
        
        issue_tuple = random.choice(prod_data["issues"])
        issue_cat = issue_tuple[0]
        sub_issue = random.choice(issue_tuple[1])
        
        channel = np.random.choice(channels, p=channel_weights)
        
        # Complaint Text Narrative Generation
        templates = [
            f"I am writing regarding my {sub_prod} account. I encountered a severe {sub_issue.lower()} on {comp_date.strftime('%Y-%m-%d')}. I tried resolving this via {channel} but the service was disappointing.",
            f"Extremely frustrated with the {sub_issue.lower()} on my {sub_prod}. This has happened multiple times and customer support failed to resolve it promptly.",
            f"Urgent issue: {sub_issue} regarding {prod}. I request an immediate refund and resolution. My account tenure is {c_info['tenure']} months and I expect better service.",
            f"Disputed charge and {sub_issue.lower()} on {sub_prod}. The app crashed and agent on phone was unable to waive fees.",
            f"Filing a formal complaint about {sub_issue.lower()}. Resolution has taken too long and I am considering closing my account."
        ]
        complaint_text = random.choice(templates)
        
        # Base escalation probability depends on issue category and channel
        base_esc_prob = 0.12
        if issue_cat in ["Fraud & Unauthorized Transaction", "Billing & Fee Dispute"]:
            base_esc_prob += 0.08
        if channel in ["Phone / Contact Center", "Written / Mail"]:
            base_esc_prob += 0.05
        if c_info["segment"] in ["High Net Worth", "Premium Cardholder"]:
            base_esc_prob += 0.04
            
        escalation_flag = 1 if random.random() < base_esc_prob else 0
        
        # Resolution metrics
        if escalation_flag == 1:
            res_days = int(np.random.normal(8.5, 3.0))
            res_days = max(3, min(25, res_days))
            team = "Tier 2 Escalations"
        else:
            res_days = int(np.random.exponential(2.8)) + 1
            res_days = min(14, res_days)
            if prod == "Digital Banking":
                team = "Digital Tech Support"
            elif issue_cat == "Fraud & Unauthorized Transaction":
                team = "Fraud Ops"
            elif issue_cat == "Billing & Fee Dispute":
                team = "Billing Services"
            else:
                team = "Tier 1 General"
                
        response_date = comp_date + timedelta(hours=random.randint(2, 24))
        resolution_date = comp_date + timedelta(days=res_days, hours=random.randint(1, 12))
        
        # Resolution Status & Type
        if escalation_flag == 1:
            res_status = np.random.choice(["Closed with Monetary Relief", "Closed with Non-Monetary Relief", "Closed with Explanation"], p=[0.45, 0.35, 0.20])
        else:
            res_status = np.random.choice(["Closed with Monetary Relief", "Closed with Non-Monetary Relief", "Closed with Explanation"], p=[0.25, 0.40, 0.35])
            
        if "Monetary" in res_status:
            res_type = np.random.choice(["Full Refund", "Fee Waived", "Statement Credit"])
        elif "Non-Monetary" in res_status:
            res_type = np.random.choice(["System Fix", "Policy Exception", "Service Courtesy"])
        else:
            res_type = np.random.choice(["Policy Explanation", "Dispute Denied"])
            
        # Satisfaction score (1 to 5) - strongly linked to resolution days and escalation
        if escalation_flag == 1 and res_days > 7:
            sat_score = np.random.choice([1, 2, 3], p=[0.60, 0.30, 0.10])
        elif res_days <= 2:
            sat_score = np.random.choice([3, 4, 5], p=[0.15, 0.45, 0.40])
        else:
            sat_score = np.random.choice([1, 2, 3, 4, 5], p=[0.20, 0.30, 0.25, 0.15, 0.10])
            
        rows.append({
            "complaint_id": comp_id,
            "customer_id": cid,
            "complaint_date": comp_date.strftime("%Y-%m-%d %H:%M:%S"),
            "product": prod,
            "sub_product": sub_prod,
            "issue": issue_cat,
            "sub_issue": sub_issue,
            "complaint_channel": channel,
            "customer_age": c_info["age"],
            "customer_segment": c_info["segment"],
            "geography": c_info["geography"],
            "account_tenure_months": c_info["tenure"],
            "transaction_frequency": c_info["transaction_frequency"],
            "monthly_spend": c_info["monthly_spend"],
            "complaint_text": complaint_text,
            "response_date": response_date.strftime("%Y-%m-%d %H:%M:%S"),
            "resolution_date": resolution_date.strftime("%Y-%m-%d %H:%M:%S"),
            "resolution_status": res_status,
            "resolution_type": res_type,
            "escalation_flag": escalation_flag,
            "satisfaction_score": sat_score,
            "agent_team": team
        })

    df = pd.DataFrame(rows)

    # Introduce realistic dirty data issues (5% missing values, inconsistent casing, date outliers)
    print("Introducing realistic operational data noise (missing values, inconsistent cases)...")
    
    # Missing complaint text in ~1.5% of records
    missing_text_idx = df.sample(frac=0.015, random_state=seed).index
    df.loc[missing_text_idx, "complaint_text"] = np.nan
    
    # Missing satisfaction scores in ~4% of uncompleted surveys
    missing_sat_idx = df.sample(frac=0.04, random_state=seed).index
    df.loc[missing_sat_idx, "satisfaction_score"] = np.nan

    # Inconsistent channel casing in 2% records
    casing_idx = df.sample(frac=0.02, random_state=seed).index
    df.loc[casing_idx, "complaint_channel"] = df.loc[casing_idx, "complaint_channel"].str.lower()

    output_dir = os.path.join("data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "raw_complaints.csv")
    df.to_csv(file_path, index=False)
    print(f"Raw dataset saved successfully to {file_path} with {len(df)} records.")
    return df

if __name__ == "__main__":
    generate_synthetic_complaints(num_records=50000)
