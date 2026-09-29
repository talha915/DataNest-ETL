import duckdb
from pathlib import Path

def create_database():
    db_path = Path("database/spotify.duckdb")

    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        print("Creating database")
    else:
        print("Database already exists.")

    con = duckdb.connect(str(db_path))

    return con    