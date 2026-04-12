Data Processing Architecture for AI Assisted Root Cause Analysis
==================================================

1. Ingress / Raw Telemetry Layer
--------------------------------
Purpose: Capture all mission telemetry from ArduPilot logs into a wide-flat schema for maximum granularity.

Table: mission_master
- Each row corresponds to a single telemetry message.
- Key fields:
  - mission_id – unique mission identifier
  - msg_type – MAVLink/log message type (e.g., GPS, ATT)
  - TimeUS / inode – precise temporal and data order reference
  - [Telemetry fields] – 300+ parameters per msg_type (roll, pitch, NSats, HDop, etc.)
- Notes:
  - TimeUS + inode allows exact replay and windowing.
  - No pre-filtering; all NAV-domain messages captured.

2. Metadata & Statistical Layer
-------------------------------
Purpose: Summarize mission-wide statistics for fast AI reasoning and feature extraction.

Tables:
  a. mission_stats
     - Aggregates mission-level metrics: rows, segments, NSats/HDop stats.
     - Columns: mission_rows, segment_count, mission_nsats_avg, mission_hdop_min, etc.

  b. mission_nsat_windows
     - Divides mission into windows based on NSats or other telemetry events.
     - Columns: start_timeus, end_timeus, nsats_value, window_hdop_avg
     - Purpose: Allows temporal segmentation of missions for root-cause analysis.

3. Evidence Layer
-----------------
Purpose: Store telemetry anomalies or rule-triggered evidence for AI reasoning.

Table: nav_evidence_view (view)
- Each row: a window + telemetry parameter that triggered a rule.
- Key fields: mission_id, window_id, rule_id, parameter, actual_value
- Aggregates raw telemetry into AI-friendly event windows.

4. Knowledge / Rule Layer
--------------------------
Purpose: Encapsulate domain knowledge and thresholds for telemetry parameters.

Table: rule_master
- Each row defines:
  - rule_id, domain, msg_type, parameter
  - operator, threshold, severity, description
- Used by AI to score telemetry windows and assign violations.

5. Diagnostic / AI Layer
-------------------------
Purpose: Generate AI-assisted root-cause analysis and mission summaries.

Table: nav_ai_assistance
- Combines: windowed evidence + mission stats + rule evaluation.
- Key fields:
  - Window boundaries: window_start_timeus, window_end_timeus
  - Rule evaluation: threshold_operator, threshold_value, threshold_violations, severity
  - Mission-level context: mission_rows, mission_nsats_null_count
- Enables downstream root cause flow, scoring, and AI reasoning.

6. Windowing, Contextualization and Labelling
-----------------------------------------------
Process:
1. Windowing:
   - Segment mission by event triggers or fixed intervals (LAG() on NSats/HDop or maneuvers).
   - Windows stored in mission_nsat_windows with start/end inode & TimeUS.

2. Contextualization:
   - Each window inherits mission-level metadata (mission_stats)
   - Parameter-level info linked via msg_type_master → domain, msg_type, parameter type, description.

3. Labelling:
   - Apply rules from rule_master to windows.
   - Produce nav_evidence_view and nav_ai_assistance records with evidence of threshold violations.

4. Root Cause Flow:
   - AI evaluates rules per window → aggregates to mission segments → identifies primary anomalies and likely root causes.

5. Scorecard Summary:
   - Aggregates AI findings across mission:
     - % windows failing each rule
     - NSats/HDop distributions
     - Domain-specific integrity score (NAV, EST, POWER, COM, SYS)
   - Stored in reporting tables or dashboards.

7. Master Reference Layer
--------------------------
Purpose: Provide a single source of truth for all msg_type → parameters → domain mappings.

Table: msg_type_master
- Columns: domain, msg_type, param_list_json, description, version
- AI & human-readable reference for all telemetry parameters.

8. Key Design Principles
------------------------
- TimeUS + inode: Always used for precise windowing and replay.
- Parameter-driven evidence: parameter column in nav_ai_assistance allows per-field evaluation.
- Denormalized for AI: mission-level, window-level, and evidence-level stats available in one table for faster AI queries.
- Domain-centric grouping: Domains (NAV, EST, POWER, COM, SYS) enable narrowing root cause analysis paths.

Summary:
--------
This structure allows any domain telemetry to be fully analyzed with maximum granularity, clear lineage and AI-ready root cause mapping. It supports windowing, contextualization, labelling, root-cause flow, and mission scorecard generation.
