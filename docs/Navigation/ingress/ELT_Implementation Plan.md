# ELT_Implementation Plan

## **Final Implementation Plan (Locked)**

This document formalizes the **final, production-grade implementation plan** for extending the existing ingress and plumbing into a fully lineage-safe **Bronze–Silver–Gold** data system.

This is a **lock-stock-and-barrel** design: once adopted, only additive changes are allowed.

---

## **1. Architectural Intent (Non‑Negotiable)**

**Primary Goal:**
Preserve real-time safety while enabling deterministic replay, analytics, and expert inference.

**Core Principle:**

> *Position data once. Shape it once. Derive insight many times.*

---

## **2. Canonical Data Contract**

### **Bronze (🥉 — Stock / Barrel In)**

**Purpose:** Immutable capture of ground truth

* Raw MAVLink frames or extracted JSON payloads
* Append-only
* No joins, no interpretation, no filtering

**Primary Key (Data Positioning):**

```
(inode, time_ms | time_us)
```

**Rules:**

* Written exactly once
* Never updated
* Never cross-domain

---

### **Silver (🥈 — Positioned & Pactised)**

**Purpose:** Canonical, domain-scoped shaping

* Derived from Bronze only
* Domain-isolated (Nav, Health, Safety, etc.)
* Deterministic SQL transforms

**Primary Key (Preserved):**

```
(inode, time_ms | time_us)
```

**Rules:**

* No cross-domain joins
* No fan-out writes
* SQL logic only (no Python transforms)

Silver is the **only layer allowed to write structured tables**.

---

### **Gold (🥇 — Expert Surface)**

**Purpose:** Analytics, dashboards, inference

* Read-only views
* Cross-domain joins allowed
* Joins occur via **inode lineage**

**Rules:**

* No persistence side effects
* No ingestion coupling
* Views may live in separate schemas

---

## **3. Virtual Inode (Lineage Anchor)**

```text
<session_id>/<segment_id>/<sequence_no>
```

| Component   | Responsibility             |
| ----------- | -------------------------- |
| session_id  | Mission / SITL / Swarm run |
| segment_id  | WAL or file rotation       |
| sequence_no | Arrival ordering guarantee |

The inode is the **end-to-end lineage spine** across Bronze → Silver → Gold.

---

## **4. Ingress Responsibilities (Already Implemented)**

The existing ingress stack remains **unchanged**.

### **Ingress Guarantees**

* Non-blocking listener
* msgid → queue routing
* Immutable `meta_pckg`
* Bounded queues with drop visibility

Ingress **does not know** about Bronze/Silver/Gold.

---

## **5. Storage Responsibilities**

### **Bronze Writes**

* Raw envelopes (`meta_pckg` or extracted JSON)
* Stored with inode + time
* DuckDB WAL-backed

### **Silver Materialization**

* Executed via **precompiled SQL**
* Triggered:

  * On batch completion, or
  * On controlled replay windows

No streaming writes into Silver.

---

## **6. Failure Semantics (Locked)**

| Scenario      | Outcome             |
| ------------- | ------------------- |
| Decoder crash | In-memory loss only |
| Process kill  | WAL-safe Bronze     |
| SQL failure   | Silver untouched    |
| Gold error    | No ingestion impact |

Real-time safety **always wins**.

---

## **7. Verified Current State (Reference)**

The following structures are **validated and correct**:

### **Silver Tables**

* `silver.gps_observation`
* `silver.nav_state`

### **Gold Views**

* `gold.nav_context`

Primary keys and schemas are correctly aligned.

---

## **8. Canonical File Structure (Extension)**

This extends the **existing ingress and plumbing**, without breaking changes.

```
src/
├─ ingress/                # Already implemented
│  ├─ listener.py
│  ├─ envelope.py
│  ├─ ingress_switch.py
│  └─ domain_decoder.py
│
├─ storage/
│  ├─ bronze_writer.py     # Raw envelope persistence
│  ├─ silver_materializer.py
│  └─ duckdb_connection.py
│
├─ marts/
│  ├─ nav/
│  │  ├─ silver.sql        # Deterministic transforms
│  │  └─ gold_views.sql
│  ├─ health/
│  └─ safety/
│
├─ schemas/
│  ├─ bronze.sql
│  ├─ silver.sql
│  └─ gold.sql
│
├─ replay/
│  └─ replay_controller.py
│
└─ CHANGELOG.md
```

---

## **9. Execution Sequence (Operational)**

1. **Ingress running** → envelopes captured
2. **Bronze populated** (inode-positioned)
3. **Silver materialization invoked** (SQL only)
4. **Gold views queried** by experts

No layer calls the next directly.

---

## **10. Change Control (Strict)**

Any modification must state impact on:

* Real-time safety
* Domain isolation
* Lineage guarantees
* Failure semantics

If any invariant is weakened, the change is rejected.

---

## ✅ Final Status

**Architecture: LOCKED**

This document is now the **canonical physical implementation plan** for O‑Level ingress + Bronze–Silver–Gold analytics.
