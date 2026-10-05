from datetime import datetime, timezone

from ..schemas.tables import Meta, qualified


class Watermark:
    """
    Tracks last processed file per layer/job.
    """

    def __init__(self, db):
        self.db = db
        self.table = qualified(Meta, "watermark")

    def get(self, layer: str, job_name: str) -> str | None:
        row = self.db.fetchone(
            f"""
            SELECT last_value FROM {self.table}
            WHERE layer = ? AND job_name = ?
            """,
            [layer, job_name],
        )
        return row[0] if row else None

    def set(self, layer: str, job_name: str, last_value: str) -> None:
        self.db.execute(
            f"""
            INSERT INTO {self.table}
            (layer, job_name, last_value, last_run_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (layer, job_name) DO UPDATE SET
                last_value = excluded.last_value,
                last_run_at = excluded.last_run_at
            """,
            [layer, job_name, last_value, datetime.now(timezone.utc)],
        )