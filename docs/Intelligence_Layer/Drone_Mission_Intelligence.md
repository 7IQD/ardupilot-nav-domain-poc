# 🏛️ Drone Mission Intelligence

Reference for telemetry domains, key fields and intelligence potential.

---

## **Domain 1: Navigation (fact_nav)**
**Source:** GPS & Position Updates

| Field Name       | Type     | Description / Use |
|------------------|---------|-----------------|
| mission_id        | VARCHAR | Join key across domains |
| mission_time      | DOUBLE  | Phase segmentation & sync |
| wall_ns           | BIGINT  | High-res time anchor |
| mavpackettype     | VARCHAR | Packet classification |
| lat               | DOUBLE  | Latitude |
| lng               | DOUBLE  | Longitude |
| nSats             | DOUBLE  | GPS satellites count |
| hDop              | DOUBLE  | GPS accuracy / precision |
| spd               | DOUBLE  | Speed dynamics |
| vZ                | DOUBLE  | Vertical velocity / altitude drift |
| relHomeAlt        | DOUBLE  | Relative altitude from home |
| relOriginAlt      | DOUBLE  | Relative altitude from origin |

---

## **Domain 2: System Stress (fact_sys)**
**Source:** Vibration & Control Targets

| Field Name | Type   | Description / Use |
|------------|-------|-----------------|
| mission_id  | VARCHAR | Join key |
| mission_time | DOUBLE | Phase sync |
| thI         | DOUBLE | Input throttle / pilot control |
| thO         | DOUBLE | Output throttle / actuator control |
| dAlt        | DOUBLE | Delta altitude (control target) |
| alt         | DOUBLE | Actual altitude (alignment with NAV) |
| dCRt        | DOUBLE | Delta control rate |
| CRt         | DOUBLE | Control rate output |
| vibeX       | DOUBLE | X-axis vibration |
| vibeY       | DOUBLE | Y-axis vibration |
| vibeZ       | DOUBLE | Z-axis vibration (hover fault) |
| clip        | DOUBLE | Actuator saturation / clipping indicator |

---

## **Domain 3: Estimator / EKF (fact_est)**
**Source:** State Prediction & Innovations

| Field Name | Type   | Description / Use |
|------------|-------|-----------------|
| mission_id  | VARCHAR | Join key |
| mission_time | DOUBLE | Phase sync |
| pE          | DOUBLE | Position error X |
| pD          | DOUBLE | Position error Y |
| vWN         | DOUBLE | Wind influence North |
| vWED        | DOUBLE | Wind influence East |
| iDX         | DOUBLE | Innovation delta X |
| iDY         | DOUBLE | Innovation delta Y |
| iS          | DOUBLE | Innovation delta State |

---

## **Domain 4: Power & Metabolism (fact_power)**
**Source:** Electrical Health & Battery

| Field Name | Type   | Description / Use |
|------------|-------|-----------------|
| mission_id  | VARCHAR | Join key |
| mission_time | DOUBLE | Phase sync |
| volt        | DOUBLE | Voltage monitoring |
| curr        | DOUBLE | Current |
| currTot     | DOUBLE | Total current consumption |
| enrgTot     | DOUBLE | Total energy used |
| temp        | DOUBLE | Temperature / thermal stress |
| remPct      | BIGINT | Battery remaining (%) |

---

## **Domain 5: Communication (fact_communication)**
**Source:** Link Quality & RC Pilot Input

| Field Name | Type   | Description / Use |
|------------|-------|-----------------|
| mission_id  | VARCHAR | Join key |
| mission_time | DOUBLE | Phase sync |
| message     | VARCHAR | Event / packet logging |
| c1          | DOUBLE | RC Roll |
| c2          | DOUBLE | RC Pitch |
| c3          | DOUBLE | RC Throttle |
| c4          | DOUBLE | RC Yaw |
| c5          | DOUBLE | RC Mode |

---

## **Intelligence Mapping**

| Domain Pair | Observables                         | Insight / Score Potential |
|-------------|-------------------------------------|---------------------------|
| NAV + SYS   | alt drift, vZ, vibeZ               | Stability / Hover Faults |
| NAV + EST   | hDop, pE, pD, iDX, iDY             | Accuracy / Filter Health |
| SYS + POWER | vibeX/Y/Z, curr, enrgTot, temp     | System Stress / Endurance |
| COMM        | RC channels, messages               | Pilot Input / Link Reliability |
| All Domains | Weighted KPIs across NAV, EST, SYS | Mission Scorecard / Readiness |