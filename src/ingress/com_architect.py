import pandas as pd
import os
import time

class ComArchitect:
    def __init__(self, limit=50):
        self.buffer = []
        self.limit = limit
        # Symmetric staging area (Matches NavArchitect and SysArchitect)
        self.vault_b = "bin/vault/vault_b"
        os.makedirs(self.vault_b, exist_ok=True)

    def record(self, msg, inode, mission_id, src_sys, src_comp):
        """
        CONTRACT:
        Maintains the Universal Spine (inode) while capturing
        domain-specific communication metrics.
        """
        try:
            data = msg.to_dict()
            data.update({
                # --- IDENTITY & SOURCE ---
                "mission_id": mission_id,
                "inode": inode,
                "src_sys": src_sys,
                "src_comp": src_comp,

                # --- TEMPORAL SPINE ---
                "wall_ns": time.time_ns(),
                "best_ts": getattr(msg, "time_boot_ms",
                           getattr(msg, "time_usec",
                           getattr(msg, "timestamp", None))),

                # --- PROTOCOL METADATA ---
                "mavpackettype": msg.get_type(),
                "domain": "com",

                # --- DOMAIN SPECIFIC: COMMS HEALTH ---
                "rssi": getattr(msg, "rssi", -100),
                "latency_ms": getattr(msg, "latency", 0.0),
                "drop_count": getattr(msg, "drop_count", 0),
            })

            self.buffer.append(data)

            if len(self.buffer) >= self.limit:
                self.flush()
        except Exception:
            # Silent failure to ensure SITL loop continuity
            pass

    def flush(self):
        """
        Pushes fragments to Vault B with the exact 'com_raw_' prefix
        required by the Clerk.
        """
        if not self.buffer:
            return

        df = pd.DataFrame(self.buffer)

        # KEY SYMMETRY: Prefix must be 'com_raw_' for Clerk to identify it
        filename = f"com_raw_{time.time_ns()}.parquet"

        target_path = os.path.join(self.vault_b, filename)
        df.to_parquet(target_path, index=False)

        self.buffer = []

    def stop(self):
        """Final flush on user interrupt."""
        self.flush()