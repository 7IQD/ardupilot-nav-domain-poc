#!/usr/bin/env python3
import collections
import collections.abc

# --- Monkeypatch for Python 3.12 compatibility ---
for attr in ["MutableMapping","Mapping","Sequence","MutableSequence","Iterable","Callable"]:
    if not hasattr(collections, attr):
        setattr(collections, attr, getattr(collections.abc, attr))

import time
from dronekit import connect, VehicleMode
from pymavlink import mavutil

# Monkeypatch for DroneKit compatibility
for attr in ["MutableMapping", "Mapping", "Sequence", "MutableSequence", "Iterable", "Callable"]:
    if not hasattr(collections, attr):
        setattr(collections, attr, getattr(collections.abc, attr))

# --- CONFIGURATION ---
print("="*40)
print("🔧 TELEMETRY SETUP")
print("In MAVProxy run:")
print("   link add udp:127.0.0.1:14551")
print("Then verify using:")
print("   link list")
print("You should see: 127.0.0.1:14551")
print("="*40)

input("Press ENTER once the telemetry link is active...")

# Connect via the UDP port you configured in SITL (--out=udp:127.0.0.1:14551)
connection_string = 'udp:127.0.0.1:14551'
print(f"📡 Connecting to SITL on {connection_string}...")
vehicle = connect(connection_string, wait_ready=True, timeout=60, heartbeat_timeout=60)
print("🟢 Connected! Systems Nominal.")

def send_anchor(msg_text):
    """Writes a timestamp marker to the .BIN log for the Refinery Engine."""
    msg = vehicle.message_factory.statustext_encode(
        mavutil.mavlink.MAV_SEVERITY_NOTICE,
        msg_text.encode()
    )
    vehicle.send_mavlink(msg)
    print(f"⚓ Anchor Logged: {msg_text}")

# --- ⚙️ PARAMETER ALIGNMENT (Confirmed Build-Compatible) ---
print("⚙️ Aligning Failsafe Parameters...")
vehicle.parameters['FS_GCS_ENABLE'] = 1
vehicle.parameters['FS_GCS_TIMEOUT'] = 2.0
vehicle.parameters['SIM_RC_FAIL'] = 0
vehicle.parameters['LOG_BITMASK'] = 65535

# --- PHASE 1: STABILIZED BASELINE ---
while vehicle.gps_0.fix_type < 3:
    print("📡 Waiting for GPS Fix...")
    time.sleep(2)

print("🚀 Phase 1: Arming and establishing 15s Baseline...")
vehicle.mode = VehicleMode("GUIDED")
vehicle.armed = True
while not vehicle.armed:
    time.sleep(1)

vehicle.simple_takeoff(15)
time.sleep(15)
print("✅ Baseline established.")

# --- PHASE 2: TRIGGER COM FAILURE ---
send_anchor("EXP_START_T5_COM_FAIL")
print("\n" + "="*40)
print("🚨 PHASE 2: TRIGGER COM FAILURE")
print("Step 1: In MAVProxy run: link list")
print("Step 2: Identify the link sending telemetry to 127.0.0.1:14551")
print("Step 3: Remove that link using: link remove <link_number>")
print("Step 4: Once telemetry stops, press [ENTER] here.")
print("="*40)

vehicle.parameters['SIM_RC_FAIL'] = 1
input("Press Enter once link is removed...")

# --- PHASE 3: BLIND COUNTDOWN ---
print("\n⏱️ PHASE 3: MONITORING FAILSAFE DRIFT")
for i in range(25, 0, -1):
    print(f"   [BLIND COUNTDOWN] {i}s remaining...")
    time.sleep(1)

# --- PHASE 4: RESTORE COM LINK ---
print("\n" + "="*40)
print("🔵 PHASE 4: RESTORE COM LINK")
print("1. In MAVProxy, run: link add udp:127.0.0.1:14551")
print("2. Wait for telemetry to resume, then press [ENTER] here.")
print("="*40)

input("Press Enter once link is restored...")

print("🔄 Reconnecting to MAVLink...")

vehicle.close()

while True:
    try:
        vehicle = connect(connection_string, wait_ready=True, timeout=60)
        print("✅ Telemetry restored.")
        break
    except:
        print("⏳ Still waiting for MAVLink connection...")
        time.sleep(3)

vehicle.parameters['SIM_RC_FAIL'] = 0
send_anchor("EXP_END_T5_COM_FAIL")

print(f"🏁 Experiment Complete. Final Mode: {vehicle.mode.name}")
vehicle.close()