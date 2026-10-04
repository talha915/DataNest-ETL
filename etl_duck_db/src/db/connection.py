from pathlib import Path
import duckdb

from ..pipeline.schemas import ALL_SCHEMAS


class Database:

    def __init__(self, db_path: str = "warehouse/music.duckdb"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        if self.db_path.exists():
            print("Database already exists.")
        else:
            print("Creating database.")

        self.conn = duckdb.connect(str(self.db_path))

    def create_schemas(self):
        for cls in ALL_SCHEMAS:
            self.conn.execute(
                f'CREATE SCHEMA IF NOT EXISTS "{cls.name}"'
            )

    def read_json(self, path: str):
        return self.conn.read_json(
            path, format="newline_delimited", sample_size=-1
        )

    def read_parquet(self, path: str):
        return self.conn.read_parquet(path)

    def execute(self, query: str):
        return self.conn.execute(query)

    def close(self):
        self.conn.close()