import time
import sys
from pymavlink import mavutil

class Orchestrator:
    def __init__(self, nav_arch, sys_arch):
        self.nav_arch = nav_arch
        self.sys_arch = sys_arch

        # MAVLink Connection (Ground Run Default)
        self.connection = mavutil.mavlink_connection('udp:127.0.0.1:14551')

        # --- THE UNIVERSAL SPINE ---
        self.inode_counter = 0
        self.mission_id = int(time.time())

        # GATES:
        # NAV: GPS, GLOBAL_POS, VFR_HUD, ATTITUDE, AHRS2
        self.NAV_GATE = [24, 33, 74, 30, 163]
        # SYS: SYS_STATUS, BATTERY_STATUS, STATUSTEXT
        self.SYS_GATE = [1, 147, 253]

    def run(self):
        print(f"🛰️  Mission ID: {self.mission_id}")
        print("🚀 [ENGINE] Waiting for MAVLink Heartbeat...")
        self.connection.wait_heartbeat()
        print("💓 Heartbeat Detected. Capturing...")

        try:
            while True:
                msg = self.connection.recv_match(blocking=True)
                if not msg: continue

                # 1. Increment Universal Inode (Primary Key)
                self.inode_counter += 1

                # 2. Extract Source Identity
                m_id = msg.get_msgId()
                src_sys = msg.get_srcSystem()
                src_comp = msg.get_srcComponent()

                # 3. Route to Architects
                if m_id in self.NAV_GATE:
                    self.nav_arch.record(msg, self.inode_counter, self.mission_id, src_sys, src_comp)

                elif m_id in self.SYS_GATE:
                    self.sys_arch.record(msg, self.inode_counter, self.mission_id, src_sys, src_comp)

                # 4. Universal HUD
                if self.inode_counter % 20 == 0:
                    sys.stdout.write(
                        f"\r📦 [INODE: {self.inode_counter}] "
                        f"| SRC: {src_sys} "
                        f"| TYPE: {msg.get_type()[:10]} "
                        f"| M: {self.mission_id}"
                    )
                    sys.stdout.flush()

        except KeyboardInterrupt:
            print(f"\n🛑 [STOP] Finalizing Universal Spine...")
            self.nav_arch.stop()
            self.sys_arch.stop()
            raise