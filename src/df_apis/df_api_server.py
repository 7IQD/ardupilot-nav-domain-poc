#!/usr/bin/env python3
import os
import duckdb
import numpy as np
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# --- Enable CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROBUST PATH LOGIC ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
WAREHOUSE_DF = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")
DB_PATH = os.path.join(WAREHOUSE_DF, "drone_df_views.db")
MISSION_VAULT = os.path.join(PROJECT_ROOT, "bin/vault/missions")

print(f"--- SERVER STARTING ---")
print(f"DEBUG: Database Path: {DB_PATH}")

# --- List available parquet domains ---
@app.get("/api/domains")
async def list_domains():
    if not os.path.exists(WAREHOUSE_DF):
        return {"domains": []}
    files = [f.replace(".parquet", "") for f in os.listdir(WAREHOUSE_DF) if f.endswith('.parquet')]
    return {"domains": sorted(files)}

# --- Serve domain data via DuckDB (SECURE & FILTERED) ---
@app.get("/api/domain")
async def get_domain_data(
    view: str = Query(...),
    mission_id: str | None = Query(None)
):
    print(f"\nDEBUG: UI Request: {view} | Filter: {mission_id}")

    if not os.path.exists(DB_PATH):
        return JSONResponse(status_code=404, content={"error": "Database not found"})

    # --- WHITELIST MAPPING (Controlled Aperture) ---
    mapping = {
        "com_df_master": "view_comm_link_quality",
        "est_df_master": "view_est_master",
        "nav_df_master": "ui_nav_drone_monitor",
        "sys_df_master": "view_system_vibe_stress",
        "power_df_master": "view_power_health"
    }

    if view not in mapping:
        print(f"ERROR: Unauthorized view access attempt: {view}")
        return JSONResponse(status_code=400, content={"error": f"Invalid domain: {view}"})

    db_view_name = mapping[view]
    con = duckdb.connect(DB_PATH, read_only=True)

    try:
        # --- SECURE PARAMETERIZED QUERY ---
        query = f"SELECT * FROM {db_view_name}"
        params = []

        if mission_id:
            query += " WHERE mission_id = ?"
            params.append(mission_id)

        print(f"DEBUG: Executing: {query} | Params: {params}")

        df = con.execute(query, params).df()
        row_count = len(df)

        # Sanitize for JSON (NaN -> None)
        data = df.replace({np.nan: None}).to_dict(orient="records")

        return {
            "mission_id": mission_id,
            "view": db_view_name,
            "row_count": row_count,
            "telemetry": data
        }

    except Exception as e:
        print(f"ERROR during query: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        con.close()

# --- Restore Missions Endpoint ---
@app.get("/forensic/missions")
async def list_missions():
    if not os.path.exists(MISSION_VAULT):
        return {"missions": []}
    missions = [d for d in os.listdir(MISSION_VAULT) if os.path.isdir(os.path.join(MISSION_VAULT, d)) or d.endswith('.parquet')]
    return {"missions": sorted(missions)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)