from pathlib import Path
from pipeline.bronze import Bronze


def test_bronze_creates_table(db, source_dir, parquet_dir):
    Bronze(db, str(source_dir), str(parquet_dir)).run()

    rows = db.fetchone('SELECT COUNT(*) FROM bronze.listen_events')[0]
    assert rows == 2


def test_bronze_creates_parquet_file(db, source_dir, parquet_dir):
    Bronze(db, str(source_dir), str(parquet_dir)).run()

    parquet_files = list(parquet_dir.glob("**/*.parquet"))
    assert len(parquet_files) == 1
    assert parquet_files[0].name == "dataset.parquet"


def test_bronze_adds_event_id(db, source_dir, parquet_dir):
    Bronze(db, str(source_dir), str(parquet_dir)).run()

    rows = db.conn.execute(
        "SELECT event_id FROM bronze.listen_events"
    ).fetchall()

    assert len(rows) == 2
    for (event_id,) in rows:
        assert event_id is not None
        assert len(event_id) == 32


def test_bronze_adds_source_file_path(db, source_dir, parquet_dir):
    Bronze(db, str(source_dir), str(parquet_dir)).run()

    rows = db.conn.execute(
        'SELECT DISTINCT source_file_path FROM bronze.listen_events'
    ).fetchall()

    assert len(rows) == 1
    assert "dataset.parquet" in rows[0][0]


def test_bronze_idempotent(db, source_dir, parquet_dir):
    Bronze(db, str(source_dir), str(parquet_dir)).run()
    Bronze(db, str(source_dir), str(parquet_dir)).run()

    rows = db.fetchone('SELECT COUNT(*) FROM bronze.listen_events')[0]
    assert rows == 2


def test_bronze_run_log(db, source_dir, parquet_dir):
    Bronze(db, str(source_dir), str(parquet_dir)).run()

    row = db.fetchone("""
        SELECT status, rows FROM meta.run_log
        WHERE layer = 'bronze'
    """)

    assert row[0] == "SUCCESS"
    assert row[1] == 2