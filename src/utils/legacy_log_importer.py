import os
from pymavlink import mavutil
from src.ingress.data_manager import Clerk
from src.ingress.architects.nav_architect import NavArchitect
from src.ingress.architects.sys_architect import SysArchitect

class IngressEngine:
    def __init__(self, source_log="mav.tlog"):
        self.source_log = source_log
        self.clerk = Clerk()

        # Initialize architects with a high batch limit for one-shot processing
        self.nav_arch = NavArchitect(limit=5000)
        self.sys_arch = SysArchitect(limit=5000)

    def run(self):
        """Processes the log file and flushes data to the warehouse."""
        if not os.path.exists(self.source_log):
            print(f"❌ Source log '{self.source_log}' not found.")
            return

        print(f"📂 Opening log source: {self.source_log}")
        # mavutil.mavlink_connection handles both .tlog and .bin files
        connection = mavutil.mavlink_connection(self.source_log)

        count = 0
        try:
            while True:
                msg = connection.recv_match(blocking=False)
                if msg is None:
                    break

                # Route messages to the appropriate architect
                msg_type = msg.get_type()

                if msg_type in ['GLOBAL_POSITION_INT', 'EKF_STATUS_REPORT']:
                    self.nav_arch.ingest(msg)
                elif msg_type in ['SYS_STATUS', 'BATTERY_STATUS']:
                    self.sys_arch.ingest(msg)

                count += 1
                if count % 1000 == 0:
                    print(f"📈 Processed {count} messages...")

        except Exception as e:
            print(f"⚠️ Error during ingestion: {e}")
        finally:
            # Crucial: Flush buffers to Parquet files in the warehouse
            print("💾 Finalizing warehouse synchronization...")
            self.nav_arch.flush()
            self.sys_arch.flush()
            self.clerk.finalize_run()
            print(f"✅ Ingress complete. Total messages parsed: {count}")

if __name__ == "__main__":
    # Point this to your actual log file
    engine = IngressEngine(source_log="mav.tlog")
    engine.run()