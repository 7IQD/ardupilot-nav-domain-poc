#!/usr/bin/env python3
"""
df_refinery.py
DuckDB-Based Domain Refinery (Aviation-Grade)

Modified:
- Added RAM safeguards (PRAGMAs) to prevent WSL2 hangs.
- Uses SSD spilling for out-of-core processing.
"""

import sys
import os
import glob
import duckdb
from vault.clerk_df import ClerkDF

# Path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class DFRefiner:
    def __init__(self, clerk, mission_id=None):
        self.clerk = clerk
        self.mission_id = mission_id or "unknown"

    def refine_domain(self, domain):
        domain = domain.upper()

        # ✅ ClerkDF will now point to bin/vault/warehouse_df/
        target = self.clerk.get_warehouse_path(domain)
        os.makedirs(os.path.dirname(target), exist_ok=True)

        shard_pattern = os.path.join(
            self.clerk.vault_b,
            f"{domain.lower()}_domain_shard_*.parquet"
        )

        shard_files = glob.glob(shard_pattern)
        if not shard_files:
            print(f"⏩ [Refiner] {domain}: No shards found. Skipping.")
            return

        print(f"🏗️  [Refiner] {domain} → Streaming {len(shard_files)} shards via DuckDB")

        try:
            # 🔥 CORE ENGINE (Backend-Focused)
            with duckdb.connect() as con:

                # 🛡️ THE SAFETY VALVE (Crucial for WSL2)
                # Limits RAM usage and enables disk-spilling to prevent hangs
                con.execute("PRAGMA memory_limit='4GB';")
                con.execute("PRAGMA temp_directory='/tmp/duckdb_spill';")

                # Step 1: Create virtual source (schema union handled here)
                con.execute(f"""
                    CREATE OR REPLACE VIEW src AS
                    SELECT * FROM read_parquet('{shard_pattern}', union_by_name=True);
                """)

                # Step 2: Deduplicate + time align
                # QUALIFY handles the heavy sorting at the backend level
                con.execute(f"""
                    COPY (
                        SELECT *
                        FROM src
                        QUALIFY ROW_NUMBER() OVER (
                            PARTITION BY TimeUS
                            ORDER BY wall_ns DESC
                        ) = 1
                        ORDER BY TimeUS ASC
                    )
                    TO '{target}'
                    (FORMAT PARQUET, COMPRESSION 'SNAPPY');
                """)

                # Step 3: Simple validation
                count = con.execute(
                    f"SELECT COUNT(*) FROM read_parquet('{target}')"
                ).fetchone()[0]

                print(f"✅ [Refiner] {domain:<6} → {count} rows written to Warehouse")

        except Exception as e:
            print(f"❌ [Refiner] {domain} failed: {e}")


def main():
    clerk = ClerkDF()
    mission_id = os.environ.get("MISSION_ID", "unknown")

    print(f"💎 [Refinery] Mission: {mission_id}")

    refiner = DFRefiner(clerk, mission_id)

    # 👉 One domain at a time (NAV first)
    active_domains = ["NAV"]  # Expand later

    for domain in active_domains:
        refiner.refine_domain(domain)

    print("🏆 [Refinery] Domain processing complete.")


if __name__ == "__main__":
    main()