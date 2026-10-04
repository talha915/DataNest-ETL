from pathlib import Path
import json

import pytest

from pipeline.database import Database
from pipeline.schemas import create_schemas, create_tables


# ------------------------------------------------------------------
# Temporary database
# ------------------------------------------------------------------

@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test.duckdb"
    database = Database(str(db_path))
    create_schemas(database)
    create_tables(database)
    yield database
    database.close()


# ------------------------------------------------------------------
# Sample NDJSON data
# ------------------------------------------------------------------

@pytest.fixture
def sample_events():
    return [
        {
            "track_metadata": {
                "artist_name": "Artist A",
                "track_name": "Track A",
                "release_name": "Album A",
                "additional_info": {
                    "artist_msid": "art-1",
                    "release_msid": "rel-1",
                    "recording_msid": "rec-1",
                    "recording_mbid": "mbid-1",
                },
            },
            "listened_at": 1555286560,
            "recording_msid": "rec-1",
            "user_name": "user-1",
        },
        {
            "track_metadata": {
                "artist_name": "Artist B",
                "track_name": "Track B",
                "release_name": "Album B",
                "additional_info": {
                    "artist_msid": "art-2",
                    "release_msid": "rel-2",
                    "recording_msid": "rec-2",
                    "recording_mbid": "mbid-2",
                },
            },
            "listened_at": 1555286570,
            "recording_msid": "rec-2",
            "user_name": "user-1",
        },
    ]


@pytest.fixture
def source_dir(tmp_path, sample_events):
    src = tmp_path / "source"
    src.mkdir()

    with (src / "dataset.json").open("w", encoding="utf-8") as f:
        for event in sample_events:
            f.write(json.dumps(event) + "\n")

    return src


# ------------------------------------------------------------------
# Temporary parquet directory
# ------------------------------------------------------------------

@pytest.fixture
def bronze_parquet_dir(tmp_path):
    return tmp_path / "bronze_parquet"


@pytest.fixture
def silver_parquet_dir(tmp_path):
    return tmp_path / "silver_parquet"