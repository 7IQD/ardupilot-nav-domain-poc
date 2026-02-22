# 🏛️ Scorecard Logic

---

## 1️⃣ Quantitative Assessment (Data → Information)

*Derived from mission_time & inode anchors.*

| Assessment Area | Nav Domain Example | Power Domain Example | System Domain Example |
|-----------------|-----------------|-------------------|--------------------|
| **Accuracy** | `RelHomeAlt` MAE vs `DAlt` | Voltage sag vs load profile | Target tracking error (`DCRt` vs `CRt`) |
| **Reliability** | GPS consistency (`HDop`) | Current spikes / outlier count | `Clip` events (sensor saturation) |
| **Response** | Phase Lag (Input vs `VZ`) | Recovery time after high draw | PID overshoot / Oscillation count |

**Methodology (Statistical Engine):**

* Z-Score → Anomaly detection.
* RMSE → Penalize large deviations in path/altitude.
* Standard Deviation → Jitter in steady-state phases.

**Presentation (Visual Dimensions):**

* Line Chart → Time vs error.
* Histogram → Distribution of `VibeZ`.
* Bar Chart → Energy cost per flight phase.

---

## 2️⃣ Qualitative Assessment (Information → Knowledge)

*Derived from cross-domain stitching.*

| Assessment Area | Intra-Domain Focus | Inter-Domain Focus |
|-----------------|-----------------|-----------------|
| **Integrity** | Data continuity | EST errors correlate with NAV drift |
| **Safety Margin** | Altitude safety | Volt near floor |
| **Agility** | Smooth orientation changes | Power response vs NAV commands |

**Scoring (Likert Scale 1–5):**

* 1 – Critical: Active failure or sensor clipping
* 2 – Marginal: High drift or energy intensity
* 3 – Nominal: Baseline SITL performance
* 4 – Efficient: Better than baseline, low power draw
* 5 – Optimal: Near-zero error, zero vibration, ideal energy

---

## 3️⃣ Common Binding Logic

* **Temporal (`mission_time`)** → Intra-/Inter-domain stitching & phase alignment.
* **Relational (`inode` / `mission_id`)** → Mission comparison, degradation tracking.

---

## 4️⃣ Information Layer – NAV Domain (High-Level Metrics)

| Information Goal | Insight |
|-----------------|--------|
| Vertical Stability | Std deviation of `RelHomeAlt` for hover/landing precision |
| Horizontal Velocity | Instantaneous & mean `Spd` for transit efficiency |
| Vertical Performance | Rate of change in `VZ` for climb/descent evaluation |
| Signal Integrity | GPS reliability (`NSats`, `HDop`) |
| Trajectory Volume | 3D path spread (`Lat`, `Lng`, `RelHomeAlt`) |
| Mission Duration | Mission time difference |
| Attitude State | Orientation/rotation (`Q1-Q4`) |
| Vertical Accuracy | Planned vs actual altitudes |
| Mechanical Stress | Vibration influence on motion |
| Transit Efficiency | Energy consumption per speed |
| Estimation Trust | Position error vs EKF |
| Command Response | Pilot/Autopilot input vs trajectory |
| Energy Cost | Total consumption per distance |
| System Stress | Vibration peaks vs flight phase |

---

