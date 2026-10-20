import logging

from src.pipeline.config import load_config_file
from src.pipeline.database import Database
from src.pipeline.schemas import create_schemas, create_tables
from src.pipeline.bronze import Bronze
from src.pipeline.silver import Silver
from src.pipeline.gold import Gold


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
        cfg.silver.data_path,
    ).run()

    Gold(db).run()

    db.close()
    print("Pipeline completed successfully")


if __name__ == "__main__":
    main()