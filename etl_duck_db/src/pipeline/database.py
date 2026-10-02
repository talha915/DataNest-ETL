from pathlib import Path
from typing import Any

import duckdb


class Database:

    def __init__(self, path: str):
        database_path = Path(path)

        database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.conn = duckdb.connect(str(database_path))

    def sql(self, query: str):

        return self.conn.sql(query)

    def read_json(self, path: str,**kwargs: Any):
        """
        Read JSON/NDJSON into a DuckDB Relation.
        """
        return self.conn.read_json(path, **kwargs)

    def table(self, table_name: str):
        """
        Return a Relation for an existing DuckDB table.
        """
        return self.conn.table(table_name)

    def execute(self, query: str, parameters: list[Any] | tuple[Any, ...] | None = None):
        """
        Execute imperative or parameterized SQL.
        """
        if parameters is None:
            return self.conn.execute(
                query
            )

        return self.conn.execute(
            query,
            parameters,
        )

    def begin(self) -> None:
        self.conn.execute("BEGIN")

    def commit(self) -> None:
        self.conn.execute("COMMIT")

    def rollback(self) -> None:
        self.conn.execute("ROLLBACK")

    def initialize_schemas(self, bronze_schema: str, silver_schema: str, gold_schema: str, pipeline_schema: str) -> None:
        schemas = [
            bronze_schema,
            silver_schema,
            gold_schema,
            pipeline_schema,
        ]

        for schema in schemas:
            self.execute(
                f'CREATE SCHEMA IF NOT EXISTS "{schema}"'
            )

    def close(self) -> None:
        self.conn.close()

    def enter(self):
        return self

    def exit(self):
        self.close()