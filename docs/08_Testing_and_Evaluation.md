# Testing and Evaluation (NAV Domain)

## Purpose

Controlled SITL tests are used to generate reproducible NAV anomalies and validate the RCA pipeline.

These tests produce .BIN logs which are processed through the DF pipeline and NAV service layer.

---

## Test Setup

NAV test scripts are used to simulate flight anomalies in SITL.

Location:
~/tests/

### Available Test Scripts

- gps_test_gps_loss.py         → GPS signal loss
- gps_test_GPS_EKF_GLITCH.py   → GPS glitch affecting EKF
- gps_test_vibration.py        → High vibration conditions
- gps_test_imu_failure.py      → IMU noise / clipping
- gps_test_com_failure.py      → Communication link failure

---

## Generated Test Logs

Logs are stored in:
bin/vault/df_source/

### Test Cases

| ID | Scenario | Description |
|----|----------|-------------|
| T1 | GPS Loss | Loss of satellite lock |
| T2 | Vibration | High vibration impact |
| T3 | IMU Failure | IMU clipping / noise |
| T4 | Compass Failure | Magnetic interference |
| T5 | COM Link Loss | Radio / telemetry loss |
| T6 | GPS + EKF | GPS glitch affecting EKF |

---

## Validation Objective

Each test case is processed through the NAV pipeline to verify:

- anomaly detection (via nav_windows)
- correct state mapping (LOSS / DEGRADED / HEALTHY)
- mismatch detection (sensor vs FC)
- window generation (start/end TimeUS, inode)
- deterministic RCA output

---

## Expected Output

For each anomaly:

- detected windows with duration
- state transitions (sensor vs FC)
- root cause classification
- confidence score
- traceable evidence (TimeUS, inode)

---

## Role in System

These test cases ensure:

- pipeline correctness
- repeatable validation
- coverage across NAV anomaly types

They act as a controlled dataset for verifying the service layer and database pipeline.

---

## Note

Detailed evidence and step-by-step validation are maintained in notebooks:

~/notebooks/**.ipynb