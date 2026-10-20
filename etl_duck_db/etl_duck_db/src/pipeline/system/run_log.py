import uuid
from datetime import datetime, timezone

from ..schemas.tables import Meta, qualified


class RunLogger:
    """
    Writes pipeline runs to meta.run_log.
    """

    def __init__(self, db):
        self.db = db
        self.table = qualified(Meta, "run_log")

    def start(self, layer: str, job_name: str) -> str:
        run_id = str(uuid.uuid4())

        self.db.execute(
            f"""
            INSERT INTO {self.table}
            (run_id, layer, job_name, status, started_at)
            VALUES (?, ?, ?, 'RUNNING', ?)
            """,
            [run_id, layer, job_name, datetime.now(timezone.utc)],
        )

        return run_id

    def success(self, run_id: str, rows: int) -> None:
        self.db.execute(
            f"""
            UPDATE {self.table}
            SET status = 'SUCCESS',
                completed_at = ?,
                rows = ?
            WHERE run_id = ?
            """,
            [datetime.now(timezone.utc), rows, run_id],
        )

    def failure(self, run_id: str, error: str) -> None:
        self.db.execute(
            f"""
            UPDATE {self.table}
            SET status = 'FAILED',
                completed_at = ?,
                error = ?
            WHERE run_id = ?
            """,
            [datetime.now(timezone.utc), error, run_id],
        )