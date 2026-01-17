# 🟢 NAVIGATION DOMAIN – MASTER DOCUMENT

This file consolidates:

* **NAV_REPORT** – Static mission diagnostic
* **UI Contract** – Frozen dashboard layout & traceability
* **Phase-Wise Live Reporting Framework** – LRU / SRU logging for upstream & downstream monitoring

---

## ✅ NAV REPORT

(✔ = implemented, ⚠ = declared gap)

# [FDR-NAV] NAVIGATION LABORATORY DIAGNOSTIC REPORT

**Ref No:** `GSOC-2026-NAV-ANALYSIS` | **Class:** `Automated System Audit`

---

### 0. METADATA & PIPELINE STATUS ✔

* **Run Identifier:** `SITL_NAV_LAB_001`
* **Source Stream:** ☑ SITL ☐ Log File ☐ MAVLink
* **ETL Integrity:** ☑ Deterministic ☑ Read-Only
* **Runtime Libraries:** `Pandas / NumPy / Matplotlib`

**Status:** *Pipeline verified, reproducible.*

---

### 1. OPERATOR SUMMARY (Mission Level) ✔

**Objective:** Immediate GCS-level understanding.

* **System Verdict:** ☑ NOMINAL ☐ DEGRADED ☐ CRITICAL
* **Drift Assessment:** Low vertical & horizontal drift observed
* **Operator Action:** ☑ Proceed ☐ Monitor ☐ Abort

> **Summary:**
> Low-motion SITL scenario. Navigation solution not stressed.
> No statistically significant anomalies detected.

---

### 2. ENGINEERING DIAGNOSTICS (Nav Domain Contracts) ✔

**Objective:** Evidence-based validation (what we *can* prove).

| Sub-Domain | Metric            | Observed   | Threshold | Status          |
| ---------- | ----------------- | ---------- | --------- | --------------- |
| Nav        | Max |Lat Z|       | `0.00`     | `< 3.0`   | PASS            |
| Nav        | Max |Lon Z|       | `0.00`     | `< 3.0`   | PASS            |
| Nav        | Max |Alt Z|       | `0.00`     | `< 3.0`   | PASS            |
| Nav        | Mean Alt Drift    | `0.01 m`   | ≈ 0       | PASS            |
| Dynamics   | Mean Ground Speed | `0.01 m/s` | N/A       | INFO            |
| EKF        | NIS (Pos/Vel)     | —          | —         | ⚠ NOT AVAILABLE |

**Diagnostic Verdict:**
Navigation solution statistically stable **within observable parameters**.

---

### 3. SYSTEM INTERPRETATION (Causality Trace) ✔ / ⚠

**Objective:** Early “why” without overclaim.

* **Innovation Stress:** ☐ Exercised ☑ Not Exercised
* **Speed-Drift Correlation:** Weak / Non-significant
* **EKF Consistency:** ⚠ Not inferable (NIS unavailable)
* **Root Cause ID:** Nominal motion regime (SITL hover)

> ⚠ Causality limited by low-excitation scenario.

---

### 4. DATA GAPS & SENSOR HONESTY ✔

**Objective:** Explicit transparency (review-critical).

**Missing / Not Captured:**

* ☐ EKF NIS
* ☐ GPS HDOP
* ☐ Satellite Count
* ☐ Vibration (VIBE)
* ☐ EKF Covariances

**Reason:**
Not present in current nav_mart schema / SITL export.

---

### 5. ETL INTEGRITY STATEMENT ✔

* **Reproducibility:** Report derived directly from deterministic ETL. No manual edits.
* **Logic Version:** `v1.0.0`

**Authorized By:** `Student – GSoC Navigation`
**Review Status:** ☑ READY FOR UPSTREAM

---

### 📊 COVERAGE SCORECARD (Why this is 70%)

| Area                 | Coverage      |
| -------------------- | ------------- |
| Metadata / ETL       | 100%          |
| Operator Summary     | 100%          |
| Drift & Stability    | 100%          |
| Z-Score Monitoring   | 100%          |
| Causal Insight       | ~50%          |
| EKF Health           | 0% (declared) |
| Sensor Honesty       | 100%          |
| Review Defensibility | 100%          |

---

### 🔑 WHY THIS WORKS (IMPORTANT)

✔ Matches **your proposed vision structurally**
✔ Does **not fake EKF internals**
✔ Explicitly declares limitations
✔ Scales cleanly when new parameters arrive
✔ Safe for a beginner
✔ Strong for GSoC / academic review

---

### 🚀 Next Upgrade Path (Optional)

* GPS `HDOP + SatCount` → Sensor honesty
* EKF `NIS` → True consistency checks

---

## 🟢 NAVIGATION DOMAIN UI – DISPLAY CONTRACT

**Frozen 4-Panel Layout**

| Left Column (Visual Core) | Right Column (Executive Insight) |
|---------------------------|---------------------------------|
| Panel 1: Spatial Innovation Heatmap | Panel 1: Operator Verdict |
| Panel 2: Error Distribution Frequency | Panel 2: Nav Stability Metrics |
| Panel 3: Z-Score Anomaly Watchdog | Panel 3: Anomaly & Stress Watch |
| Panel 4: Causal Analysis | Panel 4: Data Honesty & Limits |

**Rules:**

* 2×2 central grid is fully locked, fixed axes & colormaps
* UI never computes logic – pipeline feeds **JSON-only**
* Columns 1 & 3 scrollable for remarks / metadata
* Each text panel maps 1:1 to NAV_REPORT section

---

## 🟢 PHASE-WISE LIVE REPORTING FRAMEWORK

### Purpose
Turn NAV_REPORT sections into live, dynamic **ETL-aware logging blocks**, catching navigation drift and missing data in real-time.

---

### 1. Reporting Units

| Unit | Acronym | Scope | Behavior | Analogy |
|------|---------|-------|---------|---------|
| Main Report | LRU (Line-Replaceable Unit) | Mission-level | Rolling updates; overwrites previous line | High-level NAV_REPORT summary |
| Component Logs | SRU (Shop-Replaceable Unit) | ETL / domain aggregates | Append-only; maintains full history | Heartbeat debug logs |

---

### 2. ETL-Wise Assertions

* **Ingress:** Telemetry completeness, timestamp monotonicity
* **Transformation:** GPS ↔ EKF alignment, unit scaling
* **Weaving:** ASOF JOIN correctness, drift computation
* **Audit:** Z-score thresholds, innovation stress, missing fields

**Behavior:**

* **LRU:** Mission verdict, drift summary (overwrites previous line)
* **SRU:** Individual metric logs with assertion results

---

### 3. Implementation Flow

