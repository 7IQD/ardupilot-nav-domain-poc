#!/usr/bin/env python3
"""
NAV Domain Registry: Physical Mapping & Location Service
Authority: Structure + Location + Counts
No Quality Auditing (Profile) permitted here.
"""

import os
import sys
import duckdb

# --- CONFIGURATION ---
if len(sys.argv) < 2:
    print("Usage: python3 create_nav_registry.py <MISSION_FOLDER_NAME>")
    sys.exit(1)

MISSION_FOLDER = sys.argv[1]
MISSION_ID = MISSION_FOLDER.replace("_parts", "")
DOMAIN = "NAV"

BASE_DIR = os.path.expanduser("~/ardupilot-nav-domain-poc")
WAREHOUSE_DIR = f"{BASE_DIR}/bin/vault/warehouse_df/{MISSION_FOLDER}"
REGISTRY_DB = f"{BASE_DIR}/src/df_domain_data_services/nav/nav_registry.duckdb"
SHARD_PATTERN = os.path.join(WAREHOUSE_DIR, "**", "*.parquet")


def main():
    if not os.path.exists(WAREHOUSE_DIR):
        print(f"ERROR: Mission folder not found: {WAREHOUSE_DIR}")
        sys.exit(1)

    os.makedirs(os.path.dirname(REGISTRY_DB), exist_ok=True)
    con = duckdb.connect(REGISTRY_DB)

    print(f"[Registry] Indexing {DOMAIN} Structure: {MISSION_ID}")

    # ----------------------------
    # CORE REGISTRY LOGIC (FINAL)
    # ----------------------------
    con.execute(f"""
        CREATE OR REPLACE TABLE nav_registry AS

        SELECT
            '{MISSION_ID}' AS mission_id,
            '{DOMAIN}'     AS domain,

            msg_type       AS param_name,
            filename       AS shard_path,
            segment_id,

            COUNT(*) AS row_count,
            MIN(TimeUS) AS time_min_us,
            MAX(TimeUS) AS time_max_us,

            SUM(COUNT(*)) OVER (PARTITION BY msg_type) AS total_param_count

        FROM read_parquet('{SHARD_PATTERN}', filename=true)

        WHERE
            msg_type LIKE 'ATT%' OR
            msg_type LIKE 'AHR2%' OR
            msg_type LIKE 'GPS%' OR
            msg_type LIKE 'GPSS%' OR
            msg_type LIKE 'XKF%' OR
            msg_type LIKE 'XKFS%' OR
            msg_type LIKE 'XKQ%' OR
            msg_type LIKE 'XKT%' OR
            msg_type LIKE 'XKTV%' OR
            msg_type LIKE 'XKV%' OR
            msg_type LIKE 'ANG%' OR
            msg_type LIKE 'RATE%' OR
            msg_type LIKE 'CTUN%' OR
            msg_type LIKE 'ORGN%' OR
            msg_type LIKE 'PID%'

        GROUP BY msg_type, filename, segment_id
    """)

    # Index for fast lookup
    con.execute("""
        CREATE INDEX IF NOT EXISTS idx_nav_lookup
        ON nav_registry (param_name, segment_id);
    """)

    print(f"[Done] Registry persisted to: {REGISTRY_DB}")

    # Simple audit
    res = con.execute("""
        SELECT COUNT(DISTINCT param_name), SUM(row_count)
        FROM nav_registry
    """).fetchone()

    print(f"[Info] Parameters indexed: {res[0]}")
    print(f"[Info] Total data points mapped: {res[1]}")

    con.close()


if __name__ == "__main__":
    main()