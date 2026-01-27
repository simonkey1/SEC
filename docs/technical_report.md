# Informe Técnico: Ingeniería de Datos y Metodología (Behind the Scenes)

**Proyecto**: Monitor de Interrupciones SEC Chile  
**Versión**: 1.0 (Enero 2026)

---

## 1. Introducción: La Arquitectura del Dato

Este documento detalla la ingeniería subyacente que permitió construir el dataset de 6.2 millones de registros utilizado en el *Research Paper*. A diferencia de un análisis estático, este proyecto requirió la construcción de una infraestructura ETL (Extract, Transform, Load) capaz de reconstruir la historia de las interrupciones eléctricas en Chile a partir de "trazos efímeros" publicados por el regulador.

> [!TIP]
> Para una narrativa más detallada sobre la evolución del proyecto y los desafíos de ingeniería, consulta la **[Crónica Técnica](technical_chronicle.md)**.

### 1.1 Diagrama de Alto Nivel

```mermaid
graph LR
    SEC[SEC Website API] -->|Snapshot Polling| Scraper[Async Scraper Worker]
    Scraper -->|Raw JSON| Transformer[Data Transformer]
    Transformer -->|Hash ID| Deduplicator[Deduplication Logic]
    Deduplicator -->|Clean Row| PG[(Local PostgreSQL)]
    PG -->|Sync| Supabase[(Supabase Cloud)]
    Supabase -->|API| Dashboard[Frontend Svelte]
```

---

## 2. Estrategia de Extracción (Scraping)

### 2.1 El Desafío: Datos Efímeros
La Superintendencia de Electricidad y Combustibles (SEC) no ofrece un histórico descargable. Solo muestra una "foto" (snapshot) del estado actual del sistema cada 10 minutos. Si no se captura el dato en ese instante, se pierde para siempre.

### 2.2 Solución: Polling Inteligente
Implementamos un sistema de *polling* que consulta la API pública (`/api/v1/interrupciones`) a intervalos estratégicos.
*   **Problema**: Bloqueos de IP y Cloudflare.
*   **Solución**: Rotación de User-Agents y manejo de *Backoff Exponencial* para respetar los límites del servidor.

---

## 3. Transformación y Limpieza (Data Engineering)

### 3.1 De Snapshot a Evento
Uno de los mayores desafíos metodológicos fue definir **"¿Qué es un corte?"**.
La API devuelve estados: "A las 14:00 hay 500 clientes sin luz en Maipú". A las 14:10 dice "300 clientes".
*   **Decisión Metodológica**: No podemos saber si los 200 que volvieron son los mismos 200 originales sin un ID de ticket único.
*   **Lógica de Hashing**: Generamos un `hash_id` único basado en la tupla `(Comuna, Empresa, Fecha, Hora_Inicio, Clientes_Afectados)`. Esto nos permite identificar un evento específico a lo largo de múltiples snapshots sin duplicar la estadística final.

---

## 4. Almacenamiento y Modelado (PostgreSQL)

Utilizamos un esquema **Estrella (Star Schema)** optimizado para consultas analíticas (OLAP):
*   **Fact Table**: `fact_interrupciones` (6.2M filas).
*   **Dimensions**: `dim_geografia`, `dim_empresa`, `dim_tiempo`.

Este diseño permite realizar las agregaciones espaciales (Mapas de Calor) y temporales (Series de Tiempo) en milisegundos, facilitando la generación de los gráficos del paper.

---

## 5. Visualización del Pipeline (Descriptivo)

Para garantizar la integridad del proceso, monitoreamos dos métricas clave: el *Volumen de Ingesta* y la *Consistencia Temporal*.

![Volumen Mensual](figures/tech_fig1_volume.png)
*Figura T1: Volumen de registros procesados por mes. Se observa la consistencia en la captura histórica desde 2017.*

![Cobertura Horaria](figures/tech_fig2_coverage.png)
*Figura T2: Mapa de Calor de Cobertura (Hora vs Día). La distribución uniforme indica que el scraper opera 24/7 sin "puntos ciegos" significativos, validando la estrategia de polling continuo.*

---

## 6. Arquitectura: "Hybrid Medallion" (Local-First)

Para resolver los desafíos de costos y escala, implementamos una **Arquitectura Medallion Híbrida**. Este patrón desacopla el procesamiento pesado (Local) del consumo ligero (Cloud):

1.  **Bronze Layer (Local - Raw)**:
    *   *Datos*: `Snapshots JSON` crudos del scraper.
    *   *Volumen*: ~100 GBs de archivos temporales.
    *   *Ubicación*: Disco Local (Borde).

2.  **Silver Layer (Local - Clean)**:
    *   *Datos*: `fact_interrupciones` en PostgreSQL. Datos deduplicados, limpios y enriquecidos.
    *   *Proceso*: Hashing MD5 para unicidad.
    *   *Ubicación*: PostgreSQL Local.

3.  **Gold Layer (Cloud - Business)**:
    *   *Datos*: `dashboard_stats` en Supabase.
    *   *Definición*: Métricas agregadas listas para el Dashboard (KPIs, Series de Tiempo pre-calculadas).
    *   *Ventaja*: Subimos solo ~10MBs de "inteligencia" en lugar de 6GB de "historia", evitando costos de *Request Units* y latencia.

---

## 7. Diccionario de Datos Clave

### Tabla de Hechos: `fact_interrupciones`
Corazón del sistema. Cada fila es un "snapshot" de un corte en un momento dado.

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `hash_id` | PK (MD5) | `MD5(Comuna + Empresa + Fecha + Hora + Afectados)`. Clave de deduplicación. |
| `id_tiempo` | FK (Int) | Enlace a `dim_tiempo`. Formato `YYYYMMDD`. |
| `id_geografia`| FK (Int) | Enlace a `dim_geografia` (Región/Comuna). |
| `clientes_afectados`| Int | Número de clientes reportados sin servicio. |
| `hora_interrupcion` | Time | Hora declarada de inicio del corte. |

### Dimensiones Principales
*   **`dim_geografia`**: Normaliza nombres de comunas (ej: "Valparaiso" -> "VALPARAISO").
*   **`dim_empresa`**: Unifica razones sociales (ej: "CGE DISTRIBUCION" -> "CGE").
*   **`dim_tiempo`**: Permite jerarquías temporales (Año > Trimestre > Mes > Día).
