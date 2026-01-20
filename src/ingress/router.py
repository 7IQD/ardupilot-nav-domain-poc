# router.py
from pymavlink import mavutil
from data_manager import DataManager
import time

# 1️⃣ Connect to SITL (UDP port may vary)
connection = mavutil.mavlink_connection('udp:127.0.0.1:14551')

# 2️⃣ Setup DataManager (canonical storage)
db = DataManager(base_name="flight_test", folder="bin")
db.initialize_storage(overwrite=True)

print("Waiting for MAVLink heartbeats...")
connection.wait_heartbeat()
print("Heartbeat received! Recording started...")

try:
    while True:
        msg = connection.recv_match(blocking=True)
        if not msg:
            continue

        # Capture raw bytes and write to storage
        raw_bytes = msg.get_msgbuf()
        inode = db.write_entry(raw_bytes)

        if inode % 50 == 0:
            print(f"Captured {inode} packets...")

except KeyboardInterrupt:
    print("\nRecording stopped by user.")
