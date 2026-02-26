import pandas as pd
import os
from data_mart_engine.database_manager import DatabaseManager

class NavRefinery:
    def __init__(self):
        self.db = DatabaseManager()
        self.warehouse_path = "bin/vault/warehouse/nav_master.parquet"

    def refine_navigation_data(self):
        if not os.path.exists(self.warehouse_path):
            print(f"❌ Nav Warehouse file missing: {self.warehouse_path}")
            return

        df = pd.read_parquet(self.warehouse_path)
        if df.empty:
            return

        # 🔹 Standardize Mission/Domain
        df['domain'] = 'Nav'
        if 'mission_id' not in df.columns or df['mission_id'].iloc[0] == 'UNKNOWN_MISSION':
            df['mission_id'] = 'MAV_FLIGHT_001'

        refined_df = pd.DataFrame()

        # 1. Timestamp
        if 'wall_ns' in df.columns:
            refined_df['timestamp'] = pd.to_datetime(df['wall_ns'], unit='ns').dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
        else:
            refined_df['timestamp'] = pd.Timestamp.now().strftime('%Y-%m-%dT%H:%M:%S.%f')

        # 2. Metadata
        refined_df['mission_id'] = df['mission_id'].astype(str)
        refined_df['domain'] = df['domain'].astype(str)

        # 3. Metrics
        refined_df['vel_variance'] = df['velocity_variance'].fillna(0.0).astype(float) if 'velocity_variance' in df.columns else 0.0
        refined_df['pos_variance'] = df['pos_horiz_variance'].fillna(0.0).astype(float) if 'pos_horiz_variance' in df.columns else 0.0
        refined_df['ekf_healthy'] = (refined_df['vel_variance'] < 0.05).astype(int)

        # 🔹 DuckDB-compatible string casting (suppresses Pandas4Warning)
        for col in refined_df.select_dtypes(include='string').columns:
            refined_df[col] = refined_df[col].astype('string')

        print(f"🏗️  Saving facts to Gold Vault...")
        self.db.save_gold_fact("fact_nav_precision", refined_df)
        print("✅ Refinement Success.")


if __name__ == "__main__":
    NavRefinery().refine_navigation_data()
