# Research Principles

## 1. Research Focus

Study how heterogeneous, asynchronous UAV telemetry can be represented
and presented so that domain experts can investigate behaviour,
relationships and incidents effectively.

## 2. Expert-Centred

The system supports UAV/aviation/ArduPilot experts.

It does not replace expert judgement.

## 3. Evidence First

Every analytical view must be backed by data.

The user must be able to drill down from a presentation to the
observations supporting it.

## 4. Preserve Native Observations

Telemetry recorded at different rates must retain its original
observations and timing.

Any derived, aligned or reconstructed data must be identifiable as
such.

## 5. Stream Integrity

Each telemetry stream has expected characteristics.

Violations of those characteristics must be detectable and retained
as evidence.

## 6. Metadata

Telemetry must carry the semantic information required to interpret
its observations.

Metadata is treated separately from the observations themselves.

## 7. Domain Analysis

The research starts with NAV and will investigate:

- NAV
- EST
- COM
- SYS
- POWER

Both intra-domain and inter-domain relationships are in scope.

## 8. Existing Open-Source Approaches

Existing drone log-analysis applications must be studied before
claiming a research gap.

The investigation must examine:

**what they provide, how they provide it and the consequences of
that representation.**

## 9. Standards and Protocols

The underlying standards, protocols, formats and semantic definitions
used by existing systems must be identified and kept separate from
application-specific behaviour.

## 10. Open Standard

A future standard is an expected research outcome, not an assumption.

Its requirements must emerge from:

literature + existing systems + experiments + expert evaluation.

## 11. Bottom-Up / Top-Down

The implementation will be developed bottom-up from working
experiments.

The resulting framework and standard will be defined top-down from
validated requirements.

## 12. Research Discipline

Do not introduce technology or scope without a research reason.

AI, agents, autonomous RCA and causal inference are not assumptions
of the research.