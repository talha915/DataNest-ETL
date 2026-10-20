import logging
from pathlib import Path

from ..schemas.tables import (
    Silver as SilverSchema,
    Bronze as BronzeSchema,
    Meta as MetaSchema,
    qualified
)
from ..system import RunLogger, Watermark


log = logging.getLogger(__name__)


LAYER = "silver"
JOB = "listen_events"


class Silver:

    def __init__(self, db, parquet_dir: str):
        self.db = db
        self.sql_dir = Path(__file__).parent.parent / "sql" / "silver"
        self.parquet_dir = Path(parquet_dir)
        self.parquet_dir.mkdir(parents=True, exist_ok=True)
        # Destination Table
        self.table = qualified(SilverSchema, JOB)
        # Source table
        self.source_table = qualified(BronzeSchema, JOB)
        self.quarantine_table = qualified(MetaSchema, "quarantine")

        self.logger = RunLogger(db)
        # Watermark tracks the last processed listened_at timestamp
        # so that only new events are processed on each run.
        self.watermark = Watermark(db)          

    def run(self):
        """
        Silver transformation with logging and error handling
        """
        run_id = self.logger.start(LAYER, JOB)

        try:
            rows = self.load()
            self.logger.success(run_id, rows)
            log.info(f"Silver done. New rows: {rows}")

        except Exception as e:
            self.logger.failure(run_id, str(e))
            log.exception("Silver failed.")
            raise

    def load(self) -> int:
        """
        Load new valid events into Silver and quarantine invalid rows.

        Working Steps:
            - Filter Bronze events by watermark (only new events).
            - Apply valid rows filter.
            - Deduplicate by event_id.
            - Anti-join against existing Silver rows (if table exists).
            - Insert new rows into Silver.
            - Route invalid rows to quarantine.
            - Update watermark to max listened_at.

        Returns:
            Number of rows inserted into Silver.
        """
        # Read last processed timestamp from watermark (default 0)
        last_ts = self.watermark.get(LAYER, JOB) or "0"
        log.info(f"Watermark last_value: {last_ts}")

        # unnest nested json and filter by watermark
        base = self.load_sql("transform").format(
            source_table=self.source_table,
            last_ts=last_ts,
        )

        # Valid rows to ingest into silver table (valid_events is sql query {sql/silver/})
        valid_query = self.load_sql("valid_events").format(source=base)

        # Deduplicate data {sql/silver/}
        dedup = self.load_sql("dedup").format(source=valid_query)
        deduped = f"SELECT * FROM ({dedup})"

        # Final data ready to ingest into silver {sql/silver/}
        if self.exists():
            final = self.load_sql("final_silver").format(
                source=deduped,
                target=self.table,
            )
        else:
            final = deduped

        rel = self.db.sql(final)

        rows = self.db.fetchone(
            f"SELECT COUNT(*) FROM ({rel.sql_query()})"
        )[0]

        if rows > 0:
            # Exclude helper columns not part of the Silver schema.
            select = f"""
                SELECT * EXCLUDE (
                    rn,
                    additional_recording_msid,
                    top_level_recording_msid,
                    source_file_path
                )
                FROM ({rel.sql_query()})
            """

            if not self.exists():
                self.db.execute(f"CREATE TABLE {self.table} AS {select}")
                log.info(f"Created {self.table}")
            else:
                self.db.execute(f"INSERT INTO {self.table} {select}")
                log.info(f"Appended {rows} rows")
        # invalid rows to quarantine.
        self.quarantine(base)

        max_ts = self.db.fetchone(f"""
            SELECT MAX(listened_at) FROM {self.source_table}
        """)[0]

        if max_ts is not None:
            self.watermark.set(LAYER, JOB, str(max_ts))

        return rows

    def quarantine(self, base: str):
        invalid_query = self.load_sql("invalid_events").format(source=base)

        invalid_rows = self.db.fetchone(
            f"SELECT COUNT(*) FROM ({invalid_query})"
        )[0]

        if invalid_rows > 0:
            self.db.execute(
                f"INSERT INTO {self.quarantine_table} {invalid_query}"
            )
            log.info(f"Quarantined {invalid_rows} rows")

    def exists(self) -> bool:
        """
        Check whether the Silver table exists
        """
        row = self.db.fetchone(f"""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = '{SilverSchema.name}'
              AND table_name = '{JOB}'
        """)
        return row[0] > 0

    def load_sql(self, name: str) -> str:
        """
        Load a SQL file from the silver SQL directory.
        Args:
            name: SQL file name without extension.
        Returns:
            SQL file contents as a string.
        """
        return (self.sql_dir / f"{name}.sql").read_text(encoding="utf-8")