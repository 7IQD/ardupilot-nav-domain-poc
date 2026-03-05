#!/usr/bin/env python3
import os
import duckdb
import pandas as pd
import numpy as np
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ArduPilot Nav Domain AI API")

# --- PATH CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
# Direct path to our persistent Gold Database
DB_PATH = os.path.join(PROJECT_ROOT, "bin/vault/drone_df_views.db")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HELPER: SAFE GOLD CONNECTION ---
def get_gold_df(query: str, params: list = []):
    """Provides a read-only, thread-safe connection to the Gold Feature Store."""
    if not os.path.exists(DB_PATH):
        raise HTTPException(
            status_code=500,
            detail=f"Gold Store Missing at {DB_PATH}. Run create_views.py first."
        )

    # read_only=True is critical for concurrent UI + AI access
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute(query, params).df()

# --- 1. THE INTELLIGENCE ENDPOINT (Verdict) ---
@app.get("/api/nav/verdict/{mission_id}")
async def get_mission_verdict(mission_id: str):
    """
    Analyzes the Gold State Vector to produce an AI 'Verdict'.
    Logic: Ground-Strike detection (High Spd + Low Alt).
    """
    query = """
        SELECT Alt, spd_gps, Roll, Pitch
        FROM fact_nav_state_vector
        WHERE mission_id = ?
    """
    df = get_gold_df(query, [mission_id])

    if df.empty:
        return {"mission_id": mission_id, "verdict": "UNKNOWN", "reason": "No mission data found in Gold Layer."}

    # --- AI LOGIC (Hardened) ---
    # Identify unsafe states: Moving > 5m/s while essentially on the ground (< 0.3m)
    unsafe_mask = (df['spd_gps'] > 5.0) & (df['Alt'] < 0.3)
    unsafe_events = df[unsafe_mask]

    verdict = "PASS" if unsafe_events.empty else "FAIL"
    analysis = "Normal Flight Operations" if verdict == "PASS" else f"Detected {len(unsafe_events)} unsafe ground-speed incidents."

    # Safe metric extraction (Handles NaNs to prevent JSON crashes)
    max_spd = df['spd_gps'].max()
    avg_alt = df['Alt'].mean()

    return {
        "mission_id": mission_id,
        "layer": "GOLD_ANALYSIS",
        "verdict": verdict,
        "ai_analysis": analysis,
        "metrics": {
            "max_spd": float(max_spd) if not pd.isna(max_spd) else 0.0,
            "avg_alt": float(avg_alt) if not pd.isna(avg_alt) else 0.0,
            "unsafe_samples": len(unsafe_events)
        }
    }

# --- 2. THE TELEMETRY ENDPOINT (UI/Forensics) ---
@app.get("/api/nav/telemetry/{mission_id}")
async def get_gold_telemetry(mission_id: str):
    """Fetches the full fused Gold state vector for dashboard plotting."""
    query = "SELECT * FROM fact_nav_state_vector WHERE mission_id = ? ORDER BY TimeUS ASC"
    df = get_gold_df(query, [mission_id])

    # Replace NaNs with None so FastAPI converts them to null in JSON
    data = df.replace({np.nan: None}).to_dict(orient="records")

    return {
        "mission_id": mission_id,
        "layer": "GOLD_STATE_VECTOR",
        "count": len(data),
        "telemetry": data
    }

if __name__ == "__main__":
    import uvicorn
    # Port 8000 is the standard for GSoC AI Agent development
    uvicorn.run(app, host="0.0.0.0", port=8000)