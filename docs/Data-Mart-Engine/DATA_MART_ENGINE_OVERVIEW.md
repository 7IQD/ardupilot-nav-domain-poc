# Data Mart Engine — Overview

The Data Mart Engine consumes append-only telemetry from the Silver Mart and produces
multiple audience-specific analytical artifacts in the Gold Mart.

The engine operates in periodic pulses and is mission-aware but stateless.

## Inputs
- Silver Mart Parquet files (append-only)
- Mission identifiers
- Product type selectors (pilot, ekf, forensics)

## Outputs
- Gold Mart Parquet artifacts
- Dashboard-readable analytical slices
- Evidence-ready data subsets

## Design Principle
"One math path, many products."

All geometric and temporal calculations are centralized and shared.
Downstream dashboards remain dumb and declarative.
