# DOMAIN SPECIFICATION: Navigation (Nav-Mart)

## 1. Objective
Analyze the relationship between **GPS reference data** and **EKF state estimation** to detect navigation drift, estimation lag, and innovation stress during flight, without modifying ArduPilot core logic.

---

## 2. Domain Scope (Non-Intrusive)
This domain operates as a **passive auditor**:
- Consumes MAVLink telemetry only.
- Does not alter control loops or estimator behavior.
- Produces reproducible analytical artifacts for post-flight review.

---

## 3. Domain Entities (`src/entities/navigation.py`)

### GpsEntity
- **Source**: `GLOBAL_POSITION_INT`
- **Role**: External reference signal.
- **Key fields**: position, velocity, timestamp (`time_boot_ms`).

### EkfEntity
- **Source**: `EKF_STATUS_REPORT`
- **Role**: Autopilot perception of state.
- **Key fields**: position variance, velocity variance, health flags.

> **Note**: GPS is treated as a **reference**, not absolute truth.

---

## 4. Temporal Weaving (`src/weaving/navigation.py`)
- GPS and EKF operate at different update rates.
- Alignment is performed using **DuckDB ASOF JOIN**.
- **Join Key**: `time_boot_ms`.
- **Purpose**: Recover the EKF state that existed at the moment a GPS fix was observed.

---

## 5. Audit Logic (`src/audit/navigation.py`)

### Success Metrics
- Horizontal position divergence < **2.0 m**.
- Velocity variance < **0.5 m/s**.
- No telemetry gaps > **200 ms**.

### Failure Indicators
- Sustained GPS–EKF divergence beyond threshold.
- Rising EKF variance while GPS remains stable.
- EKF unhealthy flags during valid GPS reception.

---

## 6. Outputs (`mart/navigation/`)
- Mission-partitioned DuckDB database.
- Parquet segments for long-term trend analysis.
- All artifacts are tagged with **Mission Tokens** for traceability.

---

## 7. Traceability
- **Core Security** → `src/core/security.py` (Identity & Signing)
- **Entities** → `src/entities/navigation.py`
- **Weaving** → `src/weaving/navigation.py`
- **Audit** → `src/audit/navigation.py`
- **Orchestration** → `src/runner/main.py`