# O-Level Telemetry Ingress Architecture Charter

## 1. Purpose

This charter formally freezes the **O-Level Telemetry Ingress Architecture** for for all telemetry domains (Navigation, Health, Safety, Swarm, and future domains). The objective is to guarantee **loss-tolerant, non-blocking, high-rate MAVLink ingestion** while preserving **full data lineage** from reception to persistence.

This document is the **authoritative planning-level reference**. Its primary role is to **prevent scope creep**, enforce architectural invariants, and protect real-time ingress behavior from downstream complexity.

---

## 2. Architectural Scope (IN-SCOPE)

The architecture strictly covers the flow from **byte reception to crash-safe storage**:

* **Listener 📩**
  Raw MAVLink byte reception and creation of the **Atomic Envelope** at first contact.

* **Routing 🚦**
  MsgID-based **Domain_Decoder registration**. Only registered traffic is routed.

* **Queuing ⏳**
  Bounded, non-blocking queues per domain to prevent system poisoning and backpressure.

* **Persistence 🦆**
  Domain-specific decoding and commitment to DuckDB (Bronze / Domain Marts).

* **Audit 📖**
  Post-session reconciliation and ledger-based integrity verification.

---

## 3. Explicit Non-Goals (OUT-OF-SCOPE)

To preserve **KISS** and protect ingress guarantees, the following are **explicitly excluded**:

* Real-time control-loop feedback
* Cross-domain coupling or decoder chaining
* ML, inference, or predictive logic during ingress
* UI, dashboards, or visualization layers

Any proposal introducing these concerns into O-Level ingress constitutes a **charter violation**.

---

## 4. Frozen Architectural Invariants

The following principles are **non-negotiable**:

1. **Listener Isolation**
   The Listener must never block on decoding, queuing, or storage.

2. **Atomic Envelope**
   Raw bytes and metadata are bound at first contact and never separated.

3. **Bounded Queues** 📉
   Overflow drops the **oldest** packets; loss is observable and recorded.

4. **Domain Independence**
   Each domain operates as an isolated ledger line with no runtime dependency on others.

5. **Post-Session Truth**
   Integrity is asserted via reconciliation, not runtime blocking or coordination.

---

## 5. Ledger & Session Integrity Model

Each domain maintains an independent **traffic ledger**.

A session is considered **successfully closed** only if:

> **Listener Envelope Count == Total Committed Rows across all domain tables**

Discrepancies are surfaced as audit findings, never hidden or corrected inline.

This model provides a **chain-of-custody guarantee** from first inode to final commit.

---

## 6. Change Control

Any change that:

* Introduces blocking behavior
* Breaks envelope lineage
* Alters queue semantics
* Adds cross-domain dependency

Requires a **formal revision of this charter** and explicit re-approval.

---




