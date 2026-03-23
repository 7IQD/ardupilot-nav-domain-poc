#!/usr/bin/env python3
"""
NAV Data Profile Runs
- Run 1: Health audit
- Run 2: Timeline integrity validation
- Run 3: Flight phase tagging
- Run 4: Anomaly detection (GPS loss)
"""

import pandas as pd
from .helpers import get_shard_paths, save_run_output


# -------------------------
# Run 1: Health Audit
# -------------------------
def run_1_stats_health(con, mission_id, msg_types):
    print(f"[Run 1] Auditing Health for: {msg_types}")
    all_stats = []

    for msg in msg_types:
        # ✅ FIX: pass mission_id
        paths = get_shard_paths(con, msg, mission_id)
        if not paths:
            continue

        cols_df = con.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{paths[0]}')"
        ).df()

        target_cols = [
            c for c in cols_df['column_name'].tolist()
            if c.startswith(f"{msg}_") or c in ['Roll', 'Pitch', 'Yaw', 'Alt', 'Speed', 'NSats', 'HDop']
        ]

        sql_parts = []
        for col in target_cols:
            sql_parts.append(f"""
                COUNT(*) FILTER (WHERE "{col}" IS NULL) AS {col}_nulls,
                COUNT(*) FILTER (WHERE isnan("{col}"::DOUBLE)) AS {col}_nans,
                MIN("{col}") AS {col}_min,
                MAX("{col}") AS {col}_max
            """)

        sql_query = f"""
            SELECT {', '.join(sql_parts)}
            FROM read_parquet({paths})
            WHERE msg_type = '{msg}'
        """

        stats_raw = con.execute(sql_query).df()

        for col in target_cols:
            null_count = stats_raw[f"{col}_nulls"].iloc[0]

            all_stats.append({
                "mission_id": mission_id,
                "msg_type": msg,
                "field_name": col,
                "null_count": null_count,
                "nan_count": stats_raw[f"{col}_nans"].iloc[0],
                "min_val": stats_raw[f"{col}_min"].iloc[0],
                "max_val": stats_raw[f"{col}_max"].iloc[0],
                "locf_required": True if null_count > 0 else False
            })

    df = pd.DataFrame(all_stats)
    save_run_output(df, "run1_nulls_locf")
    return df


# -------------------------
# Run 2: Integrity Check
# -------------------------
def run_2_integrity_check(con, mission_id, threshold_us=100000):
    print(f"[Run 2] Timeline Integrity Validation...")

    df = con.execute(f"""
        SELECT param_name, segment_id, shard_path, time_min_us, time_max_us
        FROM nav_registry
        WHERE mission_id = '{mission_id}'
        ORDER BY time_min_us ASC
    """).df()

    df['time_gap'] = df['time_min_us'] - df['time_max_us'].shift(1)
    df['is_gap_critical'] = df['time_gap'] > threshold_us

    save_run_output(df, "run2_integrity")
    return df


# -------------------------
# Run 3: Flight Phase Tagging
# -------------------------
def run_3_flight_phase(con, mission_id):
    print(f"[Run 3] Flight Phase Tagging (Adaptive)...")

    paths = get_shard_paths(con, 'XKF1', mission_id)
    if not paths:
        return pd.DataFrame()

    # 🔍 STEP 1: FORCE DYNAMIC COLUMN DISCOVERY
    # This reads the actual headers from your Parquet files
    cols_df = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{paths[0]}')").df()
    actual_cols = cols_df['column_name'].tolist()

    # 🔍 STEP 2: MAPPING (The 'Shield')
    # ArduPilot uses 'Spd' in XKF1, but might use 'Speed' or 'Vel' elsewhere
    spd_col = next((c for c in ['Spd', 'Speed', 'Vel'] if c in actual_cols), None)
    alt_col = next((c for c in ['Alt', 'AltMSL', 'BaroAlt'] if c in actual_cols), 'Alt')

    if not spd_col:
        print(f"❌ ERROR: 'Speed/Spd' column not found in {actual_cols}")
        return pd.DataFrame()

    # 🚀 STEP 3: EXECUTE WITH ALIASING
    # We rename 'Spd' to 'Speed' in the SQL result so the Python logic remains clean
    df = con.execute(f"""
        SELECT TimeUS, {alt_col} AS Alt, {spd_col} AS Speed
        FROM read_parquet({paths})
        ORDER BY TimeUS
    """).df()

    def tag_phase(row):
        if row['Alt'] < 1.5: return "GROUND"
        if row['Speed'] > 4.0: return "CRUISE"
        return "HOVER"

    df['flight_phase'] = df.apply(tag_phase, axis=1)
    save_run_output(df, "run3_flight_phase")
    return df


# -------------------------
# Run 4: Anomaly Detection
# -------------------------
def run_4_anomaly_detection(con, mission_id):
    print(f"[Run 4] Anomaly Detection (GPS Loss)...")

    # ✅ FIX: pass mission_id
    paths = get_shard_paths(con, 'GPS', mission_id)
    if not paths:
        return pd.DataFrame()

    df = con.execute(f"""
        SELECT TimeUS, NSats, HDop
        FROM read_parquet({paths})
        ORDER BY TimeUS
    """).df()

    if df.empty:
        return df

    anomalies = []
    in_loss = False
    start_time = None

    for _, row in df.iterrows():
        if row['NSats'] == 0 and not in_loss:
            in_loss = True
            start_time = row['TimeUS']

        elif row['NSats'] > 0 and in_loss:
            anomalies.append({
                "mission_id": mission_id,
                "root_cause": "GPS_SIGNAL_LOSS",
                "start_time": start_time,
                "end_time": row['TimeUS'],
                "confidence": 0.93,
                "evidence": "NSats dropped to 0"
            })
            in_loss = False

    df_out = pd.DataFrame(anomalies)

    save_run_output(df_out, "run4_anomalies")
    return df_out