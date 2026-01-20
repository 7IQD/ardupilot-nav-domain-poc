# NAVIGATION FLIGHT SAFETY DASHBOARD CONTRACT
**Status:** Final (Locked)
**Scope:** Navigation Domain Only
**Audience:** Safety Reviewers, Mentors, Maintainers
**Nature:** Authoritative Presentation Contract (Non-Negotiable)

---

## 1. Purpose & Scope

This document defines the **mandatory visual, analytical, and behavioral contract**
for the **Navigation Flight Safety Dashboard**.

The dashboard is a **post-flight and replay-safe safety review artifact**.
It **does not perform control, estimation, or inference**, and it **does not alter**
ArduPilot runtime behavior.

**Domain Scope:**
- Navigation domain only
- Consumes Navigation Mart outputs
- No cross-domain inference (Control, Power, Mission handled separately)

---

## 2. Dashboard Layout Contract (3-Column Standard)

### Fixed Structural Layout

| Column | Role | Description |
|------|------|-------------|
| **Left** | Parameters / Remarks | Scrollable annotations, thresholds, reviewer notes |
| **Center** | **Locked 2×2 Visual Grid** | Core safety visuals (non-movable, non-resizable) |
| **Right** | Metadata / Summary | Mission identity, timestamps, summary stats |

### Locked Central Grid (Invariant)

| Position | Panel |
|--------|-------|
| Top-Left | Error Histogram + Descriptive Statistics |
| Top-Right | Causal / Correlation Heatmap |
| Bottom-Left | Z-Score Anomaly Monitor |
| Bottom-Right | Spatial Drift Heatmap |

**Rules:**
- Central grid is **locked**
- Axes, units, and scales are fixed
- Layout identical across missions and vehicles

---

## 3. Data → UI Binding (Frozen Mapping)

| Data Meaning | Mart Column | Visual Element |
|-------------|------------|---------------|
| Latitude / Longitude | `latitude_deg`, `longitude_deg` | Spatial Heatmap |
| Lateral Deviation | `lat_dev_m` | Histogram, Z-Score |
| Control Inputs (aggregated) | `ctrl_*` | Causal Heatmap |
| Timestamp | `time_boot_ms` | Metadata |
| Altitude / Speed | `alt_m`, `vel_mps` | Contextual overlays |

> **Rule:** UI consumes **only mart outputs**.
> No raw MAVLink or JSON enters the dashboard.

---

## 4. Temporal & Causal Alignment Rules (Critical)

### 4.1 Time Anchor (Golden Thread)

- **Primary clock:** `time_boot_ms`
- All visuals must be traceable to this clock
- Wall-clock time is never used for analysis

---

### 4.2 Causal Window (Mandatory)

Control effects are **not instantaneous**.

**Rule:**
A control input at time `t` is evaluated against navigation deviation observed in:


Where:
- `Δmin` = 100–200 ms (actuator + dynamics latency)
- `Δmax` = 1000 ms (upper attribution bound)

**Implication:**
- Heatmaps represent **lagged correlation**, not instantaneous causality
- Prevents false attribution and reviewer bias

---

### 4.3 Granularity & Sampling (Locked)

- Control inputs operate at higher frequency (50–400 Hz)
- GPS / EKF act as the **reference witness**

**Rule:**
> Control inputs MUST be **down-sampled or aggregated**
> to the GPS / EKF witness rate before correlation.

Allowed aggregation:
- Mean
- RMS
- Last-value-held (explicitly declared)

**Raw high-frequency control streams are prohibited** in visualization.

---

## 5. Visual Scaling & Color Semantics

### 5.1 Numeric Scaling (Locked)

| Metric | Nominal | Warning | Violation |
|------|---------|---------|-----------|
| Lateral Deviation | 0 m | ≤ 2.0 m | > 2.0 m |

- All missions share identical numeric bounds
- No auto-scaling permitted

---

### 5.2 Color Rules (Partially Locked)

**Mandatory:**
- Color mapping must be **monotonic**
- Symmetric around zero where applicable
- Fixed numeric bounds

**Deferred (Allowed):**
- Exact RGB palette (may evolve without semantic change)

---

## 6. Quadrant Semantics (What Each Panel Proves)

### Top-Left: Error Histogram & Statistics
- Distribution of lateral deviation
- Bias, spread, stability
- First-order safety assessment

### Top-Right: Causal / Correlation Heatmap
- Lag-aware correlation between control input and deviation
- Indicates stress, not blame
- Uses causal window rules (Section 4)

### Bottom-Left: Z-Score Anomaly Monitor
- Flags statistically extreme deviations
- Automated alert basis
- Thresholds fixed across missions

### Bottom-Right: Spatial Drift Heatmap
- Geographic localization of navigation error
- Reveals terrain- or phase-specific issues

---

## 7. Metadata & Traceability (Always Visible)

Right-hand column MUST display:
- Vehicle ID
- Mission ID
- Mission Token (Git Hash + Session ID)
- Mission start / end time
- Summary safety statistics

This ensures **replayability and audit trust**.

---

## 8. Runtime vs Analysis Mode

| Mode | Behavior |
|----|---------|
| **OLTP (Live)** | Static layout, minimal visuals, alert-oriented |
| **OLAP (Post-Flight)** | Full 3-column dashboard, all quadrants |

No visual behavior divergence is permitted beyond this distinction.

---

## 9. Safety & Compliance Principles

- Locked layout prevents narrative bias
- Fixed scales prevent cherry-picking
- Explicit causal delay prevents false blame
- Identical dashboards enable fleet-wide comparison

---

## 10. Traceability Links

- **Domain Spec:** `docs/domains/navigation/navigation.md`
- **Implementation Framework:** `NAV_MART_IMPLEMENTATION_FRAMEWORK.md`
- **Weaving Logic:** `src/weaving/navigation.py`
- **Audit Rules:** `src/audit/navigation.py`
- **Orchestration:** `src/runner/main.py`

---

## Contract Status

This document is **binding**.

Any dashboard implementation that violates:
- layout,
- temporal rules,
- scaling,
- or data bindings

is considered **non-compliant**.

---
