from .nav_data_service import NavDataService
from .nav_stats import NavStatsEngine
from .nav_action_map import NavActionMap

class NavController:
    def __init__(self, mission_id):
        self.mission_id = mission_id
        self.data_service = NavDataService(mission_id)

    def run_audit(self):
        df = self.data_service.get_state_report(self.mission_id)
        if df.empty:
            return {"evaluation": {"verdict": "ERROR", "message": "No flight data."}}

        # Truncate startup noise (first 10 seconds of fix)
        df = df[df['mission_time'] > 10].copy()

        stats = NavStatsEngine.calculate_metrics(df)
        evaluation = NavActionMap.evaluate(stats)

        return {
            "mission_id": self.mission_id,
            "stats": stats,
            "evaluation": evaluation
        }