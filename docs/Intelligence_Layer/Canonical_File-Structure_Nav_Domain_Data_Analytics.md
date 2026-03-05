# Canonical File Structure & Phase 1 NAV Domain Pipeline

---

## Project Layout & Purpose

```

ardupilot-nav-domain-poc/
├─ bin/vault/
│  ├─ drone_df_views.db         # Gold DuckDB database with fact_nav_state_vector, view_clean_est, view_clean_nav
│  └─ warehouse_df/             # Optional Silver-layer parquet files for rebuilding Gold
├─ src/dashboard/nav/
│  ├─ **init**.py               # Module marker
│  ├─ nav_data_service.py       # Service layer: fetch, fuse, scale, score telemetry
│  ├─ app.py                    # FastAPI endpoints: /telemetry, /verdict
│  ├─ nav_action_map.py         # Optional: domain-specific action mapping
│  ├─ nav_controller.py         # Optional controllers for simulation/live integration
│  ├─ nav_live_monitor.py       # Optional live telemetry monitoring
│  ├─ nav_stats.py              # Optional domain statistics
│  └─ verify_nav_gold.py        # Optional terminal verification of fused data
├─ src/utils/
│  ├─ **init**.py               # Module marker
│  ├─ metrics_helpers.py        # Metric calculations: scaling, scoring, mission health
│  ├─ db_connector.py           # Optional DB utilities
│  ├─ db_helpers.py             # Optional DB helper functions
│  ├─ legacy_log_importer.py    # Optional historical log import
│  └─ visualiser.py             # Optional plotting/visualization

```

### Core Phase 1 Files (Minimum Required)

- `nav_data_service.py` → NAV + EST fusion, scaling, scoring, returns DataFrame & summary
- `metrics_helpers.py` → scaling, rolling variance, stability score, mission health
- `app.py` → FastAPI endpoints serving scaled & scored telemetry and AI verdict
- `drone_df_views.db` → Gold DuckDB database

Optional but recommended:

- `verify_nav_gold.py` → Terminal verification of Gold-layer data

### Data Flow & Dependencies

```

[drone_df_views.db]  -->  NavDataService --> metrics_helpers.py
fetch_fused_telemetry() --> scaled & scored DataFrame
get_summary() --> mission-level health & stability
[app.py] --> calls NavDataService
├── /api/nav/telemetry/{mission_id} --> JSON telemetry
└── /api/nav/verdict/{mission_id} --> JSON AI verdict + health

````

**Key Notes:**

- All telemetry scaling and scoring occurs in `NavDataService` using `metrics_helpers.py`.
- API endpoints do **not** query DuckDB directly; they rely on the service layer for consistency.
- Future expansion (POWER, COM domains) should follow the same pattern: `Silver → Gold → Service → API`.

### Phase 1 Execution Steps

1. Verify Gold Data:
   ```bash
   python src/dashboard/nav/verify_nav_gold.py
````

2. Run FastAPI Server:

   ```bash
   python src/dashboard/nav/app.py
   ```
3. Query Endpoints:

   * Telemetry: `GET http://localhost:8000/api/nav/telemetry/manual_run`
   * Verdict: `GET http://localhost:8000/api/nav/verdict/manual_run`
4. Optional Dashboard: Use JSON from `/telemetry` or `/verdict` to display GREEN/AMBER/RED pilot status cards

**Principles for Phase 1**

* **Single Source of Truth:** All scaling, fusion, scoring in `NavDataService`
* **Consistency:** API & terminal scripts return identical metrics
* **Modular Helpers:** `metrics_helpers.py` can be tested independently
* **Extensible:** Ready for additional domains or AI scoring pipelines

```

This is compact, single-section, and contains everything needed for **implementation and reference**.

If you want, I can also **append a one-line “Phase 1 Launch Checklist”** at the bottom to make it copy-paste ready for deployment. Do you want me to do that?
```
