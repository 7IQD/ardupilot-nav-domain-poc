import pandas as pd
import os
from src.data_mart_engine.database_manager import DatabaseManager

class ComRefinery:
    def __init__(self):
        self.db = DatabaseManager()
        self.warehouse_path = "bin/vault/warehouse/com_master.parquet"

    def refine_comms_data(self):
        if not os.path.exists(self.warehouse_path):
            print(f"❌ Comms Warehouse file missing: {self.warehouse_path}")
            return

        df = pd.read_parquet(self.warehouse_path)
        if df.empty:
            return

        refined_df = pd.DataFrame()

        # 🔹 Metadata
        df['domain'] = 'Comms'
        if 'mission_id' not in df.columns or df['mission_id'].iloc[0] == 'UNKNOWN_MISSION':
            df['mission_id'] = 'MAV_FLIGHT_001'
        refined_df['mission_id'] = df['mission_id'].astype(str)
        refined_df['domain'] = df['domain'].astype(str)

        # 🔹 Communication metrics
        refined_df['frame_id'] = df['frame_id'] if 'frame_id' in df.columns else None
        refined_df['status'] = df['status'] if 'status' in df.columns else None
        refined_df['latency_ms'] = df['latency_ms'].fillna(0.0).astype(float) if 'latency_ms' in df.columns else 0.0
        refined_df['success'] = df['success'].fillna(0).astype(int) if 'success' in df.columns else 0

        # 🔹 Fix for DuckDB string compatibility (suppress Pandas4Warning)
        for col in refined_df.select_dtypes(include='string').columns:
            refined_df[col] = refined_df[col].astype('string')

        print(f"🏗️  Saving Communication facts to Gold Vault...")
        self.db.save_gold_fact("fact_comms_status", refined_df)


if __name__ == "__main__":
    ComRefinery().refine_comms_data()
