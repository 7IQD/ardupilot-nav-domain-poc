#!/usr/bin/env python3
import os
import duckdb

# --- Paths ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
WAREHOUSE_DF = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")
VAULT_DB = os.path.join(WAREHOUSE_DF, "drone_df_views.db")

# --- Connect to DuckDB ---
conn = duckdb.connect(VAULT_DB)

# --- Map of parquet masters ---
MASTER_MAP = {
    "nav": "nav_df_master.parquet",
    "sys": "sys_df_master.parquet",
    "power": "power_df_master.parquet",
    "com": "com_df_master.parquet",
    "est": "est_df_master.parquet",
}

# --- 1️⃣ Create base fact tables ---
for domain, parquet_file in MASTER_MAP.items():
    parquet_path = os.path.join(WAREHOUSE_DF, parquet_file)
    if os.path.exists(parquet_path):
        fact_table = f"fact_{domain if domain != 'com' else 'communication'}"
        conn.execute(f"""
            CREATE OR REPLACE TABLE {fact_table} AS
            SELECT * FROM read_parquet('{parquet_path}')
        """)
        print(f"✅ Fact Table: {fact_table}")

# --- 2️⃣ Analytical Views ---
# NAV / SYS / POWER
conn.execute("CREATE OR REPLACE VIEW ui_nav_drone_monitor AS SELECT * FROM fact_nav")
conn.execute("CREATE OR REPLACE VIEW view_system_vibe_stress AS SELECT * FROM fact_sys")
conn.execute("CREATE OR REPLACE VIEW view_power_health AS SELECT * FROM fact_power")

# COM (Safe Mode)
cols = [row[0] for row in conn.execute("DESCRIBE fact_communication").fetchall()]
rssi_logic = "COALESCE(RSSI, RemRSSI)" if "RSSI" in cols else "NULL"
noise_logic = "Noise" if "Noise" in cols else "NULL"

conn.execute(f"""
    CREATE OR REPLACE VIEW view_comm_link_quality AS
    SELECT
        timestamp_sec,
        {rssi_logic} AS signal_strength,
        {noise_logic} AS noise_floor,
        mavpackettype
    FROM fact_communication
""")
print("✅ View created: view_comm_link_quality (Safe Mode)")

# EST View (Optional: direct mapping)
conn.execute("CREATE OR REPLACE VIEW view_est_master AS SELECT * FROM fact_est")
print("✅ View created: view_est_master")

# --- Close connection ---
conn.close()
print("\n✅ All fact tables and views are now created. Ready for API/UI consumption.")
