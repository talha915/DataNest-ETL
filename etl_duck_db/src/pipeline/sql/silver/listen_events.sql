SELECT *
FROM (
    SELECT
        track_metadata.artist_name    AS artist_name,
        track_metadata.track_name     AS track_name,
        track_metadata.release_name   AS release_name,

        track_metadata.additional_info.release_msid AS release_msid,
        track_metadata.additional_info.recording_mbid AS recording_mbid,
        track_metadata.additional_info.release_mbid AS release_mbid,
        track_metadata.additional_info.release_group_mbid AS release_group_mbid,

        track_metadata.additional_info.isrc AS isrc,
        track_metadata.additional_info.spotify_id AS spotify_id,
        track_metadata.additional_info.tracknumber AS tracknumber,
        track_metadata.additional_info.track_mbid AS track_mbid,
        track_metadata.additional_info.artist_msid AS artist_msid,
        track_metadata.additional_info.recording_msid AS recording_msid,

        listened_at,
        to_timestamp(listened_at) AS listened_at_ts,
        CAST(to_timestamp(listened_at) AS DATE) AS listened_date,

        recording_msid AS top_level_recording_msid,
        user_name
    FROM bronze.listen_events
) sub
WHERE recording_msid IS NOT NULL
  AND user_name IS NOT NULL