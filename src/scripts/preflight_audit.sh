#!/bin/bash
# Pre-flight Audit: Ensuring the Vault is accessible and the SITL is ready.

echo "--- 🛫 STEP 1: INFRASTRUCTURE CHECK ---"
if [ ! -d "bin" ]; then
    mkdir bin
    echo "📁 Created bin directory."
fi

echo "--- 📊 STEP 2: PASSIVE VAULT PEEK (HUD) ---"
# This runs the read_only HUD to check the current state of the database.
python3 src/core/inspect_flight.py

# THE CRITICAL SYNC: 1-second delay
# This ensures the OS releases the file handle before the Architect grabs it.
echo "⏳ Waiting for DB handle release..."
sleep 1

echo "--- 🛰️ STEP 3: LAUNCHING NAVIGATION AUTHORITY ---"
# Launches the Orchestrator which binds NavClerk to the Materializer.
python3 src/ingress/sim_vehicle_ingress.py