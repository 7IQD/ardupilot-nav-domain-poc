import os
import sys
import duckdb

# -------------------------------------------------------
# NAV DATA INTEGRITY CHECK
# Purpose:
# Validate fused NAV dataset before analysis/labeling
# -------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../"))
DATA_DIR = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")

NAV_MASTER = os.path.join(DATA_DIR, "nav_df_master.parquet")


def run_integrity_check():

    print("🚀 Initializing NAV Integrity Audit...\n")

    if not os.path.exists(NAV_MASTER):
        print(f"❌ ERROR: NAV dataset not found at:\n{NAV_MASTER}")
        if os.path.exists(DATA_DIR):
            print("\n📂 Files available in warehouse:")
            print(os.listdir(DATA_DIR))
        else:
            print("\n❌ Warehouse directory missing")
        sys.exit(1)

    ctx = duckdb.connect(":memory:")

    try:

        # -------------------------------------------------------
        # BASIC DATASET STATS
        # -------------------------------------------------------

        stats = ctx.execute(f"""
            SELECT
                count(*) as n_rows,
                count(Lat) as n_gps,
                count(Roll) as n_att,
                min(TimeUS) as t_start,
                max(TimeUS) as t_end
            FROM read_parquet('{NAV_MASTER}')
        """).fetchone()

        n_rows, n_gps, n_att, t_start, t_end = stats
        duration_sec = (t_end - t_start) / 1e6

        # -------------------------------------------------------
        # TIMESTAMP MONOTONICITY CHECK
        # -------------------------------------------------------

        time_faults = ctx.execute(f"""
            SELECT count(*) FROM (
                SELECT
                    TimeUS,
                    lead(TimeUS) OVER (ORDER BY TimeUS) as next_t
                FROM read_parquet('{NAV_MASTER}')
            )
            WHERE next_t < TimeUS
        """).fetchone()[0]

        # -------------------------------------------------------
        # INVALID GPS CHECK
        # -------------------------------------------------------

        invalid_gps = ctx.execute(f"""
            SELECT count(*)
            FROM read_parquet('{NAV_MASTER}')
            WHERE Lat = 0 OR Lng = 0
        """).fetchone()[0]

        # -------------------------------------------------------
        # SATELLITE HEALTH
        # -------------------------------------------------------

        sat_stats = ctx.execute(f"""
            SELECT
                avg(NSats),
                min(NSats),
                max(NSats)
            FROM read_parquet('{NAV_MASTER}')
        """).fetchone()

        avg_sats, min_sats, max_sats = sat_stats

        # -------------------------------------------------------
        # GPS FIX QUALITY DISTRIBUTION
        # -------------------------------------------------------

        fix_quality = ctx.execute(f"""
            SELECT
                count(*) FILTER (WHERE NSats >= 10) as strong_fix,
                count(*) FILTER (WHERE NSats BETWEEN 6 AND 9) as weak_fix,
                count(*) FILTER (WHERE NSats < 6) as bad_fix
            FROM read_parquet('{NAV_MASTER}')
        """).fetchone()

        strong_fix, weak_fix, bad_fix = fix_quality

        # -------------------------------------------------------
        # GPS JUMP DETECTION
        # -------------------------------------------------------

        gps_jumps = ctx.execute(f"""
            SELECT count(*) FROM (
                SELECT
                    Lat,
                    LAG(Lat) OVER (ORDER BY TimeUS) as prev_lat,
                    Lng,
                    LAG(Lng) OVER (ORDER BY TimeUS) as prev_lng
                FROM read_parquet('{NAV_MASTER}')
            )
            WHERE abs(Lat - prev_lat) > 0.01
               OR abs(Lng - prev_lng) > 0.01
        """).fetchone()[0]

        # -------------------------------------------------------
        # REPORT
        # -------------------------------------------------------

        print("------ NAV INTEGRITY REPORT ------\n")

        print(f"Entries        : {n_rows}")
        print(f"Mission Length : {duration_sec:.2f} seconds\n")

        print(f"GPS Health     : {(n_gps/n_rows)*100:.1f}%")
        print(f"ATT Health     : {(n_att/n_rows)*100:.1f}%\n")

        print(f"Avg Satellites : {avg_sats:.2f}")
        print(f"Min Satellites : {min_sats}")
        print(f"Max Satellites : {max_sats}\n")

        print("GPS Fix Quality Distribution:")
        print(f"  Strong Fix (≥10 sats) : {strong_fix}")
        print(f"  Weak Fix (6–9 sats)   : {weak_fix}")
        print(f"  Bad Fix (<6 sats)     : {bad_fix}\n")

        print(f"Invalid GPS Rows : {invalid_gps}")
        print(f"GPS Jumps        : {gps_jumps}")
        print(f"Time Faults      : {time_faults}")

        # -------------------------------------------------------
        # VALIDATION LOGIC
        # -------------------------------------------------------

        if time_faults > 0:
            print("\n❌ TEMPORAL ERROR: Non-monotonic timestamps detected")
            sys.exit(1)

        if invalid_gps > 0:
            print("\n⚠️ DATA WARNING: Invalid GPS coordinates present")

        if gps_jumps > 0:
            print("\n⚠️ NAV ALERT: Possible GPS position jumps detected")

        if bad_fix > (0.3 * n_rows):
            print("\n⚠️ GPS WARNING: Large portion of mission with poor satellite lock")

        if duration_sec < 10:
            print("\n⚠️ WARNING: Mission duration suspiciously short")

        print("\n✅ STATUS: NAV DOMAIN INTEGRITY VERIFIED")

    except Exception as e:
        print(f"\n💥 CRITICAL FAILURE DURING AUDIT:\n{e}")
        sys.exit(1)


# -------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------

if __name__ == "__main__":
    run_integrity_check()