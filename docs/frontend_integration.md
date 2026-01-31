# Frontend Integration Specification: Technical Document

This document details the data structure available in Supabase (`dashboard_stats`) specifically for replicating the visualizations in the **Technical Chronicle**.

> **Note**: The rest of the visualizations (Market Map, ROI, etc.) are considered already resolved and are not included in this specification.

---

## 🏗️ Data Transparency (Data Quality)
**Payload ID**: `eda_quality_stats`

Data for **Figure 1** of the Chronicle. Shows the number of records that required imputation.

### TypeScript Schema
```typescript
interface DataQualityStat {
  category: string;     // E.g., "Affected = 0 (Imputed)"
  count: number;        // Absolute record count
  percentage: number;   // 0.0 to 1.0 (E.g., 0.05 is 5%)
}
```

### Visualization Rules
- **Chart Type**: Bar Chart (Horizontal or Vertical).
- **Mapping**:
    - **Categorical Axis**: `category`.
    - **Numeric Axis**: `count`.
- **Tooltip/Label**: Show both the absolute number and the formatted percentage (e.g., `0 (0.00%)`).
- **Context**: Explain that "0" is the ideal result (consistency rules not triggered).

---

## 🏗️ Project Distribution (SEIA)
**Payload ID**: `eda_projects_dist`

Data for **Figure 2** of the Chronicle. Shows the number of electrical investment projects by region.

### TypeScript Schema
```typescript
interface ProjectDistributionItem {
  nombre_region: string; // E.g., "ANTOFAGASTA", "METROPOLITANA"
  count: number;         // Project count
}
```

### Visualization Rules
- **Chart Type**: Horizontal Bar Chart (for readable long region names).
- **Sorting**: Descending by `count` (already sorted by backend, but visually confirm).
- **Mapping**:
    - **Y-Axis**: `nombre_region`.
    - **X-Axis**: `count`.
- **Style**: Use a soft sequential palette (e.g., Blues).