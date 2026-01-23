## 1. Ingestion: The “Sealed Artifact” Rule

**Method**
- Bulk Post-Processing (ELT)

**Process**
- Mission ends
- Log files are hashed and sealed
- Python ingests all raw data into DuckDB in a single atomic batch

**Benefit**
- Full determinism
- Re-running the same mission log produces identical Z-scores and spike detections every time

---

## 2. Live Visibility: Dual-Track Reporting Framework

| Track | Scope | Technology | Primary Question Answered |
|-----:|-------|------------|---------------------------|
| LRU (Local Reporting Unit) | Rolling window | In-memory buffers | “Am I safe right now?” (operator heartbeat, live vibration) |
| SRU (Stream Recording Unit) | Append-only | Flat files / inode-style logs | “What is the forensic trail?” (future Bronze input) |

---

## 3. Separation of Concerns (The Firewall)

- **Baseline Database**
  - Populated only from finalized, hashed mission artifacts
  - Read-only during all analysis phases

- **Live Stream**
  - Operates in transient memory or append-only logs
  - Never writes partial, jittery, or in-flight data into the Baseline DB

---

## 4. Implementation Flow (Phase-Separated)

**Phase 1: Runtime (Live, Non-Persistent)**
- Telemetry flows into in-memory evaluators.
- LRU updates a single rolling mission-status line.
- SRU appends timestamped assertion results to flat files.

**Phase 2: Mission End (Seal Point)**
- SRU files are closed and hashed (SHA-256).
- Artifacts become the immutable "Bronze" source.

**Phase 3: Post-Mission (Baseline ELT)**
- Python performs a single bulk load into DuckDB (Extract & Load).
- Transformations occur purely via DuckDB SQL Views (Silver/Gold).

**→ Workflow Summary**
- **Runtime:** LRU (in-memory) + SRU (flat files) → no DuckDB writes
- **Seal Point:** SRU logs hashed & finalized → eligible for Bronze load
- **Post-Mission:** Python bulk-loads SRU logs → Bronze → Silver → Gold
