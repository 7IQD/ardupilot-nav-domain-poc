# Flight Telemetry Warehouse: Architecture & Data Flow

## 1. DF Path Processing Stages

| Stage            | Storage Object             | Purpose                                                   | Data Shape               | Example Columns                              |
| ---------------- | -------------------------- | --------------------------------------------------------- | ------------------------ | -------------------------------------------- |
| **Vault B**      | **Sharded Parquets**       | Raw decoded DataFlash messages stored exactly as emitted. | **Message Stream**       | `TimeUS`, `MsgType`, `NSats`, `Roll`, `Volt` |
| **Warehouse DF** | **Domain Master Parquets** | Cleaned domain-specific sensor streams. Null cleanup.     | **Domain Tables**        |                                              |
|                  | `nav_master.parquet`       | Navigation sensor records                                 | GPS specific rows        | `TimeUS`, `NSats`, `Lat`, `Lng`, `HDOP`      |
|                  | `est_master.parquet`       | EKF / estimator timeline                                  | High-freq state spine    | `TimeUS`, `Roll`, `Pitch`, `Yaw`             |
|                  | `power_master.parquet`     | Power system                                              | Battery health           | `TimeUS`, `Volt`, `Curr`, `ConsumedMah`      |
|                  | `com_master.parquet`       | Communication metadata                                    | Link quality             | `TimeUS`, `FixType`, `HDOP`, `VDOP`          |
|                  | `sys_master.parquet`       | Vehicle system state                                      | Mode / arming / failsafe | `TimeUS`, `Mode`, `Armed`, `Failsafe`        |
| **Fact Table**   | `fact_nav_state_vector`    | Clean NAV sensor stream for diagnostics.                  | **Filtered Timeline**    | `mission_id`, `TimeUS`, `NSats`, `Lat`       |
| **Flight State** | `fact_flight_diagnostics`  | Dynamic time alignment using EST spine via ASOF JOIN.     | **Aligned Fusion**       | `TimeUS`, `Roll`, `NSats`, `Volt`, `Mode`    |

---

## 2. Conceptual Data Flow

```text
DataFlash BIN
      │
      ▼
Vault B (Sharded Parquets)
      │
      ▼
Warehouse DF (Domain Master Parquets)

┌───────┬───────┬───────┬───────┬───────┐
│  NAV  │  EST  │ POWER │  COM  │  SYS  │
└───┬───┴───┬───┴───┬───┴───┬───┴───┬───┘
    │       │       │       │       │
    ▼       ▼       ▼       ▼       ▼

Fact Tables (Filtered Signals)
    │               │
    └───────┬───────┘
            ▼

Flight State Fusion (fact_flight_diagnostics)
(ASOF aligned on EST Time Spine)
```
