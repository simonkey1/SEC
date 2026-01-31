# MASTER PROMPT FOR FRONTEND CONSTRUCTION (SvelteKit)

**Role**: You are an expert Software Engineer in SvelteKit, TailwindCSS, and Data Visualization (D3.js / LayerChart).

**Project Context**: 
We have processed 6.2 million records of power outages in Chile (2017-2025). The data is already processed, validated, and loaded into **Supabase**. Your mission is to build the public interface ("Network Status") that tells the story of electrical fragility and the impact of investment.

---

## 1. Technology Stack
- **Framework**: SvelteKit (App Router)
- **Styles**: TailwindCSS (Dark Mode, "Institutional Cyberpunk" Palette: Slate-900, Emerald-400 for success, Rose-500 for failures).
- **Graphics**: LayerChart or ECharts (high performance needed).
- **Backend/Data**: Supabase (Table `dashboard_stats`).

---

## 2. The Data Source (Supabase)
The data already exists in a Key-Value table for maximum speed. You don't have to process anything, just fetch JSONs.

**SQL Table**:
```sql
create table dashboard_stats (
  id text primary key, -- IDs: market_map, time_series, investment_roi, company_ranking, investment_validation
  data jsonb not null
);
```

**Available IDs and JSON Structure**:
1.  `market_map`: List of communes with `instability_index` (0-100) to color a map of Chile.
2.  `time_series`: Array of objects `{month: '2020-01-01', affected: 5000}`.
3.  `investment_roi`: Ranking of regions with `efficiency_ratio` and `maturity_note` (e.g., "3-year Lag").
4.  `company_ranking`: List of companies (`company_name`, `total_affected`) for the "Ranking of Shame."
5.  `investment_validation`: Array of 4 case studies (`project`, `delta`, `context`) proving investment success/failure.

---

## 3. Visualization Requirements (The 5 Key Views)

### A. The Heatmap ("The Scar")
- **Visual**: A map of Chile divided by communes/regions.
- **Logic**: Color according to `instability_index`. Intense red = Critical Zone.
- **Interaction**: Hover shows "Commune X: Y average hours without power."

### B. The Pulse Monitor ("Zapping")
- **Visual**: Full time-series graph (2017-2025).
- **Style**: Similar to a heart rate or stock monitor.
- **Narrative**: Should highlight the 2017 (Snow) and 2024 (Wind) peaks as "Black Swan Events."

### C. The Wall of Inefficiency (Social ROI)
- **Visual**: Horizontal bar chart.
- **Axes**: Y-axis = Region, X-axis = Inefficiency ($ spent / people without power).
- **Critical Detail**: You must show the `maturity_note` tooltips (e.g., "Ñuble looks bad, but it's because its works are delivered in 2027").

### D. Operator Ranking (Bad Actors)
- **Visual**: Stylized table or Leaderboard.
- **Order**: By `total_affected_customers`.
- **Goal**: Full transparency. Who fails the most.

### E. Investment Evidence (Before/After)
- **Visual**: Comparative cards or slope chart.
- **Data**: Use the `investment_validation` JSON.
- **Story**: Show how Cardones-Polpaico lowered outages after 3 years (Lag), while REDENOR lowered them immediately.

---

## 4. Design Instructions (Look & Feel)
- **Vibe**: "Premium Data Journalism." Serious, clean, Sans-Serif typography (Inter or Geist).
- **Colors**: Dark background (`bg-slate-950`). Light gray text (`text-slate-300`). Semantic accents (Red = Outage, Green = Approved investment).
- **Responsive**: Must work perfectly on mobile (people check their power from their phones).

---

## 5. Your Initial Task
1.  Initialize the SvelteKit project.
2.  Create a simple Supabase client to read `dashboard_stats`.
3.  Implement the "Overview Page" that loads these 5 JSONs and displays them in a bento-style CSS Grid.

Start!
