-- Rebuild the derived monthly summary from imported subscription records.
-- Replaces any partial monthly_metrics import; leaves source tables unchanged.
USE [SaaSRevenueAnalytics];
GO
SET XACT_ABORT ON;
BEGIN TRY
    BEGIN TRANSACTION;

    IF (SELECT COUNT_BIG(*) FROM dbo.fact_subscription) <> 43200
        THROW 50001, 'Expected 43200 subscription rows. No summary changes saved.', 1;

    SELECT month,
        SUM(previous_mrr) AS start_mrr, SUM(mrr) AS end_mrr,
        SUM(new_mrr) AS new_mrr, SUM(reactivation_mrr) AS reactivation_mrr,
        SUM(expansion_mrr) AS expansion_mrr, SUM(contraction_mrr) AS contraction_mrr,
        SUM(churn_mrr) AS churn_mrr, SUM(retained_mrr) AS retained_mrr,
        SUM(active) AS active_accounts, SUM(starting_active) AS starting_accounts,
        SUM(churned) AS churned_accounts
    INTO #monthly_refresh
    FROM dbo.fact_subscription
    GROUP BY month;

    IF (SELECT COUNT(*) FROM #monthly_refresh) <> 18
        THROW 50002, 'Expected 18 months. No summary changes saved.', 1;

    IF EXISTS (SELECT 1 FROM #monthly_refresh
        WHERE end_mrr - start_mrr - new_mrr - reactivation_mrr
              - expansion_mrr - contraction_mrr - churn_mrr <> 0)
        THROW 50003, 'Revenue bridge does not reconcile. No summary changes saved.', 1;

    DELETE FROM dbo.monthly_metrics;
    INSERT INTO dbo.monthly_metrics
        (month, start_mrr, end_mrr, new_mrr, reactivation_mrr,
         expansion_mrr, contraction_mrr, churn_mrr, retained_mrr,
         active_accounts, starting_accounts, churned_accounts,
         nrr, logo_churn_rate, bridge_residual)
    SELECT month, start_mrr, end_mrr, new_mrr, reactivation_mrr,
        expansion_mrr, contraction_mrr, churn_mrr, retained_mrr,
        active_accounts, starting_accounts, churned_accounts,
        CAST(retained_mrr AS float) / NULLIF(CAST(start_mrr AS float), 0),
        CAST(churned_accounts AS float) / NULLIF(CAST(starting_accounts AS float), 0),
        end_mrr - start_mrr - new_mrr - reactivation_mrr
            - expansion_mrr - contraction_mrr - churn_mrr
    FROM #monthly_refresh;

    DROP TABLE #monthly_refresh;
    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;

SELECT * FROM dbo.monthly_metrics ORDER BY month;
