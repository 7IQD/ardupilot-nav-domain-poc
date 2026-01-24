import os
import duckdb

# 🔹 Ensure DB path is always relative to 'src' folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src/core
DB_PATH = os.path.join(BASE_DIR, "..", "bin", "nav_domain.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def initialize_vault():
    conn = duckdb.connect(DB_PATH)
    print(f"🏗️  Re-Initializing Synchronized Vault: {DB_PATH}")

    try:
        # 1️⃣ Schemas
        conn.execute("CREATE SCHEMA IF NOT EXISTS silver;")
        conn.execute("CREATE SCHEMA IF NOT EXISTS gold;")

        # 2️⃣ Metadata Table
        conn.execute("CREATE TABLE IF NOT EXISTS meta_ledger (last_inode INTEGER NOT NULL);")
        if conn.execute("SELECT COUNT(*) FROM meta_ledger").fetchone()[0] == 0:
            conn.execute("INSERT INTO meta_ledger VALUES (0);")

        # 3️⃣ Silver Tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS silver.nav_state (
                ts_boot DOUBLE PRIMARY KEY,
                pos_n DOUBLE, pos_e DOUBLE, pos_d DOUBLE,
                vel_n DOUBLE, vel_e DOUBLE, vel_d DOUBLE,
                vel_test_ratio DOUBLE,
                control_mode VARCHAR
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nav_state_ts_boot ON silver.nav_state(ts_boot)")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS silver.gps_observation (
                ts_boot DOUBLE PRIMARY KEY,
                lat DOUBLE, lon DOUBLE, alt_msl DOUBLE,
                fix_type INTEGER CHECK (fix_type >= 0),
                satellites_visible INTEGER CHECK (satellites_visible >= 0)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_gps_observation_ts_boot ON silver.gps_observation(ts_boot)")

        # 4️⃣ Raw Telemetry (Pre-activation)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS nav_gps (
                inode INTEGER PRIMARY KEY NOT NULL,
                timestamp_us BIGINT,
                lat_raw INTEGER, lon_raw INTEGER, alt_raw INTEGER,
                rel_alt_raw INTEGER, vx INTEGER, vy INTEGER, vz INTEGER
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nav_gps_inode ON nav_gps(inode)")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS nav_attitude (
                inode INTEGER PRIMARY KEY NOT NULL,
                timestamp_us BIGINT,
                roll_raw DOUBLE, pitch_raw DOUBLE, yaw_raw DOUBLE,
                rollspeed_raw DOUBLE, pitchspeed_raw DOUBLE, yawspeed_raw DOUBLE
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nav_attitude_inode ON nav_attitude(inode)")

        # 5️⃣ Gold View (Playback Contract)
        conn.execute("""
            CREATE OR REPLACE VIEW gold.nav_context AS
            SELECT * FROM silver.nav_state ORDER BY ts_boot ASC
        """)

        print("✅ Vault Synchronized with Iteration-1 Structural Plan.")

    except Exception as e:
        print(f"❌ Initialization Failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_vault()
