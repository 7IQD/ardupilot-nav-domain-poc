# DF Domain Service Layer Integration With Data Model

## Purpose

The service layer executes deterministic diagnosis using precomputed tables and persists the final result.

It connects:
- prepared evidence (tables)
- reasoning logic (modules)
- final output (diagnosis)

---

## Architecture

nav_windows
→ nav_data_service (bounded fetch from nav_master)
→ nav_data_integrity_check
→ nav_stats
→ nav_labeler
→ nav_verdict_map
→ nav_ai_assistance

---

## Table Roles

### nav_master
Raw telemetry store
Used only for bounded extraction

---

### nav_windows
Primary entry point for analysis
Contains time and inode anchors

---

### mission_stats
Mission-level summary
Used to enrich diagnosis context

---

### rule_master
Defines anomaly logic
Used by labeler/verdict (should not be hardcoded)

---

### nav_rca_context (optional)
Intermediate correlation layer
Can be precomputed or skipped

---

### nav_ai_assistance
Final persistence layer

Stores:
- root cause
- confidence
- evidence (TimeUS, inode)
- suggested fixes

---

## Execution Contract

For each window in nav_windows:

1. Extract telemetry (bounded by TimeUS/inode)
2. Validate data integrity
3. Compute statistics
4. Assign states and detect mismatch
5. Generate verdict
6. Persist result

---

## Persistence Requirement

The service must write output to nav_ai_assistance.

This ensures:
- reproducibility
- auditability
- dataset creation for future learning

---

## Design Principles

- deterministic
- traceable to raw telemetry

---

## Outcome

Each run produces a structured diagnostic record stored in nav_ai_assistance:

- what happened
- where it happened
- why it happened
- supporting evidence