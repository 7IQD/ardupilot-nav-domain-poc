# 📘 Monte-Carlo Driven Labelling Charter

---

## 🎯 Objective

Establish a **reproducible, benchmark-driven labelling system** for Nav & Est domains using controlled Monte-Carlo simulations before automation.

The system must be:

* Measurable
* Versioned
* Reproducible
* Defensible to third parties

---

# 🧭 Scope (Phase 1)

**Domains:**

* Navigation (Nav)
* Estimation (Est)

**Data Source:**

* Existing clean SITL-generated `.bin`
* DuckDB settled Parquets

Out of Scope:

* Real crash data
* Other domains (Power, Vibe, etc.)
* Full automation

---

# 🏗️ Execution Plan (Agile Phases)

---

## 🔹 Sprint 1 — Define the Labelling Registry

Create:

```
labelling_registry_v0_1.yaml
```

Contains:

### Carrier Labels (Time Windows)

* TakeoffPhase
* GPSFixWindow
* HighVibrationWindow
* DriftWindow

### Outcome Labels (Post-Analysis)

* DriftScore
* ResidualScore
* StabilityScore

Rules:

* No thresholds yet
* No logic
* Only vocabulary definition
* Version controlled

✅ Deliverable: Versioned registry with documented label meanings.

---

## 🔹 Sprint 2 — External Monte-Carlo Calibration

Using existing clean `.bin`:

1. Run controlled simulations externally (Notebook / Excel / Tool).
2. Inject controlled variation.
3. Record outputs.

Create:

```
calibration_registry_v0_1.parquet
```

Must include:

| simulation_id | parameter_set | threshold_used | drift_score | residual_score |
| ------------- | ------------- | -------------- | ----------- | -------------- |

Rules:

* Every simulation must be logged.
* Each threshold must be traceable.
* Each run must have an ID.

✅ Deliverable: Benchmark dataset (ground truth reference).

---

## 🔹 Sprint 3 — DuckDB Reproduction

Objective:
SQL must reproduce calibration results.

Steps:

1. Create vertical-slice views in DuckDB.
2. Apply thresholds from calibration registry.
3. Compare SQL results vs simulation outputs.

If mismatch:

* Adjust thresholds.
* Update calibration registry version.

✅ Deliverable: SQL reproducibility confirmed.

---

## 🔹 Sprint 4 — Integrate Calibration Engine

Only after:

* Registry stable
* Calibration reproducible
* SQL validated

Then:

1. Build calibration module (like refinery stage).
2. Load calibration_registry at runtime.
3. Apply labels to mission records.
4. Log:

   * calibration_version
   * simulation_reference_id

✅ Deliverable: Automated labelling engine with version traceability.

---

# 🧪 Calibration Governance

Every benchmark must answer:

* Who created it?
* When was it run?
* What parameters were used?
* What simulation ID certified it?

No threshold enters production without:

* Simulation ID
* Version reference
* Registry update

---

# 🏷️ Labelling Architecture Model

Two Phases:

## 1️⃣ Pre-Analysis Labelling (Switching Layer)

* Runs immediately after Parquet settlement.
* Detects static patterns.
* Produces:

```
[start_time, end_time, label_type]
```

Purpose:
Define routing windows.

---

## 2️⃣ Post-Analysis Labelling (Enrichment Layer)

* Runs after domain residual calculations.
* Applies outcome scores.
* Attaches performance cargo to carrier labels.

Purpose:
Attach measurable outcomes.

---

# 🔍 Verification Principles

* Monte-Carlo remains external during calibration.
* DuckDB must reproduce results.
* Registry must be versioned.
* Labels must be explainable in plain language.
* Every label must trace to a simulation ID.

---

# 🚫 What This Is Not

* Not AI-based auto-labelling.
* Not arbitrary thresholds.
* Not undocumented simulations.
* Not a black box.

---

# 🏁 Final State Vision

| Layer                | Role                     |
| -------------------- | ------------------------ |
| Registry             | Defines vocabulary       |
| Calibration Registry | Stores benchmark truth   |
| DuckDB Views         | Reproduce logic          |
| Calibration Engine   | Automates application    |
| Mission Records      | Receive traceable labels |

---

# 🧾 Success Criteria

* Same `.bin` always produces same labels.
* Every threshold traceable to simulation ID.
* Third party can audit calibration source.
* No hidden logic.
* Versioned evolution.

---


