#!/bin/bash

# --------------------------------------------------
# NAVIGATION DOMAIN PRE-FLIGHT AUDIT
# --------------------------------------------------

echo "--------------------------------------------------"
echo "[INFO] Running Navigation Domain Pre-Flight Audit..."
python3 src/core/verify_bridge.py

echo ""
echo "[INFO] Fetching Latest Synchronized Telemetry..."
python3 src/core/inspect_flight.py

echo ""
echo "[INFO] Checking Meta Ledger in DuckDB..."
duckdb src/bin/nav_domain.db <<SQL
SELECT * FROM meta_ledger;
SQL

echo ""
echo "[INFO] Listing All Tables in DuckDB..."
duckdb src/bin/nav_domain.db <<SQL
SHOW TABLES;
SQL

echo ""
echo "[INFO] Preflight audit completed."
echo "--------------------------------------------------"
