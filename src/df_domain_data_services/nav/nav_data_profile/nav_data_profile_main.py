#!/usr/bin/env python3
"""
NAV Domain Main Profiler - Warehouse Edition
- Runs Health, Integrity, and Rule-Based Anomaly Scan
- Inserts anomalies into nav_meta_log (safe schema)
"""

import duckdb
import sys
import os
import pandas as pd

# --- Bootstrap sys.path ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- Imports ---
from src.df_domain_data_services.nav.nav_data_profile.nav_profile_utils import save_run_output
from src.df_domain_data_services.nav.nav_data_profile.nav_profile_runs import (
    run_1_stats_health,
    run_2_integrity_check,
    run_3_anomaly_detection
)

def run_nav_profile(mission_id):
    print(f"\n🚀 NAV Profiling Started for Mission: {mission_id}")

    # --- Warehouse Path ---
    WAREHOUSE_PATH = os.path.join(
        PROJECT_ROOT,
        "bin/vault/warehouse_df",
        f"{mission_id}_parts",
        "nav_master.duckdb"
    )

    if not os.path.exists(WAREHOUSE_PATH):
        print(f"❌ Warehouse not found at {WAREHOUSE_PATH}")
        return

    con = duckdb.connect(WAREHOUSE_PATH, read_only=False)
    print(f"🔗 Connected to Warehouse")

    # -----------------------------
    # Ensure Meta Log Table Exists
    # -----------------------------
    con.execute("""
        CREATE TABLE IF NOT EXISTS nav_meta_log (
            inode BIGINT,
            TimeUS BIGINT,
            rule_id VARCHAR,
            parameter VARCHAR,
            actual_value DOUBLE,
            mission_id VARCHAR,
            segment_id INTEGER
        )
    """)

    # Optional cleanup (avoid duplicate runs)
    con.execute(f"DELETE FROM nav_meta_log WHERE mission_id = '{mission_id}'")

    # -----------------------------
    # Message Types (Segment 1)
    # -----------------------------
    available_msgs = con.execute(
        "SELECT DISTINCT msg_type FROM nav_segment_1"
    ).fetchall()

    msg_types_found = [row[0] for row in available_msgs]
    print(f"📡 Message types in Segment 1: {msg_types_found}")

    # POC Mode
    target_types = ['ATT', 'GPS', 'XKF1']
    print(f"🧪 POC Mode: Profiling types {target_types}")

    # -----------------------------
    # Run 1: Health
    # -----------------------------
    df_health = run_1_stats_health(con, mission_id, target_types)
    #save_run_output(df_health, "mission_health")

    # -----------------------------
    # Run 2: Integrity
    # -----------------------------
    df_integrity = run_2_integrity_check(con, mission_id)
    #save_run_output(df_integrity, "mission_integrity")

    # -----------------------------
    # Run 3: Rule-Based Scan
    # -----------------------------
    rule_ids = ['C-1', 'E-1', 'E-2', 'E-3', 'N-1', 'N-2']
    all_anomalies_list = []

    print(f"\n🕵️ Starting Anomaly Scan (Segment 1)...")

    for rid in rule_ids:
        df_rid = run_3_anomaly_detection(con, mission_id, rid)

        if not df_rid.empty:
            # ✅ SAFE INSERT (matches 7 columns)
            con.execute("""
                INSERT INTO nav_meta_log (
                    inode,
                    TimeUS,
                    rule_id,
                    parameter,
                    actual_value,
                    mission_id,
                    segment_id
                )
                SELECT * FROM df_rid
            """)

            save_run_output(df_rid, f"anomaly_{rid}")
            all_anomalies_list.append(df_rid)

            print(f"   ✅ {rid}: {len(df_rid)} hits")
        else:
            print(f"   ⚪ {rid}: 0 hits")

    # Combine all anomalies
    df_anomalies = pd.concat(all_anomalies_list) if all_anomalies_list else pd.DataFrame()

    con.close()

    # -----------------------------
    # Summary
    # -----------------------------
    print("\n✅ NAV Profiling Complete")
    print("-" * 30)
    print(f"Health Records:     {len(df_health)}")

    gaps = len(df_integrity[df_integrity['is_gap'] == True]) if not df_integrity.empty else 0
    print(f"Integrity Gaps:     {gaps}")

    print(f"Anomalies Found:    {len(df_anomalies)}")
    print("-" * 30)

    return df_health, df_integrity, df_anomalies


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 nav_data_profile_main.py <mission_id>")
        sys.exit(1)

    run_nav_profile(sys.argv[1])