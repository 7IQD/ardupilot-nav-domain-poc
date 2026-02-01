# Nav Domain POC — Iteration 1
## Data Mart Implementation Plan (Silver & Gold Layers)

### Objective
Establish the **digital skeleton** of the Navigation Domain POC by freezing
data structures, responsibilities, and contracts **before** wiring data flow.

This iteration focuses on **structure only** — not integration, tuning, or UI.

---

## Iteration Declaration

**Iteration:** 1
**Theme:** Structural Skeleton (No Data Flow)
**Status:** Frozen

This iteration defines *only* the structural contracts:
- Schemas
- Tables
- Views
- Playback query interface

All ingestion logic, thresholds, and cross-domain joins are explicitly deferred.

---

## 1. Architectural Principle

We explicitly separate:

- **Structure Planning** → tables, views, contracts (this iteration)
- **Flow Activation** → ingestion wiring (later)
- **Reasoning** → health logic, transitions (later)

> Structure may lead flow.
> Flow must never lead structure.

---

## 2. Layered Data Model

### 2.1 Canonical Storage (Silver Layer)

Silver represents **estimator truth**, not raw sensors.

#### `silver.nav_state` (ACTIVE)

| Column | Type | Description |
|------|------|------------|
| ts_boot | DOUBLE | Seconds since boot (monotonic) |
| pos_n | DOUBLE | Position North (m) |
| pos_e | DOUBLE | Position East (m) |
| pos_d | DOUBLE | Position Down (m) |
| vel_n | DOUBLE | Velocity North (m/s) |
| vel_e | DOUBLE | Velocity East (m/s) |
| vel_d | DOUBLE | Velocity Down (m/s) |
| vel_test_ratio | DOUBLE | EKF velocity innovation ratio |
| control_mode | VARCHAR | Labeled nav mode (gps, dead_reckon, etc.) |

Rules:
- Scalars only (no vectors/arrays)
- No bitmasks
- No derived health states
- One row = one estimator belief at time *t*

---

#### `silver.gps_observation` (INACTIVE SLOT)

Reserved for future correlation. Not wired in Iteration-1.

| Column | Type | Description |
|------|------|------------|
| ts_boot | DOUBLE | Time alignment key |
| lat | DOUBLE | Latitude (deg) |
| lon | DOUBLE | Longitude (deg) |
| alt_msl | DOUBLE | Altitude MSL (m) |
| fix_type | UINTEGER | GPS fix status |
| satellites_visible | UINTEGER | Satellite count |

Rules:
- No velocity vectors
- No joins in this iteration

---

### 2.2 Reasoning Surface (Gold Layer)

Gold is a **Data Mart View**, not a table.

It is the **only surface visible** to Context Playback.

#### `gold.nav_context` (VIEW)

Purpose:
- Playback-safe
- Deterministic ordering
- Human-understandable projection

Contents:
- Time
- Position vectors
- Velocity vectors
- EKF health signal(s) (derived later)

Ordering:
```sql
ORDER BY ts_boot ASC;

3. Playback Contract (Frozen)

All consumers (HUD, replay, analysis) use the same query pattern.
SELECT *
FROM gold.nav_context
WHERE ts_boot BETWEEN ? AND ?
ORDER BY ts_boot ASC;

4. Code Structure
4.1 Module Responsibilities

| Module                     | Responsibility                |
| -------------------------- | ----------------------------- |
| `core/initialize_db.py`    | Create schemas, tables, views |
| `ingress/materializers.py` | Map telemetry → Silver        |
| `weaving/navigation.py`    | Query Gold for time windows   |
| `runner/main.py`           | Wire lifecycle                |

4.2 Project Directory Layout
nav_poc/
├── data/                         # DuckDB database file (.db)
├── core/
│   └── initialize_db.py           # Table & view setup
├── ingress/
│   └── materializers.py           # Canonical ingestor
├── weaving/
│   └── navigation.py              # Playback engine
├── runner/
│   └── main.py                    # Lifecycle orchestrator
├── docs/
│   └── iteration_1_structure.md
└── tests/                         # Verification scripts

5. Iteration-1 Boundaries

Included

Table and view skeletons

Naming conventions

Playback query contract

Explicitly Excluded

Data wiring

Thresholds

UI logic

GPS vs EKF comparison

Analytics

6. Exit Criteria

Iteration-1 is complete when:

DuckDB initializes with all schemas

gold.nav_context can be queried

Playback engine runs without caring how data arrived

At this point, the system becomes context-aware by construction.

7. Project Mapping for Implementation

| Planned Component  | Existing Location          | Responsibility                                |
| ------------------ | -------------------------- | --------------------------------------------- |
| Schema Setup       | `core/initialize_db.py`    | Runs DDL for `silver` tables and `gold` views |
| Canonical Ingestor | `ingress/materializers.py` | Maps raw telemetry → `silver.nav_state`       |
| Playback Engine    | `weaving/navigation.py`    | Retrieves time slices from `gold.nav_context` |
| Lifecycle Control  | `runner/main.py`           | Orchestrates system start-up                  |

8. Implementation Kick-off: Phase 1 (Foundation)

Verify core/initialize_db.py contains the exact SQL projection for gold.nav_context.

Ensure it creates the Silver tables and Gold view without populating data.

This acts as the Smart Lens 🖼️ for the playback engine.

Note: The ingestion logic and any scaling/conversions will be added in Iteration-2. Iteration-1 is purely structural.