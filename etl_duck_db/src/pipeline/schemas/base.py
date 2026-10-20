from dataclasses import dataclass


@dataclass
class Table:
    name: str
    is_source_table: bool = False
    ddl: str = ""


class DatabaseSchema:
    """
    Base class for a database schema (e.g. Bronze, Silver, Gold, Meta)
    """
    name: str = ""
    tables: list[Table] = []

    @classmethod
    def table(cls, name: str) -> Table:
        """
        Search table by name
        Args:
            name: Table name
        Returns:
            The matching Table object.
        raises: value error if table not found
        """
        for t in cls.tables:
            if t.name == name:
                return t
        raise ValueError(f"Table {name} not found in {cls.name}")


ALL_SCHEMAS = []


def create_schemas(db):
    """
    Create schemas (bronze, silver, gold, meta)
    """
    for cls in ALL_SCHEMAS:
        db.execute(f'CREATE SCHEMA IF NOT EXISTS "{cls.name}"')


def create_tables(db):
    """
    Create meta tables (run_log, watermark).
    """
    from .tables import Meta

    for table in Meta.tables:
        db.execute(f"""
            CREATE TABLE IF NOT EXISTS
            "{Meta.name}"."{table.name}" (
                {table.ddl}
            )
        """)