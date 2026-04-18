# NAV Log Diagnosis – Overview

This repository implements a deterministic NAV-domain diagnostic pipeline for ArduPilot DataFlash logs.

## Problem
Raw `.BIN` logs contain mixed telemetry streams that are difficult to interpret, correlate, and debug manually.

## Solution
The system converts raw telemetry into structured, time-aligned datasets and produces an evidence-backed diagnosis.

## Output
Each run produces:
- Root cause
- Confidence score
- Suggested fixes
- Evidence (TimeUS and inode ranges)

The system is deterministic, reproducible, and traceable to raw telemetry.

