class NavStatsEngine:
    """
    STEP 3 & 4: Distributions
    """

    @staticmethod
    def get_distributions(con):
        df_status = con.execute("""
            SELECT Status, COUNT(*) AS count
            FROM nav_master
            WHERE msg_type = 'GPS'
            GROUP BY Status ORDER BY Status;
        """).df()

        df_nsats = con.execute("""
            SELECT NSats, COUNT(*) AS count
            FROM nav_master
            WHERE msg_type = 'GPS'
            GROUP BY NSats ORDER BY NSats;
        """).df()

        return df_status, df_nsats