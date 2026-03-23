#!/usr/bin/env python3
"""
NAV Data Profile Helpers
- Handles Local Artifact Storage (profile_outputs)
- Resolves Shard Paths from the Nav Registry
- Authority: Local Service Encapsulation
"""

import os
import pandas as pd

# --- LOCAL PATH RESOLUTION ---
# This anchors the output to the 'profile_outputs' folder relative to THIS file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "profile_outputs")

def save_run_output(df, run_name):
    """
    Saves a DataFrame as a Parquet artifact in the local profile_outputs folder.
    Ensures the directory exists before writing.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    file_path = os.path.join(OUTPUT_DIR, f"{run_name}.parquet")

    # Save with snappy compression (standard for high-frequency telemetry)
    try:
        df.to_parquet(file_path, index=False, compression='snappy')
        print(f"[Artifact] Saved {run_name} to {file_path}")
    except Exception as e:
        print(f"❌ Error saving artifact {run_name}: {e}")

    return file_path

def get_shard_paths(con, msg_type, mission_id):
    """
    Queries the 'nav_registry' table in DuckDB to find all physical
    Parquet file paths for a specific message type and mission.
    """
    query = f"""
        SELECT shard_path
        FROM nav_registry
        WHERE mission_id = '{mission_id}'
          AND msg_type = '{msg_type}'
    """
    try:
        results = con.execute(query).fetchall()
        # Return a list of strings (paths)
        return [r[0] for r in results]
    except Exception as e:
        print(f"❌ Error retrieving shard paths for {msg_type}: {e}")
        return []

def get_mission_metadata(con, mission_id):
    """
    Optional: Retrieves start/end times for the entire mission
    to bound the diagnostic window.
    """
    query = f"""
        SELECT MIN(time_min_us), MAX(time_max_us)
        FROM nav_registry
        WHERE mission_id = '{mission_id}'
    """
    return con.execute(query).fetchone()