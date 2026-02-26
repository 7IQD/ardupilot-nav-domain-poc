#!/usr/bin/env python3
"""
df_refinery.py
Refinement Entry Point: Staging (Vault B) -> Warehouse (Vault C)
"""

import os
import sys

# --- PATH FIX ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

try:
    from weaving.ingest_df.refiners import DFRefiner
    from weaving.ingest_df.df_action_map import DFActionMap
    from vault.clerk_df import ClerkDF
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def main():
    clerk = ClerkDF()
    refiner = DFRefiner(clerk=clerk, mission_id="manual_run")

    print("=" * 60)
    print("💎 Stage 4: Refining Staged Shards into Warehouse...")
    print("=" * 60)

    # Clean the warehouse before starting
    clerk.clear_warehouse()

    # Refine each domain
    for domain in DFActionMap.get_domains():
        print(f"🛠️  Refining Domain: {domain: <6}")

        # This calls the DuckDB logic we wrote earlier
        refiner.refine_domain(domain)

    print("=" * 60)
    print("🏆 SUCCESS: Data Warehouse is fully populated!")
    print(f"📂 Location: bin/vault/vault_c/")
    print("=" * 60)

if __name__ == "__main__":
    main()