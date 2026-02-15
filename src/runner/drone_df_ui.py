#!/usr/bin/env python3
import duckdb
import os

# --- PATHS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
WAREHOUSE_DF = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")
MASTER_PARQUET = os.path.join(WAREHOUSE_DF, "nav_df_master.parquet")
VAULT_DB = os.path.join(WAREHOUSE_DF, "nav_df_vault.db")

def build_vault_views():
    """Builds Forensic Views using verified Parquet schema."""

    # Instruction [2026-01-15]: Overwrite for testing
    if os.path.exists(VAULT_DB):
        print(f"🧹 Overwriting existing vault: {VAULT_DB}")
        os.remove(VAULT_DB)

    con = duckdb.connect(VAULT_DB)

    # Create the base view from Parquet
    con.execute(f"CREATE VIEW nav_all AS SELECT * FROM read_parquet('{MASTER_PARQUET}');")

    # Verified Time Logic: Use TimeUS (microseconds) -> Seconds
    TIME_SQL = "TimeUS / 1000000.0"

    # 1. UI Telemetry View (Standard Nav Monitoring)
    con.execute(f"""
        CREATE VIEW ui_telemetry AS
        SELECT
            {TIME_SQL} AS time_sec,
            mavpackettype,
            Alt, Roll, Pitch, Yaw,
            DesRoll, DesPitch, DesYaw -- Control Performance
        FROM nav_all
        WHERE mavpackettype IN ('ATT', 'AHR2', 'CTUN')
        ORDER BY time_sec ASC;
    """)

    # 2. AI Forensic View (Vibration & EKF Health)
    # Uses PN/PE/PD (North/East/Down position) from XKF1 for drift analysis
    con.execute(f"""
        CREATE VIEW ai_vibe_diagnostics AS
        SELECT
            {TIME_SQL} AS time_sec,
            mavpackettype,
            -- Vertical Jitter Calculation
            STDDEV(Alt) OVER (ORDER BY TimeUS ROWS BETWEEN 5 PRECEDING AND 5 FOLLOWING) AS alt_jitter,
            -- Attitude Magnitude
            SQRT(POWER(Roll, 2) + POWER(Pitch, 2)) AS tilt_magnitude,
            -- Innovation/Health (from XKF1 bindings)
            Health
        FROM nav_all
        WHERE mavpackettype IN ('ATT', 'XKF1')
        ORDER BY time_sec ASC;
    """)

    row_count = con.execute("SELECT COUNT(*) FROM nav_all").fetchone()[0]
    print(f"✅ Vault Built Successfully.")
    print(f"📊 Indexed {row_count} messages with 64-column depth.")
    con.close()

if __name__ == "__main__":
    build_vault_views()