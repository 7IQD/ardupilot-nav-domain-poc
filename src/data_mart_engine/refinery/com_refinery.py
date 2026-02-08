import pandas as pd
import os
from src.data_mart_engine.database_manager import DatabaseManager

class ComRefinery:
    def __init__(self):
        self.db = DatabaseManager()
        self.warehouse_path = "bin/vault/warehouse/com_master.parquet"

    def refine_communication_data(self):
        if not os.path.exists(self.warehouse_path):
            print(f"❌ Com Warehouse file missing: {self.warehouse_path}")
            return

        df = pd.read_parquet(self.warehouse_path)
        if df.empty: return

        print(f"📂 Processing {len(df)} Comms frames...")
        refined_df = pd.DataFrame()

        # 1. Timestamp & Metadata
        if 'wall_ns' in df.columns:
            refined_df['timestamp'] = pd.to_datetime(df['wall_ns'], unit='ns').dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
        else:
            refined_df['timestamp'] = pd.Timestamp.now().isoformat()

        refined_df['mission_id'] = df['mission_id'].astype(str) if 'mission_id' in df.columns else "MAV_FLIGHT_001"
        refined_df['domain'] = 'COM'

        # 2. Link Quality Metrics
        refined_df['rssi'] = df['rssi'].fillna(0).astype(int) if 'rssi' in df.columns else 0
        refined_df['remrssi'] = df['remrssi'].fillna(0).astype(int) if 'remrssi' in df.columns else 0
        refined_df['drop_rate'] = df['fixed'].fillna(0).astype(float) if 'fixed' in df.columns else 0.0

        print(f"🏗️  Saving Communication facts...")
        self.db.save_gold_fact("fact_comms_status", refined_df)

if __name__ == "__main__":
    ComRefinery().refine_communication_data()