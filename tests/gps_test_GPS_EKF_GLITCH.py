import time
from pymavlink import mavutil

UDP_PORT = "udp:127.0.0.1:14551"
master = mavutil.mavlink_connection(UDP_PORT)

def set_param(name, value):
    master.mav.param_set_send(
        master.target_system,
        master.target_component,
        name.encode('utf-8'),
        float(value),
        mavutil.mavlink.MAV_PARAM_TYPE_REAL32
    )

def setup_streams():
    print("🎯 Opening telemetry streams")

    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        0, 32, 100000, 0,0,0,0,0
    )

    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        0, 193, 100000, 0,0,0,0,0
    )


print("📡 Waiting for Heartbeat...")
master.wait_heartbeat()
print("✅ Connected to SITL")

setup_streams()

# clean baseline
set_param("SIM_GPS1_GLTCH_X", 0)
set_param("SIM_GPS1_GLTCH_Y", 0)
set_param("SIM_GPS1_GLTCH_Z", 0)

print("🚀 Starting anomaly sequence")

start = time.time()

try:

    while True:

        msg = master.recv_msg()

        if msg:

            elapsed = time.time() - start

            # ---- PHASES ----

            if 10 < elapsed < 30:
                set_param("SIM_GPS1_GLTCH_X", 56)     # PN glitch

            elif 30 < elapsed < 50:
                set_param("SIM_GPS1_GLTCH_X", 0)
                set_param("SIM_GPS1_GLTCH_Y", 56)     # PE glitch

            elif 50 < elapsed < 70:
                set_param("SIM_GPS1_GLTCH_Y", 0)
                set_param("SIM_GPS1_GLTCH_Z", 15)     # Z glitch

            elif 70 < elapsed < 90:
                set_param("SIM_GPS1_GLTCH_X", 56)
                set_param("SIM_GPS1_GLTCH_Y", 56)     # XY glitch

            elif 90 < elapsed < 120:
                # gradual profile
                t = elapsed - 90
                if t < 5:
                    g = 20
                elif t < 10:
                    g = 35
                elif t < 15:
                    g = 50
                elif t < 20:
                    g = 56
                elif t < 25:
                    g = 40
                elif t < 30:
                    g = 20
                elif t < 35:
                    g = 10
                else:
                    g = 0

                set_param("SIM_GPS1_GLTCH_X", g)

            elif elapsed > 130:
                print("\n🏁 Experiment complete")
                break


            # ---- EKF Monitoring ----

            if msg.get_type() == "EKF_STATUS_REPORT":
                v_var = msg.velocity_variance
                print(f"🏥 VelVar:{v_var:.4f}", end="\r")

            if msg.get_type() == "LOCAL_POSITION_NED":
                pn = msg.x
                pe = msg.y
                status = master.messages.get("EKF_STATUS_REPORT")
                v_var = getattr(status, "velocity_variance", 0.0)

                print(f"💎 PN:{pn:7.2f} PE:{pe:7.2f} VelVar:{v_var:.4f}")

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n🛑 Capture stopped")
