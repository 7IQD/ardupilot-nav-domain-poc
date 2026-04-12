================================================================
          NAV POC DATA FLASH PIPELINE: END-TO-END PROCESS
================================================================

1. OVERVIEW
The Data Flash pipeline for  telemetry ingestion system has been
designed for ArduPilot .BIN logs. It facilitates,
decoding and full traceability from raw binary to
AI-diagnostic evidence.

----------------------------------------------------------------
2. CORE PIPELINE COMPONENTS & FILE PURPOSE
----------------------------------------------------------------

[ORCHESTRATION LAYER]
- df_main.py:
  The primary entry point. Orchestrates the loading of the .BIN file,
  initializes the FMT registry, and triggers the ingestion architecture.

- build_fmt_registry():
  (Internal to df_main) Extracts the schema from the .BIN file's FMT messages thereby the pipeline is aligned to the specific firmware version of the flight log.

- df_action_map.py (DFActionMap):
  Loads 'FMT_Library.json'for "Domain Routing"
  (e.g., mapping msg_type 'GPS' to 'NAV_DOMAIN') but does NOT
  define the schema or filter any data.

[INGESTION LAYER]
- df_mav_ingress_architect.py (DFIngressMavArchitect):
  The engine that reads the binary stream. It uses 'mlog.recv_msg()'
  to capture every packet and 'msg.to_dict()' to transform raw bytes
  into structured rows.

[STORAGE & STAGING]
- ClerkDF:
  Manages the physical file paths and workspace transitions.

- Vault B (Staging):
  Stores raw ingestion results as 'nav_domain_shard_*.parquet'.
  These shards preserve the original message-wise structure.

[REFINERY & WAREHOUSE]
- create_domain_master_db.sh:
  The "Refinery" script. It aggregates all shards from Vault B using
  the 'union_by_name=True' logic. It partitions the mission into
  'segment_id=1..5' for scalable querying.

- nav_master.duckdb:
  The final analytical warehouse. It exposes the 'mission_master'
  table, providing a unified SQL interface for all mission segments.

----------------------------------------------------------------
3. CRITICAL DATA BEHAVIOR: "MESSAGE-WISE" STORAGE
----------------------------------------------------------------

A core design principle of this pipeline is the "Message-Wise"
representation. Unlike a flattened spreadsheet, the 'mission_master'
table stores each ArduPilot message as a unique row.

- STRUCTURAL REALITY:
  One Row = One Message Instance (e.g., one GPS update).

- WHY ROWS ARE SPARSE:
  Since a GPS message does not contain Velocity data (VN/VE),
  and an XKF1 message does not contain Satellite data (NSats),
  the columns belonging to other message types are filled with NULLs.

- THE "COVERAGE" PARADOX:
  Global coverage metrics (e.g., NSats count vs Total Rows) will
  appear low (e.g., 0.17%). This is EXPECTED and CORRECT. It
  reflects the relative frequency of different sensors, not data loss.

----------------------------------------------------------------
4. DOWNSTREAM DIAGNOSTIC LAYERS
----------------------------------------------------------------

- mission_stats:
  Generates high-level summaries (row counts, durations, signal density).

- mission_nsat_windows:
  Builds time-sequenced windows to detect GPS signal transitions/loss.

- nav_meta_log:
  Maintains the "Chain of Custody" between anomaly windows and
  raw mission rows.

- nav_ai_assistance:
  Structures statistical features and rule-engine outputs into
  prompts for AI-driven root cause analysis.

- nav_evidence_view:
  The final inspection layer. It fuses anomaly windows with rule
  triggers to show exactly what happened, when, and why.

================================================================
STATUS: Lossless | Schema-Aligned | Traceable | AI-Ready
================================================================