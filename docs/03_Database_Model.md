# Database Model (NAV Domain)

This database supports deterministic NAV log diagnosis with full traceability to raw telemetry (TimeUS, inode).

The design follows a layered approach:
ingestion → windowing → evidence → diagnosis → persistence

---

## Table Overview

| Table Name              | Purpose                                         |
|------------------------|-------------------------------------------------|
| fmt_master             | BIN schema definition (msg_type → parameters)   |
| msg_type_master        | Message identity and parameter mapping          |
| nav_master             | Flattened NAV telemetry store                   |
| mission_stats          | Mission-level aggregates and sanity checks      |
| nav_windows            | Time-based state windows (anchors)              |
| nav_sig_state_timeline | Signal state evolution over time                |
| nav_mot_state_timeline | Motion state evolution over time                |
| nav_rca_context        | Context linking signals and conditions          |
| rule_master            | Rule definitions (thresholds and conditions)    |
| nav_ai_assistance      | Final diagnosis persistence layer               |

---

## 1. Configuration Layer

### msg_type_master
Defines message structure and expected parameters.

| Field | Description |
|------|-------------|
| domain | System domain (NAV, EST, etc.) |
| msg_type | Log message type (GPS, ATT, IMU) |
| param_list_json | Expected parameters (JSON) |
| description | Human-readable meaning |
| version | Firmware compatibility |

---

## 2. Ingress Layer

### nav_master
Primary telemetry table for NAV domain.

| Field | Description |
|------|-------------|
| TimeUS | Timestamp (microseconds) |
| inode | Row identifier |
| msg_type | Message type |
| mission_id | Mission identifier |
| segment_id | Segment grouping |
| Telemetry | 300+ parameters (NSats, HDop, etc.) |

Usage:
- read-only
- accessed through bounded queries using TimeUS and inode

---

## 3. Preparation Layer

### mission_stats
Mission-level summary for validation and profiling.

Includes:
- row counts
- mission duration
- NSats / HDop statistics
- message coverage

---

### nav_windows
Time-compressed windows derived from signal state changes.

| Field | Description |
|------|-------------|
| start_timeus / end_timeus | Window time boundaries |
| start_inode / end_inode | Row boundaries |
| duration_sec | Duration of window |
| sensor_state | Derived signal state (LOSS, DEGRADED, HEALTHY) |
| fc_state | Flight controller state |
| integrity_flag | Alignment between sensor and FC |
| row_count | Rows contributing to window |

Role:
- primary entry point for analysis
- replaces earlier anchor-layer concepts by directly storing boundaries

---

## 4. State & Timeline Layer

### nav_sig_state_timeline
Tracks signal state transitions over time.

### nav_mot_state_timeline
Tracks motion-related state transitions.

Purpose:
- supports advanced correlation (signal vs motion)
- used for extended NAV anomaly detection

---

## 5. Evidence Layer

### nav_rca_context
Links windows with contextual information used during diagnosis.

Contains:
- window references
- signal conditions
- contextual parameters

Role:
- bridges raw telemetry and reasoning
- optional precomputed layer (can be derived dynamically)

---

## 6. Knowledge Layer

### rule_master
Defines anomaly detection logic.

| Field | Description |
|------|-------------|
| rule_id | Unique rule identifier |
| parameter | Evaluated field |
| operator | Comparison (>, <, =) |
| threshold | Trigger value |
| severity | Impact level |
| description | Rule meaning |

Usage:
- consumed by labeler and verdict modules
- keeps logic outside code (config-driven)

---

## 7. Diagnostic & Persistence Layer

### nav_ai_assistance
Final structured diagnostic output.

Stores:
- window boundaries (TimeUS, inode)
- detected anomaly (root cause)
- confidence score
- supporting evidence
- suggested fixes

Role:
- persistence of RCA results
- enables audit, reuse, and comparison across missions

---

## Execution Relationship with Service Layer

The service layer operates on top of these tables:

nav_windows
→ bounded fetch from nav_master
→ integrity check
→ stats
→ labeling
→ verdict
→ write to nav_ai_assistance

---

## Design Principles

- Deterministic: outputs are rule-based and reproducible
- Traceable: every result maps to raw telemetry (TimeUS, inode)
- Layered: ingestion → windows → evidence → diagnosis
- Efficient: avoids repeated full-log scans using window anchors
- Persistent: final RCA results are stored for reuse and validation