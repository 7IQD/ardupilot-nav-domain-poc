import duckdb
import pandas as pd
import os
import warnings

print("HUD FILE:", __file__)
# Suppress the pandas downcasting warning for cleaner HUD
warnings.filterwarnings("ignore", category=FutureWarning)

def run_hud():
    # Canonical pathing
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "bin", "nav_domain.db")

    if not os.path.exists(db_path):
        print(f"❌ DB not found at {db_path}")
        return

    conn = duckdb.connect(db_path)

    # 1. Inventory Check (including the new Estimator table)
    print("\n📊 --- NAVIGATION DOMAIN: VAULT INVENTORY ---")
    tables = ["nav_gps", "nav_attitude", "nav_estimator", "sys_battery"]
    for t in tables:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"   {t.ljust(15)}: {count} rows")
        except:
            print(f"   {t.ljust(15)}: [MISSING]")

    # 2. The Synchronized HUD Query
    # We join everything onto the GPS table (our primary spatial reference)
    query = """
    SELECT
        g.inode,
        g.rel_alt_raw / 1000.0 AS alt_m,
        ROUND(a.roll_raw, 3) AS roll,
        ROUND(a.pitch_raw, 3) AS pitch,
        b.volt_raw / 1000.0 AS batt_v,
        ROUND(e.velocity_variance, 4) AS vel_var,  -- The Confidence Anchor
        ROUND(e.pos_horiz_variance, 4) AS pos_var -- The Spatial Anchor
    FROM nav_gps g
    ASOF LEFT JOIN nav_attitude a ON g.timestamp_us >= a.timestamp_us
    ASOF LEFT JOIN sys_battery b  ON g.timestamp_us >= b.timestamp_us
    ASOF LEFT JOIN nav_estimator e ON g.timestamp_us >= e.timestamp_us
    ORDER BY g.inode DESC
    LIMIT 10
    """

    try:
        df = conn.execute(query).df()
        print("\n✈️  --- LATEST SYNCHRONIZED TELEMETRY ---")
        if df.empty:
            print("   [No data in vault]")
        else:
            # Clean display
            # Before the print statement:
            # 1. Fill NaNs with your placeholder string
            # 2. Force the object type to avoid the downcasting warning
            display_df = df.fillna("---").astype(str)

            print("\n✈️  --- LATEST SYNCHRONIZED TELEMETRY ---")
            print(display_df.to_string(index=False))

            # Health Logic
            latest_alt = df.iloc[0]['alt_m']
            status = "🟢 HEALTHY"

            # Check for EKF drift
            if df.iloc[0]['pos_var'] != None and df.iloc[0]['pos_var'] > 0.5:
                status = "🟠 WARNING: EKF DRIFT"

            state = "Airborne" if latest_alt > 0.5 else "Grounded"
            print(f"\n✅ SYSTEM STATUS: {state} ({latest_alt}m) | {status}")

    except Exception as e:
        print(f"HUD Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_hud()