#!/usr/bin/env python3
"""
df_main.py
Dynamic Ingress Orchestrator (Object Zero + JSON-driven DFActionMap)
"""

import os
import argparse
from pymavlink import mavutil
from weaving.ingest_df.df_action_map import DFActionMap
from weaving.ingest_df.df_mav_ingress_architect import DFIngressMavArchitect
from vault.clerk_df import ClerkDF
import pandas as pd
from pathlib import Path
import shutil

def build_fmt_registry(bin_path):
    """Extracts the FMT ground truth (dynamic schema)."""
    mlog = mavutil.mavlink_connection(bin_path)
    registry = {}

    while True:
        msg = mlog.recv_match(type='FMT', blocking=False)
        if msg is None:
            break
        name = msg.Name.strip()
        registry[name] = msg.Columns.split(',')

    return registry

def check_bin_replication(vault_b):
    """Old-style row-count check per domain shard."""
    domains = ["NAV_DOMAIN", "EST_DOMAIN", "POWER_DOMAIN", "COM_DOMAIN", "SYS_DOMAIN"]
    vault_path = Path(vault_b)

    print("\n🛰 BIN Replication Check (Rows per Domain Shard)")

    total_rows = 0
    for domain in domains:
        shards = list(vault_path.glob(f"{domain.lower()}_shard_*.parquet"))
        if not shards:
            print(f"{domain}: 0 shards")
            continue

        domain_rows = sum(len(pd.read_parquet(shard)) for shard in shards)
        total_rows += domain_rows
        print(f"{domain}: {len(shards)} shard(s), {domain_rows} rows")

    print(f"✅ Total BIN messages captured across all domains: {total_rows}\n")

def main():
    parser = argparse.ArgumentParser(description="ArduPilot DataFlash Ingress")
    parser.add_argument("bin_path", help="Path to .BIN file")
    args = parser.parse_args()

    # --- Load DFActionMap from JSON ---
    action_map = DFActionMap()  # automatically loads FMT_Library.json
    print(f"🔧 Loaded {len(action_map.msg_to_domain)} MsgType mappings from JSON policy.")

    clerk = ClerkDF()

    print("🧹 Stage 1: Resetting Vault B (Staging)")
    if os.path.exists(clerk.vault_b):
        shutil.rmtree(clerk.vault_b)
    os.makedirs(clerk.vault_b, exist_ok=True)

    print("📡 Stage 2: Discovering FMT Registry")
    fmt_registry = build_fmt_registry(args.bin_path)
    print(f"📊 Discovered {len(fmt_registry)} Message Formats.")

    print("🚀 Stage 3: Running Lossless Ingress Architect")
    architect = DFIngressMavArchitect(
        bin_path=args.bin_path,
        fmt_registry=fmt_registry,
        action_map=action_map  # pass the JSON-driven mapping
    )
    architect.process_flight()

    # --- BIN replication check ---
    check_bin_replication(clerk.vault_b)

    print("🏁 Stage 4: Ingress Complete. Ready for df_refinery.")

if __name__ == "__main__":
    main()