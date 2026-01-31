# GSoC 2026: SITL Analytical Observability Engine

## A Multi-Domain Framework for Causal Analysis

---

## Write-Up

**Objective:**
Enable multi-domain causal analysis of ArduPilot SITL by aligning asynchronous telemetry into **analytical Evidence Rooms** using **DuckDB-powered Data Marts**.

**Scope & Deliverable:**
* Capture, normalize, and denormalize MAVLink telemetry in a non-intrusive side-car layer.
* Deploy a **Live-Chain pipeline** with interactive analytics for multi-domain exploration.
* Support **temporal As-Of Joins** for precise signal synchronization across disparate frequencies.

**Architecture Overview:**
* **Upstream (Pipe / Clerks):** Immutable JSON capture of MAVLink streams. The modular **Clerk** abstraction allows new domains to be added without altering the core pipeline.
* **Canonical Warehouse (DuckDB):** High-performance denormalized tables utilizing vectorized As-Of Joins for sub-millisecond signal alignment.
* **Orchestrator (Ingress Hub):** Consolidates Clerk queues and manages data sequencing via a restart-persistent **inode ledger**.
* **Evidence Rooms:** Materialized analytical views (e.g., GPS + EKF + Battery) providing synchronized "snapshots" for causal "Why" analysis.

**Motivation:**
Traditional GCS focus on **real-time telemetry (OLTP)**, which excels at monitoring but limits historical causal analysis. This engine enables **DIKW traversal** (Data → Information → Knowledge → Wisdom) by providing the "How" and "Why" behind vehicle behavior.

**PoC Success:**
A Navigation domain baseline has been established on the `engine3-dev` branch. The system successfully aligned **805 high-frequency Nav points** (GPS at 5 Hz and EKF at 50 Hz) via the Live-Chain, with zero data loss during ingestion.

**Impact:**
Facilitates expert causal analysis across Navigation, Health, and Safety domains. The architecture is **non-intrusive**, ensuring no impact on flight-critical SITL logic while remaining scalable for future domains (Power, Swarm).

---
<div style="page-break-after: always;"></div>

## Architecture Diagram

```
              ```
                ┌─────────────┐
                │ MAVLink SITL│
                └─────┬──────┘
                      │ Live telemetry (Non-intrusive)
        ┌──────────────┼──────────────┐
        │              │              │
┌──────▼───────┐ ┌────▼───────┐ ┌────▼───────┐
│  NavClerk    │ │ HealthClerk│ │ SafetyClerk│
│ (Nav Domain) │ │  (Health)  │ │  (Safety)  │
└──────┬───────┘ └────┬───────┘ └────┬───────┘
       │ Queue A      │ Queue B      │ Queue C
       └──────┬───────┴──────────────┘
              │
       ┌──────▼─────────────────────┐
       │   Orchestrator Hub         │
       │ (Ingress & inode Tracking) │
       └──────┬─────────────────────┘
              │
       Canonical DB (DuckDB)
       ┌────────────────────────────┐
       │ Evidence Room (ASOF Joins) │
       │ ┌──────────┐ ┌──────────┐  │
       │ │ nav_gps  │ │ sys_batt │  │
       │ └──────────┘ └──────────┘  │
       └──────────┬─────────────────┘
                  │
                  ▼
       📝 Meta Ledger (last_inode)

```

</div>