DATABASE LAYER - OVERVIEW
--------------------------------------------------
1. DESIGN PRINCIPLE
--------------------------------------------------

The system is divided into two layers:

1. Data Layer (SQL / DuckDB)
   - Captures all telemetry and windows
   - Preserves full fidelity and traceability
   - No loss of information

2. Logic Layer (Python / Service)
   - Interprets data into states
   - Performs root-cause reasoning
   - Computes confidence and outputs diagnosis


--------------------------------------------------
2. GLOBAL KEYS
--------------------------------------------------

mission_id   : Unique flight/session identifier
domain       : NAV / EST / POWER / COM / SYS
window_id    : Atomic anomaly segment identifier
TimeUS       : Timestamp (microseconds)
inode        : Log row trace reference

Primary alignment key:
(mission_id, window_id)

--------------------------------------------------
3. DATA SCHEMA (BY LAYER)
--------------------------------------------------

A. INGRESS LAYER

Table: mission_master
Purpose: Raw telemetry ingestion

Fields:
- mission_id
- TimeUS
- msg_type
- parameter
- value
- domain
- inode
- segment_id

--------------------------------------------------

B. WINDOW LAYER

Table: mission_nsat_windows
Purpose: Fine-grained NSats segmentation

Fields:
- mission_id
- window_id
- start_timeus
- end_timeus
- start_inode
- end_inode
- nsats_value
- row_count
- segment_count
- window_hdop_avg
- window_hdop_min
- window_hdop_max

Note:
- Each window represents a constant NSats run
- Windows are intentionally granular
- DO NOT merge in SQL

--------------------------------------------------

C. ANCHOR / META LAYER

Table: nav_meta_log

Purpose:
- Anchor each window to traceable telemetry
- Provide rule linkage

Fields:
- mission_id
- window_id
- inode
- TimeUS
- rule_id
- parameter
- actual_value

--------------------------------------------------

D. BASELINE LAYER

Table: mission_stats

Purpose:
- Store mission-level baseline metrics

Fields:
- mission_id
- domain
- parameter
- mean_val
- std_dev
- p95_val
- min_val
- max_val

Optional fields (current system):
- mission_rows
- segment_count
- mission_hdop_min
- mission_hdop_max

--------------------------------------------------

E. EVIDENCE LAYER

View: nav_evidence_view

Purpose:
- Link windows with triggered rules
- Provide explainability

Fields:
- mission_id
- window_id
- nsats_value
- row_count
- segment_count
- start_timeus
- end_timeus
- rule_id
- parameter
- actual_value

--------------------------------------------------

F. DETECTION LAYER

Table: rule_master

Purpose:
- Define anomaly detection rules

Fields:
- rule_id
- domain
- msg_type
- parameter
- operator
- threshold
- severity
- description

Example:
- NSats == 0 → GPS Loss
- HDOP > 5 → Poor GPS quality

--------------------------------------------------

G. DIAGNOSIS LAYER

Table: root_cause_master

Purpose:
- Define root-cause logic

Fields:
- cause_id
- domain
- cause_name
- parameter_class
- condition_type
- min_conditions_required
- suggested_fix
- base_confidence

Requirements:
- Must define mandatory conditions
- Must support multi-parameter evaluation
- Must remain domain-independent

--------------------------------------------------

H. OUTPUT LAYER

Table: nav_ai_assistance

Purpose:
- Store final diagnosis

Fields:
- mission_id
- domain
- window_id
- root_cause
- confidence_score
- match_score
- suggested_fix
- evidence_summary

Note:
- Output is stored per window
- Derived from logic layer

--------------------------------------------------
4. PROCESS FLOW (19-STEP CONTRACT)
--------------------------------------------------

1. rule_master detects anomalies
2. nav_evidence_view captures evidence
3. anomaly-driven segmentation
4. mission_nsat_windows created
5. extract window telemetry
6. compute window stats
7. compute mission baseline
8. deviation analysis
9. NSats classification (LOSS / WEAK / OK)
10. HDOP classification (POOR / GOOD)
11. EKF classification (STABLE / UNSTABLE)
12. context layer creation
13. root-cause mapping
14. mandatory condition check
15. optional condition evaluation
16. match_score calculation
17. trigger decision
18. persistence + strength evaluation
19. write nav_ai_assistance

--------------------------------------------------
5. ARCHITECTURE RULES
--------------------------------------------------

1. Do not alter schema during logic development
2. Preserve all windows (no SQL merging)
3. Use Python for:
   - classification
   - grouping
   - trend detection
   - reasoning
4. Use window_id for alignment across parameters
5. Maintain domain-agnostic design
6. Store only final results in nav_ai_assistance

--------------------------------------------------
6. KEY DESIGN INSIGHT
--------------------------------------------------

SQL windows = atomic signal units
Python logic = semantic interpretation

Aggregation is LOGICAL, not PHYSICAL.

--------------------------------------------------
7. ONE-LINE SUMMARY
--------------------------------------------------

Store everything in SQL, interpret in Python, diagnose using rules, and write final results to nav_ai_assistance.

--------------------------------------------------
END OF DOCUMENT
--------------------------------------------------
```
