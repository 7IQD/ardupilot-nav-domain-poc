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

        # 3️⃣ Silver Tables (Operational State)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS silver.nav_state (
                ts_boot DOUBLE PRIMARY KEY,
                pos_n DOUBLE, pos_e DOUBLE, pos_d DOUBLE,
                vel_n DOUBLE, vel_e DOUBLE, vel_d DOUBLE,
                vel_test_ratio DOUBLE,
                control_mode VARCHAR
            )
        """)

        # 4️⃣ Gold Fact Tables (Refinery Targets)
        # These MUST exist for nav_refinery and sys_refinery to succeed
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fact_nav_precision (
                mission_id VARCHAR,
                timestamp VARCHAR,
                ekf_healthy INTEGER,
                vel_variance DOUBLE,
                pos_variance DOUBLE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS fact_sys_status (
                mission_id VARCHAR,
                timestamp VARCHAR,
                cpu_load DOUBLE,
                voltage_bat DOUBLE
            )
        """)

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