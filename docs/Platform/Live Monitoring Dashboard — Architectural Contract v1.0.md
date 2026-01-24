# Live Monitoring Dashboard — Architectural Contract (v1.0)

## 1. Purpose

This document defines the **formal architectural contract** for a browser-based Live Monitoring Dashboard intended for Flight Test Engineers (FTEs). The dashboard is designed to present **information, not data**, enabling assessment of **performance, behavior, and system state linkages** without statistical derivation.

This contract is UI-agnostic, domain-extensible, and compatible with live monitoring and replay.

---

## 2. Scope

### In Scope

* Live observability of flight behavior across multiple domains
* Context-driven information surfacing ("Prescriptions")
* State-based visualization (Green / Yellow / Red)
* Temporal and cross-domain linkage presentation

### Out of Scope (Non-Goals)

* Statistical analysis (mean, variance, trend, ML)
* Control or actuation decisions
* Optimization recommendations
* Competition with existing GCS tools (e.g., QGC)

---

## 3. Core Design Principle

> **The Live Dashboard shall not compute insights.**

All insights, classifications, and state determinations are performed **upstream** by the Observability Engine. The dashboard functions strictly as a **semantic renderer**.

---

## 4. Information vs Data Policy

### Prohibited

* Raw sensor streams
* Statistical aggregates
* Derived trends or probabilities

### Permitted

* Discrete state labels
* Boundary crossings
* Sample-count violations
* Timing windows
* Domain and sensor linkages

---

## 5. Stability & Nominal State Definition

A parameter is considered **STABLE / NOMINAL** when:

* It remains within defined upper and lower boundaries
* For a fixed number of consecutive samples (N)
* Within a specified time window

No averaging, smoothing, or statistical inference is permitted.

---

## 6. State Classification Model

Each monitored parameter emits the following semantic record:

```yaml
parameter_id
source_domain
state: GREEN | YELLOW | RED
breach_type: NONE | UPPER | LOWER | OSCILLATION
sample_count: integer
window_us: integer
timestamp_us
```

### State Semantics

| State  | Meaning                          | Operator Intent      |
| ------ | -------------------------------- | -------------------- |
| Green  | Nominal, stable                  | Suppress             |
| Yellow | Boundary approach or degradation | Surface context      |
| Red    | Boundary violation               | Investigate linkages |

> **Red is not an action trigger.** It is a signal for correlation and understanding.

---

## 7. Quadrant Display Model

The dashboard is logically divided into four quadrants:

| Quadrant | Responsibility       |
| -------- | -------------------- |
| Q1       | Navigation           |
| Q2       | Energy / Power       |
| Q3       | Structural / Motion  |
| Q4       | Contextual Deep Dive |

### Q4 — Context Deep Dive Rules

* Activated only on Yellow or Red states
* Displays associated parameters, domains, and timing windows
* No insight generation or aggregation
* Information may rotate **only if space-constrained**
* Rotation cadence must be slow and analysis-friendly

---

## 8. Context (“Prescription”) Model

A **Context** is a predefined semantic bundle selected by the FTE.

Example:

```yaml
context_id: NAV_EKF_HEALTH
primary_markers:
  - pos_horiz_variance
  - velocity_variance
dependent_domains:
  - IMU
  - GPS
  - CPU
lock_duration_us: 5000000
```

Rules:

* Contexts are declarative, not inferred
* Dashboard does not alter context logic
* Context controls what is surfaced, not how it is computed

---

## 9. Temporal Lock & Rotation Policy

* Upon Yellow/Red detection, relevant parameters are **locked** into Q4
* Lock persists for a defined duration
* Rotation is allowed only to reveal additional associated data
* Rotation must remain stable (no flashing or rapid cycling)

---

## 10. Dashboard I/O Contract

### Input (from Observability Engine)

```yaml
context_id
active_state
time_window_start_us
time_window_end_us
locked_parameters[]
domain_states[]
```

### Output (to Operator)

* Colored state indicators
* Parameter identifiers
* Domain labels
* Timing windows

No data mutation or feedback is permitted.

---

## 11. Extensibility

* New domains may be added without dashboard modification
* New contexts may be introduced via configuration
* Replay systems consume the same contract

---

## 12. SDLC Positioning (GSoC)

This contract enables:

* Clear separation of concerns
* Safe focus on Data Mart and Replay infrastructure
* A demonstrable, research-grade observability framework

---

## 13. Status

**Version:** 1.0
**State:** Frozen

---


