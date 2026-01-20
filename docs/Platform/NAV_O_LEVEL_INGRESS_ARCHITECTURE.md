# Architecture Rationale: High-Speed “O-Level” Telemetry Ingress

## 1. Executive Summary
This architecture defines a **non-blocking telemetry ingress pipeline** for MAVLink data from SITL or multi-vehicle systems.
The primary goal is to **guarantee real-time reception without backpressure**, while preserving full data lineage and ensuring crash-safe persistence.

---

## 2. Core Design Elements

### A. Ingress Firewall: Bounded Queue 🛡️
- **Implementation:** Fixed-size `queue.Queue(maxsize=N)`
- **Overflow Policy:** Drop **oldest** packet
- **Reasoning:** In high-rate telemetry, *current state* is more valuable than stale data.
  This prevents memory exhaustion and keeps the Listener fully isolated from database latency.
- **Observability:** A `dropped_packet_counter` records all intentional loss for health monitoring.

---

### B. Atomic Ingest Unit (`meta_pckg`) 🧬
- **Structure:**
  `{ raw_bytes, msg_id, sys_id, timestamp, inode }`
- **Principle:** Raw data and metadata are **bound at the moment of arrival**.
- **Benefit:** Ensures “ground truth” is preserved, independent of downstream processing delays or failures.

---

### C. Virtual Inode (Lineage Anchor) 📂
- **Format:**
  `<session_id>/<segment_id>/<sequence_no>`

| Field | Purpose |
|---|---|
| `session_id` | Identifies a single mission / SITL run |
| `segment_id` | Tracks file rotation (e.g., every 100 MB) |
| `sequence_no` | Enforces strict arrival order |

- **Rationale:**
  Enables deterministic recovery, fast SQL joins, and unbroken lineage across rotated files and WAL replays.

---

## 3. Session Lifecycle & Failure Semantics 🏁

| Scenario | Mechanism | Result |
|---|---|---|
| **Graceful Shutdown** | Listener emits a `None` poison pill. Worker drains queue, flushes final batch, commits, and closes DB. | Clean close with an explicit session-end marker |
| **Abrupt Termination** | DuckDB Write-Ahead Logging (WAL) | No corruption; only uncommitted in-memory packets are lost |

This explicitly favors **real-time safety over last-packet durability**, by design.

---

## 4. Implementation & Validation Plan

### Phase 1: Ingress Conduit 🐍
- Implement bounded queue with explicit drop policy
- Run Listener (producer) and Worker (consumer) in separate threads

### Phase 2: Bronze Storage 🗄️
- Define DuckDB Bronze tables
- Route packets to categorized bins (Sensors, Controllers, etc.) using Inode linkage

### Phase 3: Stress & Failure Validation 🧪
- **Artificial Lag Test:** Insert `time.sleep()` in Worker
- **Pass Criteria:**
  - Listener never blocks
  - Packets continue to arrive
  - `dropped_packet_counter` increments
  - Process remains responsive

---

## 5. Change Control
Any deviation from this architecture must be recorded in `CHANGELOG.md`, including a justification describing its impact on **real-time behavior**, **data integrity**, or **failure recovery guarantees**.
