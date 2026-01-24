#!/usr/bin/env python3
import time
import json
import os
from queue import Queue
from threading import Thread
from pymavlink import mavutil
from src.runner.main import start_architect

# Paths
BRONZE_PATH = "bin/flight_test.jsonl"
DB_PATH = "bin/nav_domain.db"

def run_ingress(queue, fresh=False):
    """
    Clerk:
    - Listens to SITL
    - Assigns monotonic inode
    - Writes Bronze log
    - Forwards packets to Architect via queue
    """
    os.makedirs("bin", exist_ok=True)

    if fresh:
        open(BRONZE_PATH, "w").close()
        print("🧹 Fresh start: Bronze ledger cleared.")
    elif not os.path.exists(BRONZE_PATH):
        open(BRONZE_PATH, "a").close()

    # Resume inode from DuckDB if exists
    current_inode = 0
    try:
        if os.path.exists(DB_PATH):
            conn = duckdb.connect(DB_PATH, read_only=True)
            res = conn.execute("SELECT last_inode FROM meta_ledger").fetchone()
            if res:
                current_inode = res[0]
            conn.close()
            print(f"🔄 Resuming from Inode {current_inode}")
    except Exception:
        print("⚠️ No existing Inode found. Starting at 0.")

    # Connect to SITL
    connection = mavutil.mavlink_connection("udp:127.0.0.1:14551")
    print("🛰️ Waiting for SITL heartbeat on 14551...")
    connection.wait_heartbeat()
    print("💓 Heartbeat received!")
    print(f"➡️  CLERK → QUEUE | inode={current_inode} | {msg.get_type()}")

    received = 0
    with open(BRONZE_PATH, "a") as bronze_vault:
        try:
            while True:
                msg = connection.recv_match(blocking=True)
                if not msg:
                    continue

                received += 1
                current_inode += 1

                packet = {
                    "inode": current_inode,
                    "msg_type": msg.get_type(),
                    "timestamp": time.time(),
                    "data": msg.to_dict()
                }

                bronze_vault.write(json.dumps(packet) + "\n")
                bronze_vault.flush()

                queue.put(packet)

                if received % 100 == 0:
                    print(f"📦 Packets captured: {received} | Last inode: {current_inode}", end="\r")

        except KeyboardInterrupt:
            print(f"\n📥 Clerk stopped at inode {current_inode}")
            queue.put(None)  # shutdown Architect

# -----------------------------
# Main block: restores full pipeline
# -----------------------------
if __name__ == "__main__":
    packet_queue = Queue()
    Thread(target=start_architect, args=(packet_queue,), daemon=True).start()
    run_ingress(packet_queue)
