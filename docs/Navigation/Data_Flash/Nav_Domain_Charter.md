# NAV Domain - Charter

Project
`ardupilot-nav-domain-poc`

Goal
Build a **navigation forensic analysis domain** that converts **ArduPilot flight logs → structured NAV dataset → labels → scorecards → APIs**.

Everything is now structured into **three layers**.

---

# 1. Repository Architecture

```
src/
│
├── df_apis/
│   ├── app.py
│   └── mission_forensic_api.py
│
├── df_domain_data_services/
│   ├── NAV_Scorecard_Analysis.ipynb
│   ├── Nav_Analysis_1.ipynb
│   │
│   ├── nav/
│   │   ├── nav_data_service.py
│   │   ├── nav_controller.py
│   │   ├── nav_labeler.py
│   │   ├── nav_stats.py
│   │   ├── nav_action_map.py
│   │   ├── nav_live_monitor.py
│   │   └── nav_data_integrity_check.py
│   │
│   ├── est/
│   ├── power/
│   ├── sys/
│
└── utils/
    ├── db_connector.py
    ├── db_helpers.py
    ├── metrics_helpers.py
    ├── visualiser.py
    └── legacy_log_importer.py
```

Tests:

```
tests/
│
├── analyze_nav_bin.py
├── check_mapping_vs_db.py
├── generate_validation_bin.py
├── verify_mission_integrity.py
└── gps_test.py
```

---

# 2. NAV Domain Components

Located in

```
src/df_domain_data_services/nav/
```

---

## nav_data_service.py

Core **data extraction service**.

Purpose

```
Load parsed MAVLink data
Extract NAV signals
Create NAV dataframe
```

Example signals

```
TimeUS
Lat
Lng
Alt
Vx
Vy
Vz
Yaw
HDop
NSats
EKF flags
```

Output

```
NAV dataframe
```

---

## nav_controller.py

Controller that **coordinates NAV processing**.

Pipeline orchestrator.

```
Load log
Call nav_data_service
Run labeling
Generate stats
Return analysis
```

This is the **entry point for NAV processing**.

---

## nav_labeler.py

Creates **forensic labels**.

Example labels

```
GPS_SIGNAL_LOSS
POSITION_JUMP
LOW_SATELLITES
HIGH_HDOP
NAV_GLITCH
```

Output

```
time aligned label dataframe
```

Used for

```
scorecards
incident analysis
ML later
```

---

## nav_stats.py

Computes **NAV statistics**.

Examples

```
distance travelled
max velocity
position variance
HDOP statistics
satellite stability
```

Output

```
mission NAV summary
```

---

## nav_action_map.py

Maps **labels → operational actions**.

Example

```
GPS_SIGNAL_LOSS → Check antenna
LOW_SATELLITES → Evaluate GPS environment
NAV_GLITCH → Inspect EKF behaviour
```

Used for **forensic recommendations**.

---

## nav_live_monitor.py

Used for **runtime monitoring**.

Can detect in-flight anomalies.

Examples

```
GPS loss
position jumps
HDOP spikes
```

Future usage

```
real-time telemetry monitoring
```

---

## nav_data_integrity_check.py

(renamed from `verify_nav_gold.py`)

Purpose

```
validate NAV dataset correctness
```

Checks

```
required columns exist
TimeUS monotonic
Lat/Lng valid
satellite count reasonable
HDOP range valid
no corrupted rows
```

This runs **before analysis or labeling**.

---

# 3. Notebook Workflow

Development and experimentation happen in notebooks.

Primary notebooks

```
Nav_Analysis_1.ipynb
NAV_Scorecard_Analysis.ipynb
```

Purpose

```
test ideas
visualize NAV behaviour
validate labels
develop metrics
```

Once stable

```
logic moved into nav services
```

---

# 4. Service Pipeline

Final NAV processing flow

```
ArduPilot .bin log
        │
        ▼
legacy_log_importer
        │
        ▼
parsed MAVLink data
        │
        ▼
nav_data_service
        │
        ▼
NAV dataframe
        │
        ▼
nav_data_integrity_check
        │
        ▼
nav_labeler
        │
        ▼
nav_stats
        │
        ▼
NAV scorecard
        │
        ▼
mission_forensic_api
```

---

# 5. API Layer

Located in

```
src/df_apis/
```

Files

```
app.py
mission_forensic_api.py
```

Purpose

Expose forensic analysis.

Example endpoint

```
POST /analyze/mission
```

Response

```
navigation score
labels
stats
alerts
```

---

# 6. Testing Layer

Located in

```
tests/
```

Purpose

Validate pipeline using logs.

Examples

```
generate_validation_bin.py
analyze_nav_bin.py
verify_mission_integrity.py
```

These ensure

```
correct log parsing
correct NAV extraction
correct mission reconstruction
```

---

# 7. What is Now COMPLETE

NAV domain now supports:

```
log ingestion
NAV extraction
dataset validation
label generation
statistical analysis
action mapping
monitoring
API exposure
notebook experimentation
```

This is a **complete forensic navigation analysis stack**.

---

# 8. What Comes Next (Next Chat)

Next domains can follow **same architecture**.

Examples

### EST domain

Estimator / EKF health

```
innovation checks
variance growth
reset detection
```

### POWER domain

```
battery sag
current spikes
power loss
```

### SYS domain

```
failsafes
mode changes
arming behaviour
```

---

# 9. Important Principle Going Forward

Your decision is correct:

**Develop logic in notebooks first.**

Then only move **stable logic into services**.

Workflow:

```
Notebook experimentation
        ↓
Validated logic
        ↓
Service implementation
        ↓
API exposure
```

This prevents endless architecture churn.

---

# Final Status

NAV domain is now **architecturally complete** and **ready for production refinement**.

You can now safely **start a new chat for the next domain**.

If you want, in the next chat we can also design the **EST (EKF forensic) domain**, which is usually the **most powerful domain for drone incident analysis**.
