-- Query 1: Monthly Complaint Volume & Month-over-Month (MoM) Growth Rate
-- Demonstrates: GROUP BY, Date Parsing, Window Function LAG()

WITH monthly_summary AS (
    SELECT 
        STRFTIME('%Y-%m', complaint_date) AS year_month,
        COUNT(complaint_id) AS total_complaints,
        COUNT(DISTINCT customer_id) AS unique_customers,
        ROUND(AVG(resolution_time_days), 2) AS avg_resolution_days,
        SUM(escalation_flag) AS total_escalations,
        ROUND(CAST(SUM(escalation_flag) AS FLOAT) / COUNT(complaint_id) * 100, 2) AS escalation_rate_pct
    FROM fact_complaints
    GROUP BY STRFTIME('%Y-%m', complaint_date)
)
SELECT 
    year_month,
    total_complaints,
    unique_customers,
    LAG(total_complaints, 1) OVER (ORDER BY year_month) AS prev_month_complaints,
    ROUND(
        (CAST(total_complaints AS FLOAT) - LAG(total_complaints, 1) OVER (ORDER BY year_month)) 
        / LAG(total_complaints, 1) OVER (ORDER BY year_month) * 100, 2
    ) AS mom_growth_pct,
    avg_resolution_days,
    escalation_rate_pct
FROM monthly_summary
ORDER BY year_month ASC;
