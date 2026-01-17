# **Navigation Domain – Flight Safety Dashboard Contract**

### **1. Dashboard Layout (3-Column Standard)**

| Column                | Content / Purpose              | Notes                                                                                                                                                       |
| --------------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Column 1 (Left)**   | **Parameter / Remarks Column** | Lists flight parameters, threshold violations, annotations; optional scrollable.                                                                            |
| **Column 2 (Center)** | **2×2 Locked Visual Grid**     | Top-Left: Error Histogram / Descriptive Statistics<br>Top-Right: Causal Analysis Heatmap<br>Bottom-Left: Z-Score Anomalies<br>Bottom-Right: Spatial Heatmap |
| **Column 3 (Right)**  | **Metadata / Summary Column**  | Flight ID, Vehicle ID, Mission Timestamp, summary table, optional quick stats                                                                               |

* **Column 2**: Fully **locked**, standardized axes, units, and color maps.
* **Column 1 & 3**: Fixed width; Column 1 can scroll for long remarks.
* **Purpose:** Standardized, repeatable layout for **flight safety review**.

---

### **2. Display Requirements**

* **Locking:** Central 2×2 visual grid cannot move or resize; ensures safety audit compliance.

* **Scaling & Units:**

  * Lateral deviation: meters (Histogram & Z-Score).
  * Heatmaps: fixed color intensity range (Causal & Spatial).

* **Interactivity:**

  * OLAP: optional (hover details, zoom).
  * OLTP (runtime): **static**, for live drift monitoring.

* **Labels:** Each quadrant labeled with **title + metric unit**; metadata column always visible.

---

### **3. Schema → UI Mapping**

| JSON Key / SITL Message  | SQL Column              | UI Element / Plot         | Notes                                    |
| ------------------------ | ----------------------- | ------------------------- | ---------------------------------------- |
| `latitude` / `longitude` | `latitude`, `longitude` | Spatial Heatmap           | Trajectory & drift mapping               |
| `lateral_deviation`      | `lat_dev`               | Error Histogram / Z-Score | Top-Left & Bottom-Left panels            |
| `control_inputs`         | `ctrl_in`               | Causal Analysis Heatmap   | Maps input → error correlations          |
| `timestamp`              | `ts`                    | Metadata display          | Flight ID, Vehicle ID, Mission Timestamp |
| `altitude` / `speed`     | `alt`, `spd`            | Optional overlays         | Context for trajectory                   |

---

### **4. Visual & Analytical Deliverables**

| Deliverable                    | Description                                                       | Quadrant / Location |
| ------------------------------ | ----------------------------------------------------------------- | ------------------- |
| **Error Histogram**            | Lateral deviation distribution; bias, spread; flight safety alert | Top-Left            |
| **Descriptive Statistics**     | Mean, median, standard deviation; summary table                   | Top-Left (combined) |
| **Causal Analysis Heatmap**    | Correlation / contribution of inputs to navigation error          | Top-Right           |
| **Z-Score Anomalies**          | Flags extreme deviations for automated alerts                     | Bottom-Left         |
| **Spatial Heatmap**            | Geographic mapping of drift / errors over mission trajectory      | Bottom-Right        |
| **Parameter / Remarks Column** | Flight notes, thresholds, annotations                             | Column 1 (Left)     |
| **Metadata / Summary Column**  | Flight ID, Vehicle ID, Timestamp, optional quick stats            | Column 3 (Right)    |

---

### **5. Data Pipeline Integration**

```
[Sensors / SITL]
        ↓
   Router / Controller
        ↓
   UPSTREAM JSON (Frozen Contract)
        ↓
┌───────────────┬───────────────┬───────────────┐
│ Parameter /   │  2×2 Locked   │ Metadata /    │
│ Remarks       │  Visual Grid  │ Summary       │
│ (scrollable)  │               │ (fixed)       │
└───────────────┴───────────────┴───────────────┘
```

* **OLTP (runtime)**: Live feed, optional mini top-left histogram for immediate drift alerts.
* **OLAP (analysis)**: Full dashboard with **3-column layout**, locked central grid, standardized visuals.

---

### **6. Safety & Standardization Notes**

* **Locked quadrants** prevent misinterpretation or accidental repositioning.
* **Consistent layout, colors, axes, and units** ensures repeatable review across all missions.
* **Direct schema mapping** guarantees accuracy: JSON → SQL → Visuals.
* **Fixed 3-column matrix** meets aviation safety and flight review standards.
* **Optional remarks column** allows engineers to annotate or flag thresholds without changing visual layout.

---

✅ **This Release Candidate now formalizes:**

* 3-column flight safety dashboard
* 2×2 locked central visual grid
* Schema → UI mapping
* Visual & analytical deliverables
* OLTP/OLAP distinction
* Flight safety compliance standards

---

