import duckdb

def refresh_com_mart(db_path, mission_id=None):
    """
    Creates or refreshes COM mart (Communication / Link Quality)
    Mission-aware: filters by mission_id if provided.
    """
    con = duckdb.connect(db_path)
    try:
        print("📢 Refreshing COM mart...")
        mission_filter = f"WHERE mission_id = '{mission_id}'" if mission_id else ""

        con.execute(f"""
            CREATE OR REPLACE TABLE mart_com_quality AS
            SELECT
                timestamp,
                mission_id,
                rssi,
                signal_noise,
                -- Link score: 100 is perfect, lower if signal weak
                100 - (ABS(rssi + 120) * 2) AS link_score
            FROM fact_communication
            {mission_filter}
        """)
        print(f"✅ COM mart created successfully ({'mission: ' + mission_id if mission_id else 'all missions'})")
    except Exception as e:
        print(f"❌ Error refreshing COM mart: {e}")
    finally:
        con.close()
