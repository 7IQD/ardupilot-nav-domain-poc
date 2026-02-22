#!/usr/bin/env python3
import duckdb
import os

# ✅ Path to Drone-DF database (warehouse_df)
DB_PATH = "../../bin/vault/warehouse_df/drone_df_views.db"

def review_vault_timing():
    """
    Performs a temporal integrity audit on ui_nav_drone_monitor.
    Checks mission duration, gaps, and prints top 5 largest gaps.
    Also prints per-mission timing summary.
    """
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    con = duckdb.connect(DB_PATH)
    print("📋 --- DF PATH TIMING INTEGRITY AUDIT ---")

    # 1️⃣ Global range across all missions
    range_data = con.execute("""
        SELECT
            MIN(timestamp_sec) AS start_s,
            MAX(timestamp_sec) AS end_s,
            MAX(timestamp_sec) - MIN(timestamp_sec) AS duration_s
        FROM ui_nav_drone_monitor
    """).fetchone()

    print(f"⏱️ Mission Start: {range_data[0]:.2f}s")
    print(f"⏱️ Mission End:   {range_data[1]:.2f}s")
    print(f"⏱️ Total Flight:  {range_data[2]:.2f}s")

    # 2️⃣ Check for temporal gaps > 0.5s (possible CPU/log drops)
    gaps = con.execute("""
        SELECT timestamp_sec, next_ts - timestamp_sec AS gap
        FROM (
            SELECT timestamp_sec,
                   LEAD(timestamp_sec) OVER (ORDER BY timestamp_sec) AS next_ts
            FROM ui_nav_drone_monitor
        )
        WHERE gap > 0.5
        ORDER BY gap DESC
        LIMIT 5
    """).fetchall()

    if gaps:
        print("\n⚠️ LOG GAPS DETECTED (Potential CPU or Logging Hangs):")
        for g in gaps:
            print(f"   - Gap of {g[1]:.2f}s at {g[0]:.2f}s")
    else:
        print("\n✅ Temporal Continuity: No significant data gaps found.")

    # 3️⃣ Per-mission timing summary
    missions = con.execute("""
        SELECT mission_id,
               MIN(timestamp_sec) AS start_s,
               MAX(timestamp_sec) AS end_s,
               MAX(timestamp_sec) - MIN(timestamp_sec) AS duration_s
        FROM ui_nav_drone_monitor
        GROUP BY mission_id
        ORDER BY start_s
    """).fetchall()

    if missions:
        print("\n📊 Per-mission Timing Summary:")
        for m in missions:
            print(f"   - Mission {m[0]} | Start: {m[1]:.2f}s | End: {m[2]:.2f}s | Duration: {m[3]:.2f}s")
    else:
        print("⚠️ No mission_id entries found for per-mission summary.")

    con.close()

if __name__ == "__main__":
    review_vault_timing()
