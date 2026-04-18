# ArduPilot Nav-Mart
**Navigation POC — Multi-Domain Telemetry Analysis**

This project captures, organizes, and analyzes navigation telemetry (GPS/EKF) from ArduPilot SITL/logs **without changing ArduPilot**.
It creates a **reproducible evidence trail** for engineering review.

---

## Current Issue / Problem

Autopilots generate tons of telemetry, but it’s hard to review, replay, or make sense of it.
This project solves that by:

- Capturing all relevant data reliably
- Organizing it by domain
- Aligning timestamps so events can be compared easily

Navigation is used as the **reference example**.

---

## How It Works

1. **Capture:** Grab MAVLink packets from SITL or logs
2. **Organize:** Sort packets into Python structures by domain
3. **Align:** Match timestamps across domains
4. **Store:** Save in `nav_domain.db` for easy queries

Two engines handle this:

- **Engine 1:** Capture and refine → “What happened?”
- **Engine 2:** Dashboard and evidence → “What matters?”

Vaults:

- `warehouse/` → raw telemetry
- `dashboard/` → human-validated snapshots and CSVs
- `nav_domain.db` → query-ready database

---

## Analysis

- EKF ↔ GPS causal analysis
- Replayable telemetry runs
- Evidence snapshots for review

This acts as a **proof of concept** and **template for future domains**.

---

## What We Don’t Do

- No fancy UI or dashboards
- No real-time guarantees
- No multi-vehicle fusion
- No autonomous feedback to ArduPilot
- No other domains beyond Navigation

Focus is on **clarity, traceability, and reproducibility**.

---

## Clear Separation

- Capture vs. analysis is clearly separated
- Data and evidence are reproducible
- Experiments can be repeated
- Progress is incremental and reviewable

Every artifact answers:

1. What produced it?
2. What supports it?
3. When and why was it captured?

---

## Next Steps

- Add more domains
- Compare across domains
- Fleet-level benchmarking
- Generate simple reports

> Optional extensions, not part of the current POC.

---


