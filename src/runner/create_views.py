#!/usr/bin/env python3
import os
import duckdb

# --- PATH RESOLUTION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
VAULT_DIR = os.path.join(PROJECT_ROOT, "bin/vault")
WAREHOUSE_DIR = os.path.join(VAULT_DIR, "warehouse_df")
DB_PATH = os.path.join(VAULT_DIR, "drone_df_views.db")

# --- Domain Mapping (matches Refiner output) ---
DOMAINS = {
    "NAV": {"table": "fact_nav_state_vector",   "parquet": "nav_df_master"},
    "EST": {"table": "fact_est_state_vector",   "parquet": "est_df_master"},
    "PWR": {"table": "fact_power_state_vector", "parquet": "power_df_master"},
    "COM": {"table": "fact_com_state_vector",   "parquet": "com_df_master"},
    "SYS": {"table": "fact_sys_state_vector",   "parquet": "sys_df_master"}
}

def main():
    print(f"🚀 Initializing MAVLink-Aligned View Layer...")
    conn = duckdb.connect(DB_PATH)
    active_tables = []

    try:
        for key, meta in DOMAINS.items():
            p_path = os.path.join(WAREHOUSE_DIR, f"{meta['parquet']}.parquet")
            if not os.path.exists(p_path):
                print(f"⚠️  Skipping {key}: {meta['parquet']}.parquet not found.")
                continue

            print(f"🥇 Registering {meta['table']}...")

            # Since the Refiner already cleaned and deduplicated,
            # we just import the clean Parquet directly into DuckDB.
            conn.execute(f"CREATE OR REPLACE TABLE {meta['table']} AS SELECT * FROM read_parquet('{p_path}');")

            # Index for high-speed Fusion Joins
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{key.lower()}_ts ON {meta['table']} (mission_id, TimeUS);")
            active_tables.append(meta['table'])

        # --- Platinum Layer: Unified Fusion View ---
        # This uses ASOF JOINs to merge domains with different frequencies (e.g. GPS @ 5Hz, IMU @ 50Hz)
        if "fact_nav_state_vector" in active_tables:
            print("\n💎 Creating Unified Fusion View: fact_flight_diagnostics...")

            cols = ["nav.*"]
            joins = []

            # Add EST data (Roll, Pitch, Yaw)
            if "fact_est_state_vector" in active_tables:
                cols += ["est.Roll", "est.Pitch", "est.Yaw"]
                joins.append("ASOF LEFT JOIN fact_est_state_vector est ON nav.mission_id = est.mission_id AND nav.TimeUS >= est.TimeUS")

            # Add Power data (Volt, Amp - Using exact FMT names)
            if "fact_power_state_vector" in active_tables:
                cols += ["pwr.Volt", "pwr.Amp"] # Note: Changed 'Curr' back to 'Amp' to match FMT
                joins.append("ASOF LEFT JOIN fact_power_state_vector pwr ON nav.mission_id = pwr.mission_id AND nav.TimeUS >= pwr.TimeUS")

            # Build the View
            join_sql = f"CREATE OR REPLACE VIEW fact_flight_diagnostics AS SELECT {', '.join(cols)} FROM fact_nav_state_vector nav\n"
            join_sql += "\n".join(joins)
            conn.execute(join_sql)
            print("💎 Unified Fusion View created: fact_flight_diagnostics")

        print("\n✅ Gold Layer Build Successful. Your Warehouse is now Fused.")

    except Exception as e:
        print(f"💥 Deployment Failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()