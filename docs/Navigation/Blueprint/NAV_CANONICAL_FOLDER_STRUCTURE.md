nav_project/                     # Root of Nav domain project
│
├── src/ 🛠️                       # All logic
│   ├── router.py                 # Lightweight router, domain-agnostic
│   ├── controller.py             # Controller triggers ELT/view queries
│   └── domains/                  # Per-domain logic & SQL
│       ├── imu/
│       │   ├── imu_schema.sql    # Bronze schema
│       │   ├── imu_transform.sql # Silver / transformations
│       │   └── README.md         # Domain-specific notes
│       ├── gps/
│       │   ├── gps_schema.sql
│       │   ├── gps_transform.sql
│       │   └── README.md
│       ├── ekf/
│       │   ├── ekf_schema.sql
│       │   ├── ekf_alignment.sql # joins GPS + IMU
│       │   └── README.md
│       ├── controller/
│       │   └── controller_metrics.sql
│       └── system/
│           └── system_metrics.sql
│
├── data/                         # Mission data
│   ├── raw/ 📦                    # Immutable, sealed artifacts
│   │   └── m001/                 # Mission 001
│   │       ├── imu/
│   │       │   ├── accel.log
│   │       │   └── gyro.log
│   │       ├── gps/
│   │       │   ├── ublox_pos.bin
│   │       │   └── ublox_vel.bin
│   │       └── meta/
│   │           ├── manifest.json
│   │           └── checksums.sha256
│   └── processed/ 🏗️              # Derived database
│       ├── nav_baseline.duckdb    # Vectorized ELT store (ignored in Git)
│       └── views/                 # Optional: per-domain SQL views
│           ├── imu_view.sql
│           ├── gps_view.sql
│           ├── ekf_view.sql
│           └── system_view.sql
│
├── docs/ 📜                       # Documentation
│   └── domains/                   # Domain-specific reports
│       ├── imu/
│       │   └── imu_report.md
│       ├── gps/
│       │   └── gps_report.md
│       ├── ekf/
│       │   └── ekf_report.md
│       ├── controller/
│       │   └── controller_report.md
│       └── system/
│           └── system_report.md
│
└── .gitignore 🛡️                  # Exclude processed DB, temp files, caches
