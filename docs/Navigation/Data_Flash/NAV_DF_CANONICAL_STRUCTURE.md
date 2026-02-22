# Mission Portal & DataFlash Processing
## Directory & Responsibility Map

This document defines the **canonical project structure** and the responsibility of each major component.

It describes structure only — not execution flow.

---

# 🏗 System Layers

The system is divided into three logical layers:

1. **Mission Portal (UI)**
2. **API Gateway**
3. **Processing & Storage Layer**

Each layer has a clearly defined boundary.

---

# 📂 Canonical Directory Structure

| Directory / Path                  | Responsibility                                                                 |
|-----------------------------------|--------------------------------------------------------------------------------|
| `src/mission_portal/`             | **Mission Portal (UI)** — Path-agnostic SvelteKit interface (SITL + DF).     |
| `src/df_apis/`                    | **API Gateway** — FastAPI router exposing `/sitl` and `/drone`.              |
| `src/runner/`                     | **Orchestrators** — Controls extraction and projection workflows.             |
| `src/weaving/`                    | **ETL Layer** — Domain architects and refiners.                               |
| `src/vault/`                      | **Persistence Utilities** — File management and cleanup logic.                |
| `core/utils/`                     | **Shared Logic** — Math helpers, unit conversion, global time sync.           |
| `core/domain_marts/`              | **Analytics Layer** — Domain health scoring and evaluation logic.             |
| `core/dx_service_bus/`            | **DX Layer** — Message contracts and subscriber coordination.                 |
| `bin/vault/df_source/`            | **Input Source** — Authoritative `.BIN` flight logs.                          |
| `bin/vault/vault_b/`              | **Staging Area** — Temporary Parquet shards.                                  |
| `bin/vault/warehouse_df/`         | **Permanent Storage** — Mission-stamped masters + DuckDB database.            |

---

# 🧠 Architectural Principles

- The **Mission Portal** never talks directly to storage.
- All data access flows through the **API Gateway**.
- Processing logic is isolated from the UI.
- `bin/vault/warehouse_df/` contains the canonical historical database.
- Folder names reflect **responsibility**, not implementation detail.

---

This document defines structure only.
Execution and processing flow are documented separately.