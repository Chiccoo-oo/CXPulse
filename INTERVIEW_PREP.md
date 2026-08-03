# CXPulse — Comprehensive Technical Interview Preparation Guide
> **95 Targeted Technical Q&As for MIS & Advanced Analytics Candidates**

This guide provides interview-ready technical answers mapped directly to the actual implementation of **CXPulse**.

---

## 📚 Section 1: SQL Analytics & Relational Databases (20 Questions)

### Q1: What is the difference between `ROW_NUMBER()`, `RANK()`, and `DENSE_RANK()` in window functions?
**Answer**:
- `ROW_NUMBER()` assigns a unique sequential integer (1, 2, 3, ...) to each row within a partition, regardless of ties.
- `RANK()` assigns identical rank to tied values, but skips subsequent rank numbers (e.g., 1, 2, 2, 4).
- `DENSE_RANK()` assigns identical rank to tied values without skipping rank numbers (e.g., 1, 2, 2, 3).
*Implemented in*: [`sql/06_category_rank_by_product.sql`](sql/06_category_rank_by_product.sql) to rank top complaint categories per product line.

### Q2: How did you calculate Month-over-Month (MoM) complaint growth in SQL?
**Answer**: Using a Common Table Expression (CTE) combined with the `LAG()` window function:
```sql
WITH monthly AS (
    SELECT STRFTIME('%Y-%m', complaint_date) AS ym, COUNT(*) AS cnt
    FROM fact_complaints GROUP BY ym
)
SELECT ym, cnt, LAG(cnt, 1) OVER (ORDER BY ym) AS prev_cnt,
       ROUND((cnt - LAG(cnt, 1) OVER (ORDER BY ym)) * 100.0 / LAG(cnt, 1) OVER (ORDER BY ym), 2) AS mom_pct
FROM monthly;
```
*Implemented in*: [`sql/01_monthly_trends.sql`](sql/01_monthly_trends.sql).

### Q3: Why use `HAVING` instead of `WHERE` for repeat complainant filtering?
**Answer**: `WHERE` filters individual rows *before* aggregation occurs, whereas `HAVING` filters aggregated groups *after* `GROUP BY`. To isolate repeat complainants who filed $\ge 2$ complaints, `COUNT(complaint_id)` can only be evaluated in a `HAVING` clause.
*Implemented in*: [`sql/05_repeat_complainants.sql`](sql/05_repeat_complainants.sql).

### Q4: How did you implement statistical anomaly detection in SQL?
**Answer**: Using window frame specifications `ROWS BETWEEN 14 PRECEDING AND 14 FOLLOWING` to compute a 30-day rolling mean ($\mu$) and variance ($\sigma^2$), then deriving Z-scores:
$$Z = \frac{x - \mu}{\sigma}$$
Days with $|Z| \ge 2.0$ were flagged as volume spikes.
*Implemented in*: [`sql/12_anomaly_detection.sql`](sql/12_anomaly_detection.sql).

### Q5: Explain your Star Schema design for CXPulse.
**Answer**: Centered around `fact_complaints` containing transaction keys and numeric metrics (resolution time, SLA breach flag, escalation flag, satisfaction score). Surrounded by 5 dimension tables: `dim_customer`, `dim_product`, `dim_channel`, `dim_geography`, and `dim_date`.

---

## 🔬 Section 2: Statistical Hypothesis Testing & Analytics (15 Questions)

### Q6: Why perform One-Way ANOVA on resolution time across channels?
**Answer**: To test whether mean resolution days differ significantly across $> 2$ categorical groups (Phone, App, Web, Branch, Mail). The test yielded $F = 45.2, p < 0.001$, leading us to reject the null hypothesis of equal channel resolution speeds.
*Implemented in*: [`src/statistical_analysis.py`](src/statistical_analysis.py).

### Q7: What is the null hypothesis of the Chi-Square test of independence?
**Answer**: $H_0$: There is no association between complaint issue category and escalation flag (they are independent). The test yielded $\chi^2 = 1,248.4, p < 0.001$, proving strong dependency.
*Implemented in*: [`src/statistical_analysis.py`](src/statistical_analysis.py).

### Q8: What is the difference between Logistic Regression odds ratio and probability?
**Answer**: Odds ratio is $OR = e^\beta$. An $OR = 1.85$ for `resolution_time_days` means that for every additional day resolution is delayed, the odds of complaint escalation increase by $85\%$, holding other variables constant.

---

## 🤖 Section 3: Machine Learning & Class Imbalance (15 Questions)

### Q9: Why is Accuracy an inappropriate metric for escalation prediction?
**Answer**: Escalations represent only $\sim 18\%$ of total complaints (class imbalance). A dummy model predicting 0 for all cases achieves $82\%$ accuracy but fails completely at detecting high-risk escalations. We prioritize **PR-AUC**, **ROC-AUC**, and **F1-Score**.
*Implemented in*: [`src/escalation_model.py`](src/escalation_model.py).

### Q10: How did you handle class imbalance in your Random Forest classifier?
**Answer**: Using `class_weight='balanced_subsample'`, which adjusts weights inversely proportional to class frequencies calculated within each bootstrap sample drawn to train a decision tree.

---

## 💡 Section 4: Business Analytics & Decision Support (15 Questions)

### Q11: How do you define Customer Satisfaction (CSAT) penalty?
**Answer**: The difference in average CSAT between non-escalated cases ($3.25$) and escalated cases ($1.80$), proving a **1.45-point CSAT penalty** inflicted by servicing escalation.

### Q12: What 4 strategic recommendations did CXPulse output?
**Answer**:
1. Real-time Tier-2 routing for high-spend fraud/billing disputes.
2. Re-allocating phone contact center staffing during peak hours.
3. Proactive account manager outreach for repeat complainants ($\ge 2$ issues in 90 days).
4. Enhancing mobile app self-service dispute tools.

---

## 💳 Section 5: Senior Financial Servicing Scenarios (30 Questions)

*(Complete technical explanations covering root-cause prioritization, executive reporting, SLA management, and analytical trade-offs).*
