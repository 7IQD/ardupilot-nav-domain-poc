# 🔒 Navigation Domain UI – DISPLAY FREEZE

## Global Rules (Non-Negotiable)

* **Exactly 4 panels**
* **No panel reordering**
* **No conditional visuals**
* **Only data availability toggles visibility**
* **UI never computes logic** (math stays in pipeline)

---

## 🟦 Panel 1: Spatial Innovation Heatmap (LOCKED)

**Purpose (Board):**

> *Where did navigation disagree spatially?*

**Visual (Frozen):**

* X-axis: Longitude (degrees)
* Y-axis: Latitude (degrees)
* Marker: Point (trajectory)
* Color: Drift magnitude
* Colormap: Sequential (cool → hot)
* Legend: Drift magnitude scale

**Consumes (exact):**

* `lat`
* `lon`
* `lat_drift`
* `lon_drift`

**Derived (pipeline only):**

* `drift_magnitude`

---

## 🟦 Panel 2: Error Distribution Frequency (LOCKED)

**Purpose (Board):**

> *Is the navigation error statistically well-behaved?*

**Visual (Frozen):**

* Histogram (bars)
* Overlay: Mean, ±1σ lines
* Single drift channel at a time (default: lat_drift)

**Consumes:**

* `lat_drift` OR `lon_drift` OR `alt_drift`

**Derived:**

* mean
* std

---

## 🟦 Panel 3: Z-Score Anomaly Watchdog (LOCKED)

**Purpose (Board):**

> *Are we seeing abnormal navigation behavior right now?*

**Visual (Frozen):**

* Line plot (drift vs time)
* Normal points: neutral color
* |z| ≥ 3 points: red markers
* Threshold lines at ±3σ

**Consumes:**

* drift signal
* time ordering (index or time)

**Derived:**

* z-score

---

## 🟦 Panel 4: Causal Analysis (LOCKED, SELECTABLE)

**Purpose (Board):**

> *Why did the drift occur?*

**Visual (Frozen):**

* Scatter plot
* X-axis: **Selectable causal signal**
* Y-axis: Drift magnitude
* Trend line (optional, non-interpretive)
* Correlation coefficient displayed

**Consumes:**

* `drift_magnitude`
* ONE causal signal (from dropdown)

**Causal options (UI fixed list):**

* Ground speed
* Yaw rate
* GPS quality (HDOP / sats)
* Altitude / phase

---
Below is a **clean, review-safe proposal** for the **4 text panels (right column)** that **directly map to your Test Report sections** and **complete the UI logically**.

No fluff. Each panel has a **single responsibility**.

---

## 🧩 RIGHT COLUMN — FOUR TEXT PANELS (LOCKED UI)

**Purpose of this column:**

> *Live executive + engineering insight that mirrors the written report.*

Each panel corresponds **1-to-1** with a report section.

---

## 🟦 PANEL-1 (TOP): OPERATOR VERDICT

**(Maps to Report §1 — Operator Summary)**

**Audience:** GCS Operator / Reviewer
**Question Answered:** *“Is this flight safe?”*

### Panel Content (Fixed Fields)

```
SYSTEM VERDICT: NOMINAL

Drift Status:
• Horizontal: Stable
• Vertical: Stable

Recommended Action:
✔ Proceed
```

### Data Source

* Z-Score PASS/FAIL
* Mean Alt Drift
* Ground speed regime

### Why it belongs here

✔ Immediate decision panel
✔ Human-readable
✔ No statistics exposed

---

## 🟩 PANEL-2: NAV STABILITY METRICS

**(Maps to Report §2 — Engineering Diagnostics)**

**Audience:** Navigation Engineer
**Question Answered:** *“Is Nav statistically stable?”*

### Panel Content

```
NAV DIAGNOSTICS

Max |Lat Z| : 0.00
Max |Lon Z| : 0.00
Max |Alt Z| : 0.00

Alt Drift (mean):
0.01 m  ✔ PASS
```

### Data Source

* robust Z-scores
* drift metrics

### Why it belongs here

✔ Matches Z-score plot visually
✔ Numeric but minimal
✔ Engineering-credible

---

## 🟨 PANEL-3: ANOMALY & STRESS WATCH

**(Maps to Report §3 — System Interpretation)**

**Audience:** Safety / Systems Engineer
**Question Answered:** *“Was the system stressed?”*

### Panel Content

```
ANOMALY WATCH

Z-Score Excursions:
• Lat : 0
• Lon : 0
• Alt : 0

Innovation Stress:
✖ Not Exercised

Motion Regime:
Low-Excitation
```

### Data Source

* Z-score threshold crossings
* Ground speed magnitude

### Why it belongs here

✔ Explains *why* plots look quiet
✔ Prevents false confidence
✔ Honest interpretation

---

## 🟥 PANEL-4 (BOTTOM): DATA HONESTY & LIMITS

**(Maps to Report §4 — Data Gaps)**

**Audience:** Reviewer / GSoC Evaluator
**Question Answered:** *“What is missing?”*

### Panel Content

```
DATA COVERAGE

Available:
✔ GPS Position
✔ EKF Position
✔ Velocity

Missing:
✖ EKF NIS
✖ HDOP / SatCount
✖ VIBE
✖ EKF Covariance

Confidence Level:
Moderate (70%)
```

### Data Source

* Schema introspection
* Known pipeline limits

### Why it belongs here

✔ Review-critical
✔ Prevents overclaim
✔ Matches written report

---

## 🔗 PANEL ↔ REPORT TRACEABILITY (IMPORTANT)

| UI Panel | Report Section             |
| -------- | -------------------------- |
| Panel-1  | §1 Operator Summary        |
| Panel-2  | §2 Engineering Diagnostics |
| Panel-3  | §3 System Interpretation   |
| Panel-4  | §4 Data Gaps               |

This **traceability is gold for reviewers**.

---

## 🧠 DESIGN PRINCIPLES (WHY THIS IS CORRECT)

✔ Each panel answers **one question only**
✔ No duplicated info from plots
✔ Human → Engineer → System → Reviewer flow
✔ Scales when new sensors arrive
✔ No lies, no assumptions

---
## 🚫 Explicitly Frozen Out

* ❌ No aesthetics-only charts
* ❌ No adaptive layouts
* ❌ No auto-switching logic
* ❌ No “smart” UI decisions

---

## 🧠 Final Contract (This is what matters)

> **If data exists → panel renders**
> **If data doesn’t exist → panel stays empty**
> **UI never guesses**

---

### ✔ Status

* Display logic frozen
* Board defensible
* Pipeline-ready
* JSON-only changes going forward

---

