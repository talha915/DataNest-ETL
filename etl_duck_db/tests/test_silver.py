from pathlib import Path
import json

from pipeline.bronze import Bronze
from pipeline.silver import Silver


def setup_bronze(db, tmp_path, parquet_dir, events):
    src = tmp_path / "source"
    src.mkdir(exist_ok=True)

    with (src / "dataset.json").open("w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")

    Bronze(db, str(src), str(parquet_dir)).run()


def test_silver_creates_table(db, tmp_path, sample_events, parquet_dir):
    setup_bronze(db, tmp_path, parquet_dir, sample_events)

    Silver(db, str(tmp_path / "silver")).run()

    rows = db.fetchone('SELECT COUNT(*) FROM silver.listen_events')[0]
    assert rows == 2


def test_silver_flattens_columns(db, tmp_path, sample_events, parquet_dir):
    setup_bronze(db, tmp_path, parquet_dir, sample_events)

    Silver(db, str(tmp_path / "silver")).run()

    row = db.fetchone("""
        SELECT artist_name FROM silver.listen_events LIMIT 1
    """)

    assert row[0] == "Withered Hand"


def test_silver_idempotent(db, tmp_path, sample_events, parquet_dir):
    setup_bronze(db, tmp_path, parquet_dir, sample_events)

    Silver(db, str(tmp_path / "silver")).run()
    Silver(db, str(tmp_path / "silver")).run()

    rows = db.fetchone('SELECT COUNT(*) FROM silver.listen_events')[0]
    assert rows == 2


def test_silver_watermark_set(db, tmp_path, sample_events, parquet_dir):
    setup_bronze(db, tmp_path, parquet_dir, sample_events)

    Silver(db, str(tmp_path / "silver")).run()

    row = db.fetchone("""
        SELECT last_value FROM meta.watermark
        WHERE layer = 'silver'
    """)

    assert row is not None


def test_silver_quarantines_invalid(db, tmp_path, parquet_dir):
    events = [
        {
            "track_metadata": {
                "artist_name": "Artist A",
                "track_name": "Track A",
                "additional_info": {},
            },
            "listened_at": 1555286560,
            "recording_msid": "rec-1",
            "user_name": "user-1",
        },
        {
            "track_metadata": {
                "artist_name": "Artist B",
                "track_name": "Track B",
                "additional_info": {},
            },
            "listened_at": 1555286570,
            "recording_msid": None,
            "user_name": "user-2",
        },
    ]

    setup_bronze(db, tmp_path, parquet_dir, events)

    Silver(db, str(tmp_path / "silver")).run()

    silver = db.fetchone('SELECT COUNT(*) FROM silver.listen_events')[0]
    quarantine = db.fetchone('SELECT COUNT(*) FROM meta.quarantine')[0]

    assert silver == 1
    assert quarantine == 1