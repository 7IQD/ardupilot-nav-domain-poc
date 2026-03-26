#!/usr/bin/env python3
"""
NAV Profile Utilities (Local Only)
- Artifact storage
- Registry path resolution
"""

import os
import pandas as pd
from typing import List, Tuple, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "profile_outputs")


def save_run_output(df: pd.DataFrame, name: str) -> str:
    """Save profiling run output as Parquet in profile_outputs."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"{name}.parquet")
    df.to_parquet(path, index=False, compression="snappy")
    print(f"📦 Saved: {path}")
    return path


def get_shard_paths(con, msg_type: str, mission_id: str) -> List[str]:
    """Return all shard paths for a given mission and msg_type from nav_registry."""
    query = f"""
        SELECT shard_path
        FROM nav_registry
        WHERE mission_id = '{mission_id}'
          AND msg_type = '{msg_type}'
    """
    return [r[0] for r in con.execute(query).fetchall()]


def get_mission_metadata(con, mission_id: str) -> Optional[Tuple[int, int]]:
    """Return the (min_time_us, max_time_us) for the mission from nav_registry."""
    result = con.execute(f"""
        SELECT MIN(time_min_us), MAX(time_max_us)
        FROM nav_registry
        WHERE mission_id = '{mission_id}'
    """).fetchone()
    return result if result != (None, None) else None