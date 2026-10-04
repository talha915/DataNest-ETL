import logging

from pipeline.config import load_config_file
from pipeline.database import Database
from pipeline.schemas import create_schemas, create_tables
from pipeline.bronze import Bronze
from pipeline.silver import Silver


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    cfg = load_config_file()

    db = Database(cfg.database.db_path)

    # 1. Schemas
    create_schemas(db)

    # 2. System tables (run_log, watermark)
    create_tables(db)

    # 3. Bronze
    Bronze(
        db,
        cfg.source.source_path,
        cfg.bronze.data_path,
    ).run()

    Silver(
        db,
        cfg.sql.sql_path,
        cfg.silver.data_path,
    ).run()

    db.close()
    print("Done.")


if __name__ == "__main__":
    main()