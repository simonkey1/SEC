---
title: "⚡ Real-Time Power Outage Monitoring System (SEC Chile) ⚡"
description: "Production-ready modular infrastructure for extraction, transformation, and monitoring of electrical outages in Chile with automated alerts and data retention policies."
author: "Simon Gomez"
---

## 📌 Project Overview

A production-grade data engineering pipeline that evolved from a simple scraping script to a **robust, enterprise-level monitoring system**. This project demonstrates professional software engineering practices including automated testing, database management, email notifications, and resilience patterns.

### 🎯 Key Features

1. **High-Fidelity Data Extraction**: API interception (`GetPorFecha`) using Playwright instead of brittle HTML parsing
2. **Smart Data Engineering**: Server time synchronization (`GetHoraServer`) and intelligent aggregation of fragmented data
3. **Production Architecture**:
   - Circuit Breaker pattern for resilience
   - Automated email alerts (capacity, errors, data quality)
   - 30-day data retention with automated cleanup
   - Health monitoring with threshold-based alerts
4. **Professional Testing**: 22 comprehensive tests (unit + integration) with 100% pass rate
5. **Cloud Database**: Supabase (PostgreSQL) with Star Schema design for analytics

---

## 🏗️ System Architecture

### Core Modules

#### 1. [core/scraper.py](core/scraper.py) - Data Extraction

**Playwright-based network interceptor** acting as a man-in-the-middle:

- Intercepts JSON responses from `GetPorFecha` API (official SEC data source)
- Captures server time via `GetHoraServer` for accurate timestamp synchronization
- Headless browser automation with proper User-Agent handling

#### 2. [core/tranformer.py](core/tranformer.py) - ETL Pipeline

**Heart of data processing**:

- **Aggregation**: Solves fragmented data problem (multiple rows per location → single record)
- **Metrics**: Calculates `DIAS_ANTIGUEDAD` (outage age in days)
- **Unique IDs**: Generates composite hash keys including affected clients count for change detection

#### 3. [core/database.py](core/database.py) - Data Persistence & Monitoring

**Dual storage strategy**:

- CSV exports (`outputs/`) for historical records and real-time snapshots
- **Supabase integration** with capacity monitoring:
  - `check_database_capacity()`: Monitors DB size vs 500MB limit
  - Triggers email alerts at 85% threshold
  - Returns metrics: `size_mb`, `porcentaje`, `total_filas`, `alert_sent`

#### 4. [core/notifications.py](core/notifications.py) - Alert System

**EmailNotifier class** with Gmail SMTP:

- Capacity alerts (database size warnings)
- Scraper error notifications
- Circuit breaker state changes
- Configurable enable/disable via `.env`

#### 5. [core/circuitbreaker.py](core/circuitbreaker.py) - Resilience Pattern

**Fault tolerance mechanism**:

- Automatic failure detection (3 failures → OPEN state)
- 600-second cooldown before retry
- Half-open testing for recovery

#### 6. [scripts/cleanup_old_data.py](scripts/cleanup_old_data.py) - Data Retention

**Automated maintenance**:

- Deletes records older than 30 days from Supabase
- Runs every 7 days (2016 cycles × 5 min)
- Prevents database overflow on free tier

#### 7. [helper/check_variacion_historica.py](helper/check_variacion_historica.py) - Real-time Monitoring

Compares consecutive snapshots to detect significant changes in affected clients

---

## 🚀 Installation & Setup

### Prerequisites

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requeriments.txt
playwright install chromium
```

### Environment Configuration

Create a `.env` file with:

```env
# Supabase credentials
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_publishable_key

# Gmail for alerts (use app password, not regular password)
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
ALERT_EMAIL=recipient@gmail.com
EMAIL_NOTIFICATIONS_ENABLED=true
```

### Database Setup

Execute the Star Schema DDL in Supabase:

```bash
# Run db/schema.sql in your Supabase SQL Editor
# Creates: dim_geografia, dim_empresa, dim_tiempo, fact_interrupciones
```

## 🎯 Usage

### Main Orchestrator

```bash
python scripts/end.py
```

**What it does:**

1. **Infinite Loop**: Runs every 5 minutes (configurable)
2. **Circuit Breaker Protection**: Fails gracefully after 3 consecutive errors
3. **Data Pipeline**: Scrape → Transform → Save to CSV & Supabase
4. **Automated Maintenance**:
   - Health check every 24 hours (288 cycles)
   - Cleanup every 7 days (2016 cycles)
   - Email alerts when database reaches 85% capacity

### Running Tests

```bash
# Run all tests (22 tests, 100% pass rate)
pytest tests/ -v

# Run specific test suites
pytest tests/unit/ -v          # Unit tests only
pytest tests/integration/ -v   # Integration tests only
```

---

## 🧪 Testing Strategy

### Test Coverage (22 tests - 100% passing)

**Unit Tests** (`tests/unit/`):

- `test_circuit_breaker.py`: 6 tests - State transitions, failure tolerance, recovery
- `test_scraper.py`: 6 tests - Response handling, time parsing, data validation
- `test_transformer_new.py`: 4 tests - Aggregation logic, antiquity calculation, Puerto Montt case

**Integration Tests** (`tests/integration/`):

- `test_cleanup_integration.py`: Verifies 30-day retention policy with real Supabase data
- `test_health_check_integration.py`: Validates monitoring metrics and alert triggering
- `test_notifications_integration.py`: Real email delivery + flag respect verification
- `test_scraper_to_transformer_pipeline.py`: End-to-end data flow validation

**Key Testing Decisions**:

- Real database operations (no mocks) for integration tests to prove production readiness
- Pytest fixtures for reusable test components
- Comprehensive assertions on data structure, types, and business logic

## 🔍 Technical Deep-Dive: The "Puerto Montt Effect"

During reverse engineering, we discovered SEC reports outages in technical fragments. Example: Puerto Montt might have 10 rows of 1 client each (one per electrical sector).

**Our Solution**:

```python
df.groupby(['REGION', 'COMUNA', 'EMPRESA', 'FECHA']).agg({
    'CLIENTES_AFECTADOS': 'sum'
}).reset_index()
```

This consolidates fragmented data to show real impact per location.

---

## 📊 Visualización Geographic & GIS

### 🗺️ Procesamiento de Mapas

Contamos con una infraestructura de mapas basada en archivos GeoJSON y Shapefiles (ESRI) organizada por jerarquía territorial:

- **Nivel Nacional**: `maps/poligonos_chile/`
- **Nivel Regional/Provincial/Comunal**: Polígonos detallados con codificación oficial.

Además, el script `scripts/mapas.py` permite **regionalizar** el GeoJSON nacional, subdividiéndolo en archivos independientes por cada región de Chile para optimizar la carga en visores web ligeros.

### 🌐 Próximos Pasos: El Dashboard Web

El enfoque se ha desplazado hacia una plataforma web propia que utilice los archivos generados y los polígonos GeoJSON en `maps/` para crear una experiencia de usuario superior (GIS) con capas de calor y tendencias temporales.

### 📈 Legacy: Análisis en PowerBI

Si prefieres utilizar herramientas No-Code, los archivos generados siguen siendo compatibles con PowerBI. Hemos movido la guía técnica detallada y los fragmentos de código M/DAX a su propio documento:

👉 **[Guía de Configuración para PowerBI](docs/powerbi_legacy.md)**

---

## � Database Schema (Star Schema)

```sql
-- Dimension Tables
dim_geografia (id_geografia, nombre_comuna, nombre_region, nombre_provincia, codigo_comuna)
dim_empresa (id_empresa, nombre_empresa, rut_empresa)
dim_tiempo (id_tiempo, fecha, hora, año, mes, dia)

-- Fact Table
fact_interrupciones (
    id_fact,
    id_tiempo,
    id_geografia,
    id_empresa,
    clientes_afectados,
    hash_id UNIQUE,
    created_at TIMESTAMPTZ
)
```

**Design Decisions**:

- Star Schema for optimal query performance
- `hash_id` prevents duplicate insertions
- `created_at` enables 30-day retention policy
- Indices on FK columns + created_at for fast filtering

## 🛠️ Production Deployment

### Automation Options

**Windows Task Scheduler**:

```bat
@echo off
cd C:\path\to\luz
call .venv\Scripts\activate
python scripts\end.py
```

**Linux Crontab**:

```bash
*/5 * * * * cd /path/to/luz && source .venv/bin/activate && python scripts/end.py
```

### Monitoring Checklist

- ✅ Email alerts configured and tested
- ✅ Database retention policy active (30 days)
- ✅ Circuit breaker protects against API downtime
- ✅ Health checks run every 24 hours
- ✅ All 22 tests passing before deployment

## 🎓 Skills Demonstrated

This project showcases production-ready data engineering practices:

- **ETL Pipeline Design**: Scraping → Transformation → Loading with error handling
- **Database Management**: Star Schema, retention policies, capacity monitoring
- **Resilience Patterns**: Circuit Breaker for fault tolerance
- **Testing**: 100% test coverage with unit + integration strategies
- **DevOps**: Email notifications, automated cleanup, health monitoring
- **Code Quality**: Modular architecture, comprehensive documentation, English codebase

---

**Built for portfolio demonstration - Contact for collaboration opportunities** 💼
