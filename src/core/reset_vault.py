# src/core/reset_vault.py
import os
import duckdb
import sys

def force_init():
    # Correct Python path resolution (No Bash syntax!)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    DB_PATH = os.path.join(BASE_DIR, "bin", "nav_domain.db")

    # Remove old DB if it exists
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"🗑️  Overwriting existing database at: {DB_PATH}")
        except OSError as e:
            print(f"❌ CRITICAL ERROR: Could not delete database. Is another script running?\n{e}")
            sys.exit(1)

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Initialize fresh connection
    conn = duckdb.connect(DB_PATH)

    # --- Schema Initialization ---
    conn.execute("CREATE TABLE main.meta_ledger (last_inode BIGINT PRIMARY KEY);")
    conn.execute("INSERT INTO main.meta_ledger VALUES (0);")

    conn.execute("""
    CREATE TABLE main.nav_gps (
        inode BIGINT PRIMARY KEY, timestamp_us BIGINT,
        lat DOUBLE, lon DOUBLE, alt DOUBLE, relative_alt DOUBLE,
        vx DOUBLE, vy DOUBLE, vz DOUBLE
    );
    """)
    # ... (Include your other CREATE TABLE statements for attitude, estimator, battery) ...

    conn.close()
    print("✅ Vault is fresh and all tables are ready.")

if __name__ == "__main__":
    force_init()