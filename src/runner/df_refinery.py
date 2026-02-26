#!/usr/bin/env python3
"""
df_refinery.py
Refinement Entry Point: Staging (Vault B) -> Warehouse (Vault C)
Consolidated for weaving.ingest_df package.
"""

import os
import sys
import shutil

# --- PERMANENT PATH FIX ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # src/runner
SRC_DIR = os.path.dirname(SCRIPT_DIR)                   # src
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# --- IMPORTS (Corrected to use weaving.ingest_df) ---
try:
    from weaving.ingest_df.refiners import DFRefiners
    from weaving.ingest_df.df_action_map import DFActionMap
    from vault.clerk_df import ClerkDF
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    print("Ensure all files are in src/weaving/ingest_df/")
    sys.exit(1)

def main():
    # Initialize Clerk and Refiner
    clerk = ClerkDF()
    refiner = DFRefiners()

    print("=" * 60)
    print("💎 Stage 4: Refining Staged Shards into Warehouse...")
    print("=" * 60)

    # Clean the warehouse (Vault C) before starting
    print("🧹 Preparing Warehouse (Vault C)...")
    if hasattr(clerk, 'clear_warehouse'):
        clerk.clear_warehouse()
    else:
        # Manual fallback if ClerkDF method is missing
        vault_c_path = getattr(clerk, 'vault_c', 'bin/vault/vault_c')
        if os.path.exists(vault_c_path):
            shutil.rmtree(vault_c_path)
        os.makedirs(vault_c_path, exist_ok=True)

    # Process each domain defined in the Action Map
    for domain in DFActionMap.get_domains():
        print(f"🛠️  Refining Domain: {domain: <6}")

        try:
            # This calls the DuckDB logic to merge shards into single tables
            refiner.refine_domain(domain)
        except Exception as e:
            print(f"⚠️  Error refining {domain}: {e}")

    print("=" * 60)
    print("🏆 SUCCESS: Data Warehouse is fully populated!")
    print(f"📂 Location: {clerk.vault_c}")
    print("=" * 60)

if __name__ == "__main__":
    main()