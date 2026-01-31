# Logic for SEIA Data Extraction (Infrastructure Projects)

## 1. Goal
To cross-reference the SEC interruption database with electrical investment projects from the **Environmental Impact Assessment Service (SEIA)**. This allows us to validate if investment in specific regions correlates with a decrease in outages.

## 2. Scraping Strategy
The SEIA allows for geographic filtering by Region. The project uses the following logic:

### A. Geographic Filtering
We only download projects for the following regions:
- **METROPOLITANA**
- **ANTOFAGASTA**
- **COQUIMBO**
- **LOS LAGOS**
- **ARAUCANIA**

### B. Sector Filtering
We only consider projects belonging to the **"Energy"** sector. This avoids projects related to mining, agriculture, or other industries that do not directly impact the public electrical grid.

### C. Relevant Data Points
For each project, we extract:
1.  **Project Name**: Used to identify the type of infrastructure (e.g., "Cardones-Polpaico").
2.  **Investment (MMUS$)**: The amount declared in millions of US dollars.
3.  **Status**: We only consider "Approved" or "In Operation" projects to measure actual impact.

---

## 3. Data Dictionary (SEIA)

| Field | Description |
| :--- | :--- |
| `nombre` | Official project name. |
| `region` | Geographic region. |
| `monto_inversion` | Expressed in US dollars (normalized for comparison). |
| `estado` | Environmental status (Approved/Rejected/In Evaluation). |
| `fecha_aprobacion`| Critical date for "Before/After" analysis. |

---

## 4. Methodology for Cross-referencing
1.  **Temporal Maturation**: We apply a 2-3 year "Lag" (temporal maturation) to the approval date, assuming that a project does not start operating the day it is approved.
2.  **Regional Normalization**: We compare the total investment of a region against its average failure rate (SAIFI).

---

> [!NOTE]
> This data is used by `scripts/analysis/generate_eda_plots.py` to generate the "Project Distribution" figure in the documentation.
