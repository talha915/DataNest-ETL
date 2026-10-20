SELECT
    COUNT(DISTINCT user_name) AS num_active_users,
    DATE '2019-03-01' AS date
FROM silver.listen_events
WHERE listened_date = DATE '2019-03-01'