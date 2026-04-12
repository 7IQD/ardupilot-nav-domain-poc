==========================================================================
                Navigation Domain : USE CASE : GPS LOSS POC
==========================================================================
                    Architecture & Protocol
==========================================================================
--------------------------------------------------------------------------
PART 1:
--------------------------------------------------------------------------
1. Objective
Detect and explain the GPS signal loss branch from the mission log using the existing NAV DuckDB tables. The output must be deterministic, traceable, and supported by evidence stored in nav_ai_assistance.

2. Scope
Domain: NAV
Primary trigger: NSats
Anomaly class: N-1 / NSats = 0
Primary root cause: GPS_SIGNAL_LOSS
Fallback root cause: GPS_DEGRADATION
Exclusions: No ML model, no multi-parameter diagnosis, no redesign, no Z-score logic, no new persistent tables

3. Existing Inputs
A. Source and control tables
- rule_master: Defines the active rule, threshold logic, and branch policy.
- nav_meta_log: Provides the anchor layer: mission/log context, TimeUS, inode, rule_id, parameter, actual_value.
- mission_nsat_windows: Provides NSats windows, duration, persistence, and zero-value spans.
- nav_ai_assistance: Final diagnostic output table for explainable branch selection.

4. Derived Computations (Computed at runtime)
- threshold_violations: Count or measure of NSats = 0 violations in a window.
- window_duration: Duration of the continuous zero-NSats span.
- repeated_zero_count: Number of zero-NSats occurrences in the mission window.
- parameter_strength: Strength of the anomaly based on violations.
- time_factor: Persistence score based on window duration.
- confidence_score: Final confidence score derived from strength and duration.
- root_cause: Final selected branch label.
- decision_reason: Human-readable explanation of why the branch was selected.

5. Pipeline Architecture
rule_master → nav_meta_log → mission_nsat_windows → branch evaluation → scoring → decision → nav_ai_assistance

6. Execution Logic
Step 1: Load rule definition (Read active NAV rule from rule_master).
Step 2: Extract zero-NSats windows (Read mission_nsat_windows for duration, repetition, and violations).
Step 3: Build diagnostic backdrop (Use derived metrics listed above).
Step 4: Evaluate locked branches (B1: GPS_SIGNAL_LOSS if > 5s; B2: GPS_DEGRADATION if brief/intermittent).
Step 5: Score branches (confidence_score = 0.7 * parameter_strength + 0.3 * time_factor).
Step 6: Select decision (Assign root_cause and confidence_score).
Step 7: Write output (Update nav_ai_assistance with detailed decision reason).

7. Branch Definitions
B1: GPS_SIGNAL_LOSS
- Focus: complete or near-complete GPS loss
- Condition: zero-NSats is persistent
- Action path: critical handling (LAND or ALTHOLD)
- Alert: Critical GPS Loss — Immediate Action Required

B2: GPS_DEGRADATION
- Focus: temporary instability or environmental interference
- Condition: zero-NSats is brief or intermittent
- Action path: cautionary handling (LOITER or Hover)
- Alert: GPS Signal Unstable — Monitor Closely

8. Decision Rule
If NSats = 0: evaluate B1 and B2; select highest score. If strong and persistent, choose GPS_SIGNAL_LOSS; otherwise, choose GPS_DEGRADATION.

--------------------------------------------------------------------------
PART 2: NAV GPS LOSS SQL MASTER - SYSTEM DESIGN
--------------------------------------------------------------------------
PURPOSE
Defines the logic, purpose, and data flow of the NAV GPS-loss pipeline in DuckDB. It is the single reference for how telemetry is captured, windowed, traced, contextualized, and turned into a final verdict.

CORE IDEA
Raw telemetry is captured in mission_master, compressed into windows in mission_nsat_windows, anchored in nav_meta_log, and exposed via nav_evidence_view. Context and verdict are handled via mission_stats and nav_ai_assistance.

TABLE ROLES
A. msg_type_master: Reference layer for metadata.
B. mission_master: Source of truth for raw telemetry (e.g., 1,264,621 rows).
C. mission_nsat_windows: Event-based NSats windows (~286:1 compression).
D. nav_meta_log: Anchor layer for traceability (Start_inode, TimeUS).
E. nav_evidence_view: LEFT JOIN between windows and anchors for inspection.
F. rule_master: Knowledge layer defining thresholds.
G. nav_ai_assistance: Output/diagnostic layer for reasoning.
H. Context tables: mission_stats for mission-level context.

--------------------------------------------------------------------------
PART 3: NAV DOMAIN: GPS LOSS DIAGNOSTIC SEQUENCE
--------------------------------------------------------------------------
PHASE 1: BASELINE ANALYSIS (MISSION SIGNATURE)
1. Mission signature
   - Total NSats rows in mission_master.
   - Distinct NSats states (unique values observed).
   - NSats percentile spread (5th, 50th, 95th).
2. Baseline
   - Global mission average for NSats.
   - Drift calculation: deviation of each window from the mission average.

PHASE 2: TEMPORAL ANCHORING (THE PHYSICAL PATH)
3. Window map
   - Exact start_inode/start_TimeUS -> end_inode/end_TimeUS for every distinct window.
4. HDOP context
   - Mission-wide HDOP behavior (global stability).
   - HDOP behavior specifically inside the same NSats windows.

PHASE 3: MULTI-PARAMETER CORRELATION (THE SYMPTOMS)
5. Other parameters
   - Statistical check: sync check on vibration, power, and EKF health stats.
6. Flight mode context
   - Identify active flight mode during anomaly; check if mode-linked or random.
7. Dependency check
   - Binary assessment (Yes/No): does another parameter spike before/during the drop?

PHASE 4: RECOVERY AND CONTROL ANALYSIS (THE RESPONSE)
8. Recovery check
   - Did recovery happen autonomously or follow a control command/mode change?
9. EKF / innovation gates
   - Identify exact TimeUS when gates broke open and when they closed.

PHASE 5: EVIDENCE-DRIVEN VERDICT (THE TRUTH)
10. Final verdict
    - Summarized Root Cause, Supporting Evidence (Anchored), Confidence Score.

--------------------------------------------------------------------------
PART 4: DIAGNOSTIC QUESTION ORDER & PRINCIPLES
--------------------------------------------------------------------------
1. Mission signature (Total rows, states, percentile).
2. Baseline (Avg NSats, Drift).
3. Window map (Exact inode/TimeUS bounds).
4. HDOP context (Global vs Window).
5. Other parameters (Vibe, Power, EKF stats).
6. Flight mode context (Mode-linked vs Random).
7. Dependency check (Yes/No on correlation).
8. Recovery check (Autonomous vs Commanded).
9. EKF / innovation gates (Open/Close TimeUS).
10. Final verdict (Cause, Evidence, Confidence).

KEY PRINCIPLE:
Evidence accumulates outward (increasing confidence), while root cause localization moves inward toward the most precise source.

ONE-LINE SUMMARY:
The NAV GPS-loss pipeline captures raw telemetry, compresses it into NSats windows, anchors for traceability, applies thresholds from rule_master, adds mission context, and produces a final diagnostic summary in nav_ai_assistance.
==========================================================================