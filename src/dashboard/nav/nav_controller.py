import sys
import os

# Internal relative imports for the nav package
try:
    from .nav_data_service import NavDataService
    from .nav_stats import NavStatsEngine
    from .nav_action_map import NavActionMap
except ImportError:
    # Fallback for direct script execution/testing
    from nav_data_service import NavDataService
    from nav_stats import NavStatsEngine
    from nav_action_map import NavActionMap

class NavController:
    """
    ROLE: The Orchestrator for the Navigation Domain.
    CONCEPT: Coordinates the flow from Raw Data -> Math -> Verdict.
    """
    def __init__(self, mission_id):
        self.mission_id = mission_id
        self.data_service = NavDataService()

    def run_audit(self):
        """
        Executes the full forensic pipeline for a single mission.
        """
        try:
            # 1. DATA ACQUISITION
            # Fetches JSON from API and converts to DataFrame
            df = self.data_service.get_nav_swath(self.mission_id)

            if df is None or df.empty:
                return {
                    "mission_id": self.mission_id,
                    "stats": {"p95_drift": 0, "sample_count": 0},
                    "evaluation": {"verdict": "DATA_MISSING", "score": 0, "status": "INCOMPLETE"}
                }

            # 2. STATISTICAL INTELLIGENCE
            # Calculates P95, Sigma, and Sample Counts
            stats = NavStatsEngine.calculate_metrics(df)

            # 3. ACTION MAPPING (The Judge)
            # Compares stats against ArduPilot safety thresholds
            evaluation = NavActionMap.evaluate(stats)

            return {
                "mission_id": self.mission_id,
                "stats": stats,
                "evaluation": evaluation
            }

        except Exception as e:
            print(f"CRITICAL: Controller Audit Failed: {e}")
            return {
                "mission_id": self.mission_id,
                "error": str(e),
                "evaluation": {"verdict": "ERROR", "score": 0, "status": "CRITICAL"}
            }

if __name__ == "__main__":
    # Quick CLI test
    test_mission = "M_101"
    ctrl = NavController(test_mission)
    print(f"Testing Controller for {test_mission}...")
    print(ctrl.run_audit())