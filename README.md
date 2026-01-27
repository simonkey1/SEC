---
title: "⚡ SEC Chile: High-Performance Research Data Pipeline (2017-2025) ⚡"
description: "High-speed ETL infrastructure for the analysis of 6.2M electrical interruption records, optimized for econometric research on infrastructure investment vs reliability."
author: "Simon Gomez"
---

## 📌 Project Overview: From Monitoring to Research

This project has evolved from a real-time monitoring system into a **high-performance research data pipeline**. The current focus is the large-scale analysis of electrical service reliability in Chile between **2017 and 2025**, correlating service interruptions with infrastructure investment data.

### 🎯 Key Research Goal
**"Does investment in electrical infrastructure significantly reduce the frequency and duration of service interruptions?"**
To answer this, we've built a system capable of handling "Big Data" scales on local infrastructure.

---

## 🚀 High-Performance ETL Architecture

To process **6.2 million records** efficiently, the system utilizes a high-performance architecture that achieves a **3,170 records/second** throughput on standard hardware.

### 💎 The "Three Pillars" of Performance:

1.  **Parallel Processing**: Uses `ThreadPoolExecutor` to process data blocks in parallel, saturating CPU and I/O for maximum speed.
2.  **In-Memory Dimension Caching**: Drastically reduces database latency by caching geography (regions/communes) and company entities in RAM, avoiding ~12 million redundant SQL queries.
3.  **Massive Batch Insertion**: Leverages `psycopg2.extras.execute_values` to send thousands of records in a single database round-trip.

---

## 📚 Project Documentation

This repository contains the full artifacts for the **Sociotechnical Analysis of Electrical Reliability**:

### 📄 [Research Paper: "Sociotechnical Dissonance"](docs/research_paper.md)
*The final thesis document.*
*   **Key Findings**: The "Coquimbo Paradox" (Investment $\neq$ Reliability) and the "Perception Gap".
*   **Visuals**: Time Series, Heatmaps, and Case Studies (Arica vs South).

### 🛠️ [Technical Report: "Behind the Scenes"](docs/technical_report.md)
*The engineering deep-dive.*
*   **Architecture**: How we bypassed Cloudflare using a "Local-First" approach.
*   **ETL Pipeline**: From Async Scraping to Star Schema in PostgreSQL.
*   **Benchmarks**: achieving a 15x speedup (5 hours $\to$ 10 mins).

---

## 🏗️ Core System Modules

### 1. [core/async_postgres_repository.py](core/async_postgres_repository.py) - The New Engine
High-performance asynchronous repository using `asyncpg`:
-   **Connection Pooling**: Efficient management of DB connections.
-   **Batch Inserts**: `executemany` for massive throughput.

### 2. [core/historical_etl_orchestrator.py](core/historical_etl_orchestrator.py) - The Orchestrator
Coordinates the scraping and loading process.

---

## 📊 Data Scale & Performance

| Metric | Achievement |
| :--- | :--- |
| **Total Raw Records** | 6,200,095 |
| **Processed Events** | 731,666 |
| **Execution Time** | **~3.0 Minutes** |
| **Old Baseline** | ~5.0 Hours |
| **Optimization Gain** | **~100x Speedup** |

---

## 📂 Legacy: Real-Time Monitoring

While the project has pivoted to historical research, the real-time monitoring components remain available in the codebase for reference or specialized use:

-   **[scripts/legacy/end.py](scripts/legacy/end.py)**: The original real-time orchestrator.
-   **Alert System**: Email notifications and health checks for continuous monitoring.

---

## 🛠️ Getting Started

### 1. Setup Environment
```bash
pip install -r requirements.txt
```

### 2. Execute High-Speed ETL
```bash
python scripts/etl/run_historical_etl.py
```

### 3. Generate Visuals
```bash
python scripts/analysis/generate_paper_plots.py
```

---

## 🌐 Live Dashboard
The interactive data visualization platform is now live! Explore the data, maps, and case studies directly in your browser:

👉 **[Launch Dashboard](https://dashboard-sec.vercel.app/)**

*Features:*
- **Instability Map**: Validated heatmaps of service interruptions.
- **Time Series**: Historical evolution of failures (2017-2025).
- **Investment ROI**: Filtering by region and company.
