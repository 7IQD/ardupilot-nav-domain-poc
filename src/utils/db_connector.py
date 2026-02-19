# src/scorecards/utils/db_connector.py

import duckdb
from pathlib import Path

DB_PATH = Path("bin/vault/warehouse_df/drone_df_views.db")

def get_connection():
    return duckdb.connect(str(DB_PATH), read_only=True)
