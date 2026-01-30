import sys
import os
import time
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import logging

# ==========================================================
# BOOTSTRAP PATHING
# ==========================================================
current_file_dir = os.path.dirname(os.path.abspath(__file__))
src_root = os.path.abspath(os.path.join(current_file_dir, '..', '..'))

if src_root not in sys.path:
    sys.path.insert(0, src_root)

# ==========================================================
# NAV REFINERY LOGIC
# ==========================================================
class NavRefinery:
    """
    ROLE: The Alchemist.
    CONCEPT: Converts raw Silver Parquet fragments into Gold Insights.
    CONTRACT: Aggregates GPS/EKF data and calculates precision metrics.
    """
    def __init__(self, mission_id="MARATHON_POC"):
        self.mission_id = mission_id
        self.silver_dir = "bin/vault/warehouse"
        self.gold_dir = f"bin/vault/gold/nav_ekf/{self.mission_id}"

        if not os.path.exists(self.gold_dir):
            os.makedirs(self.gold_dir, exist_ok=True)

    def refine_ekf_precision(self):
        """
        The method the Orchestrator calls.
        Uses an explicit schema to prevent 'cast_null' errors.
        """
        try:
            # 1. Load the Silver Dataset
            if not os.path.exists(self.silver_dir) or not os.listdir(self.silver_dir):
                logging.warning("Refinery: Silver warehouse empty. Waiting for data...")
                return

            # --- HARDENED SCHEMA ---
            # This prevents the 'Unsupported cast from int64 to null' error
            # by defining types before the data is even touched.
            my_schema = pa.schema([
                ("lat", pa.int64()),
                ("lon", pa.int64()),
                ("alt", pa.int64()),
                ("best_ts", pa.int64()),
                ("mavpackettype", pa.string()),
                ("inode", pa.int64())
            ])

            # Use the schema to unify fragments even if some have nulls
            dataset = ds.dataset(
                self.silver_dir,
                format="parquet",
                schema=my_schema
            )

            # Convert to Pandas for calculation
            df = dataset.to_table().to_pandas()

            if df.empty:
                return

            # 2. Extract Navigation packets
            gps_raw = df[df['mavpackettype'] == 'GPS_RAW_INT'].copy()
            gps_filt = df[df['mavpackettype'] == 'GLOBAL_POSITION_INT'].copy()

            if gps_raw.empty or gps_filt.empty:
                logging.info(f"Refinery: Awaiting packet pairs (Current: {len(df)} pkts)")
                return

            # 3. Precision Math
            latest_raw = gps_raw.iloc[-1]
            latest_filt = gps_filt.iloc[-1]

            # Scaling: 1e7 for Lat/Lon, 1000 for Alt (mm to m)
            lat_err = abs(latest_raw['lat'] - latest_filt['lat']) / 1e7
            lon_err = abs(latest_raw['lon'] - latest_filt['lon']) / 1e7
            alt_err = abs(latest_raw['alt'] - latest_filt['alt']) / 1000.0

            gold_record = {
                'mission_id': self.mission_id,
                'timestamp_ms': latest_filt['best_ts'],
                'lat_err_deg': lat_err,
                'lon_err_deg': lon_err,
                'alt_err_m': alt_err,
                'total_ingested': len(df)
            }

            # 4. Save to Gold Vault
            gold_df = pd.DataFrame([gold_record])
            gold_file = os.path.join(self.gold_dir, "fact_nav_precision.parquet")

            # Atomic write of the latest refined fact
            gold_df.to_parquet(gold_file, index=False)

            logging.info(f"✨ GOLD UPDATE | LatErr: {lat_err:.8f} deg | Packets: {len(df)}")

        except Exception as e:
            logging.error(f"❌ Refinery Cycle Failed: {e}")

if __name__ == "__main__":
    refinery = NavRefinery()
    refinery.refine_ekf_precision()