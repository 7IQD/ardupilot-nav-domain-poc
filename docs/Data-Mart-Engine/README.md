# Data Mart Engine

The Data Mart Engine is the analytical execution layer of the ArduPilot Nav Domain POC.

It is responsible for transforming immutable telemetry stored in the Platform Vault
(Silver Mart) into domain-specific, human-consumable analytical products (Gold Mart),
without modifying flight software, estimators, or platform ingress logic.

This engine is intentionally non-adaptive and non-intrusive.

## Non-Goals
- No estimator tuning
- No feedback into ArduPilot
- No real-time control decisions
- No mutation of Silver data

## Role in the System
Platform answers: *Can data exist safely?*
Navigation answers: *What does correct NAV mean?*
**Data Mart Engine answers: *How do we prove it analytically?***
