# 📋 Navigation Domain – Observability Test Requirements Document (TRD)

> **Purpose**: This document is the single *Source of Truth* for the NAV Domain Proof‑of‑Concept (POC). It defines scope, inputs, expected behavior, and certification rules to prevent drift and scope creep during development.

---

## 1️⃣ Setup Prerequisites — *The Digital Garage*

**Environment**

* ArduPilot **SITL** (Copter / Rover)
* MAVProxy for command & parameter injection
* MAVLink telemetry via SITL

**Database Rule**

* **AUTO‑OVERWRITE (MANDATORY)**
* All previous NAV test tables **must be dropped and recreated** at the start of every run
* No historical carry‑over allowed

**Tooling**

* `pymavlink` → telemetry ingestion
* `numpy`, `pandas` → inference & metrics
* (Optional later) `duckdb` → temporal joins / persistence

---

## 2️⃣ Test Matrix — *Baseline → Stress*

| Test ID    | Scenario     | Generation Method (Input)            | Expected Output (Logic)                                                    |
| ---------- | ------------ | ------------------------------------ | -------------------------------------------------------------------------- |
| **NAV‑01** | Steady State | Normal flight, no parameters changed | Z‑scores ≈ 0 → **Health = GREEN**. Strong GPS–EKF correlation              |
| **NAV‑02** | Sudden Shock | `param set SIM_GPS_GLITCH_X 50`      | Z‑score spike → **Health = RED**. Latency measured from injection to alert |
| **NAV‑03** | Slow Poison  | `param set SIM_GYR1_BIAS_X 0.05`     | Gradual Z‑score rise → **Health = YELLOW**. Trend divergence detected      |

---

## 3️⃣ Observability Data Schema — *Performance Report*

Each test run produces a structured report with the following fields:

* **time_boot_ms** — MAVLink monotonic timestamp
* **Independent_Var_Status** — Raw sensor variance / noise indicators (GPS, IMU)
* **Dependent_Var_Status** — EKF output stability metrics
* **Innovation_Z** — Normalized innovation / surprise score
* **System_Inference** — Enum: `Healthy | Sensor_Anomaly | Systemic_Failure`

---

## 4️⃣ Certification Criteria — *Mechanic’s Seal*

A NAV analysis run is considered **Certified** only if **all** conditions hold:

1. **Observability Gap = 0**
   Injected fault type is correctly identified by inference logic

2. **Performance Bound Measured**
   Time from *Fault Injected → Observed Alert* is recorded and within safety limits

3. **Clean Exit**
   Database overwrite succeeded and only current‑run artifacts exist

---

## 5️⃣ Observed Output Template — *Run Log*

(To be filled after each execution)

* **Test ID**: NAV‑XX
* **Actual Latency**: ___ ms
* **False Positives**: Yes / No
* **Wisdom Gained**: EKF behavior, coupling effects, estimator sensitivity notes

---

## 6️⃣ Explicit Non‑Goals (Scope Guardrails)

* ❌ No controller tuning
* ❌ No estimator parameter optimization
* ❌ No hardware‑in‑the‑loop (HITL)
* ❌ No UI polish beyond contract validation

---

**Status**: ✅ Frozen for NAV Domain POC

