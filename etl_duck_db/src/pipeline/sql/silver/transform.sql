SELECT
    json_extract_string(track_metadata, '$.artist_name') AS artist_name,
    json_extract_string(track_metadata, '$.track_name') AS track_name,
    json_extract_string(track_metadata, '$.release_name') AS release_name,

    json_extract_string(track_metadata, '$.additional_info.release_msid') AS release_msid,
    json_extract_string(track_metadata, '$.additional_info.recording_mbid') AS recording_mbid,
    json_extract_string(track_metadata, '$.additional_info.release_mbid') AS release_mbid,
    json_extract_string(track_metadata, '$.additional_info.release_group_mbid') AS release_group_mbid,

    json_extract_string(track_metadata, '$.additional_info.isrc') AS isrc,
    json_extract_string(track_metadata, '$.additional_info.spotify_id') AS spotify_id,
    json_extract_string(track_metadata, '$.additional_info.tracknumber') AS tracknumber,
    json_extract_string(track_metadata, '$.additional_info.track_mbid') AS track_mbid,
    json_extract_string(track_metadata, '$.additional_info.artist_msid') AS artist_msid,
    json_extract_string(track_metadata, '$.additional_info.recording_msid') AS additional_recording_msid,

    listened_at,
    to_timestamp(listened_at) AS listened_at_ts,
    CAST(to_timestamp(listened_at) AS DATE) AS listened_date,

    recording_msid AS top_level_recording_msid,
    user_name,

    event_id,
    source_file_path
FROM {source_table}
WHERE listened_at > {last_ts}