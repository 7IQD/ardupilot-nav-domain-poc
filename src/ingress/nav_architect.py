import pandas as pd
import time
import os

class NavArchitect:
    def __init__(self, limit=50):
        self.buffer = []
        self.limit = limit
        self.vault_b = "bin/vault/vault_b"
        os.makedirs(self.vault_b, exist_ok=True)

    def record(self, msg, inode, mission_id, src_sys, src_comp):
        """
        CONTRACT:
        1. Universal Spine: inode
        2. Dimensionality: src_sys, src_comp
        3. Temporality: wall_ns, best_ts
        """
        try:
            data = msg.to_dict()

            # --- IDENTITY & SOURCE ---
            data['mission_id'] = mission_id
            data['inode']      = inode
            data['src_sys']    = src_sys
            data['src_comp']   = src_comp

            # --- PROTOCOL METADATA ---
            data['mavpackettype'] = msg.get_type()
            data['seq_no']        = msg.get_seq()
            data['wall_ns']       = time.time_ns()

            # Extract the best available internal clock
            data['best_ts'] = getattr(
                msg, 'time_boot_ms',
                getattr(msg, 'time_usec',
                        getattr(msg, 'timestamp', None))
            )

            self.buffer.append(data)

            if len(self.buffer) >= self.limit:
                self.flush()

        except Exception:
            pass

    def flush(self):
        if not self.buffer:
            return
        df = pd.DataFrame(self.buffer)
        filename = f"nav_raw_{time.time_ns()}.parquet"
        df.to_parquet(os.path.join(self.vault_b, filename), index=False)
        self.buffer = []

    def stop(self):
        self.flush()