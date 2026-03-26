#!/usr/bin/env python3
"""
NAV Domain Profiling Runs - Warehouse Edition
- Run 1: Stats & Health
- Run 2: Integrity Check
- Run 3: Schema-Aware Anomaly Detection (Safe Insert Ready)
"""

import duckdb
import pandas as pd

# -----------------------------
# Run 1: Stats & Health
# -----------------------------
def run_1_stats_health(con, mission_id, msg_types):
    msg_tuple = tuple(msg_types) if len(msg_types) > 1 else f"('{msg_types[0]}')"

    query = f"""
        SELECT
            msg_type,
            COUNT(*) as count,
            MIN(TimeUS) as time_min_us,
            MAX(TimeUS) as time_max_us
        FROM nav_segment_1
        WHERE msg_type IN {msg_tuple}
        GROUP BY msg_type
        ORDER BY msg_type
    """
    return con.execute(query).fetchdf()


# -----------------------------
# Run 2: Integrity Check
# -----------------------------
def run_2_integrity_check(con, mission_id):
    query = "SELECT TimeUS FROM nav_segment_1 ORDER BY TimeUS"
    df = con.execute(query).fetchdf()

    if df.empty:
        return pd.DataFrame()

    df['prev'] = df['TimeUS'].shift(1)
    df['is_gap'] = (df['TimeUS'] > (df['prev'] + 1)) & df['prev'].notnull()

    return df


# -----------------------------
# Run 3: Schema-Aware Anomaly Detection
# -----------------------------
def run_3_anomaly_detection(con, mission_id, rule_id):
    """
    Executes ONE rule safely on nav_segment_1.
    Skips rule if column not present.
    Returns dataframe ready for meta_log insertion.
    """

    # 1. Fetch rule
    rule = con.execute(f"""
        SELECT msg_type, parameter, operator, threshold
        FROM rule_master
        WHERE rule_id = '{rule_id}'
    """).fetchone()

    if not rule:
        print(f"   ⚠️ Rule {rule_id} not found")
        return pd.DataFrame()

    msg_type, param, op_str, threshold = rule

    # 2. Schema check (CRITICAL FIX)
    schema_df = con.execute("PRAGMA table_info('nav_segment_1')").fetchdf()
    col_names = schema_df['name'].tolist()

    if param not in col_names:
        print(f"   ⚠️ Skipping {rule_id}: Column '{param}' not in dataset")
        return pd.DataFrame()

    # 3. Operator mapping
    op_map = {
        "eq": "=",
        "gt": ">",
        "lt": "<",
        "gte": ">=",
        "lte": "<=",
        "neq": "!="
    }
    sql_op = op_map.get(op_str, "=")

    # 4. Safe query (NOW MATCHES nav_meta_log schema)
    query = f"""
        SELECT
            inode,
            TimeUS,
            '{rule_id}' AS rule_id,
            '{param}' AS parameter,   -- ✅ FIXED (was missing)
            {param} AS actual_value,
            '{mission_id}' AS mission_id,
            1 AS segment_id
        FROM nav_segment_1
        WHERE msg_type = '{msg_type}'
          AND {param} {sql_op} {threshold}
    """

    try:
        return con.execute(query).fetchdf()
    except Exception as e:
        print(f"   ❌ Query failed for {rule_id}: {e}")
        return pd.DataFrame()