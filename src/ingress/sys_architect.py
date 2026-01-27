import pandas as pd
import time
import os

class SysArchitect:
    def __init__(self, limit=25):
        self.buffer = []
        self.limit = limit
        self.vault_b = "bin/vault/vault_b"
        os.makedirs(self.vault_b, exist_ok=True)

    def record(self, msg, inode, mission_id, src_sys, src_comp):
        try:
            data = msg.to_dict()
            data['mission_id'] = mission_id
            data['inode']      = inode
            data['src_sys']    = src_sys
            data['src_comp']   = src_comp
            data['wall_ns']    = time.time_ns()
            data['mavpackettype'] = msg.get_type()

            self.buffer.append(data)

            if len(self.buffer) >= self.limit:
                self.flush()
        except Exception:
            pass

    def flush(self):
        if not self.buffer:
            return
        df = pd.DataFrame(self.buffer)
        filename = f"sys_raw_{time.time_ns()}.parquet"
        df.to_parquet(os.path.join(self.vault_b, filename), index=False)
        self.buffer = []

    def stop(self):
        self.flush()