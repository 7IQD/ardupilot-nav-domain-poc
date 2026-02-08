import duckdb
import os
import pandas as pd

class DatabaseManager:
    def __init__(self):
        # 🔹 Fixed Absolute Path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Moves up from src/data_mart_engine to project root, then into bin
        self.db_path = os.path.normpath(os.path.join(current_dir, "..", "..", "bin", "nav_domain.db"))

        # Ensure the bin directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def save_gold_fact(self, table_name, df_input):
        if df_input.empty:
            return

        # 🔹 Connect to the absolute path
        conn = duckdb.connect(self.db_path)
        try:
            # Explicit registration avoids 'str not recognized' errors
            conn.register("df_view", df_input)

            # Drop & recreate to fulfill the 'overwrite for testing' requirement
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df_view")

            conn.unregister("df_view")
            print(f"✅ [DB] Saved {len(df_input)} rows to {table_name} at {self.db_path}")
        except Exception as e:
            print(f"❌ [DB] Critical Error saving {table_name}: {e}")
        finally:
            conn.close()

    def query_gold(self, query: str) -> pd.DataFrame:
        conn = duckdb.connect(self.db_path)
        try:
            return conn.execute(query).df()
        except Exception as e:
            print(f"⚠️ [DB] Query Error: {e}")
            return pd.DataFrame()
        finally:
            conn.close()