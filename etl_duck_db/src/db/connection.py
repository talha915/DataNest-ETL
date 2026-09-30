import duckdb
from pathlib import Path


class SpotifyDB:

    def __init__(self, db_path: str = "database/spotify.duckdb"):
        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.db_path.exists():
            print("Creating database")
        else:
            print("Database already exists.")

        self.conn = duckdb.connect(str(self.db_path))


    def create_schemas(self):
        self.conn.execute("""
            CREATE SCHEMA IF NOT EXISTS BRONZE;
            CREATE SCHEMA IF NOT EXISTS SILVER;
            CREATE SCHEMA IF NOT EXISTS GOLD;
        """)  

    def close(self):
        self.conn.close()      