ardupilot-nav-domain-poc/
├── bin/
│   ├── vault/
│   │   ├── df_source/
│   │   │   ├── bin_anomaly_checker.py
│   │   │   ├── bin_anomaly_injector.py
│   │   │   ├── nav_calibrated_final.BIN
│   │   │   ├── v1_baseline_controlled.bin
│   │   │   └── ... (other BIN/anomaly files)
│   │   ├── warehouse_df/
│   │   │   └── nav_df_master.parquet
│   │   └── processed/
│   │       └── nav_events.parquet
│
├── notebooks/
│   ├── NAV_Mission_Summary.ipynb
│   └── NAV_Mission_Scorecard.ipynb
│
├── src/
│   ├── df_domain_data_services/
│   │   ├── __init__.py
│   │   ├── nav/
│   │   │   ├── __init__.py
│   │   │   ├── nav_labeler.py
│   │   │   ├── nav_data_service.py
│   │   │   ├── nav_stats.py
│   │   │   ├── nav_controller.py
│   │   │   ├── nav_action_map.py
│   │   │   ├── nav_data_integrity_check.py
│   │   │   └── nav_live_monitor.py
│   │   ├── power/
│   │   ├── sys/
│   │   ├── est/
│   │   ├── com/
│   │   ├── vault_writer.py
│   │   ├── mission_analyser.py
│   │   ├── dashboard_ekf.py
│   │
│   ├── runner/
│   │   ├── __init__.py
│   │   ├── df_main.py
│   │   ├── df_refinery.py
│   │   ├── create_labels.py
│   │   ├── create_views.py
│   │   ├── orchestrator.py
│   │   ├── review_time_sync.py
│   │   └── run_df_marts.py
│   │
│   ├── weaving/
│   │   ├── __init__.py
│   │   ├── ingest_df/
│   │   │   ├── __init__.py
│   │   │   ├── nav_df_architect.py
│   │   │   ├── df_mav_ingress_architect.py
│   │   │   ├── est_df_architect.py
│   │   │   ├── com_df_architect.py
│   │   │   ├── power_df_architect.py
│   │   │   ├── sys_df_architect.py
│   │   │   ├── df_action_map.py
│   │   │   └── refiners.py
│   │   └── ...
│   │
│   └── vault/
│       ├── __init__.py
│       ├── clerk.py
│       └── clerk_df.py
│
└── README.md