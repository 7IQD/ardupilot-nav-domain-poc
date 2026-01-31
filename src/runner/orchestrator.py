from pymavlink import mavutil
import sys

class Orchestrator:
    def __init__(self, nav_arch, sys_arch):
        self.nav_architect = nav_arch
        self.sys_architect = sys_arch

        # ACTION MAP GATES (Expanded for EKF visibility)
        # 230: EKF_STATUS_REPORT
        # 193: EKF_ESTIMATOR_STATUS
        self.NAV_GATE = [24, 33, 74, 30, 230, 193]
        self.SYS_GATE = [1, 147, 253]

    def run(self):
        print("🚀 [ENGINE] Starting Ground Run...")

        # Connection to SITL/Hardware
        connection = mavutil.mavlink_connection('udp:127.0.0.1:14551')

        try:
            print("📡 [ENGINE] Waiting for Heartbeat on port 14551...")
            # Added a 5-second timeout to prevent the permanent lock you saw earlier
            heartbeat = connection.wait_heartbeat(timeout=5)

            if not heartbeat:
                print("⚠️  [ENGINE] No Heartbeat detected. Check SITL/Connection.")
                return

            print(f"✅ [ENGINE] Heartbeat received from System {connection.target_system}")

            while True:
                msg = connection.recv_match(blocking=True, timeout=1.0)

                if not msg:
                    continue

                m_id = msg.get_msgId()

                # Routing Logic
                if m_id in self.NAV_GATE:
                    self.nav_architect.ingest(msg)
                elif m_id in self.SYS_GATE:
                    self.sys_architect.ingest(msg)

        except KeyboardInterrupt:
            print("\n🛑 [ENGINE] Stopping...")
            # Critical: This flushes the memory buffer to bin/vault/warehouse/
            self.nav_architect.stop()
            self.sys_architect.stop()
            print("💾 [ENGINE] Data saved to Warehouse. Ready for Refinery.")
        except Exception as e:
            print(f"❌ [ENGINE] Runtime Error: {e}")
            sys.exit(1)