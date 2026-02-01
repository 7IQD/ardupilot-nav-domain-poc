# ArduPilot Nav-Mart
**Multi-Domain Analytics & Evidence Platform (Navigation POC)**

Navigation-domain Proof of Concept for a **non-intrusive, evidence-driven observability pipeline** over ArduPilot SITL / logs.

This repository demonstrates a thin but complete vertical slice of a proposed **GSoC 2026** project: capturing, aligning, analyzing, and *freezing* navigation telemetry (GPS / EKF) to support causal reasoning — **without modifying ArduPilot core behavior**.

---

## 1. Executive Summary (WHY)

Modern autopilot systems expose rich telemetry but lack a **reproducible, reviewable evidence trail** for engineering insight.
This project converts transient telemetry into a **professional engineering record** by combining:

- Deterministic data ingestion
- Domain-aware analytical pipelines
- Human-validated evidence capture

The Navigation domain serves as the **reference implementation**.

---

## 2. Research & Vision Context (Design Intent)

### 2.1 Horizontal Architecture (The Platform)

Nav-Mart is designed as **shared infrastructure** capable of hosting multiple analytical domains without changes to core ingress or security logic.

**Global Services**
- **Ingress Hub**: Single upstream MAVLink listener with auto-detection and routing
- **Core Services**: Mission tokens, Git-hash traceability, database lifecycle
- **Runner**: Orchestrates live runs or historical replays

### 2.2 Vertical Partitions (Domain Slots)

- **Navigation (Active)**: EKF / GPS causality POC
- **Power / Vibration / System (Future)**: Reserved, unimplemented

> This separation ensures that domain expansion does not destabilize the platform.

---

## 3. Data Integrity & Scientific Traceability

To ensure reproducibility, the platform enforces a **Zero-Touch Signing Contract**:

- **Mission ID**: Unique timestamp + UUID per run
- **Git Hash Binding**: Every persisted record is signed with the current commit hash
- **Immutable Artifacts**: No in-place mutation of analytical outputs

This guarantees that *every insight is traceable to code, data, and time*.

---

## 4. Layered Domain Mart Model (WHAT)

Each domain processes telemetry through a strict pipeline:

1. **Ingress**
   MAVLink ingestion from SITL or logs

2. **Entity Layer**
   Mapping raw messages into domain-specific Python dataclass contracts

3. **Weaving Layer**
   Temporal alignment using **ASOF joins** to correlate asynchronous telemetry

4. **Mart Layer**
   Persistence into DuckDB / Parquet for high-performance analytical queries

This model enables both **intra-system** and **inter-system** analysis without redesign.

---

## 5. Engine Architecture (HOW)

The system is intentionally split into two engines for ownership clarity.

### 5.1 Engine-1 — Ingest & Refinery

**Responsibilities**
- MAVLink capture
- Domain tagging
- Silver / Gold data generation

**Key Properties**
- Stateless processing
- Append-only writes
- No visualization logic

Engine-1 answers: *“What happened?”*

---

### 5.2 Engine-2 — Dashboard & Evidence

**Responsibilities**
- Domain-specific dashboards
- Human-in-the-loop validation
- Evidence capture into the Dashboard Vault

Engine-2 answers: *“What matters?”*

---

## 6. Vault System (Evidence Contract)

The platform uses a **three-tier vault model**:

bin/vault/
├── warehouse/ # Raw, append-only telemetry
├── gold/ # Refined, query-ready domain marts
└── dashboard/ # Human-validated evidence artifacts


### 6.1 Dashboard Vault (Write-Once Evidence)

The **Dashboard Vault** stores:
- PNG snapshots of analytical views
- CSV slices of underlying data
- Markdown notes with human tags

This layer transforms dashboards from *ephemeral displays* into **auditable engineering artifacts**.

> No feedback loops into the refinery are permitted.

---

## 7. Navigation Domain POC (Deliverable)

The Navigation POC demonstrates:

- EKF ↔ GPS temporal causality
- Reproducible replay
- Evidence capture for mentor review

It serves as:
- A **technical proof**
- A **learning scaffold**
- A **template for future domains**

---

## 8. Scope & Non-Goals (Guardrails)

To prevent scope creep, the following are **explicitly out of scope**:

- ❌ UI polish or web dashboards
- ❌ Real-time guarantees
- ❌ Multi-vehicle fusion
- ❌ Autonomous feedback into ArduPilot
- ❌ Domains beyond Navigation

This POC prioritizes **correctness, traceability, and ownership** over breadth.

---

## 9. Mentor Evaluation Lens

From a mentor’s perspective, this repository demonstrates:

- Clear separation of concerns
- Evidence-based engineering practice
- Reproducible experimentation
- Incremental, reviewable progress

Every artifact answers three questions:
1. *What code produced this?*
2. *What data supports it?*
3. *When and why was it captured?*

---

## 10. Roadmap (Post-GSoC)

- Activate additional domains
- Cross-domain correlation
- Fleet-level benchmarking
- Structured report generation

These are **future extensions**, not current commitments.

---

**Status:** Navigation POC — Mentor-ready
**Intent:** Learn, own, and demonstrate systems-grade engineering rigor
