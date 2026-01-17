# ArduPilot Nav-Mart: Multi-Domain Analytics Platform

Navigation-domain Proof of Concept for a non-intrusive SITL analytical observability pipeline.

## 1. Project Mission
Demonstrates a thin vertical slice of the proposed GSoC 2026 project by capturing, aligning, and replaying navigation telemetry (GPS/EKF) to facilitate causal analysis — without modifying ArduPilot core behavior.

## 2. Horizontal Architecture (The Platform)
The Nav-Mart is built as a **Shared Infrastructure** capable of hosting multiple specialized domains. The architecture ensures that adding a new domain (e.g., Power or Vibration) requires zero changes to the core ingress or security logic.

### Infrastructure (Global Services)
* **Ingress Hub**: Single upstream MAVLink listener with auto-detection and routing.
* **Core Services**: AAA-light (Mission Tokens), Git-hash traceability, and DB management.
* **Runner**: Orchestrates the live flow or historical replay of data.

### Domain Partitions (Vertical Implementation)
* **Navigation (Active)**: Reference implementation for EKF-GPS causality.
* **Power/Vibration/System (Future)**: Scalable slots for expansion.