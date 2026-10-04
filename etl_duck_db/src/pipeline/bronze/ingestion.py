import logging
from pathlib import Path
from datetime import datetime

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
                out = self.to_parquet(file)
                total_rows += self.load(out)

            self.logger.success(run_id, total_rows)
            log.info(f"Bronze done. Ingested New rows: {total_rows}")

        except Exception as e:
            self.logger.failure(run_id, str(e))
            log.exception("Bronze failed.")
            raise


    def to_parquet(self, file: Path) -> Path:
        now = datetime.now()

        partition_dir = (
            self.parquet_dir
            / f"year={now.year}"
            / f"month={now.month}"
        )
        partition_dir.mkdir(parents=True, exist_ok=True)

        out = partition_dir / f"{file.stem}.parquet"

        if out.exists():
            log.info(f"Skip parquet: {out.name}")
            return out

        self.db.read_json(str(file)).write_parquet(str(out))
        return out

    def load(self, parquet_file: Path) -> int:
        print(parquet_file)
        if self.already_loaded(str(parquet_file)):
            log.info(f"Already loaded: {parquet_file}")
            return 0

        rel = self.db.read_parquet(str(parquet_file))
        last_ts = self.watermark.get(LAYER, JOB) or "1970-01-01"
        query = f"""
            SELECT *,
                   md5(
                       coalesce(user_name, '') || '|' ||
                       coalesce(recording_msid, '') || '|' ||
                       cast(listened_at AS VARCHAR)
                   ) AS event_id,
                   '{parquet_file}' AS source_file_path,
                   current_timestamp AS ingested_at
            FROM ({rel.sql_query()})
            WHERE listened_at > {last_ts}
        """

        if not self.exists():
            self.db.execute(f"CREATE TABLE {self.table} AS {query}")
            log.info(f"Created {self.table}")
        else:
            self.db.execute(f"INSERT INTO {self.table} {query}")
            log.info(f"Appended: {parquet_file}")

        rows = self.db.fetchone(
            f"SELECT COUNT(*) FROM ({query})"
        )[0]

        max_ts = self.db.fetchone(f"SELECT MAX(listened_at) FROM ({query})")[0]
        self.watermark.set(LAYER, JOB, str(max_ts))
        return rows

    def exists(self) -> bool:
        row = self.db.fetchone(f"""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = '{BronzeSchema.name}'
              AND table_name = '{JOB}'
        """)
        return row[0] > 0

    def already_loaded(self, file_path: str) -> bool:
        if not self.exists():
            return False

        row = self.db.fetchone(
            f"SELECT 1 FROM {self.table} "
            f"WHERE source_file_path = ? LIMIT 1",
            [file_path],
        )
        return row is not None

# data\bronze\listen_events\year=2026\month=10\dataset.parquet    