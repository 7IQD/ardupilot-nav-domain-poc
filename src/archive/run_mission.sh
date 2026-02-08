#!/bin/bash

# Configuration
MISSION_NAME="m_$(date +%Y%m%d_%H%M)"
echo "🛰️ Starting NAV Domain POC: $MISSION_NAME"

# 1. Start Ingestor in the background
PYTHONPATH=src python src/data_mart_ingest/ingest_mavlink.py &
INGEST_PID=$!

# 2. Wait for Warehouse Initialization
sleep 2

# 3. Start Refinery Orchestrator in the background
PYTHONPATH=src python src/data_mart_engine/main.py $MISSION_NAME &
REFINERY_PID=$!

# 4. Start Dashboard in the foreground
echo "🖥️ Launching EKF Expert Glass..."
PYTHONPATH=src python src/data_mart_browser/dashboard_ekf.py $MISSION_NAME

# Cleanup: Kill background processes on exit
trap "kill $INGEST_PID $REFINERY_PID; exit" SIGINT SIGTERM