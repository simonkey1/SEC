# Technical Documentation: Electrical Distribution Data Pipeline

**Version**: 1.0  
**Stack**: Python 3.12, Polars, PostgreSQL, Supabase  
**Repository**: `kaggle/luz`

---

## 1. System Architecture

The system follows a modern ELT (Extract, Load, Transform) architecture, designed to handle high event volumes (6.2M+) with minimal query latency for the final dashboard.

```mermaid
graph LR
    A[SEC Public Web] -->|Async Scraper| B(Raw CSVs)
    B -->|Ingest| C[(PostgreSQL Raw)]
    C -->|Polars ETL| D[Golden Parquet]
    D -->|Sync Script| E[(Supabase JSONB)]
    E -->|Fetch| F[SvelteKit Frontend]
```

---

## 2. Ingestion Layer (Scraping)

### 2.1 Extraction Strategy
The data source (SEC) does not offer a public API. An asynchronous scraper (`async_historical_scraper.py`) was developed to reconstruct the history from 2017-2025.

*   **Libraries**: `aiohttp`, `asyncio`, `beautifulsoup4`.
*   **Design Pattern**: Producer-Consumer with Semaphore (limited to 50 concurrent requests) to avoid overwhelming the source server.
*   **Error Handling**: Exponential Backoff for retries on 503/504 codes.
*   **Results**: 53 monthly files processed in < 4 minutes.

### 2.2 Raw Storage
Raw data is poured into PostgreSQL without transformation to preserve the "source truth."

---

## 3. Modeling Layer (PostgreSQL)

A **Star Schema** was implemented to facilitate analytical queries.

### 3.1 `public` Schema
*   `fact_interrupciones`: Fact table (6.2M rows).
    *   `id` (PK), `fecha_inicio`, `clientes_afectados`, `duracion_estimada`.
    *   FKs: `region_id`, `comuna_id`, `empresa_id`.
*   `dim_comunas`: Geographic dimension (normalized with CUT codes).
*   `dim_empresas`: Operator dimension (Name normalization: "CGE S.A." -> "CGE").

### 3.2 Integrity Challenges
*   **Duplicates**: The source reports the same event with updates.
*   **Solution**: A unique hash (MD5) was generated based on `date + commune + company` to deduplicate events, keeping only the latest version of the snapshot.

---

## 4. Transformation Layer (Polars)

For massive analysis (EDA) and metric generation, **Polars** was used for its memory efficiency and vectorized speed.

### 4.1 Data Cleaning
*   **Micro-outages**: Events with duration < 1 minute (considered recloser noise) were filtered.
*   **Temporal Normalization**: Conversion of timestamps to UTC-4 (Santiago).
*   **False Zeros**: Affected customer values were imputed using historical averages per commune when the source reported 0 during massive events.

### 4.2 Geographic Enrichment
Spatial joins with census data to calculate relative KPIs (Affected per 100k inhabitants).

---

## 5. Serving Layer (Supabase)

For the Frontend, a **"Pre-computed JSONs"** pattern was chosen to avoid near-real-time SQL latency.

### 5.1 `dashboard_stats` Table
Key-Value store optimized for fast reading.

| Key (ID) | Description | JSON Structure |
| :--- | :--- | :--- |
| `market_map` | Heatmap data | `[{comuna: "Maipú", index: 85}, ...]` |
| `time_series` | Monthly evolution | `[{mes: "2024-08", afectados: 1.2M}, ...]` |
| `company_ranking` | Performance ranking | `[{empresa: "CGE", severidad: High}, ...]` |

### 5.2 Synchronization
The `sync_dashboard_data.py` script regenerates these JSONs from the "Golden Parquet" and performs an `UPSERT` into Supabase.
*   **Benefit**: The end user receives a static JSON. Instant load (< 100ms).
*   **Security**: RLS policies configured to allow public reading and only authorized writing.

---

## 6. Analysis Stack (Data Science)

Modular Python scripts for hypothesis validation:
*   `validate_improvement.py`: Statistical test (simplified t-test) to compare Pre/Post investment time windows.
*   `social_roi_analysis.py`: Public investment efficiency ratio calculation.

---

## 7. Technical Conclusion

The infrastructure is robust, scalable, and decoupled. The use of intermediate files (Parquet) and pre-cooked JSONs (Supabase) ensures that heavy analysis does not impact user experience on the Frontend.
