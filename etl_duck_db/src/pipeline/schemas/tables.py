from dataclasses import dataclass, field
from .base import DatabaseSchema, Table, ALL_SCHEMAS


@dataclass
class MetaTable(Table):
    ddl: str = ""


class Bronze(DatabaseSchema):
    name = "bronze"
    tables = [
        Table(name="listen_events", is_source_table=True),
    ]


class Silver(DatabaseSchema):
    name = "silver"
    tables = [
        Table(name="listen_events"),
    ]


class Gold(DatabaseSchema):
    name = "gold"
    tables = [
        Table(name="top_users"),
        Table(name="users_active_on_date"),
        Table(name="users_first_song"),
        Table(name="users_top_days"),
        Table(name="daily_active_users"),
    ]


class Meta(DatabaseSchema):
    name = "meta"

    tables = [
        Table(
            name="run_log",
            ddl="""
                run_id VARCHAR,
                layer VARCHAR,
                job_name VARCHAR,
                status VARCHAR,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                rows BIGINT,
                error VARCHAR
            """,
        ),
        Table(
            name="watermark",
            ddl="""
                layer VARCHAR,
                job_name VARCHAR,
                last_value BIGINT,
                last_run_at TIMESTAMP,
                PRIMARY KEY (layer, job_name)
            """,
        ),
        Table(
            name="quarantine",
            ddl="""
                event_id VARCHAR,
                artist_name VARCHAR,
                track_name VARCHAR,
                release_name VARCHAR,
                release_msid VARCHAR,
                recording_mbid VARCHAR,
                release_mbid VARCHAR,
                release_group_mbid VARCHAR,
                isrc VARCHAR,
                spotify_id VARCHAR,
                tracknumber VARCHAR,
                track_mbid VARCHAR,
                artist_msid VARCHAR,
                additional_recording_msid VARCHAR,
                recording_msid VARCHAR,
                user_name VARCHAR,
                listened_at BIGINT,
                reason VARCHAR,
                layer VARCHAR,
                source_file_path VARCHAR,
                quarantined_at TIMESTAMP
            """
        )
    ]


ALL_SCHEMAS.extend([Bronze, Silver, Gold, Meta])


def qualified(schema_cls, table_name: str) -> str:
    schema_cls.table(table_name)
    return f'"{schema_cls.name}"."{table_name}"'