# Architecture Rationale: High-Speed “O-Level” Telemetry Ingress

## 1. Executive Summary
This document defines the **O-Level telemetry ingress architecture** for MAVLink data sourced from SITL or multi-vehicle systems.
The design guarantees **non-blocking, real-time ingestion** with explicit loss visibility, strong data lineage, and **crash-safe persistence**, while deferring all semantic decisions to downstream layers.

---

## 2. Core Components & Logic

### A. Ingress Firewall: Bounded Queue 🛡️
- **Implementation:** `queue.Queue` with a fixed `maxsize`
- **Overflow Policy:** Drop **oldest** packet
- **Rationale:**
  In high-rate telemetry, *current state outweighs stale state*.
  This prevents memory exhaustion and ensures the Listener thread remains completely independent of database latency or stalls.
- **Observability:**
  A `dropped_packet_counter` records all intentional loss for system health and auditability.

---

### B. Atomic Ingest Unit (`meta_pckg`) 🧬
- **Structure:**
  `{ raw_bytes, msg_id, sys_id, timestamp, inode }`
- **Principle:**
  Metadata is **bonded to raw binary data at the moment of arrival**.
- **Benefit:**
  Preserves ground truth regardless of downstream delays, batching, or failures.

---

### C. Virtual Inode (Lineage Anchor) 📂
- **Format:**
  `<session_id>/<segment_id>/<sequence_no>`

| Component | Meaning |
|---|---|
| `session_id` | Unique identifier for a mission or SITL run |
| `segment_id` | File-rotation boundary (e.g., 100 MB segments) |
| `sequence_no` | Monotonic arrival order within the session |

- **Rationale:**
  Enables deterministic recovery, fast SQL joins, and unbroken traceability across file rotation and WAL replay.

---

## 3. Session Lifecycle & Failure Semantics 🏁

| Scenario | Mechanism | Outcome |
|---|---|---|
| **Graceful Shutdown** | Listener emits a `None` poison pill. Worker drains queue, flushes final batch, commits, and closes DB. | Clean close with an explicit session-end marker |
| **Abrupt Termination** | DuckDB Write-Ahead Logging (WAL) | No corruption; only uncommitted in-memory packets are lost |

This design explicitly favors **real-time ingestion safety over last-packet durability**.

---

## 4. Implementation & Validation Roadmap

### Phase 1: Ingress Conduit 🐍
- Implement bounded queue with explicit drop policy
- Run Listener (producer) and Worker (consumer) in separate threads

### Phase 2: Bronze Storage 🗄️
- Define DuckDB Bronze schemas (append-only, schema-on-read)
- Route packets into categorized bins (Sensors, Controllers, etc.) using inode linkage

### Phase 3: Stress & Failure Validation 🧪
- **Artificial Lag Test:** Introduce `time.sleep()` in the Worker
- **Pass Criteria:**
  - Listener never blocks
  - Packets continue to arrive
  - `dropped_packet_counter` increments
  - Process remains responsive

---

## 5. Change Management
Any deviation from this architecture must be recorded in `CHANGELOG.md`, including a justification describing its impact on:
- real-time behavior
- data integrity
- lineage guarantees
- failure recovery semantics

---

**Status:**
Finalized for Platform POC.
All domain frameworks and marts must consume this ingress contract as-is.
