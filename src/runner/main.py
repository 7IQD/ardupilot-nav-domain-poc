#!/usr/bin/env python3
import time
from queue import Queue
from threading import Thread
from pymavlink import mavutil
from src.ingress.materializers import NavDuckDBMaterializer

def start_architect(queue):
    """Start Architect process and ingest packets from queue"""
    architect = NavDuckDBMaterializer()
    print("👤 ARCHITECT: System Online. Monitoring Queue...")

    try:
        while True:
            packet = queue.get()
            if packet is None:  # Poison pill to shutdown
                print("💾 ARCHITECT: Shutdown signal received, closing DB...")
                architect.close()
                break
            architect.ingest(packet)

    except KeyboardInterrupt:
        print("\n👋 ARCHITECT stopped by user.")
        architect.close()

def run_ingress(queue):
    """Simulated Clerk: receives MAVLink packets and pushes to queue"""
    connection = mavutil.mavlink_connection("udp:127.0.0.1:14551")
    print("🛰️ Waiting for SITL heartbeat on 14551...")
    connection.wait_heartbeat()
    print("💓 Heartbeat received!")

    inode = 0
    try:
        while True:
            msg = connection.recv_match(blocking=True)
            if not msg:
                continue
            inode += 1
            packet = {
                "inode": inode,
                "msg_type": msg.get_type(),
                "timestamp": time.time(),
                "data": msg.to_dict()
            }
            queue.put(packet)
            print(f"📦 Clerk captured: inode={inode} | type={packet['msg_type']}")

    except KeyboardInterrupt:
        print(f"\n📥 Clerk stopped at inode {inode}")
        queue.put(None)  # shutdown architect

# -----------------------------
# Main pipeline
# -----------------------------
if __name__ == "__main__":
    packet_queue = Queue()
    Thread(target=start_architect, args=(packet_queue,), daemon=True).start()
    run_ingress(packet_queue)
