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
        Table(name="daily_listening"),
        Table(name="artist_listening"),
        Table(name="track_listening"),
        Table(name="user_listening"),
    ]


class Meta(DatabaseSchema):
    name = "meta"

    tables = [
        Table(
            name="run_log",
            ddl="""
                run_id       VARCHAR,
                layer        VARCHAR,
                job_name     VARCHAR,
                status       VARCHAR,
                started_at   TIMESTAMP,
                completed_at TIMESTAMP,
                rows         BIGINT,
                error        VARCHAR
            """,
        ),
        Table(
            name="watermark",
            ddl="""
                layer        VARCHAR,
                job_name     VARCHAR,
                last_file    VARCHAR,
                last_run_at  TIMESTAMP,
                PRIMARY KEY (layer, job_name)
            """,
        ),
    ]


ALL_SCHEMAS.extend([Bronze, Silver, Gold, Meta])


def qualified(schema_cls, table_name: str) -> str:
    schema_cls.table(table_name)
    return f'"{schema_cls.name}"."{table_name}"'