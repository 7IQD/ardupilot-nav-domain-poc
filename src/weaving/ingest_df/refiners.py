import os
import glob
import duckdb
from weaving.ingest_df.df_action_map import DFActionMap

class DFRefiner:
    def __init__(self, clerk, mission_id):
        """
        Initializes the Refiner using Clerk's path authority.
        Uses in-memory DuckDB for high-speed Parquet transformation.
        """
        self.clerk = clerk
        self.mission_id = mission_id
        self.con = duckdb.connect(database=':memory:')

    def refine_domain(self, domain):
        """
        Promotes Vault B shards to Vault C Masters.
        Implements NULL-filling for domains and Universal Capture for MISC.
        """
        domain = domain.upper()

        # 1. Resolve Paths
        target_parquet = self.clerk.get_warehouse_path(domain)
        shard_pattern = os.path.join(self.clerk.vault_b, f"{domain.lower()}_shard_*.parquet")

        # 2. Simple Safety Check
        if not glob.glob(shard_pattern):
            # print(f"ℹ️ No shards found for {domain}, skipping.")
            return

        # 3. Hardware Column Discovery (FMT Alignment)
        try:
            raw_info = self.con.execute(f"DESCRIBE SELECT * FROM read_parquet('{shard_pattern}')").fetchall()
            shard_cols = [row[0] for row in raw_info]
        except Exception as e:
            print(f"⚠️ Error reading shards for {domain}: {e}")
            return

        # 4. Build Selection Clause (Zero-Drop Logic)
        if domain == "MISC":
            # Universal Capture: Everything + msg_type
            select_clause = "*"
        else:
            # Domain Capture: Ensure all ActionMap columns exist (even as NULL)
            target_columns = DFActionMap.get_columns(domain)
            select_parts = []
            for col in target_columns:
                if col in shard_cols:
                    select_parts.append(f'"{col}"')
                else:
                    select_parts.append(f'NULL AS "{col}"')
            select_clause = ", ".join(select_parts)

        # 5. Atomic Promotion (Deduplicated by TimeUS)
        try:
            self.con.execute(f"""
                COPY (
                    WITH local_shards AS (
                        SELECT
                            '{self.mission_id}' AS mission_id,
                            {select_clause},
                            wall_ns
                        FROM read_parquet('{shard_pattern}')
                    )
                    SELECT * EXCLUDE(wall_ns) FROM local_shards
                    QUALIFY ROW_NUMBER() OVER (PARTITION BY TimeUS ORDER BY wall_ns DESC) = 1
                    ORDER BY TimeUS
                ) TO '{target_parquet}' (FORMAT 'PARQUET');
            """)
            print(f"✅ [Refiner] {domain: <6} -> {os.path.basename(target_parquet)}")
        except Exception as e:
            print(f"❌ [Refiner] Failed to refine {domain}: {e}")