from src.data_mart_engine.database_manager import DatabaseManager
import pandas as pd

def run_mission_analysis():
    db = DatabaseManager()

    # 1. Dynamically identify the mission being analyzed
    id_query = "SELECT DISTINCT mission_id FROM fact_nav_precision LIMIT 1"
    id_df = db.query_gold(id_query)

    if id_df is None or id_df.empty:
        print("📊 No missions found in Gold Vault.")
        return

    target_mission = id_df.iloc[0]['mission_id']

    # 2. Comprehensive Query: Capture Status, ID, and Stats
    query = f"""
    SELECT
        COUNT(*) as nav_points,
        -- Status is 'HEALTHY' only if EVERY frame is healthy (min=1)
        CASE WHEN MIN(ekf_healthy) = 1 THEN '✅ HEALTHY' ELSE '⚠️ ISSUES DETECTED' END as nav_status,
        AVG(vel_variance) as avg_var,
        MIN(timestamp) as start_t,
        MAX(timestamp) as end_t,
        (SELECT MAX(voltage) FROM fact_sys_status WHERE mission_id = '{target_mission}' AND voltage > 0) as volt_start,
        (SELECT MIN(voltage) FROM fact_sys_status WHERE mission_id = '{target_mission}' AND voltage > 0) as volt_end
    FROM fact_nav_precision
    WHERE mission_id = '{target_mission}'
    """

    try:
        res = db.query_gold(query).iloc[0]

        # Timing calculation
        start = pd.to_datetime(res['start_t'])
        end = pd.to_datetime(res['end_t'])
        duration = (end - start).total_seconds()

        print("\n" + "═"*50)
        print(f" 🏁 MISSION REPORT: {target_mission} ")
        print("═"*50)
        print(f" 🕒 Duration:       {duration:.2f} seconds")
        print(f" 📡 Nav Status:     {res['nav_status']}")
        print(f" 📈 Avg Variance:   {res['avg_var']:.6f}")
        print("-" * 50)

        v_start = res['volt_start'] or 0.0
        v_end = res['volt_end'] or 0.0
        print(f" 🔋 Battery Start:  {v_start:.2f} V")
        print(f" 🪫 Battery End:    {v_end:.2f} V")
        print(f" 📉 Voltage Drop:   {v_start - v_end:.2f} V")
        print("═"*50 + "\n")

    except Exception as e:
        print(f"❌ Analysis Error: {e}")

if __name__ == "__main__":
    run_mission_analysis()