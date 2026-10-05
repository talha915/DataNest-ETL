SELECT * FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY event_id
               ORDER BY listened_at ASC
           ) AS rn
    FROM ({source})
) WHERE rn = 1