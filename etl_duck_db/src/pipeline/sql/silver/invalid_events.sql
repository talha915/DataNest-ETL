SELECT
    event_id,
    artist_name,
    track_name,
    release_name,
    release_msid,
    recording_mbid,
    release_mbid,
    release_group_mbid,
    isrc,
    spotify_id,
    tracknumber,
    track_mbid,
    artist_msid,
    additional_recording_msid,
    top_level_recording_msid AS recording_msid,
    user_name,
    listened_at,
    CASE
        WHEN user_name IS NULL THEN 'missing_user_name'
        WHEN top_level_recording_msid IS NULL
            THEN 'missing_recording_msid'
        WHEN listened_at IS NULL THEN 'missing_listened_at'
        WHEN listened_at <= 0 THEN 'invalid_listened_at'
        WHEN artist_name IS NULL AND track_name IS NULL
            THEN 'missing_artist_and_track_name'
        ELSE 'unknown'
    END AS reason,
    'silver' AS layer,
    source_file_path,
    current_timestamp AS quarantined_at
FROM ({source})
WHERE user_name IS NULL
   OR top_level_recording_msid IS NULL
   OR listened_at IS NULL
   OR listened_at <= 0
   OR (
        artist_name IS NULL
        AND track_name IS NULL
   )