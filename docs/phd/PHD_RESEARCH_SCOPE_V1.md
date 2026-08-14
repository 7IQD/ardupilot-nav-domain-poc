> > Status: Working Research Scope — Version 1
>
> This document defines the current research direction and scope.
> Research questions and hypotheses remain subject to refinement
> following community and literature analysis.

# PhD Research Scope — Version 1

## 1. Research Area

Evidence-preserving representation and analysis of heterogeneous,
asynchronous UAV telemetry for expert investigation.

## 2. Research Problem

UAV flight logs contain a large number of parameters recorded
asynchronously and at different rates across multiple functional
domains.

The research investigates how this telemetry can be represented,
organised and presented so that experts can:

- examine individual parameter behaviour;
- monitor stream integrity;
- investigate intra-domain relationships;
- investigate inter-domain relationships;
- locate incidents/anomalies;
- drill down to the supporting observations.

Every analytical presentation must remain traceable to its underlying
data.

## 3. Research Scope

Initial experimental system:

ArduPilot → DataFlash/BIN → NAV

The research will subsequently investigate:

NAV → EST → COM → SYS → POWER → cross-domain analysis

The scope is the representation and analysis of telemetry, not
replacement of domain-expert judgement.

## 4. Foundation

The implementation separates:

ardunav → ingestion

metadata → semantic definition

DuckDB/Parquet → observation storage

domain services → analysis

visual interface → expert investigation

controlled simulator → reproducible experiments

## 5. Core Research Questions

RQ1: How should heterogeneous and asynchronously sampled UAV
telemetry be represented while preserving its temporal, semantic and
source characteristics?

RQ2: How can the integrity of individual telemetry streams be
defined and monitored?

RQ3: How can parameters operating at different rates be presented
together without losing their original observations or introducing
misleading temporal relationships?

RQ4: How can intra-domain and inter-domain parameter relationships
be exposed for expert investigation?

RQ5: How can analytical results remain traceable to their supporting
observations and source records?

RQ6: Does the proposed representation improve an expert's ability to
locate and investigate an incident or abnormal behaviour?

RQ7: What requirements can be derived for a standard framework for
evidence-preserving analysis of asynchronous UAV telemetry?

## 6. Research Objectives

O1. Define an evidence-preserving representation for asynchronous
UAV telemetry.

O2. Define and evaluate telemetry-stream integrity mechanisms.

O3. Develop a domain-oriented representation for intra-domain and
inter-domain investigation.

O4. Develop a drill-down visual interface linking analytical views
to source observations.

O5. Evaluate the approach using controlled and real flight data.

O6. Derive requirements for a standard framework from the research
findings.

## 7. Current Experimental Foundation

The NAV POC is the first controlled research environment.

Existing work includes:

- BIN ingestion;
- parameter/message mapping;
- metadata;
- DuckDB;
- Parquet;
- NAV domain representation;
- known-pattern testing.

NAV is the starting domain, not the final research boundary.

## 8. Research Progression

1. Establish community and literature gap.
2. Freeze the research problem.
3. Define telemetry representation requirements.
4. Establish metadata and integrity model.
5. Validate NAV representation.
6. Build visual drill-down.
7. Validate with controlled patterns.
8. Extend to additional domains.
9. Evaluate intra-domain/inter-domain investigation.
10. Evaluate with domain experts.
11. Derive standard requirements.

## 9. Research Hypothesis

To be defined after the literature review and gap analysis.

## 10. Research Boundary

The research does not initially assume:

- AI;
- LLM;
- agents;
- autonomous RCA;
- causal inference;
- a particular database technology.

These may only be introduced if required by an identified research problem.

## 11. Candidate Technical Investigation

Source identity/inode may be investigated as a mechanism for
observation provenance and evidence anchoring.

Its novelty and research contribution are not yet established.

## 12. Expected Research Outcome

A validated framework for evidence-preserving representation and
visual investigation of heterogeneous asynchronous UAV telemetry,
together with requirements for a candidate standard.