#!/usr/bin/env python3
"""
df_mav_ingress_architect.py
Authoritative MAVLink Ingress - Protocol Layer
"""

import os
import time
import pandas as pd
from pymavlink import mavutil
from vault.clerk_df import ClerkDF

class DFIngressMavArchitect:
    def __init__(self, bin_path, domain_key, msg_types, limit=5000):
        self.bin_path = bin_path
        self.domain_key = domain_key.upper()
        self.msg_types = msg_types
        self.limit = limit
        self.buffer = []
        self.clerk = ClerkDF()

    def flush(self):
        """Writes current buffer to a unique Parquet shard in Vault B."""
        if not self.buffer:
            return

        # Convert buffer to DataFrame - pandas handles the varying columns automatically
        df = pd.DataFrame(self.buffer)

        # Create a unique filename using nanoseconds to avoid collisions
        shard_name = f"{self.domain_key.lower()}_shard_{time.time_ns()}.parquet"
        target_path = os.path.join(self.clerk.vault_b, shard_name)

        # Ensure the directory exists and write to Parquet
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        df.to_parquet(target_path, index=False)

        # Clear buffer for next batch
        self.buffer = []

    def process_flight(self):
        """
        AUTHORITATIVE DECODE:
        Uses mavutil to extract all fields. Metadata is prepended,
        and the raw message payload is unpacked entirely.
        """
        if not os.path.exists(self.bin_path):
            print(f"❌ BIN NOT FOUND: {self.bin_path}")
            return

        print(f"🚀 Ingress Decode [{self.domain_key}]")

        # Load the BIN with ardupilotmega dialect for full message support
        mlog = mavutil.mavlink_connection(self.bin_path, dialect="ardupilotmega")
        inode = 0

        while True:
            msg = mlog.recv_msg()
            if msg is None:
                break

            msg_type = msg.get_type()

            # Filter based on the Domain Mapping (e.g., if POWER, only take BAT)
            if msg_type not in self.msg_types:
                continue

            inode += 1
            raw = msg.to_dict()

            # THE LOSSLESS WRAPPER
            # We explicitly define tracking keys, then dump the rest of the message payload
            row = {
                "msg_type": msg_type,
                "TimeUS": raw.get("TimeUS", int(getattr(msg, "_timestamp", 0) * 1e6)),
                "inode": inode,
                "wall_ns": time.time_ns(),
                **raw  # <--- Dumps Roll, Pitch, Volt, Curr, etc. into the row
            }

            self.buffer.append(row)

            # Flush periodically to keep memory usage low
            if len(self.buffer) >= self.limit:
                self.flush()

        # Final flush for remaining messages
        self.flush()
        print(f"✅ {self.domain_key} ingress complete ({inode} messages).")