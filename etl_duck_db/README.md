# Music Listening ETL

Medallion ETL pipeline using Python and DuckDB.

## Architecture

    JSON → Parquet → Bronze → Silver → Gold

## Setup

Requires Python 3.11+ and uv
    - pip install uv
    - uv sync

## Run

Place source Json file at `data/source/listens/dataset.json`, then:

    uv run python main.py

## Test

    uv run pytest -v

## Output

- `bronze.listen_events` — raw events with `event_id`
- `silver.listen_events` — cleaned, deduplicated events
- `gold.*` — analytical tables
- `meta.quarantine` — invalid rows
- `meta.run_log` — pipeline run history
- `meta.watermark` — incremental state

## Docker (Optional)

The pipeline can be containerized. Source data is not bundles into image so please mount it at run time.

    docker-compose up --build

## Note / Improvement areas:
 - GitHub Actions workflow is not included since the assignment is submitted as a zip file.
 - Could be used with catalogs (similar to Databricks Unity Catalog) for snapshots and time travel over Parquet files.
 -  For slowly changing dimensions, snapshots and Silver upserts could be used to track history and serve valid rows to the Gold layer.
