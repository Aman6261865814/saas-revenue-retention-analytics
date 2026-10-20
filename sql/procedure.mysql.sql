DELIMITER //
CREATE PROCEDURE RegionalMetrics(IN p_from DATE, IN p_to DATE)
BEGIN
    IF p_to <= p_from THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='End date must follow start'; END IF;
    SELECT a.region AS region, COUNT(*) AS observations, SUM(f.mrr) AS metric_total
    FROM fact_subscription f JOIN dim_account a ON a.account_id = f.account_id
    WHERE f.month >= p_from AND f.month < p_to
    GROUP BY a.region;
END //
DELIMITER ;
