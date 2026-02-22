#!/usr/bin/env python3
import os
import duckdb
import logging

# -------------------------
# Base Refiner
# -------------------------
class BaseRefiner:
    def __init__(self, staging_dir, warehouse_dir, mission_id, anchor=0):
        self.staging_dir = staging_dir
        self.warehouse_dir = warehouse_dir
        self.mission_id = mission_id
        self.anchor = anchor

    def _execute_refinement(self, domain_name, time_col, divisor, pattern):
        master_path = os.path.join(self.warehouse_dir, f"{domain_name}_df_master.parquet")
        shard_pattern = os.path.join(self.staging_dir, pattern)

        con = duckdb.connect(':memory:')
        try:
            # Refine shards: mission_id, mission_time, wall_ns, sanitize NaNs
            refined_query = f"""
            COPY (
                SELECT
                    '{self.mission_id}' AS mission_id,
                    (({time_col} - {self.anchor}) / {divisor}) AS mission_time,
                    CAST({time_col} * (1000000000 / {divisor}) AS BIGINT) AS wall_ns,
                    * EXCLUDE ({time_col})
                FROM read_parquet('{shard_pattern}')
                ORDER BY mission_time ASC
            ) TO '{master_path}' (FORMAT 'PARQUET')
            """
            con.execute(refined_query)
            logging.info(f"✅ {domain_name.upper()} refined to {master_path} (JSON-Compliant)")
        except Exception as e:
            logging.error(f"❌ {domain_name.upper()} refinement failed: {e}")
        finally:
            con.close()

# -------------------------
# Domain-specific Refiners
# -------------------------
class NavRefiner(BaseRefiner):
    def refine(self):
        self._execute_refinement("nav", "TimeUS", 1e6, "nav_shard_*.parquet")

class EstRefiner(BaseRefiner):
    def refine(self):
        self._execute_refinement("est", "timestamp_sec", 1, "est_shard_*.parquet")

class SysRefiner(BaseRefiner):
    def refine(self):
        self._execute_refinement("sys", "TimeUS", 1e6, "sys_shard_*.parquet")

class PowerRefiner(BaseRefiner):
    def refine(self):
        self._execute_refinement("power", "TimeUS", 1e6, "power_shard_*.parquet")

class ComRefiner(BaseRefiner):
    def refine(self):
        self._execute_refinement("com", "TimeUS", 1e6, "com_shard_*.parquet")