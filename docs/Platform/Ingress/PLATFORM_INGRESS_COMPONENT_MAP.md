# Nav-Mart Canonical Data Map

## 1. Global Platform (The Engine)
These components are shared across all future domains.

* **Core (`src/core/`)**
    * `security.py`: AAA-light. Generates mission tokens and Git-hash signatures.
    * `database.py`: Shared DuckDB connection logic and session pooling.
* **Ingress (`src/ingress/`)**
    * `sniffer.py`: The MAVLink "Ear." Listens for raw telemetry.
    * `router.py`: The "Brain." Dispatches messages to specific domain handlers.
* **Runner (`src/runner/`)**
    * `main.py`: The Orchestrator. Manages the lifecycle of a SITL or Replay session.

---

## 2. Domain Partitions (The Logic)
These components are unique to the Navigation implementation.

* **Entities (`src/entities/`)**
    * `base.py`: The Global Contract (Parent class for all data).
    * `navigation.py`: The Schema. Definitions for GPS and EKF objects.
* **Weaving (`src/weaving/`)**
    * `navigation.py`: The Transformer. Temporal ASOF joins for causality.
* **Audit (`src/audit/`)**
    * `navigation.py`: The Guard. Validation for drift, gaps, and staleness.

---

## 3. Persistence Vault (`mart/`)
* **Navigation Partition (`mart/navigation/`)**
    * `nav.duckdb`: The active OLAP database for navigation queries.
    * `segments/`: Folder containing mission-specific Parquet files.