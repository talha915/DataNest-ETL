from .base import Table, DatabaseSchema

class Bronze(DatabaseSchema):
    name = "bronze"

    bronze_listen_events = Table(
        name = "bronze_listen_events"
    )

    file_ingestion_log = Table(
        name="file_ingestion_log"
    )


class Silver(DatabaseSchema):
    name = "silver"

    silver_listen_events = Table(
        name = "silver_listen_events"
    )

class Gold(DatabaseSchema):
    name = "gold"

    daily_listening = Table(
        name="gold_daily_listening"
    )

    artist_listening = Table(
        name="gold_artist_listening"
    )

    track_listening = Table(
        name="gold_track_listening"
    )

    user_listening = Table(
        name="gold_user_listening"
    )


class Pipeline(DatabaseSchema):
    name = "pipeline"

    run_log = Table(
        name="run_log"
    )    