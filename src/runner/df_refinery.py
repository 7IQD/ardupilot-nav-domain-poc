#!/usr/bin/env python3
import os
import sys

# --- BOOTSTRAP: Anchor to Project Root ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../"))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ------------------------------------------
from weaving.ingest_df.refiners import DFRefiner
from weaving.ingest_df.df_action_map import DFActionMap
from glob import glob
from weaving.ingest_df.refiners import DFRefiner
from weaving.ingest_df.df_action_map import DFActionMap
from vault.clerk_df import ClerkDF

def main():
    clerk = ClerkDF()

    # 1. Detect mission context
    shard_files = glob(os.path.join(clerk.vault_b, "*.parquet"))
    if not shard_files:
        print("❌ No shards found in Vault B. Ingress failed?")
        return

    mission_id = os.path.basename(shard_files[0]).split("_")[2].split(".")[0]
    refiner = DFRefiner(clerk=clerk, mission_id=mission_id)

    print(f"💎 Refining BIN-to-FACT for Mission: {mission_id}")

    # 2. Iterate through all domains + MISC
    # Logic: If a message wasn't claimed by NAV/PWR/etc, it will be in the MISC shard.
    for domain in DFActionMap.get_domains():
        refiner.refine_domain(domain)

    print("🏆 Warehouse Build Complete. Zero Data Leakage Architecture Enforced.")

if __name__ == "__main__":
    main()