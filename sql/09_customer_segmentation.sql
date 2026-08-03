-- Query 9: SQL-Based Customer Segmentation Framework
-- Demonstrates: CASE WHEN rule engine profiling customers based on spend, tenure, complaint frequency & satisfaction

WITH customer_summary AS (
    SELECT 
        c.customer_id,
        c.customer_segment,
        c.monthly_spend,
        c.account_tenure_months,
        COUNT(f.complaint_id) AS complaint_count,
        SUM(f.escalation_flag) AS escalation_count,
        AVG(f.satisfaction_score) AS avg_csat
    FROM dim_customer c
    JOIN fact_complaints f ON c.customer_id = f.customer_id
    GROUP BY c.customer_id, c.customer_segment, c.monthly_spend, c.account_tenure_months
)
SELECT 
    customer_id,
    customer_segment,
    monthly_spend,
    account_tenure_months,
    complaint_count,
    escalation_count,
    ROUND(avg_csat, 2) AS avg_csat,
    CASE 
        WHEN monthly_spend >= 5000 AND avg_csat <= 2.5 THEN 'High-Value Dissatisfied (At-Risk)'
        WHEN complaint_count >= 3 THEN 'Frequent Complainant'
        WHEN escalation_count >= 1 AND monthly_spend >= 3000 THEN 'Escalated Premium Customer'
        WHEN account_tenure_months <= 12 AND complaint_count >= 1 THEN 'New Customer Onboarding Issue'
        ELSE 'Standard Low-Risk Complainant'
    END AS behavioral_segment
FROM customer_summary
ORDER BY monthly_spend DESC, complaint_count DESC
LIMIT 25;
