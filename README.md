# ArduPilot Nav-Mart: Multi-Domain Analytics Platform

Navigation-domain Proof of Concept for a non-intrusive SITL analytical observability pipeline.

## 1. Project Mission
Demonstrates a thin vertical slice of the proposed GSoC 2026 project by capturing, aligning, and replaying navigation telemetry (GPS/EKF) to facilitate causal analysis — without modifying ArduPilot core behavior.

## 2. Horizontal Architecture (The Platform)
The Nav-Mart is built as **Shared Infrastructure** capable of hosting multiple specialized domains. The architecture ensures that adding a new domain (e.g., Power or Vibration) requires zero changes to the core ingress or security logic.

### 2.1 Infrastructure (Global Services)
* **Ingress Hub**: Single upstream MAVLink listener with auto-detection and routing.
* **Core Services**: AAA-light (Mission Tokens), Git-hash traceability, and DB management.
* **Runner**: Orchestrates the live flow or historical replay of data.

### 2.2 Domain Partitions (Vertical Implementation)
* **Navigation (Active)**: Reference implementation for EKF-GPS causality.
* **Power / Vibration / System (Future)**: Scalable slots for expansion.

## 3. Data Integrity & Traceability
To ensure scientific reproducibility, the platform implements a "Zero-Touch" signing contract:
* **Mission Tokens**: Every session is uniquely identified by a timestamp and session UUID.
* **Git-Hash Linking**: Every data record in the Mart is signed with the current Git commit hash to map data results directly to the code version used.

## 4. The Layered Domain Mart Model
The system processes data through a structured pipeline:
1. **Ingress**: MAVLink sniffing from SITL/Hardware.
2. **Entity**: Data mapping to domain-specific Python dataclass contracts.
3. **Weaving**: Temporal alignment using **ASOF joins** to correlate asynchronous telemetry.
4. **Mart**: Persistence into DuckDB/Parquet for high-performance OLAP queries.

## 5. Analytical Versatility: Systems Validation
While the primary focus is the Navigation POC, the underlying Layered Domain Mart architecture is designed to facilitate:

* **Intra-System Correlation**: Monitoring internal causality loops, such as the relationship between raw sensor inputs and estimator (EKF) perception.
* **Inter-System Performance**: Providing the data structure necessary to observe how disparate sub-systems (Navigation, Power, Actuation) influence one another.
* **Multi-Agent Benchmarking**: Using metadata to enable performance comparisons across a heterogeneous fleet (e.g., Copter vs. Rover).

By establishing a unified data contract, the platform ensures that complex systems-level insights are accessible without requiring a redesign of the core engine.