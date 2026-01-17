# ArduPilot Nav Domain PoC – Documentation

This repository contains the documentation and design artifacts for the **Navigation Domain Proof-of-Concept** (Nav Domain) for ArduPilot. It is structured to separate high-level design, implementation frameworks, UI contracts, and mission diagnostic reports.

---

## 📂 Folder Structure

### Navigation

| Subfolder | Purpose |
| ---------- | ------- |
| **Blueprint/** | High-level design, canonical data maps, and master specifications (`NAV_BLUEPRINT`, `NAV_SPEC_MART.md`). |
| **Framework/** | ETL and implementation guidelines, including the LRU/SRU reporting framework (`NAV_MART_IMPLEMENTATION_FRAMEWORK.md`). |
| **Reports/** | Mission-level or SITL diagnostics (`NAVIGATION_LABORATORY_DIAGNOSTIC_REPORT.md`). |
| **UI/** | Dashboard contracts, frozen layouts, and traceability matrices (`NAVIGATION_DOMAIN_UI_DISPLAY_CONTRACT.md`, `NAVIGATION_FLIGHT_SAFETY_DASHBOARD_CONTRACT.md`). |

### Platform

| Subfolder | Purpose |
| ---------- | ------- |
| **Platform/** | Platform-wide canonical maps and system design documents (`PLATFORM_CANONICAL_DATA_MAP.md`, `PLATFORM_SYSTEM_DESIGN.md`). |

---

## 🛠️ Usage

1. **Blueprint** – Reference for high-level architecture and canonical data mappings.
2. **Framework** – Implement ETL pipelines, LRU/SRU live reporting, and phase-wise assertions.
3. **Reports** – Generate mission or SITL diagnostic reports.
4. **UI** – Validate dashboard layout and maintain compliance with frozen display contracts.

> Each document is versioned and structured to be **self-contained**, traceable, and ready for integration into GSoC or production workflows.

---

## ⚡ Key Principles

* **Separation of Concerns** – Blueprint, Framework, UI, and Reports are clearly divided.
* **Traceability** – UI panels, ETL outputs, and NAV_REPORT sections are fully mapped.
* **Reproducibility** – All reports and diagnostics are deterministic and derived from the pipeline.
* **Scalability** – New sensors or metrics can be added without altering the core structure.


