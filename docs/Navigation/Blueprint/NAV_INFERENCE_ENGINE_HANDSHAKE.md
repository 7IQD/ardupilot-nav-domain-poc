# 🤝 Navigation Domain – Inference Engine Handshake (Interface Lock)

> **Status:** 🔒 LOCKED
> **Role:** Canonical Interface Contract
> **Purpose:** Defines the deterministic black-box interface for the NAV Inference Engine.
> This document bridges **Blueprint logic** and **Framework implementation** and MUST NOT change without TRD review.

---

## 1️⃣ Purpose

This document defines the **structural handshake** for the Navigation Domain Inference Engine.

By locking:
- Inputs
- Outputs
- State memory
- Persistence semantics

we guarantee the engine behaves as a **deterministic, verifiable black box**:
> *Synchronized State Vector → Locked Math → Verdict*

This satisfies **DO-331 verifiable logic** requirements *before* implementation.

---

## 2️⃣ Input Interface — *The Payload*

The Inference Engine consumes a **Synchronized State Vector** at a fixed frequency (10 Hz).

Each processing tick MUST contain the following fields:

| Field | Type | Description |
|-----|-----|-------------|
| `primary_ts` | `uint32` | MAVLink `time_boot_ms` (master temporal key) |
| `meas_vec` | vector | Independent sensor measurements (GPS, Baro, IMU) |
| `pred_vec` | vector | EKF predicted state corresponding to the measurement |
| `var_vec` | vector | EKF innovation variances (expected uncertainty) |

**Rules:**
- `primary_ts` is authoritative.
- All vectors MUST be temporally aligned (ASOF-joined upstream).
- Missing fields invalidate the tick.

---

## 3️⃣ Output Interface — *The Verdict*

For every valid input tick, the engine produces a **Verification Record**:

| Field | Type | Description |
|-----|-----|-------------|
| `Z_score` | float | Standardized innovation (normalized surprise) |
| `state_enum` | enum | `GREEN`, `YELLOW`, `RED` |
| `p_counter` | int | Consecutive non-GREEN frame counter |
| `verdict_final` | enum | Latched system verdict |

---

## 4️⃣ State Memory — *Persistence Logic*

To distinguish **noise** from **systemic failure**, the engine maintains bounded short-term memory per signal.

### 4.1 Rolling Window
- **`window_buffer`**: 1.0 s rolling window of Z-scores
  - Size: 10 samples (10 Hz)
  - Purpose: Temporal context (no smoothing applied)

### 4.2 Persistence Counter
- **`p_counter`**: counts consecutive frames where `Z_score` exceeds GREEN limits

**Rules:**
- If `Z_score ∈ GREEN` → `p_counter = 0`
- If `Z_score ∉ GREEN` → `p_counter += 1`
- Counter resets immediately on return to GREEN (*Fresh Start Rule*)

### 4.3 Latch Behavior
- **`latch_status`**:
  - Once **RED**, verdict remains RED
  - Reset only by:
    - Manual reset
    - Database overwrite & test restart

---

## 5️⃣ Failure Semantics — *Verdict Boundary*

The following logic defines **exact state transitions**:

### 5.1 Transient Spike
- Condition:
  - Single frame where `Z_score ∈ YELLOW`
  - Next frame returns to GREEN
- Verdict:
  - **GREEN**
  - Logged as *Noise Event*

---

### 5.2 Degraded State (YELLOW)
- Condition:
  - `p_counter ≥ 20` frames
  - (~2.0 s sustained YELLOW)
- Verdict:
  - **YELLOW**
  - Indicates estimator stress / divergence trend

---

### 5.3 Systemic Failure (RED)
Triggered by **either** condition:

1. **Persistence Failure**
   - `p_counter ≥ 10` frames of YELLOW
   - (~1.0 s sustained degradation)

2. **Immediate Structural Break**
   - Any single frame where `Z_score ∈ RED`

**Verdict:**
- **RED**
- Latched until reset
- Indicates estimator rejecting sensor or fusion collapse

---

## 6️⃣ Hysteresis Design Note

This handshake intentionally introduces **hysteresis**:
- Prevents UI flicker
- Prevents false alarms
- Ensures RED reflects confirmed systemic failure

> When RED is visible, the system has *already decided*.

---

## 7️⃣ Change Control Rule

- Any modification to:
  - Inputs
  - Outputs
  - Counters
  - State transitions

**REQUIRES:**
- Review of `NAV_TEST_REQUIREMENTS.md`
- Re-certification of NAV-01 baseline

---

## 8️⃣ Downstream Mapping

| Artifact | Dependency |
|-------|------------|
| `NAV_INFERENCE_ENGINE.py` | MUST implement this contract verbatim |
| Reports | Consume Verification Records |
| UI | Reflect `state_enum` and `verdict_final` only |
| Tests | Validate behavior against this handshake |

---

**End of Document — Interface Frozen**
