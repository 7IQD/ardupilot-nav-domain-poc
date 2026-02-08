# 🛰️ Communication Mart Contract v1.0

## 1. Lineage & Boundary

* **Domain:** Communication (fullfledged domain)
* **Upstream (Silver):** `bin/vault/comms/warehouse/comms_master.parquet`
* **Downstream (Gold):** `bin/vault/comms/gold/fact_comms_quality.parquet`

This contract defines the **exclusive responsibility boundary** of the Comms Data Mart.
Consumers MUST NOT read Silver directly.

---

## 2. Ingress Requirements (Silver)

The refinery expects the following **minimum schema** from the Silver warehouse.

| Column          | Type    | Description                                                |
| --------------- | ------- | ---------------------------------------------------------- |
| `inode`         | INT64   | Monotonic sequence ID (trace anchor)                       |
| `best_ts`       | FLOAT64 | Unified timestamp (milliseconds)                           |
| `mavpackettype` | STRING  | MAVLink message type (e.g., `RADIO_STATUS`, `LINK_STATUS`) |
| `rssi`          | INT32   | Received Signal Strength Indicator (dBm)                   |
| `latency_ms`    | FLOAT64 | Measured message latency                                   |
| `drop_count`    | INT32   | Number of packet drops since last message                  |
| `jitter_ms`     | FLOAT64 | Optional jitter metric                                     |

### Silver Guarantees

* Rows are **append-only**
* `inode` is **globally unique**
* Timestamp ordering is **non-decreasing**
* Data is domain-pure (Comms only)

Violation of these guarantees allows the refinery to **fail fast**.

---

## 3. Egress Guarantees (Gold)

The refinery emits a **read-optimized fact table** for analytics and dashboard consumers.

| Column            | Type    | Description                       |
| ----------------- | ------- | --------------------------------- |
| `inode`           | INT64   | Original inode for lineage        |
| `timestamp`       | FLOAT64 | Trigger timestamp (`best_ts`)     |
| `rssi_avg`        | FLOAT64 | Rolling average RSSI              |
| `packet_loss_pct` | FLOAT64 | Calculated packet loss percentage |
| `latency_avg_ms`  | FLOAT64 | Average latency over N samples    |
| `jitter_avg_ms`   | FLOAT64 | Average jitter                    |

### Gold Guarantees

* One row per qualifying inode
* Deterministic output for identical Silver input
* No mutation of Silver data
* Gold represents **refined truth**, not raw telemetry

---

## 4. Operational Policy

* **Granularity:** 1:1 mapping for inodes where meaningful signal & telemetry exist
* **Latency:** Eventual consistency (refinery pulse-based)
* **Retention:** Gold accumulates the full refined communication history

---

## 5. Explicit Non-Goals

* No filtering or smoothing policy defined here
* No real-time guarantees
* No control-loop coupling
* No visualization or dashboard logic (handled elsewhere)

---

## 6. Ownership

* **Silver correctness:** Engine-1 (Ingest / CommsArchitect)
* **Gold correctness:** Data Mart Engine (ComRefinery)
* **Consumption:** Read-only, Gold-only

---


