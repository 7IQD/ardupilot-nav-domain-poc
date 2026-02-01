# Platform System Design — v1.0

## 1. Purpose
This document defines the **end-to-end system design** of the platform.
It describes how telemetry flows from ingestion to domain marts, while preserving real-time safety, data lineage, and analytical determinism.

It does **not** define:
- domain-specific logic (Navigation, Control, UI)
- field semantics or units (see Canonical Data Map)

---

## 2. System Design Principles

- **Non-Blocking by Construction**
  No component upstream may block on downstream computation or storage.
- **Delayed Decision**
  Raw data is captured first; meaning is assigned later.
- **Deterministic Replay**
  Identical inputs must always produce identical analytical outputs.
- **Explicit Loss**
  Any data loss is intentional, measurable, and surfaced.
- **Layered Responsibility**
  Each layer has a single, auditable role.

---

## 3. High-Level Architecture

[MAVLink Source / SITL]
|
v
[O-Level Ingress Layer]
|
v
[Bronze Storage (Raw, WAL)]
|
v
[Silver Weaving / Normalization]
|
v
[Domain Marts (Nav, Control, etc.)]
|
v
[Reports / UI / Audit]


Each layer consumes a **contract**, not an implementation.

---

## 4. Layer Responsibilities

### 4.1 O-Level Ingress (Platform)
- Receives MAVLink frames
- Guarantees non-blocking reception
- Attaches canonical identity (`inode`, timestamps)
- Persists raw data safely

**Reference:**
`PLATFORM_O_LEVEL_INGRESS_ARCHITECTURE.md`

---

### 4.2 Bronze Storage
- Append-only, schema-on-read
- Stores raw bytes + minimal metadata
- Uses DuckDB with WAL for crash safety
- No scaling, no joins, no interpretation

Bronze answers:
> *“What exactly arrived?”*

---

### 4.3 Silver Layer (Weaving & Normalization)
- Converts raw integers to physical units
- Aligns signals using `time_boot_ms`
- Applies LOCF via ASOF JOIN
- Produces analysis-ready views

Silver answers:
> *“What did the system know at that moment?”*

---

### 4.4 Domain Marts
Each domain (Navigation, Control, Power, etc.):
- Consumes Silver views
- Applies domain logic and metrics
- Produces evidence tables and diagnostics

Example:
- Navigation Mart → EKF health, drift, estimator stress

---

### 4.5 Presentation & Audit
- Dashboards
- Reports
- Offline diagnostics
- Reviewer and safety audits

All outputs remain traceable to:
- session
- inode
- raw packet

---

## 5. Identity & Time Model

### Identity
- All records are traceable via **Virtual Inode**
- Inode structure:

### Time
- **Primary clock:** `time_boot_ms`
- Wall-clock time is secondary and optional
- No interpolation at platform level

---

## 6. Failure & Recovery Semantics

| Failure Type | Handling |
|---|---|
| DB stall | Ingress continues, queue absorbs |
| Queue overflow | Oldest packets dropped, counted |
| Process crash | WAL guarantees no corruption |
| Power loss | Last committed batch recoverable |

The platform favors **real-time integrity over last-packet durability**.

---

## 7. Determinism Guarantees

The system guarantees:
- Same SITL logs → same marts
- Same joins → same results
- No hidden state between runs

Provided that:
- Canonical Data Map is unchanged
- Mart logic is versioned

---

## 8. Relationship to Other Documents

| Document | Role |
|---|---|
| `PLATFORM_CANONICAL_DATA_MAP.md` | Defines data meaning |
| `PLATFORM_O_LEVEL_INGRESS_ARCHITECTURE.md` | Defines ingress behavior |
| This document | Defines system wiring |
| `Navigation/Blueprint/*` | Defines domain questions |

---

## 9. Change Control

Any change affecting:
- layering
- data flow
- failure semantics
- determinism guarantees

must:
1. Update this document
2. Be logged in `CHANGELOG.md`
3. Include rationale and risk assessment

---

**Status:**
Frozen for Platform POC.
All domain implementations must conform to this system design.
