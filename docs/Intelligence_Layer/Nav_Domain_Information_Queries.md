# 🏛️ NAV Domain Information Layer
---

## 1️⃣ Intra-Domain Insights (Within `fact_nav`)

*Information derived solely from the Navigation Fact Table.*

| Information Goal         | Source Field(s)         | DuckDB SQL Logic                       | Remarks                                                           |
| ------------------------ | ----------------------- | -------------------------------------- | ----------------------------------------------------------------- |
| **Vertical Stability**   | `RelHomeAlt`            | `STDDEV(RelHomeAlt)`                   | Std. dev. for altitude consistency; hover/landing precision.      |
| **Horizontal Velocity**  | `Spd`                   | `AVG(Spd), MAX(Spd)`                   | Instantaneous and mean speed; transit efficiency.                 |
| **Vertical Performance** | `VZ`                    | `MAX(ABS(VZ))`                         | Climb/descent rates; correlate with thrust effort.                |
| **Signal Integrity**     | `NSats, HDop`           | `AVG(NSats), MAX(HDop)`                | GPS reliability; high HDop / low NSats indicates potential drift. |
| **Trajectory Volume**    | `Lat, Lng, RelHomeAlt`  | `MAX(Lat)-MIN(Lat), MAX(Lng)-MIN(Lng)` | 3D flight path; mission footprint and plan deviation.             |
| **Mission Timeline**     | `mission_time, wall_ns` | `MAX(mission_time)-MIN(mission_time)`  | Temporal alignment for all phases and cross-domain events.        |
| **Attitude State**       | `Q1-Q4`                 | Raw fields for orientation             | Used for motion compensation and rotational analysis.             |

## 2️⃣ Inter-Domain Insights (NAV + Other Domains)

*Information derived by stitching NAV data with other domain Fact Tables via `mission_time`.*

| Information Goal       | NAV Field(s) | External Domain Field(s)   | DuckDB SQL Logic / Insight                                           |
| ---------------------- | ------------ | -------------------------- | -------------------------------------------------------------------- |
| **Vertical Accuracy**  | `RelHomeAlt` | `fact_sys.DAlt`            | `ABS(nav.RelHomeAlt - sys.DAlt)` – Detect hover/altitude deviations. |
| **Mechanical Stress**  | `VZ`         | `fact_sys.VibeZ`           | Vibration correlation during vertical motion.                        |
| **Transit Efficiency** | `Spd`        | `fact_power.Curr`          | `power.Curr / NULLIF(nav.Spd,0)` – Energy required per m/s.          |
| **Estimation Trust**   | `Lat, Lng`   | `fact_est.PE, fact_est.PD` | Compare GPS position vs EKF predictions; drift detection.            |
| **Command Response**   | `Spd`        | `fact_communication.C1-C4` | Control loop effectiveness; pilot/autopilot influence.               |
| **Energy Cost**        | `Spd`        | `fact_power.CurrTot`       | Total battery consumption per distance.                              |
| **System Stress**      | `Spd, VZ`    | `fact_sys.VibeX/Y/Z`       | Phase stress; mechanical peaks during cruise vs hover.               |



