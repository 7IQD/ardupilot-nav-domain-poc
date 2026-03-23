#!/usr/bin/env python3
"""
df_mav_ingress_architect.py
FMT-Aligned Lossless Ingress
"""

import os
import time
import pandas as pd
from pymavlink import mavutil
from vault.clerk_df import ClerkDF
from weaving.ingest_df.df_action_map import DFActionMap

class DFIngressMavArchitect:
    def __init__(self, bin_path, fmt_registry, action_map, limit=5000):
        self.bin_path = bin_path
        self.fmt_registry = fmt_registry
        self.limit = limit
        self.buffer = []
        self.clerk = ClerkDF()
        self.action_map = action_map

    def flush(self):
        """Writes buffer to domain-specific shards in Vault B."""
        if not self.buffer:
            return

        df = pd.DataFrame(self.buffer)

        for domain, group in df.groupby("domain"):
            shard_name = f"{domain.lower()}_shard_{time.time_ns()}.parquet"
            target_path = os.path.join(self.clerk.vault_b, shard_name)

            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            group.to_parquet(target_path, index=False)

        self.buffer = []

    def process_flight(self):
        """Authoritative sweep: captures every BIN message."""
        if not os.path.exists(self.bin_path):
            print(f"❌ BIN NOT FOUND: {self.bin_path}")
            return

        mlog = mavutil.mavlink_connection(self.bin_path, dialect="ardupilotmega")
        print(f"🚀 Ingress: Processing {len(self.fmt_registry)} MsgTypes...")

        inode = 0
        while True:
            msg = mlog.recv_msg()
            if msg is None:
                break

            m_type = msg.get_type()

            # Skip metadata/protocol messages (FMT handled separately)
            if m_type in ["FMT", "FMTU", "UNIT", "MULT", "PARM"]:
                continue

            inode += 1
            raw = msg.to_dict()
            domain = self.action_map.get_domain_for_msg(m_type)

            # Build Fact-Master ready row
            row = {
                "domain": domain,
                "msg_type": m_type,
                "TimeUS": raw.get("TimeUS", int(getattr(msg, "_timestamp", 0) * 1e6)),
                "inode": inode,
                "wall_ns": time.time_ns(),
                **raw
            }

            self.buffer.append(row)

            if len(self.buffer) >= self.limit:
                self.flush()

        self.flush()  # Final sweep
        print(f"✅ Ingress Complete. Shards written to Vault B.")