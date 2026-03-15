### NAV Domain – Fault Test (Summary)

**Objective**
Create a **controlled vibration anomaly dataset** from SITL for the NAV domain AI/log-analysis pipeline.

---

**Test Script Execution**
Script used:
`gps_test_vibration.py`

Actions performed:

```
connect SITL → arm vehicle
↓
spin motors with small throttle
↓
record baseline vibration
↓
inject high vibration via SIM parameters
↓
recover to normal
```

---

**Observed Telemetry**

Key MAVLink messages:

```
RAW_IMU
VIBE
```

Example values from log:

Baseline

```
timestamp	TimeUS	IMU	VibeX	VibeY	VibeZ	Clip
1773196725	48044108	1	0.0051981	0.005972266	0.005679397	0
1773196725	48144068	0	36.20383072	36.27555847	36.29586029	2
1773196725	48144068	1	0.005806895	0.005585691	0.005543423	0
1773196725	48244028	0	74.82375336	74.71697235	74.95243835	102
1773196725	48244028	1	0.005567632	0.005325561	0.005456407	0
1773196725	48344821	0	141.7180023	141.6444702	142.3105774	166
1773196725	48344821	1	0.005759933	0.005702475	0.779123247	0
1773196725	48444781	0	126.9576645	126.9259567	126.997818	266
1773196725	48444781	1	0.005559797	0.005670415	0.566647232	0
1773196725	48544741	0	169.9796143	170.0072937	170.1989899	331
1773196725	48544741	1	0.005484664	0.005553164	0.49556306	0
1773196725	48644701	0	163.6239014	163.685318	163.4685364	395
1773196725	48644701	1	0.005924406	0.00538499	0.310792387	0
1773196726	48744661	0	132.7223969	133.207077	133.2967224	495
1773196726	48744661	1	0.005697237	0.005949114	1.721778989	0

Injected vibration

```
VibeX ≈ 170
VibeY ≈ 170
VibeZ ≈ 170
Clip ≈ 331
```

Meaning:

* **severe vibration spike**
* **IMU clipping triggered**
* ideal anomaly dataset

---

**BIN Log Generated**

Location:

```
~/ardupilot-nav-domain-poc/bin/vault/df_source
```

File created:

```
T2_VIBRATION_RUN01.BIN
```

Size ≈ **2.2 MB**

---

** Log Verification**

Checked log types:

```
mavlogdump.py 00000008.BIN --show-types
```

Confirmed presence of:

```
IMU
VIBE
GPS
ATT
BARO
```

Exported VIBE CSV for inspection.

---

**6️⃣ Dataset Naming Convention**

Existing vault dataset:

```
T1_GPS_LOSS_RUN01.BIN
T2_VIBRATION_RUN01.BIN
```

** NAV Data Pipeline Context**

These BIN files feed the NAV DIKW pipeline:

```
BIN logs (vault)
     ↓
df_main
     ↓
decoded message tables
(GPS, IMU, VIBE, ATT, EKF)
     ↓
NAV analytics
     ↓
fault labels
     ↓
AI anomaly training dataset
```

---

**9️⃣ Current Fault Dataset Status**

| Test | Fault                    | Status     |
| ---- | ------------------------ | ---------- |
| T1   | GPS Loss                 | ✅ Complete |
| T2   | Vibration / IMU clipping | ✅ Complete |
| T3   | IMU failure              | ⏳ Next     |
| T4   | Compass interference     | ⏳ Later    |
| T5   | EKF divergence           | ⏳ Later    |

---

