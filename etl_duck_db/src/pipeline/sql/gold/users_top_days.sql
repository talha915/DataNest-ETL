WITH daily AS (
    SELECT
        user_name,
        listened_date,
        COUNT(*) AS listen_count
    FROM silver.listen_events
    GROUP BY user_name, listened_date
),
ranked AS (
    SELECT
        user_name,
        listened_date,
        listen_count,
        ROW_NUMBER() OVER (
            PARTITION BY user_name
            ORDER BY listen_count DESC, listened_date ASC
        ) AS rn
    FROM daily
)
SELECT
    user_name AS "user",
    listen_count AS number_of_listens,
    listened_date AS date
FROM ranked
WHERE rn <= 3
ORDER BY "user", number_of_listens DESC