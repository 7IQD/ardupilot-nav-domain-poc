# DF Processing

DF Path
  # Captures all the drone-reported parameters
  # lossless BIN-to-FACT Tables in the Database as FACT
  # Tabels(*.Master.parquets for NAV, POWER, SYS, COM, or EST domains)
  # Downstream domain analysis
  # Protocol-agnostic

### 1. Universal Capture at Ingress (DF Architect)

The **Architect** (`df_mav_ingress_architect.py`) performs **Universal Capture** by ingesting `.BIN` telemetry and recording **all raw drone parameters** from the flight controller. Each MAVLink message is converted into a **key-value dictionary** and written to a Parquet shard. This stage is **domain-independent**, allowing the system to automatically capture new sensors or parameters introduced in firmware, preserving **complete telemetry fidelity**.

---

### 2. Staging of Universally Captured Parameters (Vault B)

Captured parameters are staged in **Vault B**, the raw fact layer. Parquet shards support **dynamic schemas**, accommodating variations in parameter presence across missions. Vault B serves as the **authoritative evidential layer**, preserving every drone-reported value exactly as captured, ensuring a **complete and lossless dataset** for downstream refinement, labeling, and scoring.

---

### 3. Controlled Promotion to Domain Schemas (DF Refinery)

The **Refinery** enforces **canonical domain schemas** defined in the **ActionMap** while promoting parameters from Vault B to the warehouse. Only parameters compliant with a domain’s schema (e.g., `fact_nav_state_vector`, `fact_power_state_vector`) are promoted. Parameters not yet tracked remain in Vault B, ensuring **schema alignment** without losing captured data and enabling **future expansions** without re-reading `.BIN` files.

---

### 4. BIN-to-FACT Logic and Domain Assignment

1. **Capture:** Ingest `.BIN` via MAVLink; record all available drone parameters into Vault B without dropping any.
2. **Domain Assignment:** Assign each parameter to a domain defined in the **ActionMap**; unmapped parameters are routed to **MISC** only if **FMT/protocol supports them**, filtering hardware noise.
3. **Refinement:** Merge shards per domain (including MISC), deduplicate by `(mission_id, TimeUS)`, and fill missing columns with `NULL` to match the canonical schema.
4. **Service Layer Views:** Expose domains (including MISC) via views; no renaming or hardcoded aliases; downstream modules consume clean, protocol-aligned data.

---

### 5. Architectural Significance

By decoupling **Universal Capture** (Architect) from **parameter selection and alignment** (Refinery), the DF path provides a **scalable, lossless, and adaptable pipeline**. This design ensures:

* Complete retention of all drone-reported parameters across domains.
* Resilience to changes in drone hardware, MAVLink versions, or analytics requirements.
* A reliable foundation for downstream modules, including **NAV labeling**, **scorecard generation**, and **cross-domain correlation**.

---


