#!/usr/bin/env python3
from pymavlink import mavutil

def main():
    """
    Monitor: Connect to SITL and count packets.
    """
    connection = mavutil.mavlink_connection('udp:127.0.0.1:14551')
    print("💓 Heartbeat received from SITL!")
    connection.wait_heartbeat()

    received_count = 0
    try:
        while True:
            msg = connection.recv_match(blocking=True)
            if msg:
                received_count += 1
                print(f"Packets received from SITL: {received_count}", end="\r")
    except KeyboardInterrupt:
        print(f"\nTotal packets received: {received_count}")

if __name__ == "__main__":
    main()
