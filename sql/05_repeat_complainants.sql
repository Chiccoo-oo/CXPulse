-- Query 5: Identifying High-Frequency Repeat Complainants
-- Demonstrates: HAVING clause filtering for customers with 2+ complaints

WITH customer_geo AS (
    SELECT 
        c2.customer_id, 
        c2.customer_segment, 
        c2.account_tenure_months, 
        c2.monthly_spend, 
        g.region_name AS geography_region
    FROM dim_customer c2
    JOIN fact_complaints f2 ON c2.customer_id = f2.customer_id
    JOIN dim_geography g ON f2.geography_id = g.geography_id
    GROUP BY c2.customer_id, c2.customer_segment, c2.account_tenure_months, c2.monthly_spend, g.region_name
)
SELECT 
    cg.customer_id,
    cg.customer_segment,
    cg.geography_region,
    cg.account_tenure_months,
    cg.monthly_spend,
    COUNT(f.complaint_id) AS complaint_count,
    SUM(f.escalation_flag) AS total_escalated_complaints,
    SUM(f.sla_breach_flag) AS total_sla_breaches,
    ROUND(AVG(f.resolution_time_days), 2) AS avg_resolution_days,
    ROUND(AVG(f.satisfaction_score), 2) AS avg_csat_score
FROM customer_geo cg
JOIN fact_complaints f ON cg.customer_id = f.customer_id
GROUP BY cg.customer_id, cg.customer_segment, cg.geography_region, cg.account_tenure_months, cg.monthly_spend
HAVING COUNT(f.complaint_id) >= 2
ORDER BY complaint_count DESC, total_escalated_complaints DESC;
