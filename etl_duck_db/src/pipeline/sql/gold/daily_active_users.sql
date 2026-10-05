WITH all_days AS (
    SELECT day::DATE AS day
    FROM generate_series(
        (SELECT MIN(listened_date) FROM silver.listen_events),
        (SELECT MAX(listened_date) FROM silver.listen_events),
        INTERVAL 1 DAY
    ) AS t(day)
),
user_days AS (
    SELECT DISTINCT user_name, listened_date
    FROM silver.listen_events
),
totals AS (
    SELECT COUNT(DISTINCT user_name) AS total_users
    FROM silver.listen_events
)
SELECT
    d.day AS date,
    COUNT(DISTINCT u.user_name) AS number_active_users,
    ROUND(
        100.0 * COUNT(DISTINCT u.user_name) / t.total_users,
        2
    ) AS percentage_active_users
FROM all_days d
CROSS JOIN totals t
LEFT JOIN user_days u
    ON u.listened_date BETWEEN d.day - INTERVAL 6 DAY AND d.day
GROUP BY d.day, t.total_users
ORDER BY d.day