import pandas as pd
import os
import numpy as np
from src.data_mart_engine.database_manager import DatabaseManager

class SysRefinery:
    def __init__(self):
        self.db = DatabaseManager()
        self.warehouse_path = "bin/vault/warehouse/sys_master.parquet"

    def refine_system_data(self):
        if not os.path.exists(self.warehouse_path):
            print(f"❌ System Warehouse file missing: {self.warehouse_path}")
            return

        df = pd.read_parquet(self.warehouse_path)
        if df.empty:
            return

        # 🔹 Mission Alignment
        df['domain'] = 'Sys'
        if 'mission_id' not in df.columns or df['mission_id'].iloc[0] == 'UNKNOWN_MISSION':
            df['mission_id'] = 'MAV_FLIGHT_001'

        refined_df = pd.DataFrame()

        # 1. Timestamp Conversion
        if 'wall_ns' in df.columns:
            refined_df['timestamp'] = pd.to_datetime(df['wall_ns'], unit='ns').dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
        else:
            refined_df['timestamp'] = pd.Timestamp.now().isoformat()

        refined_df['mission_id'] = df['mission_id']
        refined_df['domain'] = df['domain']

        # 2. 🛡️ Data Quality Flagging (Zero-Drop Logic)
        # Identify rows that lack actual battery/load data before we fill them
        refined_df['is_imputed'] = (
            df['voltage_battery'].isin([-1, 0]) |
            df['current_battery'].isin([-1, 0]) |
            df['load'].isin([65535])
        ).astype(int)

        # 3. Unit Conversion with NaN handling
        refined_df['voltage'] = df['voltage_battery'].replace([-1, 0], np.nan) / 1000.0
        refined_df['current'] = df['current_battery'].replace([-1, 0], np.nan) / 100.0
        refined_df['cpu_load'] = df['load'].replace(65535, np.nan) / 10.0

        # 4. 🔄 Zero-Drop Forward Fill
        # We preserve the row count but use the last known good value for metrics
        refined_df['voltage'] = refined_df['voltage'].ffill().bfill()
        refined_df['current'] = refined_df['current'].ffill().bfill()
        refined_df['cpu_load'] = refined_df['cpu_load'].ffill().bfill()

        # Final safety for empty starts
        refined_df = refined_df.fillna(0.0)

        print(f"🏗️  Processed {len(refined_df)} frames. (Imputed: {refined_df['is_imputed'].sum()})")

        # Overwriting the database table for this testing cycle
        self.db.save_gold_fact("fact_sys_status", refined_df)

if __name__ == "__main__":
    SysRefinery().refine_system_data()