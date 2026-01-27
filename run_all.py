import os
import signal
import duckdb
import time
from multiprocessing import Event

# Core imports (Assuming your Orchestrator/Architects are ready)
from src.runner.orchestrator import Orchestrator
from src.ingress.nav_architect import NavArchitect
from src.ingress.sys_architect import SysArchitect

DB_PATH = "src/bin/nav_domain.db"
BIN_DIR = "src/bin"

shutdown_event = Event()

def ensure_db(overwrite=False):
    """Fulfills Overwrite requirement [2026-01-15]"""
    os.makedirs(BIN_DIR, exist_ok=True)

    if overwrite and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = duckdb.connect(DB_PATH)
    if overwrite or not os.path.exists(DB_PATH):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meta_ledger (
                id INTEGER PRIMARY KEY,
                last_inode BIGINT,
                session_start_ns BIGINT
            );
        """)
        conn.execute("INSERT OR IGNORE INTO meta_ledger VALUES (1, 0, ?);", [time.time_ns()])
    conn.close()

def handle_shutdown(sig, frame):
    print("\n👋 [SHUTDOWN] Signal received. Closing pipeline...")
    shutdown_event.set()

def main():
    signal.signal(signal.SIGINT, handle_shutdown)

    # 1. Prepare State
    # Set overwrite=True here to fulfill [2026-01-15] for a fresh POC start
    ensure_db(overwrite=True)

    # 2. Initialize Components
    nav = NavArchitect()
    sys_arch = SysArchitect()
    orchestrator = Orchestrator(nav, sys_arch)

    # 3. Restore Inode from DuckDB
    conn = duckdb.connect(DB_PATH)
    last_inode = conn.execute("SELECT last_inode FROM meta_ledger WHERE id = 1").fetchone()[0]
    orchestrator.inode_counter = last_inode
    print(f"🛰️  Engine Ready. Resuming from Inode: {last_inode}")

    try:
        # Pass the shutdown_event to your run method if modified,
        # or rely on the try/finally block
        orchestrator.run()
    finally:
        # Save state before exit
        conn.execute("UPDATE meta_ledger SET last_inode = ? WHERE id = 1", [orchestrator.inode_counter])
        conn.close()
        print(f"✅ State Saved. Final Inode: {orchestrator.inode_counter}")

if __name__ == "__main__":
    main()