import sys
import os
import time
import logging

# ==========================================================
# BOOTSTRAP PATHING
# ==========================================================
current_file_dir = os.path.dirname(os.path.abspath(__file__))
src_root = os.path.abspath(os.path.join(current_file_dir, '..'))
if src_root not in sys.path:
    sys.path.insert(0, src_root)

try:
    from data_mart_engine.refinery.nav_refinery import NavRefinery
    from data_mart_engine.database_manager import DatabaseManager
except ImportError as e:
    print(f"CRITICAL: Refinery components missing: {e}")
    sys.exit(1)

# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [Engine-2] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class MissionOrchestrator:
    """
    ROLE: The Brain.
    CONCEPT: Managing the transition from Silver (Raw) to Gold (Insight).
    CONTRACT: Runs refinery cycles on a fixed heartbeat.
    """
    def __init__(self, mission_id="MARATHON_POC"):
        self.mission_id = mission_id
        self.clerk = DatabaseManager()
        self.refinery = NavRefinery(mission_id=self.mission_id)

        # Ensure Gold folders exist
        self.clerk.ensure_vault_structure()

    def start_marathon(self, cycle_sec=5):
        """Infinite loop to process new packets."""
        logging.info(f"🚀 Mission Orchestrator active: {self.mission_id}")
        logging.info(f"Refining Silver -> Gold every {cycle_sec}s...")

        try:
            while True:
                # 1. Run the Refinery Cycle
                self.refinery.refine_ekf_precision()

                # 2. Wait for next batch of packets from Engine-1
                time.sleep(cycle_sec)
        except KeyboardInterrupt:
            logging.info("🛑 Orchestrator shutting down gracefully.")
            sys.exit(0)

if __name__ == "__main__":
    # You can pass a custom name for your marathon here
    MISSION_NAME = sys.argv[1] if len(sys.argv) > 1 else "MARATHON_TEST_01"
    orchestrator = MissionOrchestrator(mission_id=MISSION_NAME)
    orchestrator.start_marathon(cycle_sec=5)