import os
import pandas as pd
from .nav_data_service import NavDataService
from .nav_stats import NavStatsEngine
from .nav_action_map import NavActionMap

"""
NavController
Purpose:
- Orchestrate the NAV domain workflow
- Filter SITL/GPS startup noise (First 10 seconds)
- Execute the metrics -> evaluation pipeline
- Return structured audit results for the UI/CLI
"""

class NavController:

    def __init__(self, mission_id=None):
        self.mission_id = mission_id
        # Initialize the Data Service (DAO)
        self.data_service = NavDataService(mission_id)

    def run_audit(self):
        """
        Executes the full NAV audit pipeline.
        Returns: Dictionary containing mission stats and the final evaluation verdict.
        """

        # 1. Load NAV dataframe via the Data Service
        # This handles the DuckDB connection and TimeUS sorting
        df = self.data_service.get_state_report(self.mission_id)

        if df is None or df.empty:
            return {
                "mission_id": self.mission_id,
                "evaluation": {
                    "verdict": "ERROR",
                    "message": "No NAV flight data found in warehouse"
                }
            }

        # 2. Remove SITL / GPS startup noise
        # We ignore the first 10 seconds to allow the EKF to settle
        # and GPS to achieve a valid 3D fix.
        if "mission_time" in df.columns:
            df = df[df["mission_time"] > 10].copy()

        if df.empty:
            return {
                "mission_id": self.mission_id,
                "evaluation": {
                    "verdict": "ERROR",
                    "message": "Insufficient data after filtering SITL startup noise"
                }
            }

        # 3. Compute NAV statistics (Drift, Stability, and Score)
        # Calls the static methods in NavStatsEngine
        stats = NavStatsEngine.calculate_metrics(df)

        # 4. Run rule evaluation via the Action Map
        # Maps the stats to human-readable verdicts (GREEN/YELLOW/RED)
        evaluation = NavActionMap.evaluate(stats)

        # 5. Return full audit result
        return {
            "mission_id": self.mission_id,
            "sample_count": stats.get("sample_count", 0),
            "stats": stats,
            "evaluation": evaluation
        }

if __name__ == "__main__":
    # Quick Integration Test
    # Set a dummy mission_id or leave None to pull the master parquet
    controller = NavController(mission_id=None)
    result = controller.run_audit()

    print(f"NAV Audit Result for Mission: {result['mission_id']}")
    print(f"Verdict: {result['evaluation']['verdict']}")
    print(f"Total Score: {result['stats'].get('total_score')}")