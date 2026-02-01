# 💎 Data Mart Engine

The Refinement Plane for ArduPilot telemetry. This engine transforms **Silver** (Raw Warehouse) data into **Gold** (Refined Fact) data.

## 🚀 Running the Engine (Dev Mode)

This project uses a `src/` layout. For local execution without installation, expose `src/` to Python manually:

```bash
PYTHONPATH=src python src/data_mart_engine/main.py