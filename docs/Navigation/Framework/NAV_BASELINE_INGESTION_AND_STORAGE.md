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
