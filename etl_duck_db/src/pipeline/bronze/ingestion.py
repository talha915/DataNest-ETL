import logging
from pathlib import Path

from ..schemas.tables import Bronze as BronzeSchema, qualified
from ..system import RunLogger, Watermark


log = logging.getLogger(__name__)


LAYER = "bronze"
JOB = "listen_events"


class Bronze:

    def __init__(self, db, source_path: str, parquet_dir: str):
        self.db = db
        self.source = Path(source_path)
        self.parquet_dir = Path(parquet_dir)
        self.parquet_dir.mkdir(parents=True, exist_ok=True)

        self.table = qualified(BronzeSchema, JOB)
        self.logger = RunLogger(db)
        self.watermark = Watermark(db)

    def run(self):
        run_id = self.logger.start(LAYER, JOB)

        try:
            total_rows = 0

            for file in sorted(self.source.glob("*.json")):
                self.to_parquet(file)
                total_rows += self._load(file)

            self.logger.success(run_id, total_rows)
            log.info("Bronze done. New rows: %s", total_rows)

        except Exception as e:
            self.logger.failure(run_id, str(e))
            log.exception("Bronze failed.")
            raise

    # ----------------------------------------------------------

    def to_parquet(self, file: Path):
        out = self.parquet_dir / f"{file.stem}.parquet"

        if out.exists():
            log.info("Skip parquet: %s", out.name)
            return

        self.db.read_json(str(file)).write_parquet(str(out))
        log.info("Parquet: %s", out.name)

    def _load(self, file: Path) -> int:
        out = self.parquet_dir / f"{file.stem}.parquet"

        # watermark check
        if self._already_loaded(out.name):
            log.info("Watermark says already loaded: %s", out.name)
            return 0

        rel = self.db.read_parquet(str(out))

        select = f"""
            SELECT *,
                   '{out.name}' AS _source_file,
                   current_timestamp AS _ingested_at
            FROM ({rel.sql_query()})
        """

        if not self._exists():
            self.db.sql(f"CREATE TABLE {self.table} AS {select}")
            log.info("Created %s", self.table)
        else:
            self.db.sql(f"INSERT INTO {self.table} {select}")
            log.info("Appended: %s", out.name)

        # rows count
        rows = self.db.fetchone(
            f"SELECT COUNT(*) FROM ({select})"
        )[0]

        # watermark update
        self.watermark.set(LAYER, JOB, out.name)

        return rows

    def _exists(self) -> bool:
        row = self.db.fetchone(f"""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = '{BronzeSchema.name}'
              AND table_name = '{JOB}'
        """)
        return row[0] > 0

    def _already_loaded(self, file_name: str) -> bool:
        if not self._exists():
            return False

        row = self.db.fetchone(
            f"SELECT 1 FROM {self.table} "
            f"WHERE _source_file = ? LIMIT 1",
            [file_name],
        )
        return row is not None