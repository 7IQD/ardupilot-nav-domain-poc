# src/utils/db_helpers.py
from .db_connector import get_connection

# ------------------------
# NAV DOMAIN
# ------------------------
def list_missions():
    """Return all mission IDs from the NAV Gold state table."""
    with get_connection() as con:
        missions = con.execute(
            "SELECT DISTINCT mission_id FROM fact_nav_state ORDER BY mission_id DESC"
        ).fetchall()
        return [m[0] for m in missions]

def get_nav_gold(mission_id):
    """Return reconstructed telemetry (Gold Layer) for a NAV mission."""
    with get_connection() as con:
        df = con.execute(
            "SELECT * FROM fact_nav_state WHERE mission_id = ? ORDER BY TimeUS ASC",
            [mission_id]
        ).df()
        return df

def get_nav_silver(mission_id):
    """Return raw events (Silver Layer) for a NAV mission."""
    with get_connection() as con:
        df = con.execute(
            "SELECT * FROM fact_nav_events WHERE mission_id = ? ORDER BY TimeUS ASC",
            [mission_id]
        ).df()
        return df

# ------------------------
# SYS DOMAIN
# ------------------------
def get_sys(mission_id):
    """Return SYS domain telemetry (Gold Layer) for a mission."""
    with get_connection() as con:
        df = con.execute(
            "SELECT * FROM fact_sys WHERE mission_id = ? ORDER BY TimeUS ASC",
            [mission_id]
        ).df()
        return df

# ------------------------
# EST DOMAIN
# ------------------------
def get_est(mission_id):
    """Return EST domain telemetry (Gold Layer) for a mission."""
    with get_connection() as con:
        df = con.execute(
            "SELECT * FROM fact_est WHERE mission_id = ? ORDER BY TimeUS ASC",
            [mission_id]
        ).df()
        return df

# ------------------------
# POWER DOMAIN
# ------------------------
def get_power(mission_id):
    """Return POWER domain telemetry (Gold Layer) for a mission."""
    with get_connection() as con:
        df = con.execute(
            "SELECT * FROM fact_power WHERE mission_id = ? ORDER BY TimeUS ASC",
            [mission_id]
        ).df()
        return df

# ------------------------
# COMM DOMAIN
# ------------------------
def get_comm(mission_id):
    """Return COMM domain telemetry (Gold Layer) for a mission."""
    with get_connection() as con:
        df = con.execute(
            "SELECT * FROM fact_communication WHERE mission_id = ? ORDER BY TimeUS ASC",
            [mission_id]
        ).df()
        return df