import pandas as pd
import time
import os

class NavArchitect:
    def __init__(self, limit=200):
        self.buffer = []
        self.limit = limit

        # --- PATH RESOLUTION & LOGGING ---
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.vault_b = os.path.join(self.root, "bin", "vault", "vault_b")
        os.makedirs(self.vault_b, exist_ok=True)
        print(f"🛠️  [INIT] Architect Active. Target: {self.vault_b}")

    def record(self, msg, inode, mission_id, src_sys, src_comp):
        """
        Converts live or BIN message to Warehouse-ready dictionary.
        """
        try:
            data = msg.to_dict()

            # --- METADATA INJECTION ---
            data['mission_id'] = mission_id
            data['inode']      = inode
            data['src_sys']    = src_sys
            data['src_comp']   = src_comp
            data['mavpackettype'] = msg.get_type()

            # --- SEQUENCE RESOLUTION ---
            # BIN files do not have get_seq(), use inode as fallback
            data['seq_no'] = getattr(msg, 'get_seq', lambda: inode)()

            data['wall_ns'] = time.time_ns()

            # --- TIMESTAMP NORMALIZATION ---
            data['best_ts'] = getattr(msg, 'time_boot_ms',
                                getattr(msg, 'time_usec',
                                    getattr(msg, 'TimeUS',
                                        getattr(msg, 'timestamp', 0))))

            self.buffer.append(data)

            # --- BATCH FLUSH ---
            if len(self.buffer) >= self.limit:
                print(f"  📥 [BUFFER] {self.limit} reached. Flushing...")
                self.flush()

        except Exception as e:
            print(f"  ❌ [RECORD ERROR] Inode {inode} failed: {e}")

    def flush(self):
        """Writes current buffer to Parquet atomically."""
        if not self.buffer:
            return

        batch_size = len(self.buffer)
        try:
            df = pd.DataFrame(self.buffer)
            filename = f"nav_raw_{time.time_ns()}.parquet"
            path = os.path.join(self.vault_b, filename)
            df.to_parquet(path, index=False, engine='pyarrow')

            if os.path.exists(path):
                print(f"  💾 [FLUSH SUCCESS] {batch_size} rows -> {filename}")
            else:
                print(f"  ⚠️  [FLUSH WARNING] File system did not acknowledge write: {filename}")

            self.buffer = []

        except Exception as e:
            print(f"  🔥 [CRITICAL FLUSH ERROR] Batch lost: {e}")
            raise e

    def stop(self):
        """Flush any remaining messages."""
        if self.buffer:
            print(f"  🏁 [STOP] Flushing remaining {len(self.buffer)} messages...")
            self.flush()
        else:
            print(f"  🏁 [STOP] Buffer empty. Pipeline clean.")
