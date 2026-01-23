#!/bin/bash

echo "--------------------------------------------------"
echo "🔍 RUNNING NAVIGATION DOMAIN PRE-FLIGHT AUDIT..."
python3 core/verify_bridge.py

echo ""
echo "📈 FETCHING LATEST SYNCHRONIZED TELEMETRY..."
python3 core/inspect_flight.py
echo "--------------------------------------------------"
