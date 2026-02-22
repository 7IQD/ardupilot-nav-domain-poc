import duckdb

def refresh_nav_mart(db_path, mission_id=None):
    """
    Creates or refreshes NAV reliability mart.
    Mission-aware: filters by mission_id if provided.
    """
    con = duckdb.connect(db_path)
    try:
        print("📢 Refreshing NAV mart...")
        mission_filter = f"WHERE mission_id = '{mission_id}'" if mission_id else ""

        con.execute(f"""
            CREATE OR REPLACE TABLE mart_nav_reliability AS
            SELECT
                n.timestamp,
                n.mission_id,
                n.num_sats,
                n.hdop,
                e.vel_variance,
                e.pos_variance,
                (CASE
                    WHEN n.num_sats > 12 AND n.hdop < 1.5 THEN 100
                    WHEN n.num_sats > 8 THEN 70
                    ELSE 40
                 END) * 0.4 +
                 (1.0 - (e.vel_variance / 1.0)) * 60 AS reliability_score
            FROM fact_nav n
            LEFT JOIN fact_est e ON n.timestamp = e.timestamp
            {mission_filter}
        """)
        print(f"✅ NAV mart created successfully ({'mission: ' + mission_id if mission_id else 'all missions'})")
    except Exception as e:
        print(f"❌ Error refreshing NAV mart: {e}")
    finally:
        con.close()
