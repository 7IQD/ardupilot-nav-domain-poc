# src/dashboard/nav/nav_controller.py

import sys
import os

try:
    from .nav_data_service import NavDataService
    from .nav_stats import NavStatsEngine
    from .nav_action_map import NavActionMap
except ImportError:
    from nav_data_service import NavDataService
    from nav_stats import NavStatsEngine
    from nav_action_map import NavActionMap

class NavController:
    """
    ROLE: The Mission Orchestrator.
    CONCEPT: Fetches Gold telemetry, trims noise, and executes the safety audit.
    """
    def __init__(self, mission_id):
        self.mission_id = mission_id
        self.data_service = NavDataService()

    def _get_clean_df(self):
        """
        Fetches data from the Gold view and trims pre-flight ground chatter.
        Ensures the audit only reflects the active mission state.
        """
        df = self.data_service.get_state_report(self.mission_id)

        if df is not None and not df.empty:
            # 🧹 FLIGHT FILTER: Ignore the first 25 seconds of ground noise/initialization
            # This ensures the P95 Drift and HDOP stats are mission-accurate.
            df = df[df['mission_time'] > 25].copy()

        return df

    def run_audit(self):
        """
        Executes the full forensic suite.
        Returns a verdict, metrics, and actionable messages.
        """
        try:
            df = self._get_clean_df()

            if df is None or df.empty:
                return {
                    "evaluation": {
                        "verdict": "ERROR",
                        "message": "No flight data found after trimming ground noise."
                    }
                }

            # 1. Calculate forensic metrics (Drift, HDOP averages, etc.)
            stats = NavStatsEngine.calculate_metrics(df)

            # 2. Map metrics to safety verdicts (PASS/FAIL/WARNING)
            evaluation = NavActionMap.evaluate(stats)

            return {
                "mission_id": self.mission_id,
                "stats": stats,
                "evaluation": evaluation
            }

        except Exception as e:
            return {
                "evaluation": {
                    "verdict": "ERROR",
                    "message": f"Audit Pipeline Failed: {str(e)}"
                }
            }

    def get_audit_dataframe(self):
        """
        Public accessor for Notebook plotting.
        Returns the trimmed, clean Gold dataframe.
        """
        return self._get_clean_df()

if __name__ == "__main__":
    # Internal CLI sanity check
    ctrl = NavController('MISSION_1771663015')
    report = ctrl.run_audit()
    print(f"Final Verdict: {report['evaluation']['verdict']}")