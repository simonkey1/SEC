-- Esquema SQL para Supabase / PostgreSQL
-- Proyecto: Monitoreo de Cortes de Luz (SEC Scraper)

-- 1. Tablas Dimensionales (Normalización)
CREATE TABLE IF NOT EXISTS regiones (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS empresas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS comunas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    region_id INTEGER REFERENCES regiones(id),
    UNIQUE(nombre, region_id)
);

-- 2. Tabla Histórica (Data Lake / Time Series)
-- Almacena cada captura realizada por el scraper
CREATE TABLE IF NOT EXISTS cortes_historico (
    id BIGSERIAL PRIMARY KEY,
    comuna_id INTEGER REFERENCES comunas(id),
    empresa_id INTEGER REFERENCES empresas(id),
    clientes_afectados INTEGER NOT NULL,
    clientes_totales INTEGER NOT NULL,
    porcentaje_afectados NUMERIC(10, 2),
    timestamp_sec TIMESTAMPTZ NOT NULL, -- Hora oficial del servidor SEC
    id_unico_intercomuna VARCHAR(255),  -- ID_UNICO original del transformer
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Tabla de Tiempo Real (Estado Actual)
-- Optimizada para el dashboard Svelte. Se actualiza mediante UPSERT.
CREATE TABLE IF NOT EXISTS cortes_tiempo_real (
    id_unico VARCHAR(255) PRIMARY KEY, -- COMUNA_EMPRESA
    region_id INTEGER REFERENCES regiones(id),
    comuna_id INTEGER REFERENCES comunas(id),
    empresa_id INTEGER REFERENCES empresas(id),
    clientes_afectados INTEGER NOT NULL,
    clientes_totales INTEGER NOT NULL,
    porcentaje_afectados NUMERIC(10, 2),
    timestamp_sec TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para optimizar consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_historico_timestamp ON cortes_historico(timestamp_sec DESC);
CREATE INDEX IF NOT EXISTS idx_historico_comuna ON cortes_historico(comuna_id);

-- Comentario sobre la estrategia:
-- - `cortes_historico` crecerá con cada ejecución del scraper (cada 5 min).
-- - `cortes_tiempo_real` contendrá solo el "último Snapshot" de cada punto de corte.
