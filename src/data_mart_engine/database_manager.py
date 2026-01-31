import duckdb
import os
import pandas as pd

class DatabaseManager:
    def __init__(self):
        # Reliable pathing from project root
        self.root_dir = os.getcwd()
        self.db_path = os.path.join(self.root_dir, "bin", "nav_domain.db")

        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def save_gold_fact(self, table_name, df):
        """Saves or Re-aligns the table if schema is mismatched."""
        if df.empty: return
        conn = duckdb.connect(self.db_path)
        try:
            # Check for existing table
            exists = conn.execute(f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{table_name}'").fetchone()[0]
            if not exists:
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
            else:
                # Simple count check for self-healing
                db_cols = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
                if len(db_cols) == len(df.columns):
                    cols = ", ".join(df.columns)
                    conn.execute(f"INSERT INTO {table_name} ({cols}) SELECT * FROM df")
                else:
                    conn.execute(f"DROP TABLE {table_name}")
                    conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
            print(f"✅ [DB] Saved data to {table_name}")
        finally:
            conn.close()

    def query_gold(self, query: str) -> pd.DataFrame:
        """
        Executes query and returns a Pandas DataFrame.
        """
        conn = duckdb.connect(self.db_path)
        try:
            # .df() is the DuckDB native way to return a Pandas DataFrame
            return conn.execute(query).df()
        except Exception as e:
            print(f"⚠️ [DB] Query Error: {e}")
            return pd.DataFrame() # Return empty to prevent dashboard crash
        finally:
            conn.close()