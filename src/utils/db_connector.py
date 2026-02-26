# src/utils/db_connector.py
import duckdb
from pathlib import Path

# ------------------------
# DATABASE PATH
# ------------------------
# parents[2] takes us to the ardupilot-nav-domain-poc root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "bin" / "vault" / "warehouse_df" / "drone_df_views.db"

# ------------------------
# CONNECTION HELPER
# ------------------------
def get_connection(read_only=True):
    """
    Returns a DuckDB connection to the Gold warehouse.

    Parameters:
        read_only (bool): Open connection in read-only mode (default True).

    Raises:
        FileNotFoundError: If the database file does not exist.

    Returns:
        duckdb.DuckDBPyConnection: A DuckDB connection object.
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    return duckdb.connect(str(DB_PATH), read_only=read_only)