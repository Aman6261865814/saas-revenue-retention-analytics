-- Advanced, portable SQL (SQLite, SQL Server, MySQL 8); ranked regional drivers.
WITH regional AS (
 SELECT a.region AS region, f.account_id, SUM(f.mrr) AS metric_total
 FROM fact_subscription f JOIN dim_account a ON a.account_id = f.account_id
 GROUP BY a.region,f.account_id
), ranked AS (
 SELECT *, DENSE_RANK() OVER (PARTITION BY region ORDER BY metric_total DESC) AS regional_rank
 FROM regional
)
SELECT * FROM ranked WHERE regional_rank<=5 ORDER BY region,regional_rank;

-- Correlated subquery: observations above their calendar-date average.
SELECT f.account_id,f.month,f.mrr
FROM fact_subscription f
WHERE f.mrr > (SELECT AVG(g.mrr*1.0) FROM fact_subscription g WHERE g.month=f.month);
