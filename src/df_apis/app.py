#!/usr/bin/env python3
import uvicorn
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Internal Imports
from src.df_domain_data_services.nav.nav_data_service import NavDataService
from src.utils.metrics_helpers import diagnose_instability

app = FastAPI(
    title="ArduPilot Nav Domain AI API",
    description="Refactored Service-Layer API for Navigation Analytics",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ONLINE", "domain": "NAV_DOMAIN_GOLD", "engine": "DuckDB + FastAPI"}

@app.get("/api/nav/verdict/{mission_id}")
async def get_mission_verdict(mission_id: str):
    try:
        service = NavDataService(mission_id=mission_id)
        df = service.fetch_fused_telemetry()
        if df.empty:
            raise HTTPException(status_code=404, detail="Mission not found.")

        summary = service.get_summary(df)
        # AI Safety Logic
        unsafe_mask = (df['spd_gps'] > 5.0) & (df['Alt'] < 0.3)
        unsafe_incidents = int(unsafe_mask.sum())

        return {
            "mission_id": mission_id,
            "verdict": "FAIL" if unsafe_incidents > 0 or summary.get("health_status") == "RED" else "PASS",
            "metrics": summary,
            "unsafe_ground_events": unsafe_incidents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/nav/forensics/{mission_id}")
async def get_mission_forensics(mission_id: str):
    """
    GSoC-Spec: Returns Root-Cause analysis and suggested fixes.
    """
    try:
        service = NavDataService(mission_id=mission_id)
        df = service.fetch_fused_telemetry()

        # Analyze the telemetry for root causes
        findings = diagnose_instability(df)

        return {
            "mission_id": mission_id,
            "status": "ANOMALY_DETECTED" if findings else "NOMINAL",
            "findings": findings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forensics Error: {str(e)}")

@app.get("/api/nav/telemetry/{mission_id}")
async def get_gold_telemetry(mission_id: str):
    try:
        service = NavDataService(mission_id=mission_id)
        df = service.fetch_fused_telemetry()
        telemetry_data = df.replace({np.nan: None}).to_dict(orient="records")
        return {"mission_id": mission_id, "count": len(telemetry_data), "data": telemetry_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)