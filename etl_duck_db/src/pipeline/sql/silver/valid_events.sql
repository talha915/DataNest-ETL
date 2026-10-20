SELECT * FROM ({source})
WHERE user_name IS NOT NULL
  AND top_level_recording_msid IS NOT NULL
  AND listened_at IS NOT NULL
  AND listened_at > 0
  AND (
    artist_name IS NOT NULL
    OR track_name IS NOT NULL
  )