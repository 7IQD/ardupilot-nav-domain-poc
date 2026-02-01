# PLATFORM O-Level Telemetry Ingress Architecture – Rationale & Implementation Guide

> **Alignment Notice**
> This document is a **design rationale and implementation guide**.
> All mechanisms described herein **strictly conform to** the
> **PLATFORM_O_LEVEL_INGRESS_ARCHITECTURE_CHARTER**, which is the **sole authoritative specification**.
> In case of conflict, the Charter **always prevails**.

---

## 1. Purpose of This Document

This document explains the **engineering rationale**, trade-offs, and validation strategy behind the **Platform O-Level Telemetry Ingress Architecture**.

It exists to:

* Preserve **design intent**
* Prevent re-litigation of settled decisions
* Guide correct implementation sequencing
* Support code reviews and onboarding

It does **not** introduce new architecture, scope, or guarantees.

---

## 2. Platform Ingress Flow (Context)

As defined by the Platform Charter, the O-Level ingress flow is:

**Listener → Atomic Envelope → Domain Toll Booth → Domain Queue → Domain Decoder → DuckDB → Session Ledger**

This document explains *why* each stage behaves the way it does.

---

## 3. Domain Toll Booth: Bounded Queue Rationale 🛡️

### Charter Alignment

* Mechanism: **Per-domain bounded queue**
* Policy: **Drop oldest on overflow**
* Guarantee: **Listener isolation**

### Why This Design

* Telemetry ingress is bursty and unbounded by nature
* Blocking the Listener is the single highest-risk failure mode
* Dropping stale packets preserves **current system truth**

### Observability

* Every drop increments a **domain-level counter**
* Loss is explicit, measurable, and auditable

This enforces *controlled loss* rather than uncontrolled backpressure.

---

## 4. Atomic Envelope (`meta_pckg`) 🧬

### Charter Alignment

* Raw bytes and metadata are bound **at first contact**
* The envelope is immutable downstream

### Rationale

* Guarantees **ground truth preservation**
* Enables delayed decoding, replay, and forensic analysis
* Decouples ingress correctness from downstream latency

The envelope is the **unit of custody** throughout the system.

---

## 5. Platform Inode: Session Lineage Anchor 📂

### Charter Alignment

* Format: `<session_id>/<segment_id>/<sequence_no>`
* Created at ingress, closed at persistence

### Why This Matters

* Enforces strict arrival ordering
* Enables deterministic recovery after crashes
* Allows fast joins across rotated files and DuckDB tables

The inode is the **spine of the session ledger**.

---

## 6. Session Lifecycle & Failure Semantics 🏁

### Graceful Shutdown

* Listener emits a poison pill
* Workers drain queues
* Final batch committed
* Session closed explicitly

### Abrupt Termination

* DuckDB WAL guarantees consistency
* Only in-memory, uncommitted envelopes may be lost

This intentionally prioritizes **real-time safety over last-packet durability**.

---

## 7. Ledger & Reconciliation Model 📖

Each domain maintains an independent **ledger line**.

A session is considered **valid** if:

> **Listener Envelope Count == Total Committed Rows across all domain tables**

Mismatches are surfaced as audit findings, never masked or corrected inline.

This provides a **chain-of-custody guarantee** from first inode to last inode.

---

## 8. Implementation & Validation Strategy

### Phase 1: Listener & Envelope

* Raw byte reception
* Atomic envelope creation
* Zero blocking guarantees

### Phase 2: Toll Booth Routing

* MsgID-based registration
* Domain queue enforcement
* Drop observability

### Phase 3: Persistence & Audit

* DuckDB Bronze tables
* Inode-linked commits
* Session reconciliation report

### Stress Test Criteria

* Artificial consumer lag
* Listener remains responsive
* Drops recorded
* No memory growth

---

## 9. Change Discipline

Any proposal that:

* Alters queue semantics
* Introduces blocking paths
* Breaks inode lineage
* Adds cross-domain dependency

Must be evaluated **against the Platform Charter** and rejected or escalated accordingly.

---

> *“The Charter defines what must never change.
> This document explains why it was designed that way.”*
