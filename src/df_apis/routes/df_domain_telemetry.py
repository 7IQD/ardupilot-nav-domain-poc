#!/usr/bin/env python3
from fastapi import APIRouter, HTTPException
import duckdb
import os

router = APIRouter()

# --- PATH RESOLUTION ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
VAULT_DB = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df/drone_df_views.db")

# Mapping of simple domain names to the actual Fact Tables created by create_views.py
TABLE_MAP = {
    "nav": "fact_nav",
    "est": "fact_est",
    "sys": "fact_sys",
    "power": "fact_power",
    "com": "fact_communication"
}

def get_connection():
    if not os.path.exists(VAULT_DB):
        raise FileNotFoundError(f"Vault DB not found at {VAULT_DB}")
    return duckdb.connect(VAULT_DB, read_only=True)

# --- NEW: MISSION DATA FETCH (The missing link) ---
@router.get("/{domain}/{mission_id}")
async def get_mission_data(domain: str, mission_id: str, limit: int = 5000):
    """Returns all telemetry records for a specific mission and domain."""
    if domain not in TABLE_MAP:
        raise HTTPException(status_code=404, detail=f"Domain {domain} not recognized")

    table = TABLE_MAP[domain]
    con = get_connection()
    try:
        query = f"SELECT * FROM {table} WHERE mission_id = ? ORDER BY wall_ns ASC LIMIT ?"
        df = con.execute(query, [mission_id, limit]).df()

        if df.empty:
            return {"status": "empty", "message": f"No data found for mission {mission_id}"}

        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        con.close()

# --- EXISTING: LATEST FETCHER ---
def fetch_latest(table_name: str):
    con = get_connection()
    try:
        query = f"SELECT * FROM {table_name} ORDER BY wall_ns DESC LIMIT 1"
        row = con.execute(query).fetchone()
        if not row: return {}
        columns = [c[0] for c in con.description]
        return dict(zip(columns, row))
    except Exception as e:
        return {"error": str(e)}
    finally:
        con.close()

@router.get("/nav/latest")
async def latest_nav():
    data = fetch_latest(TABLE_MAP["nav"])
    if "error" in data: raise HTTPException(status_code=500, detail=data["error"])
    return data

@router.get("/power/latest")
async def latest_power():
    data = fetch_latest(TABLE_MAP["power"])
    if "error" in data: raise HTTPException(status_code=500, detail=data["error"])
    return data

@router.get("/sys/latest")
async def latest_sys():
    data = fetch_latest(TABLE_MAP["sys"])
    if "error" in data: raise HTTPException(status_code=500, detail=data["error"])
    return data

@router.get("/com/latest")
async def latest_com():
    data = fetch_latest(TABLE_MAP["com"])
    if "error" in data: raise HTTPException(status_code=500, detail=data["error"])
    return data