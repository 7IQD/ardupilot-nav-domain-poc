#!/usr/bin/env python3
import os
import duckdb
import pandas as pd

# --- PATHS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
WAREHOUSE_DF = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")
VAULT_DB = os.path.join(WAREHOUSE_DF, "drone_df_views.db")

# --- CONNECT TO DUCKDB ---
con = duckdb.connect(VAULT_DB)

# --- CANONICAL DOMAIN FACT TABLES ---
DOMAINS = [
    "fact_nav_events",
    "fact_est_state",
    "fact_sys_state",
    "fact_com_state",
    "fact_power_state"
]

# --- UI / Semantic Views ---
UI_VIEWS = [
    "view_nav_monitor",
    "view_est_analysis",
    "view_sys_health",
    "view_com_quality",
    "view_power_metrics"
]

def list_domains():
    """Return all canonical domain fact tables."""
    return DOMAINS

def fetch_domain(domain_name, limit=100):
    """Fetch sample data from a domain fact table."""
    if domain_name not in DOMAINS:
        raise ValueError(f"Unknown domain: {domain_name}")
    query = f"SELECT * FROM {domain_name} LIMIT {limit}"
    return con.execute(query).fetchdf()

def fetch_ui_view(view_name, limit=100):
    """Fetch sample data from a semantic/UI view."""
    if view_name not in UI_VIEWS:
        raise ValueError(f"Unknown view: {view_name}")
    query = f"SELECT * FROM {view_name} LIMIT {limit}"
    return con.execute(query).fetchdf()

# --- CLI / Test Harness ---
if __name__ == "__main__":
    print("🚁 Drone DF Test Harness")
    print("Available Domains:")
    for d in list_domains():
        print(f"  - {d}")

    # Sample from fact tables
    for d in DOMAINS:
        print(f"\n📄 Sample rows from {d}:")
        df = fetch_domain(d, limit=5)
        print(df)

    # Sample from UI views
    for v in UI_VIEWS:
        print(f"\n📊 Sample rows from {v}:")
        try:
            df = fetch_ui_view(v, limit=5)
            print(df)
        except Exception as e:
            print(f"⚠️ Could not fetch view {v}: {e}")