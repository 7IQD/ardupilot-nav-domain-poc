from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import uvicorn

app = FastAPI()

# 1. FIX CORS (Allows Svelte to talk to Python)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. THE LIVE DATA ROUTE (Must match /api/nav/live)
@app.get("/api/nav/live")
async def get_live_telemetry():
    """
    Returns live telemetry.
    Matches the NavStore interface in Svelte.
    """
    return {
        "telemetry": {
            "drift": round(random.uniform(0.8, 1.4), 2),
            "vx_mps": 18.5,
            "lat_drift": 0.02,
            "alt_drift": 0.05,
            "phase": "MISSION_ACTIVE",
            "sensors": {"gps": 1, "imu": 1, "baro": 1}
        },
        "pipeline": {
            "ingress_hz": 50,
            "ingest_ms": 3,
            "vault_ok": True
        },
        "logs": [
            {"stage": "VAULT", "msg": "Syncing EKF state to Parquet", "latency": 0.8}
        ]
    }

# 3. DATABASE OVERWRITE (For your future testing)
@app.post("/api/test/overwrite-db")
async def overwrite_db():
    # Insert your DuckDB/Parquet wipe logic here
    print("CRITICAL: Overwriting database for fresh test cycle.")
    return {"status": "SUCCESS", "detail": "Database cleared."}

if __name__ == "__main__":
    # Runs on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)