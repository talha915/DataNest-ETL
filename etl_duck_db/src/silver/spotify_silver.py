from src.db.connection import SpotifyDB


class SilverLayer:
    def __init__(self, db: SpotifyDB):
        self.db = db

    def transform_spotify_listen(self) -> None:
        self._create_quarantine_table()
        self._create_silver_table()

    def _create_quarantine_table(self) -> None:
        self.db.conn.execute("""
            CREATE OR REPLACE TABLE silver.spotify_listen_quarantine AS
            SELECT
                *,
                CASE
                    WHEN recording_msid IS NULL THEN 'missing_recording_msid'
                    WHEN user_name IS NULL THEN 'missing_user_name'
                    WHEN listened_at IS NULL THEN 'missing_listened_at'
                END AS rejection_reason
            FROM bronze.spotify_listen
            WHERE recording_msid IS NULL
               OR user_name IS NULL
               OR listened_at IS NULL;
        """)

    def _create_silver_table(self) -> None:
        self.db.conn.execute("""
            CREATE OR REPLACE TABLE silver.spotify_listen AS
            SELECT
                recording_msid,
                user_name,
                listened_at,

                track_metadata.artist_name AS artist_name,
                track_metadata.track_name AS track_name,
                track_metadata.release_name AS release_name,

                track_metadata.additional_info.spotify_id AS spotify_id,
                track_metadata.additional_info.duration_ms AS duration_ms,
                track_metadata.additional_info.isrc AS isrc,
                track_metadata.additional_info.albumartist AS album_artist,
                track_metadata.additional_info.source AS source

            FROM bronze.spotify_listen
            WHERE recording_msid IS NOT NULL
              AND user_name IS NOT NULL
              AND listened_at IS NOT NULL;
        """)