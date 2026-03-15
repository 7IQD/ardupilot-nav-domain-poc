## NAV Domain Controlled Failure Test Plan

## Start SITL exactly as before

Run SITL and ensure the MAVLink port is the same.

```
127.0.0.1:14551
```
## SITL Failure Injection Test Matrix (NAV Domain)

| Test | Failure              | Parameter          |
| ---- | -------------------- | ------------------ |
| T1   | GPS loss             | `SIM_GPS1_NUMSATS` |
| T2   | Vibration spike      | `SIM_VIB_AMP`      |
| T3   | IMU failure          | `SIM_ACCEL_FAIL`   |
| T4   | Compass interference | `SIM_MAG_ERROR`    |
| T5   | Radio loss           | `SIM_RC_FAIL`      |
| T6   | EKF instability      | `SIM_GPS_GLITCH_X` |

---

## Flight Telemetry transitions:

```
baseline (20s)
fault (10–15s)
recovery (10s)
```
## Stop SITL and capture the BIN

Then move the file to your vault exactly as designed:

```
bin/vault/df_source/

T1_GPS_LOSS.BIN
T2_VIBRATION.BIN
T3_IMU_FAIL.BIN
T4_COMPASS.BIN
T5_RADIO_LOSS.BIN
T6_EKF_DRIFT.BIN
```

---

## Run your existing NAV pipeline

Exactly the same process you already validated:

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
 ↓
Labels
```

---

## Verify anomaly appears in NAV signals

checks:

```
GPS → NSats drop
IMU → vibration rise
EKF → velocity innovation
Compass → heading jump
RC → RSSI loss
```
## Add label

```
mission_id: T1_GPS_LOSS
label: gps_failure
severity: high
```
Append to:

```
nav_training_dataset.parquet
```

You already proved the method with `gps_test.py`.

# Sequence of BIN File Generation:

```
start SITL
run failure script
stop SITL
collect BIN
run NAV pipeline
verify signals
label
```

Repeat until **20–40 logs exist**.

---
