#!/usr/bin/env python3
import time
import json
import duckdb
from pymavlink import mavutil
from multiprocessing import Queue

# Internal imports - adjusting to your tree
from .data_manager import DataManager

# Paths relative to the execution context (src/)
DB_PATH = "bin/nav_domain.db"
BRONZE_PATH = "bin/flight_test.jsonl"

def run_ingress(materializer_queue, fresh=False):
    """
    The Clerk: High-speed capture, stamping, and queuing.
    """
    # 1. Connection Setup
    connection = mavutil.mavlink_connection('udp:127.0.0.1:14551')
    print("🛰️  Waiting for SITL heartbeat on 14551...")
    connection.wait_heartbeat()
    print("💓 Heartbeat received!")

    # 2. Inode Resume Logic
    current_inode = 0
    if not fresh:
        try:
            conn = duckdb.connect(DB_PATH)
            current_inode = conn.execute("SELECT last_inode FROM meta_ledger").fetchone()[0]
            conn.close()
            print(f"🔄 Resuming from Inode {current_inode}")
        except Exception:
            print("⚠️ No existing Inode found. Starting at 0.")
    else:
        # If fresh, truncate the bronze ledger
        open(BRONZE_PATH, 'w').close()
        print("🧹 Fresh start: Bronze ledger cleared.")

    # 3. Main Ingestion Loop
    with open(BRONZE_PATH, "a") as bronze_vault:
        try:
            while True:
                msg = connection.recv_match(blocking=True)
                if not msg: continue

                # The Inode Stamp
                current_inode += 1

                # Standardized Packet
                packet = {
                    "inode": current_inode,
                    "msg_type": msg.get_type(),
                    "timestamp": time.time(),
                    "data": msg.to_dict()
                }

                # Step A: Persistent Bronze Write
                bronze_vault.write(json.dumps(packet) + "\n")
                bronze_vault.flush()

                # Step B: Hand-off to the Architect (Materializer)
                materializer_queue.put(packet)

        except KeyboardInterrupt:
            print("\n📥 Clerk stopped.")