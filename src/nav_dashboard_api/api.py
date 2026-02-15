from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- CONNECT TO DUCKDB ----
DB_PATH = "/home/ni/ardupilot-nav-domain-poc/bin/vault/warehouse_df/nav_dflog_domain.db"
conn = duckdb.connect(DB_PATH, read_only=True)

# ---- LIVE MOCK DATA ----
@app.get("/api/nav/live")
async def get_live_telemetry():
    return {
        "telemetry": {
            "drift": round(random.uniform(0.8, 1.4), 2),
            "vx_mps": 18.5,
            "lat_drift": 0.02,
            "alt_drift": 0.05,
            "phase": "MISSION_ACTIVE",
            "sensors": {"gps": 1, "imu": 1, "baro": 1}
        }
    }

# ---- REAL DUCKDB DOMAIN VIEW ----
@app.get("/api/nav/domain")
async def get_domain_data(view: str = Query("ui_nav_drone_monitor")):
    try:
        result = conn.execute(f"SELECT * FROM {view} LIMIT 500")
        rows = result.fetchall()
        columns = [desc[0] for desc in result.description]

        data = [dict(zip(columns, row)) for row in rows]

        return {
            "view": view,
            "row_count": len(data),
            "telemetry": data
        }

    except Exception as e:
        return {"error": str(e)}
