import duckdb
import os

DB_PATH = "bin/nav_domain.db"
os.makedirs("bin", exist_ok=True)

conn = duckdb.connect(DB_PATH)
print(f"🏗️  Re-Initializing Synchronized Vault: {DB_PATH}")

try:
    # 1. METADATA LAYER
    conn.execute("CREATE TABLE IF NOT EXISTS meta_ledger (last_inode INTEGER NOT NULL);")
    if conn.execute("SELECT COUNT(*) FROM meta_ledger").fetchone()[0] == 0:
        conn.execute("INSERT INTO meta_ledger VALUES (0);")

    # 2. DEFINITIONS (Synchronized with Audit Report)
    tables = {
        "nav_gps": """
            inode INTEGER PRIMARY KEY NOT NULL,
            timestamp_us BIGINT,
            lat_raw INTEGER, lon_raw INTEGER, alt_raw INTEGER,
            rel_alt_raw INTEGER, vx INTEGER, vy INTEGER, vz INTEGER
        """,
        "nav_attitude": """
            inode INTEGER PRIMARY KEY NOT NULL,
            timestamp_us BIGINT,
            roll_raw DOUBLE, pitch_raw DOUBLE, yaw_raw DOUBLE,
            rollspeed_raw DOUBLE, pitchspeed_raw DOUBLE, yawspeed_raw DOUBLE
        """,
        "sys_battery": """
            inode INTEGER PRIMARY KEY NOT NULL,
            timestamp_us BIGINT,
            volt_raw INTEGER, curr_raw INTEGER, battery_remaining SMALLINT
        """,
        "sys_cpu": """
            inode INTEGER PRIMARY KEY NOT NULL,
            timestamp_us BIGINT,
            load_raw SMALLINT
        """
    }

    for table_name, schema in tables.items():
        # Drop and Recreate to ensure clean alignment with the Audit
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.execute(f"CREATE TABLE {table_name} ({schema})")
        conn.execute(f"CREATE INDEX idx_{table_name}_inode ON {table_name} (inode)")

    print("✅ Vault Synchronized with Mapping Policy.")

except Exception as e:
    print(f"❌ Initialization Failed: {e}")
finally:
    conn.close()