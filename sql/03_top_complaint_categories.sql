-- Query 3: Top Complaint Categories & Sub-Issues Distribution
-- Demonstrates: GROUP BY, ORDER BY, Aggregations

SELECT 
    p.issue_category,
    p.sub_issue,
    COUNT(f.complaint_id) AS complaint_count,
    ROUND(CAST(COUNT(f.complaint_id) AS FLOAT) / (SELECT COUNT(*) FROM fact_complaints) * 100, 2) AS share_of_total_pct,
    SUM(f.escalation_flag) AS total_escalations,
    ROUND(AVG(f.resolution_time_days), 2) AS avg_resolution_days,
    ROUND(AVG(f.satisfaction_score), 2) AS avg_csat
FROM fact_complaints f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.issue_category, p.sub_issue
ORDER BY complaint_count DESC
LIMIT 15;
