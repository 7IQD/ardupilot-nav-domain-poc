import time
import json
import os
from pymavlink import mavutil
from multiprocessing import Queue

# CONFIG
BRONZE_PATH = "vault/bronze_ledger.jsonl" # JSON Lines format for easy reading
os.makedirs("vault", exist_ok=True)

def run_ingress(materializer_queue):
    """
    The Clerk: Listens to the drone, stamps Inodes, and persists to Bronze.
    """
    # 1. Connect to Drone (Update connection string as needed)
    # Use 'udpin:localhost:14550' for SITL or '/dev/ttyUSB0' for hardware
    connection = mavutil.mavlink_connection('udpin:localhost:14551')

    # 2. Inode Counter (In a full restart, you'd scan the last Inode in Bronze)
    current_inode = 0

    print("📥 Ingress Gate Open: Listening for MAVLink...")

    with open(BRONZE_PATH, "a") as bronze_vault:
        while True:
            # Receive one MAVLink message
            msg = connection.recv_match(blocking=True)
            if not msg: continue

            # THE INGRESS SWITCH: Assign the unique Inode
            current_inode += 1

            # Prepare the Standardized Packet
            stamped_packet = {
                "inode": current_inode,
                "msg_type": msg.get_type(),
                "timestamp_local": time.time(),
                "data": msg.to_dict()
            }

            # PERSIST: Write to Bronze Vault (Immutable Ledger)
            bronze_vault.write(json.dumps(stamped_packet) + "\n")
            bronze_vault.flush() # Ensure it's on disk

            # BROADCAST: Send to Materializer via Queue
            materializer_queue.put(stamped_packet)