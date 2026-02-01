#!/usr/bin/env python3
from pymavlink import mavutil
import duckdb
import os
import time
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # src/
BIN_DIR = os.path.join(BASE_DIR, "bin")
DB_PATH = os.path.join(BIN_DIR, "nav_domain.db")
MAPPING_PATH = os.path.join(BIN_DIR, "mapping.json")

def init_meta_ledger():
    """Ensure meta_ledger exists and return last inode"""
    os.makedirs(BIN_DIR, exist_ok=True)
    conn = duckdb.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS meta_ledger (
            last_inode BIGINT
        )
    """)
    res = conn.execute("SELECT COUNT(*) FROM meta_ledger").fetchone()[0]
    if res == 0:
        conn.execute("INSERT INTO meta_ledger VALUES (0)")
        conn.commit()
        print("📝 meta_ledger created with last_inode=0")
        last_inode = 0
    else:
        last_inode = conn.execute("SELECT last_inode FROM meta_ledger").fetchone()[0]
        print(f"📝 meta_ledger exists, resuming from last_inode={last_inode}")
    return conn, last_inode

def main():
    """Monitor SITL and update meta_ledger with real-time feedback"""
    # Connect to SITL
    connection = mavutil.mavlink_connection('udp:127.0.0.1:14551')
    print("Connecting to SITL...")
    connection.wait_heartbeat()
    print("✅ Heartbeat received from SITL")

    # Initialize DuckDB meta ledger
    conn, last_inode = init_meta_ledger()

    received_count = 0
    start_time = time.time()

    try:
        while True:
            msg = connection.recv_match(blocking=True)
            if msg:
                received_count += 1
                inode = received_count + last_inode  # Simulated inode

                # Update meta ledger for visibility
                try:
                    conn.execute("UPDATE meta_ledger SET last_inode = ?", (inode,))
                    conn.commit()
                except Exception as e:
                    print(f"⚠️ ERROR updating meta_ledger for inode {inode}: {e}")

                # Print every 50 packets
                if received_count % 50 == 0:
                    elapsed = time.time() - start_time
                    print(f"Packets received: {received_count} | Last inode: {inode} | Time elapsed: {elapsed:.1f}s", end="\r")

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\nTotal packets received: {received_count}")
        print(f"Last inode in meta_ledger: {inode}")
        print(f"Elapsed time: {elapsed:.1f}s")
        print(f"Approx. packets/sec: {received_count/elapsed:.1f}")
        conn.close()

if __name__ == "__main__":
    main()
