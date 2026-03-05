import pandas as pd
from .db_connector import get_connection

def get_fused_flight_diagnostics(mission_id):
    """Fetches the Platinum-tier fused view for a specific mission."""
    with get_connection() as con:
        query = """
            SELECT * FROM fact_flight_diagnostics
            WHERE mission_id = ? AND Lat != 0
            ORDER BY TimeUS ASC
        """
        return con.execute(query, [mission_id]).df()

def list_missions():
    """Returns all unique mission IDs."""
    with get_connection() as con:
        res = con.execute("SELECT DISTINCT mission_id FROM fact_nav_state_vector").fetchall()
        return [r[0] for r in res]