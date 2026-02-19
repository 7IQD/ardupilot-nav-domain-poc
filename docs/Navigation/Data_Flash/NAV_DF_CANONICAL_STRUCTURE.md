# NAV-DF / Drone-DF Canonical File Structure

A deterministic, DataFlash-centric layout for NAV refinement and DF pipelines.

| Directory / File                     | Purpose |
|-------------------------------------|---------|
| `bin/vault/df_source/`              | The Source: Authoritative `.BIN` logs (Input). |
| `bin/vault/vault_b/`                | The Ingest Staging: Transient `.parquet` shards (Auto-cleaned every run). |
| `bin/vault/warehouse_df/`           | The Engine Room: Final destination for structured navigation data. |
| ├── `nav_df_master.parquet`         | Master Artifact: Consolidated, columnar analytical dataset. |
| └── `nav_df_vault.db`               | Vault: DuckDB instance for high-speed SQL queries and forensic views. |
| `weaving/ingest_df/nav/`            | Logic Folder: NAV DFReader extraction and domain processing. |
| ├── `nav_df_architect.py`           | DFReader extraction & staging logic for NAV domain. |
| ├── `nav_refinery.py`               | Refinement & transformation logic reusing NAV-PoC module. |
| ├── `clerk.py`                      | Orchestration & helper functions for processing, validation, and vault management. |
| └── `__init__.py`                   | Python package marker for NAV folder. |
| `core/utils/`                        | Shared utilities for all domains. |
| ├── `metric_helpers.py`             | Standardized math helpers: Z-score, RMS, thresholds. |
| ├── `unit_converters.py`            | Domain unit conversions (rad → deg, m/s → km/h, etc.). |
| └── `time_sync_utils.py`            | Aligns ArduPilot boot-time to UTC / global timestamp sync. |
| `runner/df_main.py`                  | Orchestrator: Runs 3-pass workflow (Purge vault → Shard → Merge → Mart). |
| `runner/drone_df_ui.py`             | Schema Builder: Creates DuckDB views for UI, analytics, and scorecards. |
| `core/domain_marts/`                 | Service Marts: Analytical computation and domain metrics. |
| ├── `nav_reliability.py`            | NAV domain scoring (GPS, EKF, Drift, Sats). |
| ├── `est_accuracy.py`               | Estimator residuals and innovation metrics. |
| └── `power_health.py`               | Voltage, sag, and battery health metrics. |
| `core/dx_service_bus/`               | DX Service Bus: Canonical broker for domain messages. |
| ├── `dx_router.py`                  | Multi-conferencing / subscriber logic. |
| └── `contracts.py`                  | Standardized domain schemas for API and dashboard. |
| `core/scorecards/`                   | Decision Layer: Root cause mapping and multi-phase scoring. |
| ├── `mpfi_engine.py`                | Weighted scoring logic across domains. |
| └── `domain_diagnostics.py`         | Root cause inference engine for alerts / remediation. |
| `dx_service_apis/`                   | Gateway APIs: Exposes processed telemetry & scorecards. |
| ├── `main.py`                        | FastAPI entry point. |
| └── `routes/`                        | Domain endpoints. |
| ├── `domain_telemetry.py`           | Standardized telemetry streaming. |
| └── `mission_analytics.py`          | Scorecard exposure for dashboards. |
| `engine3_dashboard/`                 | Front-end: Svelte-based integrated domain scorecards. |
| ├── `package.json`                    | Node dependencies for dashboard. |
| ├── `src/lib/dx_client.js`          | Bus subscriber client for real-time updates. |
| └── `src/routes/+page.svelte`       | Dashboard main view integrating all domains. |
| `logs/nav_analysis/`                 | Evidence Locker: Forensic reports, audit logs, and timing validation. |
