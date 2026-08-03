-- Query 8: Month-over-Month Servicing Operational Shifts (Resolution Time & Escalations)
-- Demonstrates: CTEs, LAG() over multiple metrics

WITH monthly_ops AS (
    SELECT 
        STRFTIME('%Y-%m', complaint_date) AS year_month,
        COUNT(complaint_id) AS total_complaints,
        ROUND(AVG(resolution_time_days), 2) AS avg_res_days,
        SUM(sla_breach_flag) AS sla_breaches,
        SUM(escalation_flag) AS escalations
    FROM fact_complaints
    GROUP BY STRFTIME('%Y-%m', complaint_date)
)
SELECT 
    year_month,
    total_complaints,
    avg_res_days,
    LAG(avg_res_days, 1) OVER (ORDER BY year_month) AS prev_month_avg_res_days,
    ROUND(avg_res_days - LAG(avg_res_days, 1) OVER (ORDER BY year_month), 2) AS res_time_change_days,
    escalations,
    LAG(escalations, 1) OVER (ORDER BY year_month) AS prev_month_escalations,
    (escalations - LAG(escalations, 1) OVER (ORDER BY year_month)) AS escalation_count_change
FROM monthly_ops
ORDER BY year_month ASC;
