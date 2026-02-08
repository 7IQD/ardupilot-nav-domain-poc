import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

class EstimatorArchitect:
    """
    Records Estimator messages (EKF, vibration, AHRS) into Vault B (Silver).
    """
    def __init__(self, limit=50):
        self.buffer = []
        self.limit = limit
        self.inode_counter = 0
        self.vault_b = "bin/vault/vault_b"
        os.makedirs(self.vault_b, exist_ok=True)

    def record(self, msg, inode, mission_id, src_sys, src_comp):
        """
        Append a message to the buffer with universal spine metadata.
        Flush automatically when buffer reaches limit.
        """
        row = msg.to_dict()
        row.update({
            "inode": inode,
            "mission_id": mission_id,
            "src_sys": src_sys,
            "src_comp": src_comp,
            "mavpackettype": msg.get_type(),
            "seq_no": getattr(msg, 'seq', None),
            "wall_ns": pd.Timestamp.now().value,  # nanoseconds
            "best_ts": getattr(
                msg, 'time_boot_ms',
                getattr(msg, 'time_usec',
                        getattr(msg, 'timestamp', None))
            )
        })
        self.buffer.append(row)
        if len(self.buffer) >= self.limit:
            self.flush()

    def flush(self):
        """
        Writes buffered Estimator messages to Vault B in Parquet format.
        """
        if not self.buffer:
            return
        df = pd.DataFrame(self.buffer)
        file_name = f"est_raw_{int(pd.Timestamp.now().timestamp())}.parquet"
        file_path = os.path.join(self.vault_b, file_name)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, file_path, compression='snappy')
        self.buffer = []

    def stop(self):
        """
        Flush any remaining messages before shutdown.
        """
        self.flush()
