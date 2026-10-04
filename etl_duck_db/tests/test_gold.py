import pytest

from pipeline.bronze import Bronze
from pipeline.silver import Silver
from pipeline.gold import Gold


@pytest.fixture
def gold_ready(db, source_dir, bronze_parquet_dir, silver_parquet_dir):
    Bronze(db, str(source_dir), str(bronze_parquet_dir)).run()
    Silver(db, str(silver_parquet_dir)).run()
    return db


# ------------------------------------------------------------------
# Top users
# ------------------------------------------------------------------

def test_top_users(gold_ready):
    Gold(gold_ready).run()

    rows = gold_ready.fetchall("""
        SELECT user_name, listen_count FROM gold.top_users
    """)

    assert len(rows) == 1
    assert rows[0][0] == "user-1"
    assert rows[0][1] == 2


# ------------------------------------------------------------------
# Users active on date
# ------------------------------------------------------------------

def test_users_active_on_date(gold_ready):
    Gold(gold_ready).run()

    rows = gold_ready.fetchall(
        'SELECT * FROM gold.users_active_on_date'
    )

    assert len(rows) == 1
    # 2019-03-01 mein sample data nahi hai → 0
    # ya date check karo


# ------------------------------------------------------------------
# First song
# ------------------------------------------------------------------

def test_users_first_song(gold_ready):
    Gold(gold_ready).run()

    rows = gold_ready.fetchall("""
        SELECT user_name, first_artist, first_track
        FROM gold.users_first_song
    """)

    assert len(rows) == 1
    assert rows[0][0] == "user-1"
    assert rows[0][1] == "Artist A"


# ------------------------------------------------------------------
# Top days
# ------------------------------------------------------------------

def test_users_top_days(gold_ready):
    Gold(gold_ready).run()

    rows = gold_ready.fetchall("""
        SELECT "user", number_of_listens, date
        FROM gold.users_top_days
    """)

    assert len(rows) >= 1
    assert rows[0][0] == "user-1"


# ------------------------------------------------------------------
# Daily active users
# ------------------------------------------------------------------

def test_daily_active_users(gold_ready):
    Gold(gold_ready).run()

    rows = gold_ready.fetchall("""
        SELECT date, number_active_users, percentage_active_users
        FROM gold.daily_active_users
    """)

    assert len(rows) >= 1
    assert all(r[0] is not None for r in rows)


# ------------------------------------------------------------------
# Run log
# ------------------------------------------------------------------

def test_gold_run_log(gold_ready):
    Gold(gold_ready).run()

    rows = gold_ready.fetchall("""
        SELECT job_name, status FROM meta.run_log
        WHERE layer = 'gold'
        ORDER BY job_name
    """)

    assert len(rows) == 5
    assert all(r[1] == "SUCCESS" for r in rows)