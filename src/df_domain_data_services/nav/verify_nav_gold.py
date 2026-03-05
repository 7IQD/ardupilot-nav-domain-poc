#!/usr/bin/env python3
"""
verify_nav_gold.py
Standalone script with the CORRECT paths based on 'ls -R' discovery.
"""

import pandas as pd
import os

# --- DYNAMIC PATH SETUP ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up 3 levels to reach ardupilot-nav-domain-poc root
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../"))
# UPDATED: The files actually live in bin/vault/warehouse_df
DATA_DIR = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")

NAV_PARQUET = os.path.join(DATA_DIR, "master_NAV.parquet")
EST_PARQUET = os.path.join(DATA_DIR, "master_EST.parquet")

def run_verification():
    print(f"🚀 Initializing Verification...")
    print(f"📂 Looking for data in: {DATA_DIR}")

    if not os.path.exists(NAV_PARQUET):
        print(f"❌ ERROR: File not found at {NAV_PARQUET}")
        return

    # --- LOAD ---
    nav_df = pd.read_parquet(NAV_PARQUET)
    est_df = pd.read_parquet(EST_PARQUET)

    # --- DEDUPLICATE ---
    # Keeping the latest record if multiple entries exist for the same TimeUS
    nav_df = nav_df.sort_values(["TimeUS", "wall_ns"], ascending=[True, False]).drop_duplicates(subset=["TimeUS"])
    est_df = est_df.sort_values(["TimeUS", "wall_ns"], ascending=[True, False]).drop_duplicates(subset=["TimeUS"])

    # --- FUSION ---
    # ASOF join to align EKF (EST) states with NAV points
    fused_df = pd.merge_asof(
        nav_df.sort_values("TimeUS"),
        est_df.sort_values("TimeUS"),
        on="TimeUS",
        direction="backward",
        suffixes=("", "_est")
    )

    print(f"\n✅ SUCCESS: Data Loaded and Fused.")
    print(f"📊 NAV Rows: {len(nav_df)}")
    print(f"📊 EST Rows: {len(est_df)}")
    print(f"🔗 Fused Points: {len(fused_df)}")

    # Check for specific columns we need
    required = ['Alt', 'Roll', 'Pitch', 'Lat', 'Lng']
    missing = [col for col in required if col not in fused_df.columns]

    if missing:
        print(f"⚠️ Missing columns: {missing}")
    else:
        print(f"✨ All required flight columns (Alt, Roll, Pitch, GPS) are present.")
        print(f"🏔️ Peak Altitude in this set: {fused_df['Alt'].max():.2f}m")

if __name__ == "__main__":
    run_verification()