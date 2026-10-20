-- SQLite benchmark: capture EXPLAIN QUERY PLAN before and after the index.
EXPLAIN QUERY PLAN SELECT SUM(mrr) FROM fact_subscription
WHERE month>='2026-05-01' AND month<'2026-06-01';
CREATE INDEX IF NOT EXISTS ix_fact_subscription_date ON fact_subscription(month);
EXPLAIN QUERY PLAN SELECT SUM(mrr) FROM fact_subscription
WHERE month>='2026-05-01' AND month<'2026-06-01';
-- SQL Server: actual plan + SET STATISTICS IO,TIME ON; CREATE INDEX without IF NOT EXISTS.
-- MySQL 8.0.18+: EXPLAIN ANALYZE; CREATE INDEX without IF NOT EXISTS.
-- Never infer production speedups from this small local dataset.
