#!/usr/bin/env python3
"""
Navigation Domain
Experiment: T3 IMU Failure Dataset Generation
Target: High-noise vibration stress on EKF3
"""

import collections
import collections.abc

# Python 3.12 compatibility patch
for attr in ["MutableMapping","Mapping","Sequence","MutableSequence","Iterable","Callable"]:
    if not hasattr(collections, attr):
        setattr(collections, attr, getattr(collections.abc, attr))

from dronekit import connect, VehicleMode
import time


def wait_for_gps(vehicle):
    """Wait until SITL provides a valid GPS fix"""
    print("📡 Waiting for GPS fix...")

    while True:
        gps = vehicle.gps_0
        if gps.fix_type >= 3:
            print(f"✅ GPS FIX ACQUIRED (fix_type={gps.fix_type}, sats={gps.satellites_visible})")
            break
        else:
            print(f"   waiting... fix_type={gps.fix_type}, sats={gps.satellites_visible}")
            time.sleep(2)


def inject_noise_blanket(vehicle, level):
    """Apply noise to all IMU instances"""
    print(f"   [Action] Setting SIM_ACC/GYR_RND to: {level}")

    for i in [1,2,3]:
        try:
            vehicle.parameters[f"SIM_ACC{i}_RND"] = level
            vehicle.parameters[f"SIM_GYR{i}_RND"] = level
        except:
            pass


def run_imu_failure_test():

    connection_string = "udp:127.0.0.1:14551"
    print(f"🚀 Connecting to SITL at {connection_string}...")

    vehicle = connect(connection_string, wait_ready=True)

    # Logging setup
    print("🟢 Configuring logging...")
    vehicle.parameters["LOG_BITMASK"] = 16254
    vehicle.parameters["LOG_DISARMED"] = 1
    vehicle.parameters["ARMING_CHECK"] = 0

    # Wait for GPS/EKF
    wait_for_gps(vehicle)

    print("⏳ Waiting for EKF stabilization (10s)...")
    time.sleep(10)

    # Baseline noise
    print("🟢 Initializing baseline noise (0)...")
    inject_noise_blanket(vehicle,0)

    # Arm vehicle
    print("🟢 Arming in STABILIZE...")
    vehicle.mode = VehicleMode("STABILIZE")
    vehicle.armed = True

    while not vehicle.armed:
        print("   ...waiting for arming")
        time.sleep(1)

    print("✅ Vehicle armed")

    # Spin motors
    print("🚀 Motors active: Setting Throttle Override to 1600")
    vehicle.channels.overrides["3"] = 1600

    # Phase 1
    print("📊 Phase 1: Healthy baseline (20s)")
    time.sleep(20)

    # Phase 2
    print("🟡 Phase 2: Noise ramp begins")
    for level in [10,20,40]:
        inject_noise_blanket(vehicle,level)
        time.sleep(1)
        print(f"   [Observation] Monitoring noise level {level} (9s)")
        time.sleep(9)

    # Phase 3
    print("🟠 Phase 3: Sustained failure at peak noise (15s)")
    time.sleep(15)

    # Phase 4
    print("🔵 Phase 4: Recovery to baseline")
    inject_noise_blanket(vehicle,0)
    time.sleep(10)

    print("\n✅ T3 IMU failure dataset generation complete")

    print("🧹 Cleaning channel overrides and closing vehicle...")
    vehicle.channels.overrides = {}
    vehicle.close()


if __name__ == "__main__":
    run_imu_failure_test()