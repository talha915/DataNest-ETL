SELECT
    user_name,
    COUNT(*) AS listen_count
FROM silver.listen_events
GROUP BY user_name
ORDER BY listen_count DESC
LIMIT 10