from pathlib import Path
import json

import pytest

from pipeline.database import Database
from pipeline.schemas import create_schemas, create_tables



@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test.duckdb"
    database = Database(str(db_path))
    create_schemas(database)
    create_tables(database)
    yield database
    database.close()



@pytest.fixture
def sample_events():
    return [
        {
            "track_metadata": {
                "additional_info": {
                    "release_msid": "34dbfc73-31e4-45c3-9d6e-xxxxxxx",
                    "release_mbid": None,
                    "recording_mbid": None,
                    "release_group_mbid": None,
                    "artist_mbids": [],
                    "tags": [],
                    "work_mbids": [],
                    "isrc": None,
                    "spotify_id": None,
                    "tracknumber": None,
                    "track_mbid": None,
                    "artist_msid": "aaaaa-27e7-40af-852a-abaed88ec838",
                    "recording_msid": "1e1b2aa0-b2db-42ed-bbbb-89c303499408",
                },
                "artist_name": "Withered Hand",
                "track_name": "Love In the Time of Ecstacy",
                "release_name": "News",
            },
            "listened_at": 1555286560,
            "recording_msid": "1e1b2aa0-b2db-42ed-a8ba-89c303499408",
            "user_name": "aaaaaa",
        },
        {
            "track_metadata": {
                "additional_info": {
                    "release_msid": "34dbfc73-31e4-45c3-9d6e-xxxxx",
                    "release_mbid": None,
                    "recording_mbid": None,
                    "release_group_mbid": None,
                    "artist_mbids": [],
                    "tags": [],
                    "work_mbids": [],
                    "isrc": None,
                    "spotify_id": None,
                    "tracknumber": None,
                    "track_mbid": None,
                    "artist_msid": "aaaa-27e7-40af-852a-abaed88ec838",
                    "recording_msid": "sss-75e2-406a-8c5e-f38136aa5a68",
                },
                "artist_name": "Withered Hand",
                "track_name": "Cornflake",
                "release_name": "News",
            },
            "listened_at": 1555286378,
            "recording_msid": "283062c8-75e2-406a-8c5e-f38136aa5a68",
            "user_name": "aaaaa",
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


@pytest.fixture
def parquet_dir(tmp_path):
    return tmp_path / "parquet"