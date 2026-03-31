# AI Assisted NAV Log Diagnosis and Root Cause Detection

## Concept

During a SITL run, MAVLink telemetry arrives as mixed, asynchronous streams across Navigation, System, and Sensor domains. These streams provide a full snapshot of the vehicle state but are difficult to analyze individually or correlate across domains.

---

## Problem

Current workflows expose telemetry as a combined stream, making it hard to isolate domain-specific behavior, evaluate estimator performance, or trace issues across subsystems. Analysis often becomes manual and inconsistent.

---

## Solution

This project captures MAVLink packets without loss and organizes them into time-aligned, domain-specific datasets. The architecture enables:

- Domain-level analysis (NAV, SYS, SENSOR)
- Temporal alignment across signals
- Cross-domain correlation when required

The same design can be extended to other domains, but this repository focuses on the **NAV domain as a proof-of-concept for AI-assisted diagnosis**.

It processes ArduPilot `.BIN` logs to build a deterministic, explainable pipeline that answers:
**what happened, where it happened, and why it happened** during a flight — with full traceability to the original telemetry.

---

## How the flow works

The pipeline transforms raw logs step by step:

BIN → ingestion → shards → NAV master → DuckDB → analysis → final output

- The `.BIN` log is parsed using pymavlink and split into domain-specific parquet shards
- These shards are stored without modification to preserve raw telemetry
- A NAV master dataset is created using `mission_id` and segmented using `segment_id`
- The entire analysis runs inside DuckDB for efficient querying and reproducibility

---

## Architecture

![DF Architecture](images/df_architecture.png)

---

## What happens in the database

The database is where structured reasoning is built.

- `mission_master` represents the full mission timeline
- `mission_nsat_windows` stores state-change windows based on NSats behavior

A window is defined as a continuous period where signal conditions remain stable.

Example:
NSats = 3 → 0 → 12 → 7 → 0 → 12

This naturally creates multiple windows without assumptions.

---

## Turning data into meaning

Once windows are created:

- `rule_master` defines interpretation logic
- `nav_meta_log` stores exact anchors (TimeUS, inode ranges)
- The service layer retrieves bounded telemetry from these anchors

The pipeline then executes:
window → check → stats → label → verdict

Results are stored in:
nav_ai_assistance


This table contains:

- detected events
- supporting telemetry evidence
- structured explanations

---

## Core Design

The system separates **signal from interpretation**:

- windows → what actually happened
- rules → what it means

This ensures:

- deterministic outputs
- explainability
- reproducibility

---

## How to run

Step 1 — Ingestion and base pipeline

`src/runner/df_main.py`

Step 2 — Build domain datasets
`create_domain_master_db.sh`


Step 3 — Run analysis pipeline

This builds:

- mission tables
- anomaly windows
- meta logs
- AI assistance outputs

`nav_ai_assistance_builder.py`


---

## Note

The pipeline is being simplified and will be unified into a single entry point in future versions.