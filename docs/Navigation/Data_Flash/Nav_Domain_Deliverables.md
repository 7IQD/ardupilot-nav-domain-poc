# NAV Domain Deliverables

## 1️⃣ Generate logs in SITL

Use the simulator from ArduPilot SITL to produce `.BIN` DataFlash logs.

Process:

```
start SITL
run mission
save .BIN
store in vault
```

Result:

```
bin/vault/df_source/
   SITL_RUN_01.BIN
   SITL_RUN_02.BIN
   ...
```

Goal:

```
20–40 diverse flight logs
```

---

# 2️⃣ Induce known operational failures

Use recurring failures discussed in the ArduPilot community.

Examples:

```
GPS glitch
high vibration
IMU clipping
compass interference
radio signal loss
EKF divergence
```

These create **realistic diagnostic cases**.

Example testing matrix:

| Test | Failure              |
| ---- | -------------------- |
| T1   | GPS glitch           |
| T2   | Vibration spike      |
| T3   | IMU clipping         |
| T4   | Compass interference |
| T5   | Radio loss           |
| T6   | EKF divergence       |

Each test → **1 labeled BIN file**

---

# 3️⃣ Process logs through the NAV pipeline

Your existing architecture runs:

```
BIN
 ↓
Vault B
 ↓
Warehouse Parquet
 ↓
DuckDB Views
 ↓
NAV Domain Services
```

Outputs:

```
clean NAV dataframe
stats
labels
```

---

# 4️⃣ Label logs (hand-verified)

Using the NAV labeler + manual verification.

Example labels:

```
normal
vibration_fault
gps_failure
imu_clipping
ekf_instability
```

Example labeled event table:

```
mission_id
start_time
end_time
phase
label
severity
```

This produces the **training dataset**.

File:

```
nav_training_dataset.parquet
```

---

# 5️⃣ Feature extraction for ML

Features extracted from NAV signals.

Possible features:

```
vibration magnitude
IMU noise
EKF velocity stability
GPS quality
battery voltage drops
radio RSSI
```

Additional NAV-specific features:

```
NSats
HDOP
lat/lng jump
velocity variance
altitude drift
EKF innovations
```

Example feature row:

```
mission_id
vibration_rms
imu_noise
gps_quality
ekf_var
alt_drift
label
```

---

# 6️⃣ Train baseline classifier

Start with simple models:

```
Random Forest
Logistic Regression
```

Goal:

```
predict failure class from telemetry features
```

Example output:

```
Prediction: gps_failure
Confidence: 0.91
```

---

# 7️⃣ Future ML exploration

After baseline works:

```
time-series models
transformers
anomaly detection
```

These will enable **automated flight diagnosis**.

---

# 8️⃣ Create presentation views

Views needed for UI / scorecards.

### NAV scorecard view

```
mission_id
nav_score
stability_score
p95_drift
verdict
```

### NAV event view

```
mission_id
event_id
label
phase
duration
location
```

### ML feature view

```
mission_id
feature_vector
label
```

---

# 9️⃣ Final NAV deliverables

NAV domain will produce:

```
BIN logs
   ↓
Vault
   ↓
Warehouse Parquet
   ↓
DuckDB Views
   ↓
NAV Intelligence
   ↓
Event Labels
   ↓
Training Dataset
   ↓
Failure Classifier
   ↓
Mission Scorecard
```

---

# 🔒 NAV Domain Closure Criteria

NAV domain is **closed only when**:

✔ SITL failure library created
✔ 20–40 labeled logs generated
✔ training dataset built
✔ baseline classifier trained
✔ DuckDB presentation views created
✔ scorecard + labels validated

---

