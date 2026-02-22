#!/usr/bin/env python3
from fastapi import APIRouter, HTTPException
import duckdb
import os

router = APIRouter()

# --- PATH RESOLUTION ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
VAULT_DB = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df/drone_df_views.db")

def get_connection():
    if not os.path.exists(VAULT_DB):
        raise FileNotFoundError(f"Vault DB not found at {VAULT_DB}")
    return duckdb.connect(VAULT_DB, read_only=True)

@router.get("/scorecard/{mission_id}")
async def mission_scorecard(mission_id: str):
    """
    Return high-level scorecard metrics for a mission.
    Queries the 'fact_nav' table for aggregated stats.
    """
    con = get_connection()
    try:
        # 1. We use fact_nav instead of the raw .parquet file for speed
        # 2. We use '?' parameterization to handle the MISSION_ID string safely
        query = """
            SELECT
                COUNT(*) as total_records,
                MAX(alt) as max_altitude,
                MIN(alt) as min_altitude,
                AVG(alt) as avg_altitude
            FROM fact_nav
            WHERE mission_id = ?
        """

        row = con.execute(query, [mission_id]).fetchone()

        if not row or row[0] == 0:
            raise HTTPException(status_code=404, detail=f"No data found for mission: {mission_id}")

        return {
            "mission_id": mission_id,
            "summary": {
                "record_count": row[0],
                "max_alt_m": round(row[1], 2) if row[1] else 0,
                "min_alt_m": round(row[2], 2) if row[2] else 0,
                "avg_alt_m": round(row[3], 2) if row[3] else 0
            }
        }
    except Exception as e:
        print(f"❌ Analytics Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        con.close()