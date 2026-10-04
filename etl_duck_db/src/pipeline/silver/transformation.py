import logging
from pathlib import Path

from ..schemas.tables import Silver as SilverSchema, qualified
from ..system import RunLogger, Watermark


log = logging.getLogger(__name__)


LAYER = "silver"
JOB = "listen_events"


class Silver:

    def __init__(self, db, sql_dir: str, parquet_dir: str):
        self.db = db
        self.sql_dir = Path(__file__).parent.parent / "sql" / "silver"
        self.parquet_dir = Path(parquet_dir)
        self.parquet_dir.mkdir(parents=True, exist_ok=True)

        self.table = qualified(SilverSchema, JOB)
        self.logger = RunLogger(db)
        self.watermark = Watermark(db)

    def run(self):
        run_id = self.logger.start(LAYER, JOB)

        try:
            rows = self._load()
            self.logger.success(run_id, rows)
            log.info("Silver done. New rows: %s", rows)

        except Exception as e:
            self.logger.failure(run_id, str(e))
            log.exception("Silver failed.")
            raise

    # ----------------------------------------------------------

    def _load(self) -> int:
        # 1. last processed timestamp
        last_ts = self.watermark.get(LAYER, JOB) or "1970-01-01 00:00:00"
        log.info("Watermark last_value: %s", last_ts)

        # 2. base silver query
        base = self._load_sql(JOB)

        # 3. filter naye rows (watermark)
        query = f"""
            SELECT * FROM ({base})
            WHERE listened_at_ts > TIMESTAMP '{last_ts}'
        """

        # 4. anti-join — sirf woh rows jo silver mein nahi hain
        if self._exists():
            query = f"""
                SELECT s.* FROM ({query}) s
                LEFT JOIN {self.table} t
                  ON s.user_name = t.user_name
                 AND s.recording_msid = t.recording_msid
                 AND s.listened_at = t.listened_at
                WHERE t.user_name IS NULL
            """

        rel = self.db.sql(query)

        # 5. create / insert
        if not self._exists():
            self.db.execute(
                f"CREATE TABLE {self.table} AS SELECT * FROM ({rel.sql_query()})"
            )
            log.info("Created %s", self.table)
        else:
            self.db.execute(
                f"INSERT INTO {self.table} SELECT * FROM ({rel.sql_query()})"
            )
            log.info("Appended to %s", self.table)

        # 6. rows count
        rows = self.db.fetchone(
            f"SELECT COUNT(*) FROM ({rel.sql_query()})"
        )[0]

        # 7. watermark update — max listened_at_ts
        max_ts = self.db.fetchone(
            f"SELECT MAX(listened_at_ts) FROM ({rel.sql_query()})"
        )[0]

        if max_ts:
            self.watermark.set(LAYER, JOB, str(max_ts))

        return rows

    def _exists(self) -> bool:
        row = self.db.fetchone(f"""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = '{SilverSchema.name}'
              AND table_name = '{JOB}'
        """)
        return row[0] > 0

    def _load_sql(self, name: str) -> str:
        return (self.sql_dir / f"{name}.sql").read_text(encoding="utf-8")