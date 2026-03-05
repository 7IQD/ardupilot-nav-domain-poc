import duckdb
from pathlib import Path

# Resolve absolute path to project root
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
DB_PATH = PROJECT_ROOT / "bin" / "vault" / "drone_df_views.db"

def get_connection(read_only=True):
    """Factory to return a DuckDB connection. Depends on nothing."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"❌ Database not found at {DB_PATH}")
    return duckdb.connect(str(DB_PATH), read_only=read_only)