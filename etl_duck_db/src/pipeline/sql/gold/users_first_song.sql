WITH ranked_cte AS (
    SELECT
        user_name,
        artist_name,
        track_name,
        listened_at_ts,
        ROW_NUMBER() OVER (
            PARTITION BY user_name
            ORDER BY listened_at_ts ASC
        ) AS rn
    FROM silver.listen_events
)
SELECT
    user_name,
    artist_name AS first_artist,
    track_name AS first_track,
    listened_at_ts AS first_listened_at
FROM ranked_cte
WHERE rn = 1
ORDER BY user_name