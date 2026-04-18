# NAV DF Service Pipeline (Execution Flow)

## Purpose

This pipeline performs deterministic root-cause analysis on NAV telemetry using precomputed windows and a step-by-step service layer.

It answers:
- what happened
- where it happened
- why it happened

---

## Execution Entry Point

The pipeline is executed through:

src/df_domain_data_services/nav/nav_controller.py

This script orchestrates all analysis steps in sequence.

---

## End-to-End Flow

nav_windows
→ nav_data_service (bounded telemetry from nav_master)
→ nav_data_integrity_check
→ nav_stats
→ nav_labeler
→ nav_verdict_map
→ nav_ai_assistance (final output)

---

## Step-by-Step Execution

### STEP 1: Availability Check

**Module:** nav_data_service.py

Checks if required NAV messages (e.g., GPS) exist.

Purpose:
- avoid unnecessary processing
- ensure data presence

---

### STEP 2: Integrity Check

**Module:** nav_data_integrity_check.py

Validates required fields:
- NSats
- Status

Purpose:
- ensure no missing or null data
- prevent downstream errors

---

### STEP 3–4: Distributions

**Module:** nav_stats.py

Computes:
- NSats distribution
- Status distribution

Purpose:
- provide mission-level signal overview
- detect presence of anomalies (e.g., NSats = 0)

---

### STEP 5: State Mapping and Mismatch Detection

**Module:** nav_labeler.py

Transforms raw values into states:

- NSats → LOSS / DEGRADED / HEALTHY
- Status → FC state

Then detects mismatch:

Example:
LOSS (sensor) + HEALTHY (FC) → MISMATCH

Purpose:
- convert numeric telemetry into interpretable states
- detect disagreement between sensor and controller

---

### STEP 6: Windowing (Time Compression)

**Module:** nav_labeler.py

Groups consecutive rows into windows based on:
- sensor_state
- fc_state
- integrity_flag

Each window contains:
- start_timeus / end_timeus
- start_inode / end_inode
- duration
- row_count

Source table:
nav_windows

Purpose:
- compress large telemetry into meaningful segments
- define analysis boundaries

---

### STEP 7: Verdict Generation

**Module:** nav_verdict_map.py

Processes only mismatch windows.

For each window:
- assigns score based on:
  - sensor failure
  - FC state
  - mismatch condition

Outputs:
- root cause
- confidence score
- suggested fixes
- evidence table (TimeUS + inode)

---

## Output

### Printed Output (Interactive)

- step-by-step analysis
- evidence table
- chain summary

---

### Persisted Output

Stored in:

nav_ai_assistance

Contains:
- window boundaries
- root cause
- confidence
- evidence summary

---

## Key Design Decisions

### 1. Window-First Analysis
All reasoning starts from nav_windows instead of raw telemetry.

---

### 2. Bounded Data Access
Only relevant telemetry is fetched using:
- TimeUS
- inode

---

### 3. Deterministic Logic
- no black-box inference
- rule-based scoring
- reproducible results

---

### 4. Separation of Concerns

| Layer | Responsibility |
|------|--------------|
| DuckDB tables | data + windows |
| Service modules | processing logic |
| nav_controller | orchestration |
| nav_ai_assistance | final storage |

---

## Example Flow (GPS Loss Case)

1. NSats drops to 0
2. FC remains HEALTHY
3. Mismatch detected
4. Window created (e.g., 249 sec)
5. Score = 1.0
6. Root cause: GPS Loss with EKF Lag

---

## Outcome

The pipeline produces a structured diagnostic result with:

- clear anomaly identification
- precise time boundaries
- traceable evidence
- explainable reasoning