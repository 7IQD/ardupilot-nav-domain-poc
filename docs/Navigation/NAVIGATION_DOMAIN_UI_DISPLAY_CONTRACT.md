# 🔒 Navigation Domain UI – Flight Safety Dashboard Contract

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

**Consumes:** `lat_drift` OR `lon_drift` OR `alt_drift`

**Derived:** mean, std

---

## 🟦 Panel 3: Z-Score Anomaly Watchdog (LOCKED)

**Purpose (Board):**

> *Are we seeing abnormal navigation behavior right now?*

**Visual (Frozen):**

* Line plot (drift vs time)
* Normal points: neutral color
* |z| ≥ 3 points: red markers
* Threshold lines at ±3σ

**Consumes:** drift signal, time ordering (index or time)

**Derived:** z-score

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

**Consumes:** `drift_magnitude`, ONE causal signal (from dropdown)

**Causal options (UI fixed list):**

* Ground speed
* Yaw rate
* GPS quality (HDOP / sats)
* Altitude / phase

---

## 🧩 RIGHT COLUMN — FOUR TEXT PANELS (LOCKED UI)

**Purpose of this column:**

> *Live executive + engineering insight that mirrors the written report.*

| Panel | Purpose / Report Section |
|-------|--------------------------|
| Panel-1 | Operator Verdict (§1) |
| Panel-2 | Nav Stability Metrics (§2) |
| Panel-3 | Anomaly & Stress Watch (§3) |
| Panel-4 | Data Honesty & Limits (§4) |

**Rules:**

* Each panel answers **one question only**
* No duplicated info from plots
* UI renders **only what pipeline provides**
* Panels are **immutable** — no resizing, moving, or auto-computation

---

## 🔗 PANEL ↔ REPORT TRACEABILITY

| UI Panel | Report Section             |
| -------- | -------------------------- |
| Panel-1  | §1 Operator Summary        |
| Panel-2  | §2 Engineering Diagnostics |
| Panel-3  | §3 System Interpretation   |
| Panel-4  | §4 Data Gaps               |

---

## 🧠 DESIGN PRINCIPLES

* Display logic frozen
* Board defensible
* Pipeline-ready
* JSON-only changes going forward

---

## APPENDIX A — PIPELINE → UI JSON CONTRACT (DISPLAY ONLY)

**Purpose:** Freeze the data handshake between pipeline and UI. UI never computes anything; all fields are pre-computed.

### Panel-1: Operator Verdict
* `system_verdict` : enum ∈ { NOMINAL, WARNING, CRITICAL }

### Panel-2: Nav Stability Metrics
* `max_lat_z` : float
* `max_lon_z` : float
* `max_alt_z` : float
* `mean_alt_drift_m` : float

### Panel-3: Anomaly & Stress Watch
* `z_exceed_count_lat` : int
* `z_exceed_count_lon` : int
* `z_exceed_count_alt` : int
* `motion_regime` : enum

### Panel-4: Data Honesty & Limits
* `unavailable_fields` : [string]
* `confidence_level_pct` : int

**Rules for Pipeline → UI:**

* Only the fields above are delivered to UI
* UI renders fields verbatim; no computation allowed
* Missing fields remain empty; UI never infers
* JSON contract versioned alongside pipeline for traceability

---

### ✅ Status

* Display logic frozen
* Board defensible
* Pipeline-ready
* JSON-only changes going forward
