import pandas as pd
import time
import os

class NavArchitect:
    def __init__(self, limit=50):
        self.buffer = []
        self.limit = limit
        self.vault_b = "bin/vault/vault_b"
        os.makedirs(self.vault_b, exist_ok=True)

    def ingest(self, msg):
        try:
            data = msg.to_dict()
            data['wall_ns'] = time.time_ns()
            data['msg_type'] = msg.get_type()
            self.buffer.append(data)

            if len(self.buffer) >= self.limit:
                self.flush()
        except:
            pass

    def flush(self):
        if not self.buffer: return
        df = pd.DataFrame(self.buffer)
        filename = f"nav_raw_{time.strftime('%H%M%S')}_{time.time_ns()}.parquet"
        df.to_parquet(os.path.join(self.vault_b, filename))
        self.buffer = []

    def stop(self):
        self.flush()