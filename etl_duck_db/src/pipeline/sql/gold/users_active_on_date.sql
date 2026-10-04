SELECT DISTINCT user_name
FROM silver.listen_events
WHERE listened_date = DATE '2019-03-01'
ORDER BY user_name