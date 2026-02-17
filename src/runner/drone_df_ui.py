#!/usr/bin/env python3
import os
import duckdb
import pandas as pd

# --- PATHS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
WAREHOUSE_DF = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")
VAULT_DB = os.path.join(WAREHOUSE_DF, "drone_df_views.db")

# --- CONNECT TO AGNOSTIC VAULT ---
con = duckdb.connect(VAULT_DB)

# --- DOMAIN LIST ---
DOMAINS = ["fact_navigation", "fact_estimator", "fact_system", "fact_communication", "fact_power"]

def list_domains():
    """Return available domains in the vault."""
    return [d for d in DOMAINS]

def fetch_domain(domain_name, limit=1000):
    """Fetch sample data from a domain view."""
    if domain_name not in DOMAINS:
        raise ValueError(f"Unknown domain: {domain_name}")
    query = f"SELECT * FROM {domain_name} LIMIT {limit}"
    return con.execute(query).fetchdf()

def fetch_analytical_view(view_name, limit=1000):
    """Fetch sample data from analytical perspectives."""
    query = f"SELECT * FROM {view_name} LIMIT {limit}"
    return con.execute(query).fetchdf()

# --- SIMPLE CLI FOR TESTING ---
if __name__ == "__main__":
    print("🚁 Drone DF UI | Available Domains:")
    for d in list_domains():
        print(f"  - {d}")

    # Fetch first 5 rows from each domain
    for d in list_domains():
        print(f"\n📄 Sample from {d}:")
        df = fetch_domain(d, limit=5)
        print(df)

    # Optional: Sample analytical views
    ANALYTICAL_VIEWS = ["view_telemetry_attitude", "view_perspective_delta",
                        "view_system_vibe_stress", "view_power_health"]
    for v in ANALYTICAL_VIEWS:
        print(f"\n📊 Sample from {v}:")
        try:
            df = fetch_analytical_view(v, limit=5)
            print(df)
        except Exception as e:
            print(f"⚠️ Could not fetch view {v}: {e}")
