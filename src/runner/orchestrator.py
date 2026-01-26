from pymavlink import mavutil

class Orchestrator:
    def __init__(self, nav_arch, sys_arch):
        self.nav_architect = nav_arch
        self.sys_architect = sys_arch

        # ACTION MAP GATES (Hardcoded for KISS Ground Run)
        self.NAV_GATE = [24, 33, 74, 30]
        self.SYS_GATE = [1, 147, 253]

    def run(self):
        print("🚀 [ENGINE] Starting Ground Run...")
        connection = mavutil.mavlink_connection('udp:127.0.0.1:14551')
        connection.wait_heartbeat()

        try:
            while True:
                msg = connection.recv_match(blocking=True)
                if not msg: continue

                m_id = msg.get_msgId()

                if m_id in self.NAV_GATE:
                    self.nav_architect.ingest(msg)
                elif m_id in self.SYS_GATE:
                    self.sys_architect.ingest(msg)
        except KeyboardInterrupt:
            print("\n🛑 [ENGINE] Stopping...")
            self.nav_architect.stop()
            self.sys_architect.stop()