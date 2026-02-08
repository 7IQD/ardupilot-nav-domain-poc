# 🛸 Nav Mart Contract v1.0

## 1. Lineage & Boundary
- **Domain:** Navigation (inferred by physical partitioning)
- **Upstream (Silver):** `bin/vault/warehouse/nav_master.parquet`
- **Downstream (Gold):** `bin/vault/gold/fact_nav_precision.parquet`

This contract defines the **exclusive responsibility boundary** of the Nav Data Mart.
Consumers MUST NOT read Silver directly.

---

## 2. Ingress Requirements (Silver)

The refinery expects the following **minimum schema** from the Silver warehouse.

| Column | Type | Description |
|------|------|-------------|
| `inode` | INT64 | Monotonic sequence ID (trace anchor) |
| `best_ts` | FLOAT64 | Unified timestamp (milliseconds) |
| `mavpackettype` | STRING | MAVLink source discriminator (e.g. `GPS_RAW_INT`, `GLOBAL_POSITION_INT`) |
| `lat` | INT32 | Raw latitude (WGS84 × 1e7) |
| `lon` | INT32 | Raw longitude (WGS84 × 1e7) |

### Silver Guarantees
- Rows are **append-only**
- `inode` is **globally unique**
- Timestamp ordering is **non-decreasing**
- Data is domain-pure (Navigation only)

Violation of these guarantees allows the refinery to **fail fast**.

---

## 3. Egress Guarantees (Gold)

The refinery emits a **read-optimized fact table** for HUD / analytics consumers.

| Column | Type | Description |
|------|------|-------------|
| `inode` | INT64 | Original inode for lineage |
| `timestamp` | FLOAT64 | Trigger timestamp (`best_ts`) |
| `precision_error_m` | FLOAT64 | Calculated positional drift (meters) |

### Gold Guarantees
- One row per qualifying inode
- Deterministic output for identical Silver input
- No mutation of Silver data
- Gold represents **refined truth**, not raw telemetry

---

## 4. Operational Policy
- **Granularity:** 1:1 mapping for inodes where both GPS and EKF telemetry coexist
- **Latency:** Eventual consistency (refinery pulse-based)
- **Retention:** Gold accumulates the full refined flight history

---

## 5. Explicit Non-Goals
- No filtering or smoothing policy defined here
- No real-time guarantees
- No control-loop coupling
- No visualization or HUD logic

---

## 6. Ownership
- **Silver correctness:** Engine-1 (Ingest / Materialization)
- **Gold correctness:** Data Mart Engine
- **Consumption:** Read-only, Gold-only
