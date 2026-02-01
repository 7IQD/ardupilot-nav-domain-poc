# 🖥️ Nav Mart Dashboard (Engine-3)

This is the **Consumer Plane** for the ArduPilot Navigation POC. It visualizes the refined precision facts produced by the Data Mart Engine (Engine-2) in real time.

## 🚀 Purpose

* Reads the **Gold Mart** (`fact_nav_precision.parquet`) continuously.
* Displays **precision drift** between GPS and EKF telemetry.
* Highlights deviations beyond the **Safety Fence** with dynamic status (`HEALTHY` / `CRITICAL FAIL`).

---

## 🏗️ Architecture

* **Input:** `bin/vault/gold/fact_nav_precision.parquet` (produced by Engine-2)
* **Processing:** None — the dashboard is **read-only**. All calculations are done upstream.
* **Output:** Live Matplotlib plot with:
  * Precision error line
  * Safety fence reference
  * Dynamic status in the title bar

---

## 🎛️ Running the Dashboard

```bash
PYTHONPATH=src python src/data_mart_browser/dashboard.py
