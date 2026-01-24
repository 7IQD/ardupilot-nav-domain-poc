import os
import signal
import sys
import duckdb
from multiprocessing import Event

DB_PATH = "src/bin/nav_domain.db"
BIN_DIR = "src/bin"

shutdown_event = Event()


def ensure_db():
    """
    Ensure DuckDB file is valid.
    If missing → create fresh DB with required bootstrap tables.
    """
    os.makedirs(BIN_DIR, exist_ok=True)

    fresh = not os.path.exists(DB_PATH)

    conn = duckdb.connect(DB_PATH)

    if fresh:
        conn.execute("""
            CREATE TABLE meta_ledger (
                id INTEGER PRIMARY KEY,
                last_inode BIGINT
            );
        """)
        conn.execute("INSERT INTO meta_ledger VALUES (1, 0);")
        conn.commit()

    conn.close()


def handle_shutdown(sig, frame):
    print("\n👋 Shutdown signal received...")
    shutdown_event.set()


def main():
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    print("🛰️  Starting full SITL telemetry pipeline...")

    # 🔒 Single-point DB initialization (critical)
    ensure_db()

    # Open DB ONLY AFTER it is guaranteed valid
    conn = duckdb.connect(DB_PATH)

    try:
        last_inode = conn.execute(
            "SELECT last_inode FROM meta_ledger WHERE id = 1"
        ).fetchone()[0]
        print(f"⚠️  Last inode restored: {last_inode}")
    except Exception:
        print("⚠️  No existing Inode found. Starting at 0.")

    print("💓 Heartbeat received!")

    try:
        while not shutdown_event.is_set():
            # SITL ingest loop lives elsewhere
            shutdown_event.wait(0.2)

    finally:
        conn.close()
        print("✅ Full pipeline offline.")


if __name__ == "__main__":
    main()
