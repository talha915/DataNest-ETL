class BronzeLayer:

    def __init__(self, db):
        self.db = db

    def ingest(self, json_file: str, table_name: str):
        self.db.conn.execute(f"""
            CREATE OR REPLACE TABLE bronze.{table_name} AS
            SELECT *
            FROM read_json_auto(
                '{json_file}', 
                format='newline_delimited',
                sample_size=-1);
        """)