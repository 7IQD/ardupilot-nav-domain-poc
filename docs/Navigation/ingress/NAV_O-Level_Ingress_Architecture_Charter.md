# **O‑Level Ingress Architecture – Canonical Document**

## **1. Executive Summary**

This document defines the **O‑Level (Operational-Level) telemetry ingress architecture** for MAVLink streams (SITL, single-vehicle, multi-vehicle swarms).

**Design Goals:**

* Non-blocking, real-time packet reception
* Hard **msgid-based isolation** per domain
* Full **data lineage and replay fidelity**
* Crash-safe, with real-time safety prioritized over last-packet durability

Implementation must conform to this canonical design.

---

## **2. Design Invariants (Non-Negotiable)**

1. Listener must never block on downstream logic
2. Routing is strictly **msgid → queue**
3. Only raw envelopes traverse queues (no decoded objects)
4. Backpressure is isolated per domain
5. Data loss is **explicit, bounded, and observable**
6. Real-time safety > last-packet durability

---

## **3. Core Architecture Elements**

### **A. Routing Layer — The Switch 🚦**

**Components:**

* Listener
* Domain Decoders (msgid → domain queue)

**Responsibilities:**

* **msgid → queue routing**
* No parsing or state management
* No persistence

**Startup Registration:**

```python
msgid → [domain queues]
```

Guarantees decoders never see unregistered traffic.

---

### **B. Logic Layer — The Brain 🧠**

**Components:**

* NavDecoder
* HealthDecoder
* SafetyDecoder
* Future domain decoders

**Decoder Flows:**

1. **Upstream:** lightweight state/delta → Pilot/UI
2. **Downstream:** full-fidelity envelope → analytics, replay, inference

**Rule:** No decoder performs routing.

---

## **4. Ingress Firewall: Bounded Queues 🛡️**

* **Implementation:** `queue.Queue(maxsize=N)` per domain
* **Overflow Policy:** drop oldest envelope
* **Backpressure Scope:** domain-local

**Observability:**

* Per-queue drop counters (health metrics, not errors)
* Prevents memory exhaustion and protects real-time safety

---

## **5. Atomic Ingest Envelope (`meta_pckg`) 🧬**

```python
{
    raw_bytes,         # Raw MAVLink packet
    msg_id,            # Packet ID
    sys_id,            # Source system
    timestamp_ingress, # Arrival time
    inode              # Virtual lineage anchor
}
```

**Rules:**

* Created **once** at ingress
* Immutable
* Only envelopes traverse queues
* Preserves ground truth and performance

---

## **6. Virtual Inode (Lineage Anchor) 📂**

```text
<session_id>/<segment_id>/<sequence_no>
```

| Field       | Purpose                 |
| ----------- | ----------------------- |
| session_id  | Mission/SITL/swarm run  |
| segment_id  | File or WAL rotation    |
| sequence_no | Arrival order guarantee |

**Inode is primary lineage key** across all data marts.

---

## **7. Failure Semantics 🏁**

| Scenario           | Mechanism             | Outcome                            |
| ------------------ | --------------------- | ---------------------------------- |
| Graceful shutdown  | Poison pill per queue | Clean drain & commit               |
| Abrupt termination | DuckDB WAL            | No corruption; in-memory loss only |

**Design choice:** intentional and predictable.

---

## **8. Canonical Architecture Diagram**

```text
Listener
   │
   ├── msgid → Nav Queue ──> Domain_Decoder(Nav) ──> NavDecoder
   │                               │
   │                               ├─ Upstream → Pilot/UI
   │                               └─ Downstream → DuckDB (Nav Mart)
   │
   └── msgid → System Queue ──> Domain_Decoder(System)
                                   ├─ HealthDecoder → DuckDB + UI
                                   └─ SafetyDecoder → DuckDB + Alerts
```

---

## **9. Canonical File Structure**

```
src/
 ├─ ingress/
 │   ├─ listener.py
 │   ├─ envelope.py
 │   └─ domain_decoder.py
 │
 ├─ domains/
 │   ├─ nav/nav_decoder.py
 │   ├─ health/health_decoder.py
 │   └─ safety/safety_decoder.py
 │
 ├─ storage/duckdb_writer.py
 └─ CHANGELOG.md
```

**Notes:**

* Ingress logic remains **protocol-agnostic**, routing raw envelopes.
* Domain decoders implement **upstream + downstream flows**.
* Queues enforce **msgid isolation and backpressure**.

---

## **10. Change Control**

* Any change must be logged in `CHANGELOG.md` with impact on:

  * Real-time behavior
  * Domain isolation
  * Data lineage
  * Failure guarantees

---

