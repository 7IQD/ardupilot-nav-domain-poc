
### Problem Statement
- GPS, EKF, and global position messages arrive at different rates
- Messages are asynchronous
- Naive joins corrupt causality

### Solution: Temporal Weaving

- **Master Clock:** `time_boot_ms`
- **Strategy:** Last Observation Carried Forward (LOCF)
- **Implementation:** DuckDB `ASOF JOIN`

**Invariant Rule**
> A GPS observation is paired with the EKF state that existed at that exact flight moment.

🚫 No interpolation
🚫 No smoothing
✅ Only recorded system knowledge

---

## 6. Canonical Schema & Units

### 6.1 Canonical Column Naming (Locked)

These names are invariant across all Nav tables:

- `latitude_deg`, `longitude_deg`
- `alt_m`, `rel_alt_m`
- `vel_x_mps`, `vel_y_mps`, `vel_z_mps`
- `heading_deg`
- `boot_time_ms`
- `vehicle_id`

---

### 6.2 Units & Scaling Rules

All unit conversion happens **before database insertion**.

| MAVLink Field | Wire Unit | Stored Column | Stored Unit |
|--------------|----------|--------------|------------|
| `lat`, `lon` | 1e-7 deg | `latitude_deg`, `longitude_deg` | degrees |
| `alt` | mm | `alt_m` | meters |
| `relative_alt` | mm | `rel_alt_m` | meters |
| `vx`, `vy`, `vz` | cm/s | `vel_*_mps` | m/s |
| `hdg` | centi-deg | `heading_deg` | degrees |

This guarantees a **clean, analysis-ready Mart**.

---

## 7. Navigation Tables

### Common Rules
- **Primary Key:** (`vehicle_id`, `boot_time_ms`)
- Deterministic inserts
- Replay-safe
- Append-only per mission segment

---

### 7.1 `nav_gps_raw`

- **Source:** `GPS_RAW_INT`
- **Purpose:** Raw sensor evidence

Additional fields:
- `gps_fix`
- `sat_count`

---

### 7.2 `nav_global`

- **Source:** `GLOBAL_POSITION_INT`
- **Purpose:** Fused navigation output

Additional fields:
- NED velocities
- Heading / yaw

---

## 8. Audit Logic

**Source File:**

### 8.1 Success Metrics

- Horizontal GPS–EKF divergence < **2.0 m**
- EKF velocity variance < **0.5 m/s**
- No telemetry gaps > **200 ms**

---

### 8.2 Failure Indicators

- Sustained divergence beyond threshold
- Rising EKF variance while GPS remains stable
- EKF unhealthy flags during valid GPS reception

All violations are **recorded, not suppressed**.

---

## 9. Quality Gates & Sanity Checks

### Hard Rejects
- `(latitude, longitude) = (0, 0)`
- Physically impossible altitude jumps

### Soft Flags
- Velocity > 50 m/s
- Heading change > 90° within 100 ms

### Structural Events
- `boot_time_ms` regression ⇒ **new flight segment**

---

## 10. Persistence & Outputs

**Location**

**Artifacts**
- Mission-partitioned DuckDB database
- Parquet segments for long-term trend analysis
- All records tagged with **Mission Tokens**

---

## 11. Determinism & Reproducibility

- Same SITL input ⇒ identical Nav-Mart output
- `reset_mart()` guarantees clean re-runs
- Safe for CI, replay, and mentor inspection

---

## 12. Traceability Matrix

| Concern | Implementation |
|------|----------------|
| Identity & Signing | `src/core/security.py` |
| Database Control | `src/core/database.py` |
| Entities | `src/entities/navigation.py` |
| Temporal Weaving | `src/weaving/navigation.py` |
| Audit Logic | `src/audit/navigation.py` |
| Orchestration | `src/runner/main.py` |

---

## 13. Relationship to Blueprint

This document **implements** the intent defined in:

**Navigation Domain Blueprint**
(High-level philosophy and analytical goals)

Together, the Blueprint and this Specification form a **complete, reviewable Nav-Mart design**.

---
