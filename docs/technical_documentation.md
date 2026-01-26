# Documentación Técnica: Pipeline de Datos de Distribución Eléctrica

**Versión**: 1.0  
**Stack**: Python 3.12, Polars, PostgreSQL, Supabase  
**Repositorio**: `kaggle/luz`

---

## 1. Arquitectura del Sistema

El sistema sigue una arquitectura ELT (Extract, Load, Transform) moderna, diseñada para manejar alto volumen de eventos (6.2M+) con latencia mínima de consulta para el dashboard final.

```mermaid
graph LR
    A[SEC Public Web] -->|Async Scraper| B(Raw CSVs)
    B -->|Ingest| C[(PostgreSQL Raw)]
    C -->|Polars ETL| D[Golden Parquet]
    D -->|Sync Script| E[(Supabase JSONB)]
    E -->|Fetch| F[SvelteKit Frontend]
```

---

## 2. Capa de Ingesta (Scraping)

### 2.1 Estrategia de Extracción
La fuente de datos (SEC) no ofrece API pública. Se desarrolló un scraper asíncrono (`async_historical_scraper.py`) para reconstruir la historia de 2017-2025.

*   **Librerías**: `aiohttp`, `asyncio`, `beautifulsoup4`.
*   **Patrón de Diseño**: Producer-Consumer con Semáforo (limitado a 50 requests concurrentes) para no saturar el servidor origen.
*   **Manejo de Errores**: Exponential Backoff para retries en códigos 503/504.
*   **Resultados**: 53 archivos mensuales procesados en < 4 minutos.

### 2.2 Almacenamiento Raw
Los datos crudos se vierten en PostgreSQL sin transformación para preservar la "verdad del origen".

---

## 3. Capa de Modelado (PostgreSQL)

Se implementó un **Esquema Estrella** (Star Schema) para facilitar consultas analíticas.

### 3.1 Esquema `public`
*   `fact_interrupciones`: Tabla de hechos (6.2M filas).
    *   `id` (PK), `fecha_inicio`, `clientes_afectados`, `duracion_estimada`.
    *   FKs: `region_id`, `comuna_id`, `empresa_id`.
*   `dim_comunas`: Dimensión geográfica (normalizada con códigos CUT).
*   `dim_empresas`: Dimensión de operadores (Normalización de nombres: "CGE S.A." -> "CGE").

### 3.2 Desafíos de Integridad
*   **Duplicados**: El origen reporta el mismo evento con actualizaciones.
*   **Solución**: Se generó un hash único (MD5) basado en `fecha + comuna + empresa` para deduplicar eventos, manteniendo solo la última versión del snapshot.

---

## 4. Capa de Transformación (Polars)

Para el análisis masivo (EDA) y la generación de métricas, se utilizó **Polars** por su eficiencia en memoria y velocidad Vectorizada.

### 4.1 Limpieza de Datos
*   **Micro-cortes**: Se filtraron eventos con duración < 1 minuto (considerados ruido de reconectadores).
*   **Normalización Temporal**: Conversión de timestamps a UTC-4 (Santiago).
*   **Ceros Falsos**: Se imputaron valores de clientes afectados usando promedios históricos por comuna cuando el origen reportaba 0 en eventos masivos.

### 4.2 Enriquecimiento Geográfico
Cruces espaciales con datos censales para calcular KPIs relativos (Afectados por 100k habitantes).

---

## 5. Capa de Servicio (Supabase)

Para el Frontend, se optó por un patrón de **"Pre-computed JSONs"** para evitar latencia SQL en tiempo real.

### 5.1 Tabla `dashboard_stats`
Almacén Key-Value optimizado para lectura rápida.

| Key (ID) | Descripción | Estructura JSON |
| :--- | :--- | :--- |
| `market_map` | Datos para mapa de calor | `[{comuna: "Maipú", index: 85}, ...]` |
| `time_series` | Evolución mensual | `[{mes: "2024-08", afectados: 1.2M}, ...]` |
| `company_ranking` | Ranking de desempeño | `[{empresa: "CGE", severidad: High}, ...]` |

### 5.2 Sincronización
El script `sync_dashboard_data.py` regenera estos JSONs desde el "Golden Parquet" y realiza un `UPSERT` en Supabase.
*   **Beneficio**: El usuario final recibe un JSON estático. Carga instantánea (< 100ms).
*   **Seguridad**: Políticas RLS configuradas para permitir lectura pública y escritura solo autorizada.

---

## 6. Stack de Análisis (Ciencia de Datos)

Scripts Python modulares para validación de hipótesis:
*   `validate_improvement.py`: Test estadístico (t-test simplificado) para comparar ventanas de tiempo Pre/Post inversión.
*   `social_roi_analysis.py`: Cálculo de ratios de eficiencia de inversión pública.

---

## 7. Conclusión Técnica

La infraestructura es robusta, escalable y desacoplada. El uso de archivos intermedios (Parquet) y JSONs pre-cocinados (Supabase) asegura que el análisis pesado no impacte la experiencia de usuario en el Frontend.
