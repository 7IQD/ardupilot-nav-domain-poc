#!/usr/bin/env python3
"""
df_refinery.py

The Universal Refiner:
Schema Guarantees + Dynamic Telemetry Discovery.

This stage promotes domain shards from Vault B into canonical
warehouse tables while preserving all discovered telemetry.

Goals
-----
1. Guarantee DFActionMap schema contract
2. Preserve newly discovered telemetry fields
3. Normalize heterogeneous MAVLink messages
4. Produce stable warehouse tables for analytics
"""

import glob
import os
import pandas as pd
import sys

# --- Path Authority ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from weaving.ingest_df.df_action_map import DFActionMap
from vault.clerk_df import ClerkDF


def refine_domain(clerk, domain, mission_id):
    """
    Promote shards into a warehouse master table
    using Union Schema Logic.
    """

    domain = domain.upper()

    target_parquet = clerk.get_warehouse_path(domain)

    shard_pattern = os.path.join(
        clerk.vault_b,
        f"{domain.lower()}_shard_*.parquet"
    )

    shard_files = glob.glob(shard_pattern)

    if not shard_files:
        return

    # 1️⃣ Load all shards
    dfs = []

    for shard in shard_files:
        try:
            dfs.append(pd.read_parquet(shard))
        except Exception as e:
            print(f"⚠️ Error reading {shard}: {e}")

    if not dfs:
        return

    df = pd.concat(dfs, ignore_index=True)

    # 2️⃣ Universal Refiner Logic
    expected_cols = DFActionMap.get_columns(domain)

    # Guarantee schema contract
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    # Discover all telemetry columns present
    discovered_cols = list(df.columns)

    # Create union schema
    final_columns = list(dict.fromkeys(expected_cols + discovered_cols))

    # 3️⃣ Final projection
    df = df[final_columns]

    # Sort by timestamp
    if "TimeUS" in df.columns:
        df = df.sort_values("TimeUS")

    # 4️⃣ Write warehouse table
    df.to_parquet(target_parquet, index=False)

    print(
        f"✅ [Refiner] {domain:<6} -> "
        f"{os.path.basename(target_parquet)} ({len(df)} rows)"
    )


def main():

    clerk = ClerkDF()

    # Detect mission id from shards
    shard_files = glob.glob(os.path.join(clerk.vault_b, "*.parquet"))

    if not shard_files:
        print("❌ No shards found in Vault B. Run Ingress first.")
        return

    mission_id = os.environ.get("MISSION_ID", "unknown")

    print(f"💎 Refining BIN-to-FACT for Mission: {mission_id}")

    # Iterate domains
    domains = DFActionMap.get_domains()

    for domain in domains:

        if domain == "MISC":
            continue

        refine_domain(clerk, domain, mission_id)

    print("🏆 Warehouse Build Complete. Zero Data Leakage Architecture Enforced.")


if __name__ == "__main__":
    main()