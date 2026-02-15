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

# --- ROBUST BASE CLASS ---
try:
    from nav_architect_poc import NavArchitect as LegacyArchitect
except ImportError:
    # If legacy is missing, we provide a fully functional mini-architect
    class LegacyArchitect:
        def __init__(self, limit=5000):
            self.buffer = []
            self.limit = limit

        def record(self, msg, inode, mission_id, src_sys, src_comp):
            d = msg.to_dict()
            d['inode'] = inode
            d['wall_ns'] = time.time_ns()
            d['mavpackettype'] = msg.get_type()
            self.buffer.append(d)
            if len(self.buffer) >= self.limit:
                self.flush()

        def flush(self):
            # This will be overridden by NavDFArchitect
            pass

class NavDFArchitect(LegacyArchitect):
    def __init__(self, bin_path, limit=5000, vault_b=None):
        super().__init__(limit=limit)
        self.bin_path = bin_path
        # Use absolute path for vault_b to avoid relative path drift
        self.vault_b = vault_b or os.path.join(ROOT, "bin/vault/vault_b")
        os.makedirs(self.vault_b, exist_ok=True)
        self.whitelist = ['ATT', 'POS', 'GPS', 'XKF1', 'NKF1', 'AHR2', 'CTUN', 'MAG']

    def process_flight(self):
        if not os.path.exists(self.bin_path):
            print(f"❌ BIN NOT FOUND: {self.bin_path}")
            return False

        reader = DFReader_binary(self.bin_path)
        inode = 0
        recorded_count = 0

        print(f"📖 Streaming Binary: {os.path.basename(self.bin_path)}")
        while True:
            msg = reader.recv_msg()
            if msg is None: break
            inode += 1

            m_type = msg.get_type()
            if m_type in self.whitelist:
                # This calls LegacyArchitect.record which appends to self.buffer
                self.record(msg, inode, "FDR_FLIGHT_LOCKED", 1, 1)
                recorded_count += 1

                if recorded_count % 2000 == 0:
                    print(f"  🔹 Processed {inode} raw / {recorded_count} NAV messages...")

        # Final flush for the remaining messages in buffer
        self.flush()
        print(f"✅ Extraction complete. {recorded_count} messages sharded to {self.vault_b}")
        return True

    def flush(self):
        """CRITICAL: Physically write the buffer to vault_b."""
        if not self.buffer:
            return

        # Convert buffer to DataFrame
        df = pd.DataFrame(self.buffer)

        # Naming: must start with 'nav' for the orchestrator to find it
        shard_name = f"nav_shard_{time.time_ns()}.parquet"
        target_path = os.path.join(self.vault_b, shard_name)

        try:
            df.to_parquet(target_path, index=False)
            # print(f"      💾 Saved shard: {shard_name} ({len(df)} rows)")
            self.buffer = [] # Reset buffer
        except Exception as e:
            print(f"❌ Failed to write shard: {e}")