import duckdb

class NavDataService:
    """
    STEP 1: Availability
    """

    @staticmethod
    def check_availability(con):
        return con.execute("""
            SELECT msg_type, COUNT(*) as count
            FROM nav_master
            WHERE msg_type = 'GPS'
            GROUP BY msg_type;
        """).df()