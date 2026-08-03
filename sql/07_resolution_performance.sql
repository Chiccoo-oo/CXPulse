-- Query 7: Resolution Performance & SLA Breach Analysis by Support Team & Channel
-- Demonstrates: Operational performance metrics, SLA breach rates, Channel performance

SELECT 
    f.agent_team,
    c.channel_name,
    COUNT(f.complaint_id) AS total_handled,
    ROUND(AVG(f.resolution_time_days), 2) AS avg_resolution_time_days,
    SUM(f.sla_breach_flag) AS sla_breaches,
    ROUND(CAST(SUM(f.sla_breach_flag) AS FLOAT) / COUNT(f.complaint_id) * 100, 2) AS sla_breach_rate_pct,
    SUM(f.escalation_flag) AS escalations,
    ROUND(CAST(SUM(f.escalation_flag) AS FLOAT) / COUNT(f.complaint_id) * 100, 2) AS escalation_rate_pct,
    ROUND(AVG(f.satisfaction_score), 2) AS average_csat
FROM fact_complaints f
JOIN dim_channel c ON f.channel_id = c.channel_id
GROUP BY f.agent_team, c.channel_name
ORDER BY total_handled DESC;
