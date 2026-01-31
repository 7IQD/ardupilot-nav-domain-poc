import pandas as pd
import os
from src.data_mart_engine.database_manager import DatabaseManager

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
            print("⚠️ Nav Warehouse data is empty.")
            return

        # 🔹 Aligning Mission ID with the System Domain for joined reporting
        df['domain'] = 'Nav'
        if 'mission_id' not in df.columns or df['mission_id'].iloc[0] == 'UNKNOWN_MISSION':
            df['mission_id'] = 'MAV_FLIGHT_001'

        print(f"📂 Processing {len(df)} Navigation frames for {df['mission_id'].iloc[0]}...")

        refined_df = pd.DataFrame()

        # 1. Timestamp Conversion
        if 'wall_ns' in df.columns:
            refined_df['timestamp'] = pd.to_datetime(df['wall_ns'], unit='ns').dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
        else:
            refined_df['timestamp'] = pd.Timestamp.now().isoformat()

        refined_df['mission_id'] = df['mission_id']
        refined_df['domain'] = df['domain']

        # 2. Precision Metrics
        # Mapping standard ArduPilot/MAVLink variance fields
        refined_df['vel_variance'] = df['velocity_variance'].fillna(0.0) if 'velocity_variance' in df.columns else 0.0
        refined_df['pos_variance'] = df['pos_horiz_variance'].fillna(0.0) if 'pos_horiz_variance' in df.columns else 0.0

        # 3. Nav Status Logic (EKF Health)
        # Threshold: Velocity variance < 0.05 is considered healthy (1), else unhealthy (0)
        # This bit drives the "✅ HEALTHY" vs "⚠️ ISSUES DETECTED" on the dashboard
        refined_df['ekf_healthy'] = (refined_df['vel_variance'] < 0.05).astype(int)

        print(f"🏗️  Saving {len(refined_df)} Navigation facts to Gold Vault...")

        # Overwrites the database for future testing as requested
        self.db.save_gold_fact("fact_nav_precision", refined_df)

if __name__ == "__main__":
    refinery = NavRefinery()
    refinery.refine_navigation_data()