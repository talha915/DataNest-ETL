from pathlib import Path
import duckdb


class Database:

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        if self.db_path.exists():
            print("Database already exists.")
        else:
            print("Creating database.")

        self.conn = duckdb.connect(str(self.db_path))

    def read_json(self, path: str):
        return self.conn.read_json(
            path, format="newline_delimited", sample_size=-1
        )

    def read_parquet(self, path: str):
        return self.conn.read_parquet(path)

    def sql(self, query: str):
        return self.conn.sql(query)

    def execute(self, query: str, params=None):
        if params is None:
            return self.conn.execute(query)
        return self.conn.execute(query, params)

    def fetchone(self, query: str, params=None):
        if params is None:
            return self.execute(query).fetchone()
        return self.execute(query, params).fetchone()

    def close(self):
        self.conn.close()