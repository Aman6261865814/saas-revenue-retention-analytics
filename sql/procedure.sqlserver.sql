-- Dates are an inclusive start and exclusive end; no wrapping indexed column in a function.
CREATE OR ALTER PROCEDURE dbo.usp_RegionalMetrics
    @FromDate date, @ToDate date
AS
BEGIN
    SET NOCOUNT ON;
    IF @ToDate <= @FromDate THROW 50001, 'End date must follow start', 1;
    SELECT a.region AS region, COUNT(*) AS observations, SUM(f.mrr) AS metric_total
    FROM fact_subscription f JOIN dim_account a ON a.account_id = f.account_id
    WHERE f.month >= @FromDate AND f.month < @ToDate
    GROUP BY a.region;
END;
GO
-- Example: EXEC dbo.usp_RegionalMetrics '2026-05-01','2026-06-01';
