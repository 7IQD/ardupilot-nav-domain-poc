# Canonical Folder Structure — Data Mart Engine

src/
└── data_mart_engine/
├── main.py # Pulse orchestrator
├── refinery/
│ └── nav_refinery.py # Domain-specific math and slicing
└── config/
└── engine_config.py # Mission & product configuration
## Vault Layout
bin/vault/
├── warehouse/ # Silver Mart (immutable)
├── gold/
│ ├── nav_pilot/
│ ├── nav_ekf/
│ └── nav_forensics/
└── dashboard/
└── <product>/<mission>/

No engine component writes outside its assigned vault boundary.
