#!/usr/bin/env python3
import os
import sys
import time
import pandas as pd
from pymavlink.DFReader import DFReader_binary

# --- DYNAMIC PATH INJECTION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# --- BASE CLASS REUSE ---
# We use the same LegacyArchitect structure to keep the "KISS" principle
class LegacyArchitect:
    def __init__(self, limit=5000):
        self.buffer = []
        self.limit = limit

    def record(self, msg, inode, mission_id, src_sys, src_comp):
        d = msg.to_dict()
        d['inode'] = inode
        d['wall_ns'] = time.time_ns()
        d['mavpackettype'] = msg.get_type()
        # [2026-01-26] Ensure we include timestamp for time-series analysis
        if 'TimeUS' in d:
            d['timestamp_sec'] = d['TimeUS'] / 1e6
        self.buffer.append(d)
        if len(self.buffer) >= self.limit:
            self.flush()

    def flush(self):
        pass

class EstDFArchitect(LegacyArchitect):
    def __init__(self, bin_path, limit=5000, vault_est=None):
        super().__init__(limit=limit)
        self.bin_path = bin_path
        # Separate vault for Estimator domain to keep testing clean [2026-01-15]
        self.vault_est = vault_est or os.path.join(ROOT, "bin/vault/vault_est")
        os.makedirs(self.vault_est, exist_ok=True)

        # --- EST DOMAIN WHITELIST ---
        # Focused on EKF, Vibrations, and Innovation variances
        self.whitelist = [
            'XKF1', 'XKF2', 'XKF3', 'XKF4',  # EKF3 Primary states
            'XKFS', 'XKFQ',                  # EKF3 Secondary/Status
            'NKF1', 'NKF2', 'NKF3',          # EKF2 (Legacy/Fallback)
            'VIBE',                          # Vibration impacts on estimation
            'ORGN',                          # EKF Origin
            'GPA', 'GPS'                     # GPS accuracy for innovations
        ]

    def process_flight(self):
        if not os.path.exists(self.bin_path):
            print(f"❌ BIN NOT FOUND: {self.bin_path}")
            return False

        reader = DFReader_binary(self.bin_path)
        inode = 0
        recorded_count = 0

        print(f"📖 Streaming EST Domain: {os.path.basename(self.bin_path)}")
        while True:
            msg = reader.recv_msg()
            if msg is None: break
            inode += 1

            m_type = msg.get_type()
            if m_type in self.whitelist:
                self.record(msg, inode, "EST_DOMAIN_LOCKED", 1, 1)
                recorded_count += 1

                if recorded_count % 2000 == 0:
                    print(f"  🔸 EST Progress: {inode} raw / {recorded_count} filtered...")

        self.flush()
        print(f"✅ EST Extraction complete. {recorded_count} shards in {self.vault_est}")
        return True

    def flush(self):
        """Physically write the EST buffer to Parquet shards."""
        if not self.buffer:
            return

        df = pd.DataFrame(self.buffer)
        # Naming: Prefix with 'est' for the orchestrator
        shard_name = f"est_shard_{time.time_ns()}.parquet"
        target_path = os.path.join(self.vault_est, shard_name)

        try:
            # [2026-01-15] Overwrite logic: Parquet provides a clean snapshot per test
            df.to_parquet(target_path, index=False)
            self.buffer = []
        except Exception as e:
            print(f"❌ EST Shard Failure: {e}")

if __name__ == "__main__":
    # Test execution
    if len(sys.argv) > 1:
        arch = EstDFArchitect(sys.argv[1])
        arch.process_flight()