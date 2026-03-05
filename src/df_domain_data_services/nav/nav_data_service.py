# src/df_domain_data_services/nav/nav_data_service.py

import duckdb
import pandas as pd
import os
from src.utils.db_connector import get_connection

class NavDataService:
    def __init__(self, mission_id=None):
        self.mission_id = mission_id

    def fetch_fused_telemetry(self) -> pd.DataFrame:
        """The core engine fetcher."""
        with get_connection() as con:
            # Pull from our Platinum View
            query = "SELECT * FROM fact_flight_diagnostics"
            if self.mission_id:
                query += f" WHERE mission_id = '{self.mission_id}'"

            df = con.execute(query).df()

        if df.empty: return df

        # Basic cleanup
        df = df.sort_values("TimeUS").drop_duplicates("TimeUS")
        return df

    def get_state_report(self, mission_id=None):
        """
        Standardized Alias for NavController.
        Calculates mission_time (seconds) for easier plotting/filtering.
        """
        if mission_id:
            self.mission_id = mission_id

        df = self.fetch_fused_telemetry()

        if not df.empty:
            # Inject mission_time (seconds from start of mission)
            start_ts = df['TimeUS'].min()
            df['mission_time'] = (df['TimeUS'] - start_ts) / 1e6

        return df