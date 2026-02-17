#!/usr/bin/env python3
import os
import sys
import time
import pandas as pd
from pymavlink.DFReader import DFReader_binary

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

class ComDFArchitect:
    """COM domain ingestion into parquet shards"""
    def __init__(self, bin_path, limit=5000, vault_b=None):
        self.bin_path = bin_path
        self.limit = limit
        self.vault_b = vault_b or os.path.join(ROOT, "bin/vault/vault_b")
        os.makedirs(self.vault_b, exist_ok=True)
        self.buffer = []
        # COM whitelist
        self.whitelist = ["RAD", "RSSI", "MSG", "EV", "RCIN", "RCOUT", "GCS"]

    def record(self, msg, inode):
        d = msg.to_dict()
        d['inode'] = inode
        d['wall_ns'] = time.time_ns()
        d['mavpackettype'] = msg.get_type()
        if 'TimeUS' in d:
            d['timestamp_sec'] = d['TimeUS'] / 1e6
        self.buffer.append(d)
        if len(self.buffer) >= self.limit:
            self.flush()

    def flush(self):
        if not self.buffer:
            return
        df = pd.DataFrame(self.buffer)
        shard_name = f"com_shard_{time.time_ns()}.parquet"
        target_path = os.path.join(self.vault_b, shard_name)
        try:
            df.to_parquet(target_path, index=False)
            self.buffer = []
        except Exception as e:
            print(f"❌ Failed to write shard: {e}")

    def process_flight(self):
        if not os.path.exists(self.bin_path):
            print(f"❌ BIN NOT FOUND: {self.bin_path}")
            return False

        reader = DFReader_binary(self.bin_path)
        raw_count = 0
        captured_count = 0

        print(f"📖 Streaming Binary: {os.path.basename(self.bin_path)}")
        while True:
            msg = reader.recv_msg()
            if msg is None:
                break
            raw_count += 1
            if msg.get_type() in self.whitelist:
                self.record(msg, raw_count)
                captured_count += 1
                if captured_count % 2000 == 0:
                    print(f"  🔹 Processed {raw_count} raw / {captured_count} COM messages...")

        self.flush()
        print(f"\n🛡️ COM INTEGRITY REPORT")
        print(f"Total Raw Packets Read : {raw_count}")
        print(f"COM Packets Captured   : {captured_count}")
        print(f"Coverage Ratio         : {(captured_count/raw_count)*100:.2f}%")
        print(f"\n✅ Extraction complete. {captured_count} messages sharded to {self.vault_b}")
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arch = ComDFArchitect(sys.argv[1])
        arch.process_flight()
