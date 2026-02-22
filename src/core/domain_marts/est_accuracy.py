import duckdb

def refresh_est_mart(db_path, mission_id=None):
    """
    Creates or refreshes EST mart (Estimator Residuals)
    """
    con = duckdb.connect(db_path)
    try:
        print("📢 Refreshing EST mart...")
        mission_filter = f"WHERE mission_id = '{mission_id}'" if mission_id else ""

        con.execute(f"""
            CREATE OR REPLACE TABLE mart_est_accuracy AS
            SELECT
                timestamp,
                mission_id,
                pos_variance,
                vel_variance,
                100 - ((pos_variance + vel_variance) * 50) AS est_score
            FROM fact_est
            {mission_filter}
        """)
        print(f"✅ EST mart created successfully ({'mission: ' + mission_id if mission_id else 'all missions'})")
    except Exception as e:
        print(f"❌ Error refreshing EST mart: {e}")
    finally:
        con.close()
