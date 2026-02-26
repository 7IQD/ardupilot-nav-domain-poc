import duckdb
import pandas as pd
from pathlib import Path

class NavDataService:
    def __init__(self):
        # 🏛️ PORTABILITY LOCK: Resolve path relative to this file
        current_file = Path(__file__).resolve()
        project_root = current_file.parents[3]

        self.db_path = project_root / "bin" / "vault" / "warehouse_df" / "drone_df_views.db"

    def _execute_safe_query(self, query, params=None):
        """Open/Close read-only execution pattern."""
        if not self.db_path.exists():
            print(f"❌ IO Error: Database not found at {self.db_path}")
            return None
        try:
            # Using read_only=True prevents locking conflicts with the CLI
            with duckdb.connect(str(self.db_path), read_only=True) as con:
                if params:
                    return con.execute(query, params).df()
                return con.execute(query).df()
        except Exception as e:
            print(f"❌ Database Query Error: {e}")
            return None

    # -----------------------------
    # Gold Layer (High-Density / Smoothed)
    # -----------------------------
    def get_state_report(self, mission_id):
        """
        REPORT 1: The 'Truth' (Gold Layer)
        Uses the Aliases "RelHomeAlt" and "RelOriginAlt" defined in create_views.py.
        """
        query = """
            SELECT
                mission_time,
                "RelHomeAlt",
                "RelOriginAlt",
                Lat, Lng, GPS_Status, NSats, HDop, VZ, inode
            FROM ui_nav_drone_monitor
            WHERE mission_id = ?
            ORDER BY mission_time ASC
        """
        return self._execute_safe_query(query, [mission_id])

    # -----------------------------
    # Silver Layer (Forensic / Raw Audit)
    # -----------------------------
    def get_event_audit(self, mission_id):
        """
        REPORT 2: The 'Audit' (Silver Layer)
        Uses raw telemetry from fact_nav (the base table).
        """
        query = """
            SELECT
                mission_time, RelHomeAlt, RelOriginAlt, inode
            FROM fact_nav
            WHERE mission_id = ?
            ORDER BY mission_time ASC
        """
        return self._execute_safe_query(query, [mission_id])

    # -----------------------------
    # Legacy / Full Telemetry Swath
    # -----------------------------
    def get_nav_swath(self, mission_id):
        """
        Fetches Navigation-domain telemetry.
        """
        query = """
            SELECT
                mission_time,
                "RelHomeAlt",
                "RelOriginAlt",
                Lat,
                Lng,
                GPS_Status,
                NSats,
                HDop,
                VZ
            FROM ui_nav_drone_monitor
            WHERE mission_id = ?
            ORDER BY mission_time ASC
        """
        return self._execute_safe_query(query, [mission_id])