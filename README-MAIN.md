> 📘 This document contains the full technical and operational details.
> Start with `README.md` for a concise overview.

# ArduPilot Nav-Mart
### **Multi-Domain Analytics & Evidence Platform (Navigation POC)**

Navigation-domain Proof of Concept for a **non-intrusive, evidence-driven observability pipeline** over ArduPilot SITL / logs.

This repository demonstrates a thin but complete vertical slice of a proposed **GSoC 2026** project: capturing, aligning, analyzing, and *freezing* navigation telemetry (GPS / EKF) to support causal reasoning — **without modifying ArduPilot core behavior**.

---

## 1. Executive Summary (WHY)
Modern autopilot systems expose rich telemetry but lack a **reproducible, reviewable evidence trail** for engineering insight. This project converts transient telemetry into a **professional engineering record** by combining:
* **Deterministic data ingestion**
* **Domain-aware analytical pipelines**
* **Human-validated evidence capture**

The Navigation domain serves as the **reference implementation**.

---

## 2. Research & Vision Context (Design Intent)

### 2.1 Horizontal Architecture (The Platform)
Nav-Mart is designed as **shared infrastructure** capable of hosting multiple analytical domains without changes to core ingress or security logic.

* **Ingress Hub**: Single upstream MAVLink listener with auto-detection and routing.
* **Core Services**: Mission tokens, Git-hash traceability, database lifecycle.
* **Runner**: Orchestrates live runs or historical replays.

### 2.2 Vertical Partitions (Domain Slots)
* **Navigation (Active)**: EKF / GPS causality POC.
* **Power / Vibration / System (Future)**: Reserved slots for modular expansion.

> This separation ensures that domain expansion does not destabilize the platform.

---

## 3. Data Integrity & Scientific Traceability
To ensure reproducibility, the platform enforces a **Zero-Touch Signing Contract**:
* **Mission ID**: Unique timestamp + UUID per run.
* **Git Hash Binding**: Every persisted record is signed with the current commit hash.
* **Immutable Artifacts**: No in-place mutation of analytical outputs.

This guarantees that *every insight is traceable to code, data, and time*.

---

## 4. Layered Domain Mart Model (WHAT)
Each domain processes telemetry through a strict pipeline:
1. **Ingress**: MAVLink ingestion from SITL or logs.
2. **Entity Layer**: Mapping raw messages into domain-specific Python dataclass contracts.
3. **Weaving Layer**: Temporal alignment using **ASOF joins** to correlate asynchronous telemetry.
4. **Mart Layer**: Persistence into DuckDB / Parquet for high-performance analytical queries.

---

## 5. Engine Architecture (HOW)
The system is intentionally split into two engines for ownership clarity.

### 5.1 Engine-1 — Ingest & Refinery
Answers: *“What happened?”*
* **Responsibilities**: MAVLink capture, Domain tagging, Silver / Gold data generation.
* **Key Properties**: Stateless processing, Append-only writes, No visualization logic.

### 5.2 Engine-2 — Dashboard & Evidence
Answers: *“What matters?”*
* **Responsibilities**: Domain-specific dashboards, Human-in-the-loop validation, Evidence capture.

---

## 6. Vault System (Evidence Contract)
The platform uses a **three-tier vault model**:

```
bin/vault/
├── warehouse/    # Raw, append-only telemetry
├── gold/         # Refined, query-ready domain marts
└── dashboard/    # Human-validated evidence artifacts (Snapshots/Notes)

## 7. Architecture Diagram

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


## 8. Engine Workflow: Live → Refinery → Dashboard
8.1 Live Run (Engine-1)

# Clear previous run
rm -rf bin/vault/warehouse/*
rm -f bin/nav_domain.db
# Start Ingestion
python3 -m src.runner.main

8.2 Replay / Refinery (Engine-2)
python3 -m src.data_mart_engine.refinery.nav_refinery
python3 -m src.data_mart_engine.refinery.sys_refinery

8.3 Dashboard Summary
python3 -m src.data_mart_engine.dashboard.domain_summary

## 9. Clean Start Script
Create a file named reset_engine.sh in the root directory:
#!/bin/bash
echo "🧹 Cleaning local analytical environment..."

rm -f ./bin/*.db
rm -f ./bin/*.duckdb
rm -f ./logs/metadata/inode_ledger.json
rm -f ./data/queues/*.json

echo "✅ Database and ledgers cleared."
echo "🚀 Run 'python3 src/runner/orchestrator.py' to begin new capture."

Make executable with: chmod +x reset_engine.sh

## 10. Scope & Guardrails
✅ Focus: Correctness, Traceability, and Ownership.

❌ Non-Goals: UI polish, Real-time guarantees, Multi-vehicle fusion, or modifying ArduPilot core.