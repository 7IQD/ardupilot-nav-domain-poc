#!/usr/bin/env python3
import os
import sys
import logging
import time

# --- 1. PATH SETUP ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- 2. IMPORT REFINERS ---
try:
    from src.weaving.ingest_df.refiners import (
        NavRefiner, EstRefiner, SysRefiner, PowerRefiner, ComRefiner
    )
    from src.vault.clerk_df import ClerkDF
    print("✅ Imports successful.")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

# --- 3. PATH CONFIG ---
VAULT_B = os.path.join(PROJECT_ROOT, "bin/vault/vault_b")
WAREHOUSE = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")
os.makedirs(WAREHOUSE, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(message)s")

def run_all_refiners():
    MISSION_ID = f"MISSION_{int(time.time())}"
    logging.info(f"🚀 Starting DF Refinery | Mission: {MISSION_ID}")

    if not os.path.exists(VAULT_B) or not os.listdir(VAULT_B):
        logging.error(f"❌ No shards found in {VAULT_B}. Run df_main.py first!")
        return

    # -------------------------
    # Domain Mapping
    # -------------------------
    domains = [
        (NavRefiner, "NAV"),
        (EstRefiner, "EST"),
        (SysRefiner, "SYS"),
        (PowerRefiner, "POWER"),
        (ComRefiner, "COM")
    ]

    for refiner_cls, name in domains:
        try:
            logging.info(f"🔹 Refining {name}...")
            refiner = refiner_cls(VAULT_B, WAREHOUSE, MISSION_ID, anchor=0)
            refiner.refine()
            logging.info(f"✅ {name} processing complete.")
        except Exception as e:
            logging.warning(f"⚠️ {name} refinement skipped: {e}")

    # -------------------------
    # Cleanup staging
    # -------------------------
    master_files = [f for f in os.listdir(WAREHOUSE) if f.endswith('.parquet')]
    if master_files:
        logging.info("🧹 Masters verified. Cleaning staging shards...")
        clerk = ClerkDF()
        clerk.reset()  # Only clears vault_b
    else:
        logging.error("❌ No Master Parquets found. Skipping cleanup.")

    logging.info(f"\n✅ DF Refinery Complete. Masters preserved in: {WAREHOUSE}")

if __name__ == "__main__":
    run_all_refiners()