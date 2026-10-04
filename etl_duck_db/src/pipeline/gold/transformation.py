import logging
from pathlib import Path

from ..schemas.tables import Gold as GoldSchema, qualified
from ..system import RunLogger, Watermark


log = logging.getLogger(__name__)


LAYER = "gold"

JOBS = [
    "top_users",
    "users_active_on_date",
    "users_first_song",
    "users_top_days",
    "daily_active_users",
]


class Gold:

    def __init__(self, db):
        self.db = db
        self.sql_dir = Path(__file__).parent.parent / "sql" / "gold"

        self.logger = RunLogger(db)
        self.watermark = Watermark(db)

    def run(self):
        for job in JOBS:
            self._run_job(job)

    def _run_job(self, job: str):
        run_id = self.logger.start(LAYER, job)

        try:
            table = qualified(GoldSchema, job)
            query = (self.sql_dir / f"{job}.sql").read_text(encoding="utf-8")

            self.db.execute(
                f"CREATE OR REPLACE TABLE {table} AS {query}"
            )

            rows = self.db.fetchone(
                f"SELECT COUNT(*) FROM {table}"
            )[0]

            self.watermark.set(LAYER, job, str(rows))
            self.logger.success(run_id, rows)

            log.info("Gold %s done. Rows: %s", job, rows)

        except Exception as e:
            self.logger.failure(run_id, str(e))
            log.exception("Gold %s failed.", job)
            raise