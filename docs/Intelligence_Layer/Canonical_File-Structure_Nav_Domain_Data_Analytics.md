NAV Intelligence Layer
Canonical File Structure


src/
├── df_apis/                              # LAYER 1 — DATA FOUNDATION (Providers)
│   ├── df_api_server.py                  # Secure DuckDB → /api/domain
│   ├── mission_forensic_api.py           # Temporal Anchor (Mission time bounds)
│   └── drone_df_ui.py                    # Read-only analytical bridge
│
├── dashboard/                            # LAYER 2 — INTELLIGENCE (Consumers)
│   ├── NAV_Scorecard_Analysis.ipynb      # Notebook-1 (Pure Consumer)
│   ├── vault_writer.py                   # Evidence freezer (PNG / CSV snapshots)
│   │
│   └── nav/                              # NAV Domain Specialization
│       ├── __init__.py                   # Module initialization
│       ├── nav_data_service.py           # HTTP client (API transport only)
│       ├── nav_stats.py                  # Deterministic math engine
│       ├── nav_action_map.py             # Threshold judge (ArduPilot logic)
│       ├── nav_scorecard.py              # Intelligence formatter
│       ├── nav_controller.py             # Orchestrator (only notebook import)
│       └── nav_live_monitor.py           # Optional live drift visualizer
│
└── bin/
    └── vault/                            # LAYER 0 — DATA VAULT
        ├── warehouse_df/
        │   └── drone_df_views.db         # DuckDB warehouse (fact_ + ui_ views)
        │
        └── dashboard/
            └── nav_audit/                # Immutable mission evidence
                └── M_<mission_id>/       # Snapshot folders (PNG / CSV)