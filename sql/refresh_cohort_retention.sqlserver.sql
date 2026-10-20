-- Rebuild the derived cohort table using the original project's definitions.
-- signup_month is a zero-based month index: 0 = January 2025.
-- Reactivated accounts count as active; only observed ages are included.
USE [SaaSRevenueAnalytics];
GO
SET XACT_ABORT ON;
BEGIN TRY
    BEGIN TRANSACTION;

    IF (SELECT COUNT_BIG(*) FROM dbo.fact_subscription) <> 43200
        THROW 50001, 'Expected 43200 subscription rows. No changes saved.', 1;

    IF EXISTS (SELECT 1 FROM dbo.fact_subscription
               WHERE age_month IS NULL OR active IS NULL OR active NOT IN (0,1))
        THROW 50002, 'Invalid cohort input values. No changes saved.', 1;

    IF EXISTS (
        SELECT account_id FROM dbo.fact_subscription GROUP BY account_id
        HAVING MIN(DATEDIFF(month, CONVERT(date,'20250101',112), month) - age_month)
            <> MAX(DATEDIFF(month, CONVERT(date,'20250101',112), month) - age_month)
    )
        THROW 50003, 'Inconsistent signup month for an account. No changes saved.', 1;

    SELECT
        DATEDIFF(month, CONVERT(date,'20250101',112), month) - age_month AS signup_month,
        age_month,
        SUM(active) AS active,
        COUNT_BIG(*) AS cohort_size,
        CAST(SUM(active) AS float) / COUNT_BIG(*) AS retention
    INTO #cohort_refresh
    FROM dbo.fact_subscription
    WHERE age_month >= 0
    GROUP BY DATEDIFF(month, CONVERT(date,'20250101',112), month) - age_month,
             age_month;

    IF (SELECT COUNT(*) FROM #cohort_refresh) <> 165
        THROW 50004, 'Expected 165 observed cohort-age combinations. No changes saved.', 1;

    DELETE FROM dbo.cohort_retention;
    INSERT INTO dbo.cohort_retention (signup_month, age_month, active, cohort_size, retention)
    SELECT signup_month, age_month, active, cohort_size, retention
    FROM #cohort_refresh;

    DROP TABLE #cohort_refresh;
    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;

SELECT * FROM dbo.cohort_retention ORDER BY signup_month, age_month;
