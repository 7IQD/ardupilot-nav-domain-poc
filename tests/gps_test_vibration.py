# gps_test_vibration.py
# --- PYTHON 3.12 COMPATIBILITY PATCH ---
import collections
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping
collections.Mapping = collections.abc.Mapping
collections.Sequence = collections.abc.Sequence
collections.Iterable = collections.abc.Iterable
collections.Callable = collections.abc.Callable
# ---------------------------------------

from dronekit import connect
import time

def run_vibration_test():
    connection_string = '127.0.0.1:14551'
    print(f"🚀 Connecting to {connection_string}...")
    vehicle = connect(connection_string, wait_ready=True)

    try:
        # --- Ensure throttle at idle BEFORE arming ---
        vehicle.channels.overrides['3'] = 1000
        print("🟢 Throttle idle set (pre-arm)")

        # --- PRE-ARM: Moderate vibration and IMU params ---
        vehicle.parameters['SIM_VIB_MOT_MASK'] = 15
        vehicle.parameters['SIM_VIB_MOT_MAX'] = 5
        vehicle.parameters['SIM_VIB_MOT_MULT'] = 20
        vehicle.parameters['SIM_VIB_FREQ_X'] = 50
        vehicle.parameters['SIM_VIB_FREQ_Y'] = 50
        vehicle.parameters['SIM_VIB_FREQ_Z'] = 50
        vehicle.parameters['SIM_ACC1_RND'] = 5
        vehicle.parameters['SIM_ACCEL1_FAIL'] = 0

        # --- Arm safely ---
        print("🟢 Arming vehicle at idle throttle...")
        vehicle.armed = True
        while not vehicle.armed:
            time.sleep(0.5)
        vehicle.channels.overrides['3'] = 1600

        # --- Listeners with reduced print rate ---
        last_vib, last_imu = 0, 0
        def vib_listener(self, name, msg):
            nonlocal last_vib
            if time.time() - last_vib > 0.5:
                print(f"VIBRATION x={msg.vibration_x:.3f}, y={msg.vibration_y:.3f}, z={msg.vibration_z:.3f}")
                last_vib = time.time()
        vehicle.add_message_listener('VIBRATION', vib_listener)

        def imu_listener(self, name, msg):
            nonlocal last_imu
            if time.time() - last_imu > 0.5:
                print(f"RAW_IMU x={msg.xacc}, y={msg.yacc}, z={msg.zacc}")
                last_imu = time.time()
        vehicle.add_message_listener('RAW_IMU', imu_listener)

        # --- PHASE 0: Baseline ---
        print("🟢 Baseline vibration (20s)")
        time.sleep(20)

        # --- PHASE 1: T2 High vibration ---
        print("🟡 Inducing HIGH vibration (T2)")
        try:
            vehicle.parameters['SIM_VIB_MOT_MULT'] = 30
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ SIM_VIB_MOT_MULT failed: {e}")
        time.sleep(15)

        # --- PHASE 2: T3 IMU fault ---
        print("🟠 Inducing IMU fault (T3)")
        try:
            vehicle.parameters['SIM_ACCEL1_FAIL'] = 1
            time.sleep(1)
            vehicle.parameters['SIM_ACC1_RND'] = 8
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ IMU fault params failed: {e}")
        time.sleep(15)

        # --- PHASE 3: Recovery ---
        print("🔵 Recovery to baseline vibration and normal IMU")
        try:
            vehicle.parameters['SIM_VIB_MOT_MULT'] = 20
            time.sleep(1)
            vehicle.parameters['SIM_ACCEL1_FAIL'] = 0
            time.sleep(1)
            vehicle.parameters['SIM_ACC1_RND'] = 5
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Reset parameters failed: {e}")
        time.sleep(10)

        print("\n✅ Vibration & IMU Test Complete. BIN logs ready for analysis.")

    finally:
        # --- Clean up listeners and overrides ---
        vehicle.channels.overrides = {}
        vehicle.remove_message_listener('VIBRATION', vib_listener)
        vehicle.remove_message_listener('RAW_IMU', imu_listener)

        # --- Close vehicle and allow MAVLink threads to finish ---
        vehicle.close()
        time.sleep(0.5)   # ensures no post-run connection errors

if __name__ == "__main__":
    run_vibration_test()