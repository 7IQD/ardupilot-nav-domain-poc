# PhD Research Scope

## Working Title

**FMT-Driven Telemetry Ingestion and Deterministic Analysis for Autonomous Systems**

## 1. Research Problem

Autonomous systems generate telemetry from multiple subsystems at different rates. In DataFlash logs these messages are stored together and their structure is defined through FMT records.

The research investigates how this telemetry can be converted into a reliable and reproducible dataset before analysis is performed.

The initial implementation will use ArduPilot DataFlash logs.

## 2. Core Idea

Separate telemetry ingestion from telemetry analysis.

```text
FMT-defined BIN
      |
      v
ardunav
      |
      v
Structured telemetry
      |
      v
Domain analysis
      |
      v
Evidence / Diagnosis
```

`ardunav` is responsible only for ingestion and data structuring.

It preserves message type, sequence, timing and domain information and produces validated DuckDB data.

## 3. First Proof of Concept

The first analysis domain will be NAV.

The objective is to demonstrate that:

* the original telemetry can be preserved
* message ordering can be maintained
* asynchronous data can be aligned
* known NAV patterns can be detected deterministically
* the result can be reproduced

NAV is the starting point and not the intended final limitation.

## 4. Pattern Simulator

The pattern simulator will generate controlled telemetry with known anomalies.

This provides ground truth for testing.

```text
Known pattern
     |
     v
Pattern simulator
     |
     v
BIN
     |
     v
ardunav
     |
     v
NAV analysis
     |
     v
Expected result
```

New patterns will be added as the research progresses.

## 5. Research Progression

The work will proceed in this order:

1. Validate `ardunav` ingestion.
2. Establish NAV analysis.
3. Validate NAV analysis using the pattern simulator.
4. Extend the approach to other domains.
5. Evaluate whether the same architecture generalises.
6. Investigate applicability to other FMT-based autonomous systems.

## 6. Research Questions

**RQ1:** Can FMT-based telemetry be ingested into a structured dataset while preserving message lineage and timing?

**RQ2:** Can deterministic analysis reliably identify known telemetry patterns from this structured data?

**RQ3:** Can the same approach be reused across different telemetry domains?

**RQ4:** Can the approach be extended to other autonomous systems using FMT-based logging?

## 7. Hypothesis

An FMT-driven ingestion approach that preserves message sequence and timing can provide a reliable foundation for deterministic analysis of asynchronous telemetry.

## 8. Research Boundary

The implementation starts with:

**ArduPilot → DataFlash → NAV → controlled testing**

The broader FMT applicability will be considered only after the ArduPilot proof of concept and cross-domain testing provide sufficient evidence.

## 9. Engineering Principle

Keep the tools separate and simple.

`ardunav` → ingestion

`ap_pattern_simulator` → controlled test data

Domain services → analysis

Research documentation → evidence and evaluation

New technologies such as agents, RAG or LLMs will only be introduced if they solve a clearly identified research problem.

## 10. Expected Outcome

The immediate goal is not to build a universal log analyser.

The goal is to establish and test a clean method for:

**FMT → reliable ingestion → structured telemetry → deterministic analysis → reproducible evidence**

If the method proves reusable across domains, its applicability to other FMT-based autonomous systems can then be investigated.
