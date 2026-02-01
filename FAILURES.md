# FAILURES.md
## Navigation Domain POC — Fail-Fast Log

This document records **early design decisions, discarded paths, and risk-reduction pivots** made during the Navigation Domain POC.
The goal is transparency, learning velocity, and architectural clarity — not post-hoc justification.

---

### Failure 001 — Treating the POC as an ArduPilot Subtree
**Initial Assumption:**
The Navigation Observability work could live directly inside the ArduPilot repository from day one.

**Observed Problem:**
- Tight coupling to ArduPilot build, SITL lifecycle, and review cadence
- Slowed iteration speed for exploratory OLAP-style analysis
- Risk of architectural rejection before the idea could be demonstrated

**Decision / Pivot:**
Create a **standalone POC repository** focused purely on the “Golden Thread” (SITL → Pipe → Mart → API → Expert).

**Outcome:**
- Faster iteration
- Clear separation between *demonstration* and *production*
- Reduced mentor risk

---

### Failure 002 — Assuming Standard SQL Would Be Sufficient
**Initial Assumption:**
Traditional row-oriented SQL (e.g., SQLite-style joins) would be adequate for aligning MAVLink telemetry.

**Observed Problem:**
- Asynchronous signal alignment (5 Hz GPS vs 50 Hz EKF) required complex joins
- Memory pressure and query complexity increased rapidly
- Temporal causality became harder to reason about

**Decision / Pivot:**
Adopt **DuckDB** as an in-process columnar OLAP engine with native **AS-OF JOIN** support.

**Outcome:**
- Cleaner temporal alignment
- Explicit causal semantics
- Reduced cognitive load in analysis queries

---

### Failure 003 — Treating Branch Naming as Cosmetic
**Initial Assumption:**
Using `master` as the default branch in the POC repo would be harmless.

**Observed Problem:**
- Semantic collision with ArduPilot’s `master`
- Risk of mentor confusion about upstream authority
- Ambiguity in repo intent (POC vs production)

**Decision / Pivot:**
Rename default branch to **`nav-poc-main`** to clearly signal scope and ownership.

**Outcome:**
- Clear mental separation from upstream ArduPilot
- Cleaner narrative during proposal and review
- Reduced cognitive overhead for reviewers

---

### Failure 004 — Underestimating Git as a Risk Vector
**Initial Assumption:**
Git mechanics were secondary to technical architecture.

**Observed Problem:**
- Early friction during repo initialization and authentication
- Risk of losing momentum due to tooling uncertainty

**Decision / Pivot:**
Stabilize Git workflow *early*, before adding code:
- Single default branch
- Minimal history
- Documentation-first commits

**Outcome:**
- Reduced operational risk
- Predictable contribution rhythm
- More time spent on domain reasoning instead of tooling recovery

---

### Living Document
This file will continue to grow during the POC sprint.
Failures are logged **when discovered**, not retroactively cleaned.

The intent is to demonstrate:
- engineering honesty
- learning speed
- and risk-aware decision making
