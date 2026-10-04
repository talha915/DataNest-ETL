import pytest

from pipeline.bronze import Bronze


# ------------------------------------------------------------------
# Basic ingestion
# ------------------------------------------------------------------

def test_bronze_creates_table(db, source_dir, bronze_parquet_dir):
    Bronze(db, str(source_dir), str(bronze_parquet_dir)).run()

    rows = db.fetchone('SELECT COUNT(*) FROM bronze.listen_events')[0]
    assert rows == 2


def test_bronze_creates_parquet_file(db, source_dir, bronze_parquet_dir):
    Bronze(db, str(source_dir), str(bronze_parquet_dir)).run()

    parquet_files = list(bronze_parquet_dir.glob("*.parquet"))
    assert len(parquet_files) == 1
    assert parquet_files[0].name == "dataset.parquet"


def test_bronze_adds_event_id(db, source_dir, bronze_parquet_dir):
    Bronze(db, str(source_dir), str(bronze_parquet_dir)).run()

    row = db.fetchone("""
        SELECT event_id FROM bronze.listen_events LIMIT 1
    """)

    assert row[0] is not None
    assert len(row[0]) == 32  # md5 hash


def test_bronze_adds_source_file(db, source_dir, bronze_parquet_dir):
    Bronze(db, str(source_dir), str(bronze_parquet_dir)).run()

    row = db.fetchone("""
        SELECT DISTINCT _source_file FROM bronze.listen_events
    """)

    assert row[0] == "dataset.parquet"


def test_bronze_adds_ingested_at(db, source_dir, bronze_parquet_dir):
    Bronze(db, str(source_dir), str(bronze_parquet_dir)).run()

    row = db.fetchone("""
        SELECT _ingested_at FROM bronze.listen_events LIMIT 1
    """)

    assert row[0] is not None


# ------------------------------------------------------------------
# Idempotency
# ------------------------------------------------------------------

def test_bronze_idempotent(db, source_dir, bronze_parquet_dir):
    Bronze(db, str(source_dir), str(bronze_parquet_dir)).run()
    Bronze(db, str(source_dir), str(bronze_parquet_dir)).run()

    rows = db.fetchone('SELECT COUNT(*) FROM bronze.listen_events')[0]
    assert rows == 2  # still 2, not 4


def test_bronze_watermark_set(db, source_dir, bronze_parquet_dir):
    Bronze(db, str(source_dir), str(bronze_parquet_dir)).run()

    row = db.fetchone("""
        SELECT last_value FROM meta.watermark
        WHERE layer = 'bronze' AND job_name = 'listen_events'
    """)

    assert row is not None
    assert row[0] == "dataset.parquet"


def test_bronze_run_log_success(db, source_dir, bronze_parquet_dir):
    Bronze(db, str(source_dir), str(bronze_parquet_dir)).run()

    row = db.fetchone("""
        SELECT status, rows FROM meta.run_log
        WHERE layer = 'bronze'
    """)

    assert row[0] == "SUCCESS"
    assert row[1] == 2


# ------------------------------------------------------------------
# Append — new file
# ------------------------------------------------------------------

def test_bronze_appends_new_file(
    db, tmp_path, sample_events, bronze_parquet_dir
):
    import json

    src = tmp_path / "source"
    src.mkdir()

    # Pehla file
    with (src / "file1.json").open("w") as f:
        f.write(json.dumps(sample_events[0]) + "\n")

    Bronze(db, str(src), str(bronze_parquet_dir)).run()
    assert db.fetchone('SELECT COUNT(*) FROM bronze.listen_events')[0] == 1

    # Doosra file
    with (src / "file2.json").open("w") as f:
        f.write(json.dumps(sample_events[1]) + "\n")

    Bronze(db, str(src), str(bronze_parquet_dir)).run()
    assert db.fetchone('SELECT COUNT(*) FROM bronze.listen_events')[0] == 2


# ------------------------------------------------------------------
# Empty source
# ------------------------------------------------------------------

def test_bronze_empty_source(db, tmp_path, bronze_parquet_dir):
    src = tmp_path / "empty"
    src.mkdir()

    Bronze(db, str(src), str(bronze_parquet_dir)).run()

    assert not db.fetchone("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = 'bronze'
          AND table_name = 'listen_events'
    """)[0]