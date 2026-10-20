WITH bridge AS (
 SELECT month, SUM(previous_mrr) AS start_mrr, SUM(mrr) AS end_mrr,
 SUM(new_mrr) AS new_mrr, SUM(reactivation_mrr) AS reactivation_mrr,
 SUM(expansion_mrr) AS expansion_mrr, SUM(contraction_mrr) AS contraction_mrr,
 SUM(churn_mrr) AS churn_mrr, SUM(retained_mrr) AS retained_mrr
 FROM fact_subscription GROUP BY month
)
SELECT *, retained_mrr * 1.0 / NULLIF(start_mrr,0) AS nrr,
 end_mrr - LAG(end_mrr) OVER (ORDER BY month) AS net_mrr_change
FROM bridge ORDER BY month;
