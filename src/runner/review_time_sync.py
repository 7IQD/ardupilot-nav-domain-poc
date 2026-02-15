#!/usr/bin/env python3
import duckdb
import os

# Path to the verified database you just queried
DB_PATH = "../../bin/vault/warehouse/nav_dflog_domain.db"

def review_vault_timing():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    con = duckdb.connect(DB_PATH)

    print("📋 --- TIMING INTEGRITY AUDIT ---")

    # 1. Check Global Range
    range_data = con.execute("""
        SELECT
            MIN(timestamp_sec) as start_s,
            MAX(timestamp_sec) as end_s,
            MAX(timestamp_sec) - MIN(timestamp_sec) as duration_s
        FROM ui_nav_drone_monitor
    """).fetchone()

    print(f"⏱️  Mission Start: {range_data[0]:.2f}s")
    print(f"⏱️  Mission End:   {range_data[1]:.2f}s")
    print(f"⏱️  Total Flight:  {range_data[2]:.2f}s")

    # 2. Check for "Time Gaps" (Nate's Root Cause Detection)
    # This finds if the log skipped more than 0.5 seconds anywhere
    gaps = con.execute("""
        SELECT timestamp_sec, next_ts - timestamp_sec as gap
        FROM (
            SELECT timestamp_sec, LEAD(timestamp_sec) OVER (ORDER BY timestamp_sec) as next_ts
            FROM ui_nav_drone_monitor
        )
        WHERE gap > 0.5
        LIMIT 5
    """).fetchall()

    if gaps:
        print("\n⚠️  LOG GAPS DETECTED (Potential CPU Hangs):")
        for g in gaps:
            print(f"   - Gap of {g[1]:.2f}s found at {g[0]:.2f}s")
    else:
        print("\n✅ Temporal Continuity: No significant data gaps found.")

    con.close()

if __name__ == "__main__":
    review_vault_timing()