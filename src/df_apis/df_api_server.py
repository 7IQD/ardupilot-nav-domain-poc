#!/usr/bin/env python3
import os
import duckdb
import numpy as np
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import your Domain Controller (The Judge)
from dashboard.nav.nav_controller import NavController

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PATH CONFIG ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
DB_PATH = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df/drone_df_views.db")

# --- Helper to determine layer type ---
def detect_layer(obj_name: str):
    if obj_name.startswith("fact_") and obj_name.endswith("_events"):
        return "SILVER_FACT"
    elif obj_name.startswith("fact_") and obj_name.endswith("_state"):
        return "GOLD_STATE"
    elif obj_name.startswith("view_"):
        return "GOLD_STATE"
    else:
        return "UNKNOWN"

# --- 1. INTELLIGENCE ENDPOINT (The Verdict) ---
@app.get("/api/nav/verdict")
async def get_nav_verdict(mission_id: str = Query(...)):
    """Triggers the NavController to run the ActionMap and return the PASS/FAIL verdict."""
    try:
        ctrl = NavController(mission_id)
        result = ctrl.run_audit()
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- 2. FORENSIC ENDPOINT (The Silver Audit) ---
@app.get("/api/nav/audit")
async def get_nav_audit(mission_id: str = Query(...)):
    """Fetch raw, sparse event data (Silver) to compare against reconstructed state."""
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        query = """
            SELECT mission_time AS TimeUS, RelHomeAlt, RelOriginAlt, inode
            FROM fact_nav_events
            WHERE mission_id = ?
            ORDER BY mission_time ASC
        """
        df = con.execute(query, [mission_id]).df()
        data = df.replace({np.nan: None}).to_dict(orient="records")
        return {"mission_id": mission_id, "layer": "SILVER_AUDIT", "telemetry": data}
    finally:
        con.close()

# --- 3. DOMAIN DATA ENDPOINT (Dynamic UI / Gold State) ---
@app.get("/api/domain")
async def get_domain_data(view: str = Query(...), mission_id: str | None = Query(None)):
    if not os.path.exists(DB_PATH):
        return JSONResponse(status_code=404, content={"error": "Database not found"})

    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        # Dynamic discovery of all available views
        available_views = [row[0] for row in con.execute("SHOW VIEWS").fetchall()]

        # Dynamic discovery of all fact tables
        available_facts = [row[0] for row in con.execute("SHOW TABLES").fetchall()
                           if row[0].startswith("fact_")]

        # Combine for validation
        all_objects = available_views + available_facts
        if view not in all_objects:
            return JSONResponse(status_code=400, content={"error": f"Invalid view/table: {view}"})

        query = f"SELECT * FROM {view}"
        params = []
        if mission_id:
            query += " WHERE mission_id = ?"
            params.append(mission_id)

        df = con.execute(query, params).df()
        data = df.replace({np.nan: None}).to_dict(orient="records")

        layer_type = detect_layer(view)
        return {
            "mission_id": mission_id,
            "view": view,
            "layer": layer_type,
            "telemetry": data
        }
    finally:
        con.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)