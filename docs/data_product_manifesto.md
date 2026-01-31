# Data Product Manifesto: "Grid Status"

## 1. Core Narrative (Validated Hypothesis)
> *"Investment in transmission is effective, but it is not magic. Its success depends on geography (Climate) and temporal maturation (Lag)."*

We have moved from "Investment doesn't work" (Correlation -0.14) to a nuanced view proven by 4 case studies:
1.  **Immediate Success**: Surgical projects (Arica/Santiago) lower outages instantly (-70%).
2.  **Late Success (Lag)**: Massive highways (Cardones-Polpaico) take 3 years to stabilize the system (-17%).
3.  **Structural Challenge**: In the South (Los Lagos), extreme weather negates investment improvements (+4%).

---

## 2. Selected Visualizations ("The Keepers")
These are the 5 visualizations that will move to the Frontend, and why:

### A. The "Social ROI" Heatmap (Inefficiency)
*   **Source**: `social_roi_analysis.py`
*   **Why**: It is the definitive business metric. It shows that **Ñuble** is a "Black Hole" (55k affected/$M invested) vs **Antofagasta** (230 affected/$M).
*   **Improvement**: Tooltips explaining the "Lag" (2027 projects) were added to avoid being unfair.

### B. The Disaster Gallery (Time-Series)
*   **Source**: `batch_visualize_events.py` (Mega View)
*   **Why**: Allows event-by-event auditing. Shows the "signature" of each storm (fast vs. slow recovery).
*   **Usage**: Drill-down for engineers/auditors.

### C. The Ranking of Shame (Companies)
*   **Source**: `company_ranking_analysis.py`
*   **Why**: Separates volume (CGE) from severity (Chilquinta). It is pure transparency for the end user.

### D. The Near-Real-Time Monitor (Zapping)
*   **Source**: `time_series_zapping.py`
*   **Why**: Shows the "minute-to-minute" pulse. It is essential to see daily stability.

### E. Investment Evidence (Before/After)
*   **Source**: `validate_improvement.py`
*   **Why**: Graphically shows the impact of the 4 major projects (Before vs. After Bars). It is proof that the system is advancing.

---

## 3. Metrics Methodology
Do we use international standards? **Yes, adapted.**

*   **SAIFI Proxy (Frequency)**: We use `total_events / total_customers`.
    *   *Adjustment*: We filter micro-outages (<1 min) to clean noise.
*   **SAIDI Proxy (Duration)**: We use `affected_customers * outage_hours`.
    *   *Weighting*: We don't treat an outage in a dense area the same as in a rural one. The "Market Map" normalizes this by population density.
*   **Social ROI (Proprietary)**: `Affected Customers / Investment MMU$`.
    *   *Innovation*: Unique metric of this project to measure public spending efficiency.

---

## 4. Current Status (Status Check)
| Layer | Status | Conclusion |
| :--- | :--- | :--- |
| **Ingestion (Raw)** | ✅ Completed | 6.2M records, clean of false zeros. |
| **Context** | ✅ Completed | Climate milestones and inauguration dates validated. |
| **Analysis** | ✅ Completed | "Lag" hypothesis statistically confirmed. |
| **Backend** | ⏸️ Pending | Scripts ready, waiting for green light for `sync_dashboard_data.py`. |
| **Frontend** | ⏳ In progress | Design defined by "Keepers" visualizations. |

We are ready to build. No data is missing.
