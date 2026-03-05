# NAV Domain FastAPI API

**File:** `src/dashboard/nav/app.py`
**Purpose:** Exposes AI-ready NAV domain telemetry and verdict endpoints, using `NavDataService` to enforce Gold-layer data integrity.

---

## Endpoints

### 1. Mission Verdict

**URL:** `GET /api/nav/verdict/{mission_id}`

**Description:**
Analyzes mission health and stability. Combines EKF stability scores with local AI logic for unsafe ground-speed detection.

**Logic:**

- Fetch fused telemetry from `NavDataService`.
- Compute stability & mission health (`metrics_helpers.py`).
- Detect unsafe ground events: `spd_gps > 5 m/s` & `Alt < 0.3 m`.
- Return JSON with verdict, health status, and metrics.

**Example Response:**

```json
{
  "mission_id": "manual_run",
  "verdict": "PASS",
  "health_status": "GREEN",
  "metrics": {
    "peak_altitude_m": 584.09,
    "stability_score": 92.5,
    "unsafe_ground_events": 0,
    "data_points": 3830
  }
}
````

---

### 2. Telemetry Vector

**URL:** `GET /api/nav/telemetry/{mission_id}`

**Description:**
Returns the full fused, scaled, and scored telemetry vector. Coordinates are converted to floats for mapping and AI consumption.

**Logic:**

* Fetch fused telemetry from `NavDataService`.
* Scale 10^7 raw coordinates to float.
* Replace NaNs with `null` for JSON safety.

**Example Response:**

```json
{
  "mission_id": "manual_run",
  "layer": "GOLD_STATE_VECTOR",
  "count": 3830,
  "data": [
    {"TimeUS": 123456, "Lat": 35.36, "Lng": 139.75, "Alt": 584.09, "Roll": 0.1, "Pitch": 0.0, ...},
    ...
  ]
}
```

---

## Dependencies

* **Service Layer:** `NavDataService`
  Handles fusion, scaling, scoring, and mission summary.
* **Metrics Helpers:** `metrics_helpers.py`
  Provides `scale_coordinates`, `compute_stability_score`, `get_mission_health`.
* **Gold Database:** `drone_df_views.db`
  Contains `fact_nav_state_vector` and `view_clean_est` tables.

---

## Execution

```bash
python src/dashboard/nav/app.py
```

**Access Endpoints:**

* Mission Verdict: `http://localhost:8000/api/nav/verdict/manual_run`
* Telemetry Vector: `http://localhost:8000/api/nav/telemetry/manual_run`

---

## Key Principles

* **Single Source of Truth:** Scaling & scoring handled only by `NavDataService`.
* **AI & Dashboard Ready:** JSON output is fused, scaled, and safe for mapping.
* **Extensible:** Future domains can integrate without API changes.
* **Error Handling:** Proper HTTP codes returned for missing missions or internal errors.

```
