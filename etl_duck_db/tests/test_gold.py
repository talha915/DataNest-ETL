import json

from pipeline.bronze import Bronze
from pipeline.silver import Silver
from pipeline.gold import Gold


def setup_silver(db, tmp_path, parquet_dir):
    src = tmp_path / "source"
    src.mkdir(exist_ok=True)

    event = {
        "track_metadata": {
            "artist_name": "Artist A",
            "track_name": "Track A",
            "additional_info": {},
        },
        "listened_at": 1551398400,
        "recording_msid": "rec-1",
        "user_name": "user-1",
    }

    with (src / "dataset.json").open("w", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    Bronze(db, str(src), str(parquet_dir)).run()
    Silver(db, str(tmp_path / "silver")).run()


def test_gold_tables_created(db, tmp_path, parquet_dir):
    setup_silver(db, tmp_path, parquet_dir)

    Gold(db).run()

    tables = db.conn.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'gold'
    """).fetchall()

    names = [t[0] for t in tables]

    assert "top_users" in names
    assert "daily_active_users" in names


def test_top_users(db, tmp_path, parquet_dir):
    setup_silver(db, tmp_path, parquet_dir)

    Gold(db).run()

    row = db.fetchone("""
        SELECT user_name, listen_count FROM gold.top_users
    """)

    assert row[0] == "user-1"
    assert row[1] == 1