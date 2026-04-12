==========================================================================
          ARDUPILOT AI-ASSISTED LOG DIAGNOSIS: GPS LOSS EVIDENCE SUMMARY
==========================================================================
`mission_master → windows → anchor → evidence → AI assistance → root cause`

1. DATA COMPRESSION & INGESTION PERFORMANCE
--------------------------------------------------------------------------
Source Table: mission_master (Raw Telemetry)
Row Count: 1,264,621 rows

Refined Table: mission_nsat_windows (Event-Based Windows)
Row Count: 4,411 rows
Compression Ratio: ~286:1

Logic:
- Uses SQL LAG window functions to detect state changes in NSats.
- Groups continuous telemetry into stable "regimes" to filter noise.
- Isolates discrete GPS performance events for downstream AI analysis.

Purpose:
- Reduces data volume while preserving critical events.
- Provides structured windows for evidence collection.

2. TRACEABILITY & INTEGRITY (THE ANCHOR LAYER)
--------------------------------------------------------------------------
Anchor Table: nav_meta_log
Row Count: 4,411 rows (1:1 match with mission_nsat_windows)

Logic:
- Maps each identified window to its start_inode and TimeUS from the original .BIN file.
- Assigns a rule_id (e.g., 'N-1') to the canonical firmware parameter (NSats).

Purpose:
- Ensures 100% data integrity despite parameter naming drift or aliases.
- Provides the "Evidence Link" required for root-cause detection.

3. FEATURE ENGINEERING & AI ASSISTANCE PIPELINE
--------------------------------------------------------------------------
View: nav_evidence_view
Logic:
- LEFT JOIN between mission_nsat_windows and nav_meta_log.

Captured Metrics:
- nsats_value: Actual satellite count per window.
- row_count: Duration or persistence of the state.
- window_hdop_avg/min/max: Signal quality metrics.
- start_timeus / end_timeus: Temporal bounds for AI analysis.

Final Output: nav_ai_assistance
Goal:
- Translates structured SQL evidence into probable root cause events
  (e.g., T1 GPS Degradation) with a calculated confidence score.

4. SQL IMPLEMENTATION (CORE LOGIC)
--------------------------------------------------------------------------
-- Window Generation Logic
WITH ordered AS (
    SELECT *, LAG(NSats) OVER (PARTITION BY mission_id ORDER BY TimeUS) AS prev_nsats
    FROM mission_master
),
flagged AS (
    SELECT *, CASE WHEN NSats IS DISTINCT FROM prev_nsats THEN 1 ELSE 0 END AS is_new_window
    FROM ordered
),
grouped AS (
    SELECT *, SUM(is_new_window) OVER (
        PARTITION BY mission_id ORDER BY TimeUS ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS window_id
    FROM flagged
)
SELECT
    mission_id,
    window_id,
    MIN(TimeUS) AS start_timeus,
    MAX(TimeUS) AS end_timeus,
    MIN(inode) AS start_inode,
    MAX(inode) AS end_inode,
    ANY_VALUE(NSats) AS nsats_value,
    COUNT(*) AS row_count,
    COUNT(DISTINCT segment_id) AS segment_count,
    AVG(HDop) AS window_hdop_avg,
    MIN(HDop) AS window_hdop_min,
    MAX(HDop) AS window_hdop_max
FROM grouped
GROUP BY mission_id, window_id
ORDER BY window_id;

--------------------------------------------------------------------------
Notes:
- Each layer builds on the previous: mission_master → mission_nsat_windows → nav_meta_log → nav_evidence_view → nav_ai_assistance.
- This structure enables clean, reproducible, AI-assisted root-cause detection.
- Windows are event-driven, not fixed intervals, ensuring meaningful telemetry segmentation.
- All temporal references rely on TimeUS + inode for precise replay and alignment.
==========================================================================

5. Middleware -> Root Cause Flow

Raw telemetry (mission_master)
Already filtered by rule_master thresholds.
Only relevant NAV-domain data passes through.

Windowing & Anchoring
mission_nsat_windows: breaks mission into discrete windows based on NSats/state changes.
nav_meta_log: anchors each window to precise inode/TimeUS, ensuring traceability.

Contextual Summaries
mission_stats & nav_stats: provide mission-level and window-level metadata for AI reasoning.

Evidence & AI Middleware
nav_evidence_view: captures rule-triggered anomalies per window.
nav_ai_assistance: combines windows, evidence, and stats to form a structured, AI-ready view.

Root Cause Reasoning
Middleware tables act as fully equipped pipelines: all relevant windows, rules, and metrics are aligned.
AI/analyst uses this 360° view to convert observed anomalies (“cows”) into verified root causes (“bulls”) with confidence scores.

In short: mission_master → windows → anchor → evidence → AI assistance → root cause. The middleware ensures no information is lost and all signals are aligned for reasoning.