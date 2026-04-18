class NavDataIntegrityCheck:
    """
    STEP 2: Integrity
    """

    @staticmethod
    def check_fields(con):
        return con.execute("""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(NSats) AS nsats_present,
                COUNT(Status) AS status_present
            FROM nav_master
            WHERE msg_type = 'GPS';
        """).df()