import os
import shutil
import duckdb
import sys
import threading
import time

class Clerk:
    def __init__(self):
        self.vault_b = 'bin/vault/vault_b'
        self.warehouse = 'bin/vault/warehouse'
        os.makedirs(self.vault_b, exist_ok=True)
        os.makedirs(self.warehouse, exist_ok=True)

    def reset(self):
        """Sterilizes staging and warehouse per [2026-01-15]."""
        print("🧹 Clerk is clearing Vault B and Warehouse...")
        for folder in [self.vault_b, self.warehouse]:
            for f in os.listdir(folder):
                path = os.path.join(folder, f)
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
        print("✅ Clerk reset successful.")

    def commit(self, domain):
        """
        Merges fragments into the master file using DuckDB.
        Enforces ordering by the Universal Spine (inode).
        """
        master_path = os.path.join(self.warehouse, f"{domain}_master.parquet")
        fragment_pattern = os.path.join(self.vault_b, f"{domain}_raw_*.parquet")

        # Check for presence of fragments manually to avoid DuckDB glob errors
        fragments_exist = any(f.startswith(f"{domain}_raw_") for f in os.listdir(self.vault_b))
        if not fragments_exist:
            print(f"ℹ️  No new fragments for {domain}. Skipping.")
            return

        print(f"📦 Consolidating {domain} fragments into {master_path}", end=' ', flush=True)

        # Heartbeat dots
        stop_heartbeat = False
        def heartbeat():
            while not stop_heartbeat:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.5)
        t = threading.Thread(target=heartbeat)
        t.start()

        try:
            # Use DuckDB for high-performance sorting and merging
            if not os.path.exists(master_path):
                # Fresh master: Sort by inode to ensure spine integrity
                duckdb.query(f"""
                    COPY (
                        SELECT * FROM read_parquet('{fragment_pattern}')
                        ORDER BY inode ASC
                    ) TO '{master_path}' (FORMAT 'PARQUET')
                """)
            else:
                # Append to existing master: Deduplicate and re-sort
                temp_path = f"{master_path}.tmp"
                duckdb.query(f"""
                    COPY (
                        SELECT * FROM (
                            SELECT * FROM read_parquet('{master_path}')
                            UNION ALL
                            SELECT * FROM read_parquet('{fragment_pattern}')
                        )
                        QUALIFY ROW_NUMBER() OVER (PARTITION BY inode ORDER BY wall_ns DESC) = 1
                        ORDER BY inode ASC
                    ) TO '{temp_path}' (FORMAT 'PARQUET')
                """)
                os.replace(temp_path, master_path)  # Atomic swap
        finally:
            stop_heartbeat = True
            t.join()
            print(" ✅")

    def finalize_run(self):
        """Finalizes the mission by committing all domains and clearing Vault B."""
        print("\n🏁 [CLERK] Finalizing run: Consolidating warehouse...")

        # Process domains defined in Orchestrator gates
        for domain in ['nav', 'sys']:
            try:
                self.commit(domain)
            except Exception as e:
                print(f"\n⚠️  Error consolidating {domain}: {e}")

        # Clear Vault B fragments after successful commit
        print("🧹 Clearing staging area (Vault B)...")
        for f in os.listdir(self.vault_b):
            if f.endswith(".parquet"):
                os.remove(os.path.join(self.vault_b, f))

        print("✅ Vault B cleared. Warehouse ready for next mission.")
        print("🏁 [CLERK] Warehouse is now locked and ready.")