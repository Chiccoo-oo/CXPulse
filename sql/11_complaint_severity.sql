-- Query 11: Business-Rule Complaint Severity Framework
-- Demonstrates: Complex CASE WHEN logic and aggregations by derived severity tier

SELECT 
    severity_level,
    COUNT(complaint_id) AS total_complaints,
    ROUND(CAST(COUNT(complaint_id) AS FLOAT) / (SELECT COUNT(*) FROM fact_complaints) * 100, 2) AS percentage_of_total,
    ROUND(AVG(resolution_time_days), 2) AS avg_resolution_days,
    SUM(escalation_flag) AS total_escalations,
    SUM(sla_breach_flag) AS total_sla_breaches,
    ROUND(AVG(satisfaction_score), 2) AS avg_csat
FROM fact_complaints
GROUP BY severity_level
ORDER BY 
    CASE severity_level 
        WHEN 'CRITICAL' THEN 1 
        WHEN 'HIGH' THEN 2 
        WHEN 'MEDIUM' THEN 3 
        WHEN 'LOW' THEN 4 
    END ASC;
