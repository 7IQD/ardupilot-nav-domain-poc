import pandas as pd
import os
from src.data_mart_engine.database_manager import DatabaseManager

class EstRefinery:
    def __init__(self):
        self.db = DatabaseManager()
        self.warehouse_path = "bin/vault/warehouse/est_master.parquet"

    def refine_estimator_data(self):
        print(f"🔍 Checking Warehouse: {self.warehouse_path}")
        if not os.path.exists(self.warehouse_path):
            print("❌ Error: Warehouse Parquet file not found!")
            return

        df = pd.read_parquet(self.warehouse_path)
        if df.empty:
            print("⚠️ Warning: Warehouse file exists but is empty.")
            return

        print(f"📂 Processing {len(df)} rows from Silver Tier...")

        # 1. Standardize Timestamp
        if 'wall_ns' in df.columns:
            ts_series = pd.to_datetime(df['wall_ns'], unit='ns').dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
        else:
            print("🕒 Estimator has no native clock. Synthesizing timestamp...")
            now_str = pd.Timestamp.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            ts_series = pd.Series([now_str] * len(df))

        # 2. Build the refined structure
        refined_df = pd.DataFrame({
            'timestamp': ts_series,
            'mission_id': df['mission_id'] if 'mission_id' in df.columns else pd.Series(["default_mission"] * len(df)),
            'xacc': df['xacc'].fillna(0.0).astype(float) if 'xacc' in df.columns else 0.0,
            'yacc': df['yacc'].fillna(0.0).astype(float) if 'yacc' in df.columns else 0.0,
            'zacc': df['zacc'].fillna(0.0).astype(float) if 'zacc' in df.columns else 0.0,
            'roll': df['roll'].fillna(0.0).astype(float) if 'roll' in df.columns else 0.0,
            'pitch': df['pitch'].fillna(0.0).astype(float) if 'pitch' in df.columns else 0.0,
            'yaw': df['yaw'].fillna(0.0).astype(float) if 'yaw' in df.columns else 0.0
        })

        # 🔹 DuckDB-compatible string casting (suppress Pandas4Warning)
        for col in refined_df.select_dtypes(include='string').columns:
            refined_df[col] = refined_df[col].astype('string')

        # 3. Save to Gold Vault
        print(f"🏗️  Updating Gold Vault: fact_estimator")
        self.db.save_gold_fact("fact_estimator", refined_df)
        print("✅ Refinement Success.")


if __name__ == "__main__":
    EstRefinery().refine_estimator_data()
