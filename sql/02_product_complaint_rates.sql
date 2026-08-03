-- Query 2: Complaint Volume and Rate Breakdown by Product Line & Sub-Product
-- Demonstrates: Multi-table JOINs, Aggregations, Percentage calculations

SELECT 
    p.product_name,
    p.sub_product_name,
    COUNT(f.complaint_id) AS total_complaints,
    COUNT(DISTINCT f.customer_id) AS impacted_customers,
    ROUND(AVG(f.resolution_time_days), 2) AS avg_resolution_time_days,
    SUM(f.sla_breach_flag) AS total_sla_breaches,
    ROUND(CAST(SUM(f.sla_breach_flag) AS FLOAT) / COUNT(f.complaint_id) * 100, 2) AS sla_breach_pct,
    ROUND(CAST(SUM(f.escalation_flag) AS FLOAT) / COUNT(f.complaint_id) * 100, 2) AS escalation_rate_pct,
    ROUND(AVG(f.satisfaction_score), 2) AS avg_satisfaction_csat
FROM fact_complaints f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_name, p.sub_product_name
ORDER BY total_complaints DESC;
