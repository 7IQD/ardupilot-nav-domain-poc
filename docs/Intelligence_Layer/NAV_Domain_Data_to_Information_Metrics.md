# 🏛️ NAV Domain Data to Information

**Project:** ArduPilot Nav-Domain Intelligence Platform
**Objective:** Establish the NAV domain as the anchor for mission scorecards, drift detection, and fault inference.

---

## 1️⃣ Intra-Domain Insights (`fact_nav`)

| Metric               | Source Field(s)       | Purpose                               |
|----------------------|---------------------|---------------------------------------|
| Vertical Stability    | RelHomeAlt           | Hover/landing precision               |
| Horizontal Velocity   | Spd                  | Transit efficiency                     |
| Vertical Performance  | VZ                   | Climb/descent dynamics                 |
| Signal Integrity      | NSats, HDop          | GPS reliability and drift detection   |
| Spatial Trajectory    | Lat, Lng, RelHomeAlt | 3D flight path and deviation          |
| Mission Timeline      | mission_time, wall_ns | Phase and event alignment             |
| Attitude State        | Q1–Q4                | Orientation / rotation for motion compensation |

---

## 2️⃣ Inter-Domain Insights (NAV + Other Domains)

| Metric               | NAV Field(s)         | External Domain Field(s) | Purpose                                 |
|----------------------|--------------------|-------------------------|-----------------------------------------|
| Vertical Accuracy     | RelHomeAlt          | fact_sys.DAlt           | Planned vs. actual altitude             |
| Mechanical Influence  | VZ                  | fact_sys.VibeZ          | Vertical motion vs. vibration           |
| Transit Efficiency    | Spd                 | fact_power.Curr         | Energy consumption per speed            |
| Estimation Trust      | Lat, Lng            | fact_est.PE, fact_est.PD| EKF vs. GPS accuracy                     |
| Command Response      | Spd                 | fact_communication.C1–C4| Pilot/autopilot impact on trajectory   |
| Energy Cost           | Spd                 | fact_power.CurrTot      | Total energy per mission distance       |
| System Stress         | Spd, VZ             | fact_sys.VibeX/Y/Z      | Phase-based mechanical stress           |

---

## 3️⃣ Summary

* All necessary metrics for NAV-based **Scorecard development** are available.
* Time-indexed `mission_time` allows precise cross-domain correlation.
* Phase-aware calculations can be applied for Takeoff, Cruise, Hover, and Landing.
* This document forms the **foundation for Intelligence Layer outputs** in the platform.