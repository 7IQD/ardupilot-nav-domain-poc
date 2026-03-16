## 📘 Chapter — Data Flow & Vault Logic (Ground-Run to Dashboard)

When you start a mission, the very first step is `src/core/initialize_db.py`. This file does not touch MAVLink or packets at all; it simply prepares the **storage world**. It creates the vault folders on disk (Vault-B staging and Warehouse folders) and ensures DuckDB is ready. Think of this as building empty shelves before stocking a store. Nothing moves yet — only space is prepared.

Next, `src/runner/main.py` starts the engine and creates the `Orchestrator` class. The Orchestrator opens a MAVLink connection (`udp:127.0.0.1:14551`). This connection is just a **live byte stream**, like water flowing through a pipe. From that pipe, `recv_match()` pulls out one **packet** at a time. A packet is a single logical measurement such as ATTITUDE or GPS_RAW_INT. At this moment, the data exists only in **memory**, not on disk and not in tables.

Each packet is handed immediately to the domain Architect classes — `NavArchitect` (`nav_architect.py`) or `SysArchitect` (`sys_architect.py`). These classes are the first place where structure appears. They decode the packet and convert it into a simple Python dictionary (one row of data). Many such rows are collected in memory and periodically grouped into a Pandas DataFrame. When the buffer fills, the DataFrame is written to disk as a small **Parquet fragment** inside Vault-B. These are your **Silver fragments**. They are just files — not tables — and they are immutable snapshots of raw decoded data.

When you stop the run (Ctrl+C), control returns to the `DatabaseManager/Clerk.finalize_run()`. The Clerk’s job is consolidation. It gathers all the small Vault-B fragments and merges them into one clean **master Parquet file per domain** inside the Warehouse (`nav_master.parquet`, `sys_master.parquet`). After merging, Vault-B is cleared. The Warehouse now holds the durable, canonical copy of the mission’s raw data. Still no SQL tables exist — only Parquet files on disk.

After storage is stable, the Refinery phase begins (`nav_refinery.py`, `sys_refinery.py`). The Refinery reads the Warehouse master Parquets, computes metrics (variance, health, battery stats, etc.), and loads the results into DuckDB. This is the first time the data becomes true **tables** (e.g., `fact_nav_precision`, `fact_sys_status`). These live inside DuckDB’s catalog and can be queried with SQL. These are your **Gold tables**.

Finally, the dashboard scripts (`mission_summary.py`, etc.) read only these Gold tables and generate reports. They never read packets or Parquet directly. They operate purely at the analytics level.

So the complete lifecycle is continuous and simple:
**bytes → packets → dict rows → DataFrame → Silver fragments → Warehouse masters → DuckDB Gold tables → dashboards.**

---

## 📘 Why the system is designed this way (the logic behind Bronze/Silver/Gold)

The design separates responsibilities so each stage stays simple and safe.

The **stream/bytes layer** exists because MAVLink is real-time telemetry. You must process packets immediately in memory or you lose them. That’s why the Orchestrator and Architects handle packets directly.

The **Silver (Vault-B fragments)** exist because writing one huge file continuously is risky and slow. Small fragments are faster, safer, and crash-tolerant. If the run stops midway, you only lose the last buffer, not everything.

The **Warehouse (master Parquet)** exists to create a single clean, durable snapshot of the mission. It is your “source of truth” on disk. Refinery always reads from here so analytics are deterministic and repeatable.

The **Gold (DuckDB tables)** exist because analytics should not scan raw Parquet repeatedly. DuckDB materializes structured fact tables for fast SQL queries and dashboards. This is the only place where data behaves like relational tables.

The **registry/bin/ledgers** exist only to track files (which fragments exist, ordering, inode IDs). They hold metadata, not telemetry. They are bookkeeping, not data storage.

Memory buffers exist for speed. Parquet exists for durable storage. DuckDB exists for querying. Each layer solves one problem only.

---

## 📘 Mental Model (keep this picture)

Think of it like a factory:

Wire (bytes) → Sorting desk (Architects) → Packing boxes (Silver Parquet) → Warehouse shelves (master Parquet) → Refinery machines (metrics) → Database tables (Gold) → Reports.

If you remember this picture, the codebase becomes obvious:

* Engine handles the wire
* Architects handle packets
* Vault-B holds fragments
* Clerk consolidates
* Refinery builds tables
* Dashboard reads tables

