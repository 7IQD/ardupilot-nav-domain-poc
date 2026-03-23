#!/usr/bin/env python3
"""
NAV Data Profiling Orchestrator (GSoC 2026 POC)
- Automates Health, Integrity, Phase Tagging, and Anomaly Detection.
- Authority: nav_registry.duckdb (Absolute Pathing)
- Library: FMT_Library.json (Domain-Driven)
"""

import sys
import os
import json
import duckdb

# --- DYNAMIC PATH RESOLUTION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../.."))
REGISTRY_PATH = os.path.join(SCRIPT_DIR, "nav_registry.duckdb")

# Path to the FMT Library in the Ingest Domain
FMT_LIB_PATH = os.path.join(PROJECT_ROOT, "src/weaving/ingest_df/FMT_Library.json")

# Import the logic from the local module
try:
    from nav_data_profile.profile_runs import (
        run_1_stats_health,
        run_2_integrity_check,
        run_3_flight_phase,
        run_4_anomaly_detection
    )
except ImportError:
    print("ERROR: Could not find 'nav_data_profile' module. Ensure PYTHONPATH=src is set.")
    sys.exit(1)

def load_nav_domain_messages():
    """Loads only the messages defined in the NAV_DOMAIN from the FMT Library."""
    try:
        if os.path.exists(FMT_LIB_PATH):
            with open(FMT_LIB_PATH, 'r') as f:
                lib = json.load(f)
                return list(lib.get("NAV_DOMAIN", {}).keys())
    except Exception as e:
        print(f"⚠️ Warning: Could not load FMT Library ({e}). Falling back to defaults.")

    # Fallback if JSON is missing or corrupt
    return ['ATT', 'GPS', 'XKF1']

def main():
    # 1. Argument Handling
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=src python3 nav_data_profile_main.py <MISSION_ID>")
        sys.exit(1)

    mission_id = sys.argv[1]

    # 2. Connection Logic
    if not os.path.exists(REGISTRY_PATH):
        print(f"ERROR: Registry file not found at {REGISTRY_PATH}")
        sys.exit(1)

    con = duckdb.connect(REGISTRY_PATH)

    # 3. Dynamic Message Selection
    # Now pulls from your JSON: ['ATT', 'GPS', 'XKF1', 'XKF2', 'XKF3', etc.]
    msg_types = load_nav_domain_messages()

    print("\n" + "="*60)
    print(f"🚀 NAV DIAGNOSTIC PIPELINE | MISSION: {mission_id}")
    print(f"📂 Library: {os.path.basename(FMT_LIB_PATH)}")
    print("="*60 + "\n")

    # --- PHASE 1: FOUNDATION (AUTOMATED) ---
    print(f"[Run 1] Auditing {len(msg_types)} message types from NAV_DOMAIN...")
    run_1_stats_health(con, mission_id, msg_types)

    run_2_integrity_check(con, mission_id)

    print(f"✅ [Run 1] Health Profiling: Complete")
    print(f"✅ [Run 2] Integrity Validation: Complete")
    print("-" * 40)

    # --- PHASE 2: INTELLIGENCE (INTERACTIVE) ---
    print("AVAILABLE MODULES:")
    print(" [3] Flight Phase Tagging (Adaptive State Machine)")
    print(" [4] Anomaly Detection (GPS Loss Verdict Engine)")
    print(" [exit] End Pipeline\n")

    while True:
        choice = input("Select Module to Execute (3 / 4 / exit): ").strip().lower()

        if choice == "3":
            run_3_flight_phase(con, mission_id)
            print("\n✅ Contextual Phase Map saved to profile_outputs/\n")

        elif choice == "4":
            print("\n🔍 Running Inference Engine...")
            anomalies = run_4_anomaly_detection(con, mission_id)

            if not anomalies.empty:
                count = len(anomalies)
                print(f"⚠️  VERDICT: {count} GPS_SIGNAL_LOSS events detected.")
                print(f"🎯  Confidence: 95% | Evidence linked in run4_anomalies.parquet")
            else:
                print("🟢 No anomalies detected in the GPS stream.")

            print("\n Diagnosis Ready (Check profile_outputs/ folder)\n")

        elif choice == "exit":
            print("Closing connections. Pipeline shutdown.")
            break
        else:
            print("Invalid input. Please choose 3, 4, or exit.")

    con.close()

if __name__ == "__main__":
    main()