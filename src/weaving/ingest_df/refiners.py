import os
import duckdb
from weaving.ingest_df.df_action_map import DFActionMap

class DFRefiner:
    def __init__(self, clerk, mission_id):
        """
        Initializes the Refiner with path management and mission context.
        """
        self.clerk = clerk
        self.mission_id = mission_id
        self.con = duckdb.connect()

    def refine_domain(self, domain):
        """
        Refines shards into a master table using schema-aware aliasing.
        """
        # 1. Get the target schema (what we WANT)
        target_columns = DFActionMap.get_columns(domain)
        if not target_columns:
            return

        # 2. Identify the source shards (what we HAVE)
        shard_pattern = os.path.join(self.clerk.vault_b, f"{domain.lower()}_shard_*.parquet")

        # 3. Schema-Awareness: Get actual column names from the shards
        try:
            raw_schema_query = f"DESCRIBE SELECT * FROM read_parquet('{shard_pattern}')"
            raw_schema = [row[0] for row in self.con.execute(raw_schema_query).fetchall()]
        except Exception as e:
            print(f"❌ {domain} schema check failed: {e}")
            return

        # 4. Build the dynamic SELECT statement
        mapping = DFActionMap.SOURCE_MAPPING.get(domain, {})
        select_parts = []

        for col in target_columns:
            source_field = mapping.get(col)

            if source_field and source_field in raw_schema:
                # Scenario A: Mapping exists and source column is found (e.g., 'Curr' -> 'Amp')
                select_parts.append(f'"{source_field}" AS "{col}"')
            elif col in raw_schema:
                # Scenario B: Target name already exists in source (e.g., 'Volt' is already 'Volt')
                select_parts.append(f'"{col}"')
            else:
                # Scenario C: Field is missing from this specific log (e.g., old log missing 'RSSI')
                # We insert a NULL column to keep the table structure consistent.
                select_parts.append(f'CAST(NULL AS DOUBLE) AS "{col}"')

        # Add mandatory metadata and sorting keys
        if "TimeUS" not in [p.split()[-1].replace('"', '') for p in select_parts]:
            select_parts.insert(0, '"TimeUS"')

        select_parts.extend(['"inode"', '"wall_ns"'])
        col_selection = ", ".join(select_parts)

        # 5. Execute the "Sling" to Warehouse (Vault C)
        output_path = os.path.join(self.clerk.warehouse_df, f"master_{domain}.parquet")

        sql = f"""
            COPY (
                SELECT
                    '{self.mission_id}' AS mission_id,
                    {col_selection}
                FROM read_parquet('{shard_pattern}')
                ORDER BY TimeUS, inode
            ) TO '{output_path}' (FORMAT 'PARQUET');
        """

        try:
            self.con.execute(sql)
            res = self.con.execute(f"SELECT COUNT(*) FROM '{output_path}'").fetchone()
            print(f"✅ {domain: <6} Refined: {res[0]: >6} rows | {len(target_columns)} columns.")
        except Exception as e:
            print(f"❌ {domain} refinement failed: {e}")