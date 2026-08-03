-- Query 6: Ranking Top Complaint Categories Within Each Product Line
-- Demonstrates: Window function ROW_NUMBER() / RANK() OVER (PARTITION BY ... ORDER BY ...)

WITH category_counts AS (
    SELECT 
        p.product_name,
        p.issue_category,
        COUNT(f.complaint_id) AS complaint_count,
        SUM(f.escalation_flag) AS total_escalations,
        ROUND(AVG(f.resolution_time_days), 2) AS avg_resolution_days
    FROM fact_complaints f
    JOIN dim_product p ON f.product_id = p.product_id
    GROUP BY p.product_name, p.issue_category
),
ranked_categories AS (
    SELECT 
        product_name,
        issue_category,
        complaint_count,
        total_escalations,
        avg_resolution_days,
        ROW_NUMBER() OVER (PARTITION BY product_name ORDER BY complaint_count DESC) AS category_rank
    FROM category_counts
)
SELECT 
    product_name,
    category_rank,
    issue_category,
    complaint_count,
    total_escalations,
    avg_resolution_days
FROM ranked_categories
WHERE category_rank <= 3
ORDER BY product_name ASC, category_rank ASC;
