import pytest

from pipeline.bronze import Bronze
from pipeline.silver import Silver


@pytest.fixture
def silver_ready(db, source_dir, bronze_parquet_dir, silver_parquet_dir):
    """Bronze chalane ke baad ka DB."""
    Bronze(db, str(source_dir), str(bronze_parquet_dir)).run()
    return db


# ------------------------------------------------------------------
# Basic transformation
# ------------------------------------------------------------------

def test_silver_creates_table(silver_ready, silver_parquet_dir):
    Silver(silver_ready, str(silver_parquet_dir)).run()

    rows = silver_ready.fetchone(
        'SELECT COUNT(*) FROM silver.listen_events'
    )[0]
    assert rows == 2


def test_silver_flattens_json(silver_ready, silver_parquet_dir):
    Silver(silver_ready, str(silver_parquet_dir)).run()

    row = silver_ready.fetchone("""
        SELECT artist_name, track_name, release_name
        FROM silver.listen_events
        ORDER BY listened_at
        LIMIT 1
    """)

    assert row[0] == "Artist A"
    assert row[1] == "Track A"
    assert row[2] == "Album A"


def test_silver_adds_listened_at_ts(silver_ready, silver_parquet_dir):
    Silver(silver_ready, str(silver_parquet_dir)).run()

    row = silver_ready.fetchone("""
        SELECT listened_at_ts FROM silver.listen_events LIMIT 1
    """)

    assert row[0] is not None


def test_silver_adds_listened_date(silver_ready, silver_parquet_dir):
    Silver(silver_ready, str(silver_parquet_dir)).run()

    row = silver_ready.fetchone("""
        SELECT listened_date FROM silver.listen_events LIMIT 1
    """)

    assert row[0] is not None


# ------------------------------------------------------------------
# Filtering
# ------------------------------------------------------------------

def test_silver_filters_null_recording_msid(
    db, tmp_path, bronze_parquet_dir, silver_parquet_dir
):
    import json

    src = tmp_path / "source"
    src.mkdir()

    with (src / "data.json").open("w") as f:
        # valid
        f.write(json.dumps({
            "track_metadata": {"artist_name": "A", "track_name": "T"},
            "listened_at": 100,
            "recording_msid": "rec-1",
            "user_name": "u1",
        }) + "\n")
        # invalid — no recording_msid
        f.write(json.dumps({
            "track_metadata": {"artist_name": "B", "track_name": "T2"},
            "listened_at": 101,
            "recording_msid": None,
            "user_name": "u2",
        }) + "\n")

    Bronze(db, str(src), str(bronze_parquet_dir)).run()
    Silver(db, str(silver_parquet_dir)).run()

    rows = db.fetchone('SELECT COUNT(*) FROM silver.listen_events')[0]
    assert rows == 1


# ------------------------------------------------------------------
# Deduplication
# ------------------------------------------------------------------

def test_silver_deduplicates_by_event_id(
    db, tmp_path, bronze_parquet_dir, silver_parquet_dir
):
    import json

    src = tmp_path / "source"
    src.mkdir()

    event = {
        "track_metadata": {"artist_name": "A", "track_name": "T"},
        "listened_at": 100,
        "recording_msid": "rec-1",
        "user_name": "u1",
    }

    with (src / "data.json").open("w") as f:
        # same event twice
        f.write(json.dumps(event) + "\n")
        f.write(json.dumps(event) + "\n")

    Bronze(db, str(src), str(bronze_parquet_dir)).run()
    Silver(db, str(silver_parquet_dir)).run()

    rows = db.fetchone('SELECT COUNT(*) FROM silver.listen_events')[0]
    assert rows == 1  # deduplicated


# ------------------------------------------------------------------
# Idempotency
# ------------------------------------------------------------------

def test_silver_idempotent(silver_ready, silver_parquet_dir):
    Silver(silver_ready, str(silver_parquet_dir)).run()
    Silver(silver_ready, str(silver_parquet_dir)).run()

    rows = silver_ready.fetchone(
        'SELECT COUNT(*) FROM silver.listen_events'
    )[0]
    assert rows == 2  # still 2, not 4


def test_silver_appends_new_events(
    db, tmp_path, bronze_parquet_dir, silver_parquet_dir
):
    import json

    src = tmp_path / "source"
    src.mkdir()

    # Pehla file
    with (src / "f1.json").open("w") as f:
        f.write(json.dumps({
            "track_metadata": {"artist_name": "A", "track_name": "T"},
            "listened_at": 100,
            "recording_msid": "rec-1",
            "user_name": "u1",
        }) + "\n")

    Bronze(db, str(src), str(bronze_parquet_dir)).run()
    Silver(db, str(silver_parquet_dir)).run()
    assert db.fetchone('SELECT COUNT(*) FROM silver.listen_events')[0] == 1

    # Doosra file
    with (src / "f2.json").open("w") as f:
        f.write(json.dumps({
            "track_metadata": {"artist_name": "B", "track_name": "T2"},
            "listened_at": 200,
            "recording_msid": "rec-2",
            "user_name": "u2",
        }) + "\n")

    Bronze(db, str(src), str(bronze_parquet_dir)).run()
    Silver(db, str(silver_parquet_dir)).run()
    assert db.fetchone('SELECT COUNT(*) FROM silver.listen_events')[0] == 2


def test_silver_run_log(silver_ready, silver_parquet_dir):
    Silver(silver_ready, str(silver_parquet_dir)).run()

    row = silver_ready.fetchone("""
        SELECT status, rows FROM meta.run_log
        WHERE layer = 'silver'
    """)

    assert row[0] == "SUCCESS"
    assert row[1] == 2