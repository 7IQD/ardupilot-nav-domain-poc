import collections
import sys

# --- PYTHON 3.12 COMPATIBILITY PATCH ---
# Dronekit relies on 'collections.MutableMapping' which was moved to 'collections.abc'
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping
collections.Mapping = collections.abc.Mapping
collections.Sequence = collections.abc.Sequence
collections.Iterable = collections.abc.Iterable
collections.Callable = collections.abc.Callable
# ---------------------------------------

from dronekit import connect
import time

def run_calibrated_test():
    # Use the port we confirmed earlier
    connection_string = '127.0.0.1:14551'
    print(f"🚀 Connecting to {connection_string}...")

    try:
        vehicle = connect(connection_string, wait_ready=True)

        def set_gps(val):
            print(f"📡 Setting SIM_GPS1_NUMSATS to {val}")
            try:
                vehicle.parameters['SIM_GPS1_NUMSATS'] = val
            except Exception as e:
                print(f"⚠️ Timeout/Error: {e} (Value usually updates anyway)")
            time.sleep(1)

        # --- PHASE 0: Baseline (12 Sats) ---
        print("🟢 Starting Baseline: 12 Sats for 20s")
        set_gps(12)
        time.sleep(20)

        # --- PHASE 1: Degraded (7 Sats) ---
        print("🟡 Entering Degraded: 7 Sats for 10s")
        set_gps(7)
        time.sleep(10)

        # --- PHASE 2: Loss (0 Sats) ---
        print("🔴 Entering Critical: 0 Sats for 10s")
        set_gps(0)
        time.sleep(10)

        # --- PHASE 3: Recovery (12 Sats) ---
        print("🔵 Recovery: Back to 12 Sats")
        set_gps(12)
        time.sleep(10)

        print("\n✅ Test Complete. Ready for DataFlash analysis.")

    finally:
        if 'vehicle' in locals():
            vehicle.close()

if __name__ == "__main__":
    run_calibrated_test()