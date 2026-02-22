import duckdb

def refresh_sys_mart(db_path, mission_id=None):
    """
    Creates or refreshes SYS mart (Vibe/Stress)
    Mission-aware: filters by mission_id if provided.
    """
    con = duckdb.connect(db_path)
    try:
        print("📢 Refreshing SYS mart...")
        mission_filter = f"WHERE mission_id = '{mission_id}'" if mission_id else ""

        con.execute(f"""
            CREATE OR REPLACE TABLE mart_sys_reliability AS
            SELECT
                timestamp,
                mission_id,
                vib_x,
                vib_y,
                vib_z,
                100 - ((ABS(vib_x) + ABS(vib_y) + ABS(vib_z))/3.0 * 10) AS stress_score
            FROM fact_sys
            {mission_filter}
        """)
        print(f"✅ SYS mart created successfully ({'mission: ' + mission_id if mission_id else 'all missions'})")
    except Exception as e:
        print(f"❌ Error refreshing SYS mart: {e}")
    finally:
        con.close()
