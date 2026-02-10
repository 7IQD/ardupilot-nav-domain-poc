import pandas as pd
import os
from src.data_mart_engine.database_manager import DatabaseManager

class SysRefinery:
    def __init__(self):
        self.db = DatabaseManager()
        self.warehouse_path = "bin/vault/warehouse/sys_master.parquet"

    def refine_system_data(self):
        if not os.path.exists(self.warehouse_path):
            print(f"❌ Sys Warehouse file missing: {self.warehouse_path}")
            return

        df = pd.read_parquet(self.warehouse_path)
        if df.empty:
            print("⚠️ Warning: Warehouse file exists but is empty.")
            return

        print(f"📂 Processing {len(df)} System health frames...")
        refined_df = pd.DataFrame()

        # 1. Timestamp & Metadata
        if 'wall_ns' in df.columns:
            refined_df['timestamp'] = pd.to_datetime(df['wall_ns'], unit='ns').dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
        else:
            refined_df['timestamp'] = pd.Timestamp.now().strftime('%Y-%m-%dT%H:%M:%S.%f')

        refined_df['mission_id'] = df['mission_id'] if 'mission_id' in df.columns else pd.Series(["MAV_FLIGHT_001"] * len(df))
        refined_df['domain'] = 'SYS'

        # 2. Performance Metrics
        refined_df['load'] = df['load'].fillna(0.0).astype(float) if 'load' in df.columns else 0.0
        refined_df['battery_volt'] = df['voltage_battery'].fillna(0.0).astype(float) if 'voltage_battery' in df.columns else 0.0
        refined_df['cpu_overload'] = (refined_df['load'] > 900).astype(int)

        # 🔹 DuckDB-compatible string casting (suppress Pandas4Warning)
        for col in refined_df.select_dtypes(include='string').columns:
            refined_df[col] = refined_df[col].astype('string')

        print(f"🏗️  Saving System facts to Gold Vault...")
        self.db.save_gold_fact("fact_system_health", refined_df)
        print("✅ Refinement Success.")


if __name__ == "__main__":
    SysRefinery().refine_system_data()
