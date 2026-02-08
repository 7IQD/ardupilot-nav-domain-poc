# src/nav_dashboard_api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import duckdb
import pandas as pd

# 🔹 MUST be named 'app'
app = FastAPI(title="NAV POC API")

# -------------------------------
# CORS (so your Svelte dashboard can fetch)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Paths
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
GOLD_PATH = BASE_DIR / "bin/vault/gold/fact_nav_precision.parquet"

# -------------------------------
# Helper: read Parquet into JSON
# -------------------------------
def fetch_gold_data():
    if not GOLD_PATH.exists():
        # Minimal dummy dataset if file missing
        return [
            {"time_sec": 0, "error_m": 0.1, "vx_mps": 1.0, "lat_drift": 0.01, "alt_drift": 0.02},
            {"time_sec": 1, "error_m": 0.15, "vx_mps": 1.2, "lat_drift": 0.02, "alt_drift": 0.03},
            {"time_sec": 2, "error_m": 0.2, "vx_mps": 1.1, "lat_drift": 0.01, "alt_drift": 0.04},
        ]
    # Use DuckDB to read Parquet efficiently
    con = duckdb.connect(database=':memory:')
    df = con.execute(f"SELECT * FROM read_parquet('{GOLD_PATH}')").df()
    con.close()
    return df.to_dict(orient="records")

# -------------------------------
# API Endpoints
# -------------------------------
@app.get("/health")
def health_check():
    return {"status": "OK", "message": "FastAPI bridge running!"}

@app.get("/api/nav/gold")
def get_gold_data():
    """
    Returns latest NAV precision data from DuckDB or dummy fallback.
    """
    return fetch_gold_data()
