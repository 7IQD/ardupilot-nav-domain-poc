
# List of Tables in nav_master.duckdb

| Seq | Table Name             | Purpose                                        |
| --- | ---------------------- | ---------------------------------------------- |
| 1   | fmt_master             | Schema from BIN (msg_type → params)            |
| 2   | msg_type_master        | Meaning/identity of each msg_type              |
| 3   | mission_master         | Flattened signal store (all values)            |
| 4   | mission_stats          | Mission-level aggregates / sanity              |
| 5   | rule_master            | Anomaly definitions (thresholds, conditions)   |
| 6   | mission_nsat_windows   | Detected GPS (NSats) anomaly windows           |
| 7   | nav_segment_1–5        | Mission segmentation (phases/blocks)           |
| 8   | nav_meta_log           | Metadata / annotations                         |
| 9   | nav_state_master       | State definitions (normal/degraded/etc.)       |
| 10  | nav_sig_state_timeline | Signal state over time                         |
| 11  | nav_mot_state_timeline | Motion state over time                         |
| 12  | nav_evidence_view      | Combined evidence (signals + states + windows) |
| 13  | nav_flight_context     | Flight-level summary/context                   |
| 14  | nav_ai_assistance      | Final diagnosis / root cause output            |

# 0. Configuration Layer (The Metadata Map)

## Table: msg_type_master
| Field Name      | Type     | Description                                  |
|-----------------|----------|----------------------------------------------|
| domain          | VARCHAR  | System domain (NAV, EST, POWER, etc.)        |
| msg_type        | VARCHAR  | ArduPilot Log Message Type (GPS, ATT, IMU)   |
| param_list_json | VARCHAR  | JSON definition of expected parameters       |
| description     | VARCHAR  | Human-readable logic (e.g., Signal Health)   |
| version         | VARCHAR  | Firmware compatibility version (v4.5)        |
┌──────────┐
│ msg_type │
│ ─────────┤
│ AHR2     │
│ ANG      │
│ ATT      │
│ CTUN     │
│ DCM      │
│ GPA      │
│ GPS      │
│ ORGN     │
│ PIDA     │
│ PIDP     │
│ PIDR     │
│ PIDY     │
│ POS      │
│ RATE     │
│ XKF1     │
│ XKF2     │
│ XKF3     │
│ XKF4     │
│ XKF5     │
│ XKFS     │
│ XKQ      │
│ XKT      │
│ XKTV     │
│ XKV1     │
│ XKV2     │ │
└──────────┘
# 1. Ingress Layer (Wide-Flat Raw Telemetry)

## Table: mission_master
| Field Name      | Type     |
|-----------------|----------|
| domain          | VARCHAR  |
| msg_type        | VARCHAR  |
| TimeUS          | BIGINT   |
| inode           | BIGINT   |
| wall_ns         | BIGINT   |
| mavpackettype   | VARCHAR  |
| [Telemetry]     | DOUBLE   |  <-- Grouped: Includes 340+ fields (Roll, Pitch, Load, etc.)
| mission_id      | VARCHAR  |
| segment_id      | BIGINT   |

## Table: nav_meta_log
| Field Name      | Type     |
|-----------------|----------|
| mission_id      | VARCHAR  |
| window_id       | HUGEINT  |
| inode           | BIGINT   |
| TimeUS          | BIGINT   |
| rule_id         | VARCHAR  |
| parameter       | VARCHAR  |
| actual_value    | DOUBLE   |

# 2. Data Collection & Preparation Layer

## Table: mission_stats
| Field Name                      | Type     |
|---------------------------------|----------|
| mission_id                      | VARCHAR  |
| mission_rows                    | BIGINT   |
| segment_count                   | BIGINT   |
| mission_timeus_start            | BIGINT   |
| mission_timeus_end              | BIGINT   |
| mission_duration_us             | BIGINT   |
| mission_msg_type_distinct_count | BIGINT   |
| mission_msg_type_counts         | VARCHAR  |
| mission_nsats_null_count        | HUGEINT  |
| mission_hdop_null_count         | HUGEINT  |
| mission_nsats_distinct_count    | BIGINT   |
| mission_nsats_distinct_values   | VARCHAR  |
| mission_hdop_distinct_count     | BIGINT   |
| mission_hdop_distinct_values    | VARCHAR  |
| mission_nsats_avg               | DOUBLE   |
| mission_nsats_min               | DOUBLE   |
| mission_nsats_max               | DOUBLE   |
| mission_hdop_avg                | DOUBLE   |
| mission_hdop_min                | DOUBLE   |
| mission_hdop_max                | DOUBLE   |
| mission_hdop_gt5_count          | HUGEINT  |

## Table: mission_nsat_windows
| Field Name      | Type     |
|-----------------|----------|
| mission_id      | VARCHAR  |
| window_id       | HUGEINT  |
| start_timeus    | BIGINT   |
| end_timeus      | BIGINT   |
| start_inode     | BIGINT   |
| end_inode       | BIGINT   |
| nsats_value     | DOUBLE   |
| row_count       | BIGINT   |
| segment_count   | BIGINT   |
| window_hdop_avg | DOUBLE   |
| window_hdop_min | DOUBLE   |
| window_hdop_max | DOUBLE   |

# 3. Evidence Layer

## Table: nav_evidence_view (View)
| Field Name    | Type     |
|---------------|----------|
| mission_id    | VARCHAR  |
| window_id     | HUGEINT  |
| nsats_value   | DOUBLE   |
| row_count     | BIGINT   |
| segment_count | BIGINT   |
| start_timeus  | BIGINT   |
| end_timeus    | BIGINT   |
| rule_id       | VARCHAR  |
| parameter     | VARCHAR  |
| actual_value  | DOUBLE   |

# 4. Knowledge Layer

## Table: rule_master
| Field Name  | Type     | Key |
|-------------|----------|-----|
| rule_id     | VARCHAR  | PRI |
| domain      | VARCHAR  |     |
| msg_type    | VARCHAR  |     |
| parameter   | VARCHAR  |     |
| operator    | VARCHAR  |     |
| threshold   | DOUBLE   |     |
| severity    | VARCHAR  |     |
| description | VARCHAR  |     |

# 5. Diagnostic Layer (38 Columns)

## Table: nav_ai_assistance
| Field Name                      | Type     |
|---------------------------------|----------|
| mission_id                      | VARCHAR  |
| window_id                       | INTEGER  |
| rule_id                         | VARCHAR  |
| parameter                       | VARCHAR  |
| actual_value                    | DOUBLE   |
| start_segment_id                | INTEGER  |
| end_segment_id                  | INTEGER  |
| segment_coverage                | INTEGER  |
| window_start_timeus             | BIGINT   |
| window_end_timeus               | BIGINT   |
| window_start_inode              | BIGINT   |
| window_end_inode                | BIGINT   |
| window_duration_us              | BIGINT   |
| window_rows                     | BIGINT   |
| window_msg_type_distinct_count  | BIGINT   |
| window_msg_type_counts          | VARCHAR  |
| window_hdop_avg                 | DOUBLE   |
| window_hdop_min                 | DOUBLE   |
| window_hdop_max                 | DOUBLE   |
| window_hdop_distinct_count      | BIGINT   |
| window_hdop_null_count          | BIGINT   |
| mission_rows                    | BIGINT   |
| mission_timeus_start            | BIGINT   |
| mission_timeus_end              | BIGINT   |
| mission_duration_us             | BIGINT   |
| mission_msg_type_distinct_count | BIGINT   |
| mission_msg_type_counts         | VARCHAR  |
| mission_nsats_null_count        | BIGINT   |
| mission_hdop_null_count         | BIGINT   |
| mission_nsats_distinct_count    | BIGINT   |
| mission_nsats_distinct_values   | VARCHAR  |
| mission_hdop_distinct_count     | BIGINT   |
| mission_hdop_distinct_values    | VARCHAR  |
| threshold_operator              | VARCHAR  |
| threshold_value                 | DOUBLE   |
| threshold_violations            | BIGINT   |
| severity                        | VARCHAR  |
| evidence_summary                | VARCHAR  |