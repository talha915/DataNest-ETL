WITH all_days as (
    select day::DATE as day
    FROM generate_series(
        (select min(listened_date) FROM silver.listen_events),
        (select max(listened_date) FROM silver.listen_events),
        INTERVAL 1 DAY
    ) as t(day)
),
user_days as (
    select DISTINCT user_name, listened_date
    FROM silver.listen_events
),
totals as (
    select count(DISTINCT user_name) as total_users
    FROM silver.listen_events
)
select
    d.day as date,
    count(DISTINCT u.user_name) as number_active_users,
    round(
        100 * count(DISTINCT u.user_name) / t.total_users,
        2
    ) as percentage_active_users
FROM all_days d
CROSS JOIN totals t
LEFT JOIN user_days u
    ON u.listened_date BETWEEN d.day - INTERVAL 6 DAY AND d.day
GROUP BY d.day, t.total_users
ORDER BY d.day