import duckdb
import pandas as pd
from pathlib import Path

class NavDataService:
    def __init__(self):
        # 🏛️ PORTABILITY LOCK: Resolve path relative to this file
        # nav/ (0) -> dashboard/ (1) -> src/ (2) -> project_root/ (3)
        current_file = Path(__file__).resolve()
        project_root = current_file.parents[3]

        self.db_path = project_root / "bin" / "vault" / "warehouse_df" / "drone_df_views.db"

    def get_nav_swath(self, mission_id):
        """
        Fetches Navigation-domain telemetry.
        Pattern: Connection-per-query (Safe for DB overwriting).
        """
        if not self.db_path.exists():
            print(f"❌ IO Error: Database not found at {self.db_path}")
            return None

        # 🏛️ ARCHITECTURAL INTEGRITY: Open/Close for every query
        # read_only=True prevents locking during active dashboard sessions
        try:
            with duckdb.connect(str(self.db_path), read_only=True) as con:
                query = """
                    SELECT
                        mission_time,
                        RelHomeAlt,
                        RelOriginAlt,
                        Lat,
                        Lng,
                        Status as GPS_Status,
                        NSats,
                        HDop,
                        VZ
                    FROM ui_nav_drone_monitor
                    WHERE mission_id = ?
                    ORDER BY mission_time ASC
                """
                # Parameterized execution to prevent SQL injection
                df = con.execute(query, [mission_id]).df()
                return df
        except Exception as e:
            print(f"❌ Database Query Error: {e}")
            return None