from dataclasses import dataclass

@dataclass(frozen=True)
class Table:
    name: str

    def table_name(self, schema: str) -> str:
        return (
            f"{schema}.{self.name}"
        )

class DatabaseSchema:
    name: str    