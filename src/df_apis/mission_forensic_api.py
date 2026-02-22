#!/usr/bin/env python3
from fastapi import FastAPI, APIRouter, HTTPException
import duckdb
import os

# --- ROUTER ---
router = APIRouter()

# --- VAULT LOCATION ---
# Resolves to project_root/bin/vault/warehouse_df/drone_df_views.db
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
VAULT_DB = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df/drone_df_views.db")

# --- DUCKDB CONNECTION ---
def get_connection():
    if not os.path.exists(VAULT_DB):
        raise FileNotFoundError(f"❌ Vault DB not found: {VAULT_DB}")
    try:
        # read_only=True is safer for API access
        con = duckdb.connect(VAULT_DB, read_only=True)
        return con
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        raise

# --- API ROUTES ---

@router.get("/")
async def root():
    return {"status": "DF API running", "message": "Drone Forensic Path operational"}

@router.get("/missions")
async def list_missions():
    """List all unique missions in the NAV fact table"""
    con = get_connection()
    try:
        # Correct: Query the physical Fact Table created by create_views.py
        missions = con.execute("SELECT DISTINCT mission_id FROM fact_nav ORDER BY mission_id DESC").fetchall()
        mission_list = [m[0] for m in missions]
        return {"missions": mission_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Query Error: {str(e)}")
    finally:
        con.close()

@router.get("/mission/{mission_id}/summary")
async def mission_summary(mission_id: str):
    """Return temporal bounds for a specific MISSION_ID string"""
    con = get_connection()
    try:
        # Use parameterized query to handle the string ID correctly
        query = "SELECT mission_id, MIN(wall_ns), MAX(wall_ns) FROM fact_nav WHERE mission_id = ? GROUP BY mission_id"
        row = con.execute(query, [mission_id]).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")

        start_ns, end_ns = row[1], row[2]
        duration_ns = end_ns - start_ns if start_ns and end_ns else 0

        return {
            "mission_id": row[0],
            "start_ns": start_ns,
            "end_ns": end_ns,
            "duration_sec": duration_ns / 1e9
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        con.close()

# --- FASTAPI APP ---
app = FastAPI(title="Drone Forensic API")
app.include_router(router, prefix="/forensic", tags=["Forensic"])

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Launching Forensic API on Port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)