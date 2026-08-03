-- Query 4: Customer-Level Aggregations (Complaints, Resolution, Spend & Tenure Profile)
-- Demonstrates: Customer-level grouping, JOINs across Fact & Dim tables

SELECT 
    c.customer_id,
    c.customer_segment,
    c.account_tenure_months,
    c.monthly_spend,
    COUNT(f.complaint_id) AS total_complaints_filed,
    SUM(f.repeat_complaint_flag) AS repeat_complaint_count,
    SUM(f.escalation_flag) AS total_escalations,
    ROUND(AVG(f.resolution_time_days), 2) AS avg_resolution_time_days,
    ROUND(AVG(f.satisfaction_score), 2) AS avg_csat_score
FROM dim_customer c
JOIN fact_complaints f ON c.customer_id = f.customer_id
GROUP BY c.customer_id, c.customer_segment, c.account_tenure_months, c.monthly_spend
ORDER BY total_complaints_filed DESC, c.monthly_spend DESC
LIMIT 20;
