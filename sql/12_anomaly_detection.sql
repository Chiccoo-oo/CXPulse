-- Query 12: Statistical Anomaly Detection in Daily Complaint Volume
-- Demonstrates: Rolling Window Aggregations, Standard Deviation, Z-Score Thresholding

WITH daily_volume AS (
    SELECT 
        DATE(complaint_date) AS comp_date,
        COUNT(complaint_id) AS daily_count
    FROM fact_complaints
    GROUP BY DATE(complaint_date)
),
stats AS (
    SELECT 
        comp_date,
        daily_count,
        AVG(daily_count) OVER(ORDER BY comp_date ROWS BETWEEN 14 PRECEDING AND 14 FOLLOWING) AS rolling_mean_30d,
        -- Approximate sample standard deviation using variance or window range
        AVG(daily_count * daily_count) OVER(ORDER BY comp_date ROWS BETWEEN 14 PRECEDING AND 14 FOLLOWING) - 
        (AVG(daily_count) OVER(ORDER BY comp_date ROWS BETWEEN 14 PRECEDING AND 14 FOLLOWING) * 
         AVG(daily_count) OVER(ORDER BY comp_date ROWS BETWEEN 14 PRECEDING AND 14 FOLLOWING)) AS rolling_var
    FROM daily_volume
),
z_scores AS (
    SELECT 
        comp_date,
        daily_count,
        ROUND(rolling_mean_30d, 2) AS rolling_mean_30d,
        ROUND(SQRT(CASE WHEN rolling_var > 0 THEN rolling_var ELSE 0.001 END), 2) AS rolling_std,
        ROUND(
            (daily_count - rolling_mean_30d) / 
            NULLIF(SQRT(CASE WHEN rolling_var > 0 THEN rolling_var ELSE 0.001 END), 0), 2
        ) AS z_score
    FROM stats
)
SELECT 
    comp_date,
    daily_count,
    rolling_mean_30d,
    rolling_std,
    z_score,
    CASE 
        WHEN z_score >= 2.0 THEN 'ANOMALY_HIGH_SPIKE'
        WHEN z_score <= -2.0 THEN 'ANOMALY_LOW_DROP'
        ELSE 'NORMAL'
    END AS anomaly_flag
FROM z_scores
WHERE ABS(z_score) >= 1.8
ORDER BY comp_date ASC;
