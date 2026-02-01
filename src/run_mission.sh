#!/bin/bash
# Master Orchestrator for ArduPilot NAV POC

# 1. Setup Environment
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
MISSION_ID="MARATHON_$(date +%Y%m%d_%H%M)"

echo "🛰️ Starting NAV Domain Mission: $MISSION_ID"

# 2. Launch Ingestor (Engine-1) - Background
python3 src/data_mart_ingest/ingest_mavlink.py &
INGEST_PID=$!
echo "📥 Ingestor Online (PID: $INGEST_PID)"

# 3. Launch Refinery (Engine-2) - Background
sleep 2 # Wait for Silver Vault initialization
python3 src/data_mart_engine/main.py $MISSION_ID &
REFINERY_PID=$!
echo "⚙️ Refinery Online (PID: $REFINERY_PID)"

# 4. Launch Expert Glass (Dashboard) - Foreground
echo "🖥️ Launching EKF Expert Dashboard..."
python3 src/data_mart_browser/dashboard_ekf.py $MISSION_ID

# 5. Cleanup on Exit
trap "kill $INGEST_PID $REFINERY_PID; echo '🛑 Shutdown Complete'; exit" SIGINT SIGTERM