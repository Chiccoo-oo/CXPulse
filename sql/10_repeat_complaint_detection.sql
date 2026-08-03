-- Query 10: Window Function Pattern Detection for Consecutive Repeat Complaints
-- Demonstrates: LAG(), JULIANDAY / Date Differences across customer timeline

WITH complaint_sequence AS (
    SELECT 
        complaint_id,
        customer_id,
        product_id,
        complaint_date,
        LAG(complaint_date, 1) OVER (PARTITION BY customer_id ORDER BY complaint_date) AS prev_complaint_date,
        LAG(complaint_id, 1) OVER (PARTITION BY customer_id ORDER BY complaint_date) AS prev_complaint_id,
        resolution_status
    FROM fact_complaints
)
SELECT 
    c.complaint_id,
    c.customer_id,
    c.complaint_date,
    c.prev_complaint_id,
    c.prev_complaint_date,
    ROUND(JULIANDAY(c.complaint_date) - JULIANDAY(c.prev_complaint_date), 1) AS days_between_complaints,
    p.product_name,
    p.issue_category
FROM complaint_sequence c
JOIN dim_product p ON c.product_id = p.product_id
WHERE c.prev_complaint_date IS NOT NULL
  AND JULIANDAY(c.complaint_date) - JULIANDAY(c.prev_complaint_date) <= 60
ORDER BY days_between_complaints ASC
LIMIT 20;
