# Current Status – ArduPilot Log Warehouse + Diagnostics Pipeline

## 1. Project Goal

Preparing infrastructure for the **AI-Assisted Log Diagnosis** project suggested by the ArduPilot community on
ArduPilot Discourse.

Mentor advice recommends:

1. Generate logs using SITL
2. Induce common failures
3. Group failures into diagnosis categories
4. Hand-label logs
5. Train a classifier

---

# 2. Current System Built

A **telemetry data warehouse pipeline** for ArduPilot `.BIN` logs has been implemented.

Architecture:

```
ArduPilot BIN logs
        ↓
MAVLink log parser
        ↓
Domain Architect ingestion
        ↓
Shard storage (Parquet)
        ↓
Universal Refiner
        ↓
Domain Warehouse tables
        ↓
SQL analytics (DuckDB)
```

SQL engine used:
DuckDB

Storage format:
Parquet telemetry lake.

---

# 3. Domain Telemetry Warehouse

The pipeline produces **five telemetry domains**:

```
bin/vault/warehouse_df/

nav_df_master.parquet
est_df_master.parquet
sys_df_master.parquet
power_df_master.parquet
com_df_master.parquet
```

Each domain groups related telemetry messages.

| Domain | Data                          |
| ------ | ----------------------------- |
| NAV    | GPS position, altitude, speed |
| EST    | IMU, vibration, EKF estimates |
| SYS    | CPU load and system metrics   |
| POWER  | battery telemetry             |
| COM    | radio signal / communication  |

---

# 4. EST Domain Verification

The **EST domain** contains sensor telemetry required for diagnostics:

```
IMU
VIBE
EKF
ATT
```

Fields verified in warehouse:

```
TimeUS
Roll Pitch Yaw
VN VE VD
VibeX VibeY VibeZ
GyrX GyrY GyrZ
AccX AccY AccZ
Clip
```

Dataset statistics:

```
Total rows:        31,370
IMU samples:       22,408
Vibration samples: 8,962
```
---

# 5. Key Architecture Feature Implemented

A **Universal Refiner** was implemented to prevent telemetry loss.

Refiner logic:

```
Expected schema columns
        +
Automatically discovered sensor fields
        =
Final warehouse schema
```

This allows the system to **auto-capture new telemetry fields** such as:

```
VIBE
IMU
future sensors
EKF innovations
```

without rewriting the schema.

This is important for **research experiments and SITL failure injection**.

---

# 7. The mentor requirements:

> generate logs → induce failures → label → train classifier

### Generate logs in SITL

Run simulated flights to produce `.BIN` logs.

---

### Induce known failures

Examples from ArduPilot forums:

```
GPS glitch
high vibration
IMU clipping
compass interference
radio signal loss
EKF divergence
```

---

### 4️⃣ Label logs

Example labels:

```
normal
vibration_fault
gps_failure
imu_clipping
ekf_instability
```

---

### Train a simple classifier

Start with:

```
random forest
logistic regression
```

Then later explore:

```
time-series models
transformers
anomaly detection
```
Possible features for ML:

```
vibration magnitude
IMU noise
EKF velocity stability
GPS quality
battery voltage drops
radio RSSI
```

