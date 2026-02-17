#!/usr/bin/env python3
import os
import shutil
import duckdb
import sys

# --- DYNAMIC PATH ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

class ClerkDF:
    """
    Orchestrates shard consolidation and warehouse management.
    High-speed deduplication using DuckDB ensures the latest packet per inode.
    """

    def __init__(self):
        self.vault_b = os.path.join(PROJECT_ROOT, "bin/vault/vault_b")
        self.warehouse_df = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")
        os.makedirs(self.vault_b, exist_ok=True)
        os.makedirs(self.warehouse_df, exist_ok=True)

    def reset(self):
        """Wipes Vault B and Warehouse DF for a fresh run."""
        print("🧹 [Clerk] Resetting Vault B and Warehouse DF...")
        for folder in [self.vault_b, self.warehouse_df]:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    path = os.path.join(folder, f)
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
        print("✅ [Clerk] Reset complete.")

    def finalize_run(self, domains=["nav"]):
        """Consolidates domain shards into warehouse masters."""
        for domain in domains:
            self._consolidate(domain)

    def _consolidate(self, domain):
        """Internal method to merge domain shards deterministically."""
        master_path = os.path.join(self.warehouse_df, f"{domain}_df_master.parquet")
        fragments = [
            os.path.join(self.vault_b, f)
            for f in os.listdir(self.vault_b)
            if f.startswith(f"{domain}_") and f.endswith(".parquet")
        ]

        if not fragments:
            print(f"⚠️  [Clerk] No fragments found for domain: {domain}")
            return

        print(f"📦 [Clerk] Merging {len(fragments)} {domain} shards via DuckDB...")

        try:
            # High-speed deduplication: keep most recent wall_ns for each inode
            con = duckdb.connect(':memory:')
            fragment_list = ",".join([f"'{f}'" for f in fragments])
            con.execute(f"""
                COPY (
                    SELECT * FROM read_parquet([{fragment_list}])
                    QUALIFY ROW_NUMBER() OVER (PARTITION BY inode ORDER BY wall_ns DESC) = 1
                    ORDER BY inode ASC
                ) TO '{master_path}' (FORMAT 'PARQUET')
            """)

            # Clean up individual shards
            for f in fragments:
                os.remove(f)

            print(f"✅ [Clerk] {domain.upper()} Master Locked: {master_path}")
        except Exception as e:
            print(f"❌ [Clerk] Failed to consolidate {domain}: {e}")
