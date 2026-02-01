# PLATFORM SYSTEM DESIGN: Layered Domain Mart Architecture

## 1. Architectural Philosophy
The Ardu-Mart Platform is a multi-tenant telemetry engine. It is designed to host various analytical "Marts" (Navigation, Power, etc.) while sharing a common infrastructure for ingress and storage.

## 2. The Layered Domain Mart Model
To ensure high-fidelity analysis, the platform organizes logic into five functional layers:

1.  **Ingress Layer (Shared)**: Non-intrusive sniffing of the MAVLink protocol.
2.  **Entity Layer (Domain)**: Canonical data contracts (e.g., GPS vs. EKF) that inherit from a shared base.
3.  **Weaving Layer (Domain)**: The "Engine Room" where temporal causality is established using ASOF joins.
4.  **Audit Layer (Domain)**: Real-time validation for data gaps or autopilot perception drift.
5.  **Persistence Layer (Shared)**: Long-term storage in the Mart (DuckDB/Parquet) for multi-mission comparison.

## 3. Temporal Consistency
The platform treats ArduPilot's `time_boot_ms` as the master clock. By weaving data at the domain level, we can correlate reality (sensors) with perception (estimation) even when message rates are inconsistent.

## 4. Mission Signing & Traceability
Every flight session is encapsulated as a "Mission." Each mission is signed with a `mission_token` derived from the system date and current Git commit hash, ensuring that every data point in the Mart is scientifically reproducible.