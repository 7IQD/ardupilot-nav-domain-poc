from pymavlink import mavutil
import sys
import time

class Orchestrator:
    def __init__(self, nav_arch, sys_arch, com_arch, est_arch):
        # Architect instances for each domain
        self.architects = {
            'NAV': nav_arch,
            'SYS': sys_arch,
            'COM': com_arch,
            'EST': est_arch
        }

        # Domain-specific MAV message gates
        self.domain_gates = {
            'NAV': [24, 33, 74, 30, 230, 193],  # GPS, VFR, ATTITUDE, EKF, Vibration
            'SYS': [1, 147, 253],               # SYS_STATUS, BATTERY, etc.
            'COM': [65, 66, 67, 109, 110],      # RC, RADIO_STATUS
            'EST': [193, 230, 150, 151, 152]    # EKF_STATUS, VIBRATION, AHRS
        }

        # Universal Spine
        self.inode_counter = 0
        self.mission_id = "default_mission"

    def run(self):
        print("🚀 [ENGINE] Starting Ground Run...")

        # Connect to SITL
        connection = mavutil.mavlink_connection('udp:127.0.0.1:14551')
        print("📡 Waiting for Heartbeat...")
        heartbeat = connection.wait_heartbeat(timeout=5)
        if not heartbeat:
            print("⚠️ No Heartbeat detected. Exiting.")
            return
        print(f"✅ Heartbeat received from System {connection.target_system}")

        try:
            while True:
                msg = connection.recv_match(blocking=True, timeout=1.0)
                if not msg:
                    continue

                m_id = msg.get_msgId()
                self.inode_counter += 1
                s_sys = getattr(msg, 'sysid', 0)
                s_comp = getattr(msg, 'compid', 0)

                # Multi-cast routing to all matching domains
                for domain, gate in self.domain_gates.items():
                    if m_id in gate:
                        self.architects[domain].record(
                            msg=msg,
                            inode=self.inode_counter,
                            mission_id=self.mission_id,
                            src_sys=s_sys,
                            src_comp=s_comp
                        )
                        # No break: allow multi-domain hits

        except KeyboardInterrupt:
            print("\n🛑 User Interrupt. Flushing all domains...")
            for arch in self.architects.values():
                arch.stop()
            print("💾 Data saved to Vault B.")

        except Exception as e:
            print(f"❌ Runtime Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
