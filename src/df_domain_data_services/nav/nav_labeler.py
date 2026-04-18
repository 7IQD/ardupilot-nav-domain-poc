class NavLabeler:
    """
    STEP 5 & 6: State + Windowing
    """

    @staticmethod
    def get_mismatches(con):
        return con.execute("""
            SELECT
                TimeUS,
                inode,
                CAST(NSats AS INTEGER) AS NSats,
                CAST(Status AS INTEGER) AS Status,
                CASE WHEN NSats = 0 THEN 'LOSS'
                     WHEN NSats < 8 THEN 'DEGRADED'
                     ELSE 'HEALTHY' END AS sensor_state,
                CASE WHEN Status <= 1 THEN 'LOSS'
                     WHEN Status >= 3 THEN 'HEALTHY'
                     ELSE 'DEGRADED' END AS fc_state,
                CASE WHEN (NSats = 0 AND Status >= 3)
                       OR (NSats >= 8 AND Status <= 1)
                     THEN 'MISMATCH'
                     ELSE 'ALIGNED' END AS integrity_flag
            FROM nav_master
            WHERE msg_type = 'GPS'
            ORDER BY TimeUS;
        """).df()

    @staticmethod
    def get_windows(con):
        return con.execute("""
            WITH base AS (
                SELECT TimeUS, inode,
                       CAST(NSats AS INTEGER) AS nsats,
                       CAST(Status AS INTEGER) AS status
                FROM nav_master WHERE msg_type = 'GPS'
            ),
            state_map AS (
                SELECT *,
                    CASE WHEN nsats = 0 THEN 'LOSS'
                         WHEN nsats < 8 THEN 'DEGRADED'
                         ELSE 'HEALTHY' END AS sensor_state,
                    CASE WHEN status <= 1 THEN 'LOSS'
                         WHEN status >= 3 THEN 'HEALTHY'
                         ELSE 'DEGRADED' END AS fc_state
                FROM base
            ),
            flags AS (
                SELECT *,
                    CASE WHEN sensor_state != fc_state
                         THEN 'MISMATCH'
                         ELSE 'ALIGNED' END AS integrity_flag
                FROM state_map
            ),
            grouped AS (
                SELECT *,
                    ROW_NUMBER() OVER (ORDER BY TimeUS) -
                    ROW_NUMBER() OVER (
                        PARTITION BY sensor_state, fc_state, integrity_flag
                        ORDER BY TimeUS
                    ) AS grp
                FROM flags
            )
            SELECT
                MIN(TimeUS) AS start_time,
                MAX(TimeUS) AS end_time,
                MIN(inode) AS start_inode,
                MAX(inode) AS end_inode,
                ROUND((MAX(TimeUS)-MIN(TimeUS))/1000000.0,2) AS duration_sec,
                sensor_state,
                fc_state,
                integrity_flag,
                COUNT(*) AS row_count
            FROM grouped
            GROUP BY grp, sensor_state, fc_state, integrity_flag
            HAVING duration_sec > 0.1
            ORDER BY start_time;
        """).df()