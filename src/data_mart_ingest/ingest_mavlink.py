import sys
import os
import time
import uuid
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pymavlink import mavutil
import logging

# ==========================================================
# BOOTSTRAP PATHING
# ==========================================================
current_file_dir = os.path.dirname(os.path.abspath(__file__))
src_root = os.path.abspath(os.path.join(current_file_dir, '..'))
if src_root not in sys.path:
    sys.path.insert(0, src_root)

try:
    from data_mart_engine.database_manager import DatabaseManager
except ImportError:
    logging.error("DatabaseManager not found. Check pathing.")

# ==========================================================
# REFINED SILVER INGESTOR
# ==========================================================
class SilverIngestor:
    def __init__(self, connection_str="udp:127.0.0.1:14551"):
        self.connection_str = connection_str
        self.warehouse_dir = "bin/vault/warehouse"
        self.buffer = []
        self.inode_counter = 0
        self.batch_size = 50
        self.last_flush_time = time.time()

        # Initialize Vault
        self.db_clerk = DatabaseManager()
        self.db_clerk.ensure_vault_structure()
        # Overwrite on startup for fresh SITL test as per instructions
        self.db_clerk.initialize_warehouse(overwrite=True)

    def connect(self):
        logging.info(f"Connecting to MAVLink: {self.connection_str}")
        self.connection = mavutil.mavlink_connection(self.connection_str)
        self.connection.wait_heartbeat()
        logging.info("✅ Heartbeat received. Ingestor Online.")

    def flush(self):
        """Writes a unique, immutable fragment to the warehouse."""
        if not self.buffer:
            return

        # Unique filename avoids any 'existing_data_behavior' or collision issues
        fragment_id = f"fragment_{int(time.time())}_{uuid.uuid4().hex[:6]}.parquet"
        file_path = os.path.join(self.warehouse_dir, fragment_id)

        try:
            df = pd.DataFrame(self.buffer)
            table = pa.Table.from_pandas(df)

            # Using basic Parquet writer - compatible with all PyArrow versions
            # This creates a NEW file every time, which the Refinery picks up.
            pq.write_table(table, file_path, compression='snappy')

            logging.info(f"💾 Flushed {len(df)} pkts to {fragment_id}")
            self.buffer = []
            self.last_flush_time = time.time()
        except Exception as e:
            logging.error(f"❌ Flush failed: {e}")

    def run(self):
        self.connect()
        try:
            while True:
                msg = self.connection.recv_match(
                    type=['GPS_RAW_INT', 'GLOBAL_POSITION_INT'],
                    blocking=True, timeout=1.0
                )
                if msg:
                    row = msg.to_dict()
                    row['best_ts'] = int(time.time() * 1000)
                    row['mavpackettype'] = msg.get_type()
                    self.buffer.append(row)
                    self.inode_counter += 1

                if len(self.buffer) >= self.batch_size or (time.time() - self.last_flush_time > 5):
                    self.flush()
        except KeyboardInterrupt:
            self.flush()
            sys.exit(0)

if __name__ == "__main__":
    SilverIngestor().run()