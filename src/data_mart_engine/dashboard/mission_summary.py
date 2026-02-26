import pandas as pd
from data_mart_engine.database_manager import DatabaseManager

class MissionSummary:
    def __init__(self):
        self.db = DatabaseManager()
        # Full domain set now that refineries are synced
        self.required_tables = ["fact_nav_precision", "fact_system_health", "fact_estimator"]

    def run_analysis(self):
        print(f"📊 [Dashboard] Generating Mission Health Summary...")

        # 1. Verification
        existing_tables = self.db.query_gold("SHOW TABLES")['name'].str.lower().tolist()
        for table in self.required_tables:
            if table.lower() not in existing_tables:
                print(f"⚠️  Missing table: {table}. Run refineries first.")
                return

        # 2. ASOF JOIN (Raw Data)
        query = """
            SELECT
                n.timestamp,
                n.mission_id,
                n.ekf_healthy,
                s.load as raw_load,
                s.battery_volt as raw_batt,
                e.xacc, e.yacc, e.zacc
            FROM fact_nav_precision n
            ASOF LEFT JOIN fact_system_health s
                ON n.timestamp >= s.timestamp AND n.mission_id = s.mission_id
            ASOF LEFT JOIN fact_estimator e
                ON n.timestamp >= e.timestamp AND n.mission_id = e.mission_id
            ORDER BY n.timestamp ASC
        """

        report_df = self.db.query_gold(query)

        if report_df.empty:
            print("⚠️  No data returned.")
            return

        # 3. Downstream Scaling (Presentation Logic)
        total_frames = len(report_df)

        # Scale Battery: mV -> V
        last_batt_raw = report_df['raw_batt'].dropna().iloc[-1] if not report_df['raw_batt'].dropna().empty else 0
        display_batt = last_batt_raw / 1000.0

        # Scale CPU: 0-1000 -> 0-100%
        avg_load_raw = report_df['raw_load'].mean()
        display_load = (avg_load_raw / 10.0) if not pd.isna(avg_load_raw) else 0.0

        ekf_issues = report_df[report_df['ekf_healthy'] == 0].shape[0]

        print("\n" + "="*45)
        print(f"🚀 MISSION SUMMARY: {report_df['mission_id'].iloc[0]}")
        print("-" * 45)
        print(f"📈 Total Nav Frames:   {total_frames}")
        print(f"💻 Avg CPU Load:       {display_load:.2f}%")
        print(f"🛡️  EKF Anomalies:      {ekf_issues}")
        print(f"🔋 Final Battery:      {display_batt:.2f}V")

        # Quick check for Vibration (Estimator Domain)
        if 'zacc' in report_df.columns:
            avg_vibe = report_df['zacc'].abs().mean()
            print(f"🫨  Avg Z-Vibration:    {avg_vibe:.2f} m/s²")

        print("="*45 + "\n")

if __name__ == "__main__":
    dashboard = MissionSummary()
    dashboard.run_analysis()