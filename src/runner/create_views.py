#!/usr/bin/env python3
import os
import duckdb

# --- 1. PATH CONFIGURATION ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
WAREHOUSE_DF = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")
VAULT_DB = os.path.join(WAREHOUSE_DF, "drone_df_views.db")

def main():
    print(f"🏗️  Starting DuckDB Optimized Projection Layer")
    print(f"📁 Source Warehouse: {WAREHOUSE_DF}")
    print(f"🗄️  Target DB: {VAULT_DB}")

    # --- 2. REFRESH FACT TABLES ---
    MASTER_MAP = {
        "nav": "nav_df_master.parquet",
        "sys": "sys_df_master.parquet",
        "power": "power_df_master.parquet",
        "com": "com_df_master.parquet",
        "est": "est_df_master.parquet",
    }

    conn = duckdb.connect(VAULT_DB)

    for domain, parquet_file in MASTER_MAP.items():
        parquet_path = os.path.join(WAREHOUSE_DF, parquet_file)
        if os.path.exists(parquet_path):
            table_name = f"fact_{domain if domain != 'com' else 'communication'}"
            conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT * FROM read_parquet('{parquet_path}')
            """)
            print(f"✅ Fact Table Refreshed: {table_name}")
        else:
            print(f"⚠️  Missing Master Parquet: {parquet_file}")

    # --- 3. OPTIMIZED BATCH VIEWS (Terminal UI / Performance Fix) ---
    print("\n🔭 Materializing Optimized Views for Terminal UI...")

    # Strategy:
    # 1. LIMIT 2000 rows per view to avoid JSON/DOM bloat.
    # 2. Optional: ORDER BY timestamp or mission_id if recent/relevant data is preferred.

    VIEWS = {
        "ui_nav_drone_monitor": "SELECT * FROM fact_nav LIMIT 2000",
        "view_system_vibe_stress": "SELECT * FROM fact_sys LIMIT 2000",
        "view_power_health": "SELECT * FROM fact_power LIMIT 2000",
        "view_est_master": "SELECT * FROM fact_est LIMIT 2000",
        "view_comm_link_quality": "SELECT * FROM fact_communication LIMIT 2000"
    }

    for view_name, query in VIEWS.items():
        try:
            conn.execute(f"CREATE OR REPLACE VIEW {view_name} AS {query}")
            print(f"🚀 Optimized View Created: {view_name}")
        except Exception as e:
            print(f"⚠️  Failed to create {view_name}: {e}")

    conn.close()
    print("\n🏁 Aperture Control Complete. Restart FastAPI to observe performance improvement.")

if __name__ == "__main__":
    main()