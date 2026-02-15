#!/usr/bin/env python3
import os
import shutil
import duckdb
import time
import sys

# --- DYNAMIC PATH ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

class ClerkDF:
    """
    Handles data orchestration and high-speed consolidation using DuckDB.
    Instruction [2026-01-15]: Overwrites warehouse for testing.
    """
    def __init__(self):
        self.vault_b = os.path.join(PROJECT_ROOT, "bin/vault/vault_b")
        self.warehouse_df = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")
        os.makedirs(self.vault_b, exist_ok=True)
        os.makedirs(self.warehouse_df, exist_ok=True)

    def reset(self):
        """Wipes the engine room for a fresh run."""
        print("🧹 [Clerk] Resetting Vault B and Warehouse DF...")
        for folder in [self.vault_b, self.warehouse_df]:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    path = os.path.join(folder, f)
                    if os.path.isfile(path): os.remove(path)
                    elif os.path.isdir(path): shutil.rmtree(path)
        print("✅ Clerk reset complete.")

    def finalize_run(self, domains=["nav"]):
        """Consolidates fragments into high-speed Parquet masters."""
        for domain in domains:
            self._consolidate(domain)

    def _consolidate(self, domain):
        master_path = os.path.join(self.warehouse_df, f"{domain}_df_master.parquet")
        fragments = [os.path.join(self.vault_b, f) for f in os.listdir(self.vault_b)
                    if f.startswith(f"{domain}_") and f.endswith(".parquet")]

        if not fragments:
            print(f"⚠️  [Clerk] No fragments found for domain: {domain}")
            return

        print(f"📦 [Clerk] Merging {len(fragments)} {domain} shards via DuckDB...")

        try:
            # High-speed deduplication: keeps the most recent wall_ns for every unique inode
            con = duckdb.connect(':memory:')
            con.execute(f"""
                COPY (
                    SELECT * FROM read_parquet({fragments})
                    QUALIFY ROW_NUMBER() OVER (PARTITION BY inode ORDER BY wall_ns DESC) = 1
                    ORDER BY inode ASC
                ) TO '{master_path}' (FORMAT 'PARQUET')
            """)

            # Clean up fragments
            for f in fragments:
                os.remove(f)
            print(f"✅ [Clerk] {domain.upper()} Master Locked: {master_path}")
        except Exception as e:
            print(f"❌ [Clerk] Failed to consolidate {domain}: {e}")