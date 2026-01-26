-- Schema de Supabase para datos históricos de SEC
-- Interrupciones eléctricas en Chile

-- Tabla principal de interrupciones
CREATE TABLE IF NOT EXISTS interrupciones (
    id BIGSERIAL PRIMARY KEY,
    
    -- Fecha y hora de la interrupción
    fecha_interrupcion DATE NOT NULL,
    hora_interrupcion INTEGER NOT NULL CHECK (hora_interrupcion >= 0 AND hora_interrupcion <= 23),
    dia_int INTEGER,
    mes_int INTEGER,
    anho_int INTEGER,
    
    -- Ubicación
    region VARCHAR(100) NOT NULL,
    comuna VARCHAR(100) NOT NULL,
    
    -- Empresa distribuidora
    empresa VARCHAR(100) NOT NULL,
    
    -- Impacto
    clientes_afectados INTEGER NOT NULL DEFAULT 0,
    
    -- Metadata
    actualizado_hace VARCHAR(200),
    fecha_int_str VARCHAR(50),
    
    -- Timestamp de scraping
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para búsquedas rápidas
    CONSTRAINT unique_interrupcion UNIQUE (fecha_interrupcion, hora_interrupcion, region, comuna, empresa)
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_fecha_interrupcion ON interrupciones(fecha_interrupcion);
CREATE INDEX IF NOT EXISTS idx_empresa ON interrupciones(empresa);
CREATE INDEX IF NOT EXISTS idx_region ON interrupciones(region);
CREATE INDEX IF NOT EXISTS idx_fecha_empresa ON interrupciones(fecha_interrupcion, empresa);
CREATE INDEX IF NOT EXISTS idx_scraped_at ON interrupciones(scraped_at);

-- Tabla de snapshots (metadata de cada scraping)
CREATE TABLE IF NOT EXISTS scraping_snapshots (
    id BIGSERIAL PRIMARY KEY,
    fecha_consultada TIMESTAMP NOT NULL,
    fecha_scraping TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    registros_capturados INTEGER DEFAULT 0,
    duracion_segundos NUMERIC(10, 2),
    
    CONSTRAINT unique_snapshot UNIQUE (fecha_consultada)
);

-- Vista agregada por empresa y mes
CREATE OR REPLACE VIEW interrupciones_por_empresa_mes AS
SELECT 
    anho_int,
    mes_int,
    empresa,
    COUNT(*) as total_interrupciones,
    SUM(clientes_afectados) as total_clientes_afectados,
    AVG(clientes_afectados) as promedio_clientes_afectados,
    MIN(fecha_interrupcion) as primera_fecha,
    MAX(fecha_interrupcion) as ultima_fecha
FROM interrupciones
GROUP BY anho_int, mes_int, empresa
ORDER BY anho_int DESC, mes_int DESC, total_interrupciones DESC;

-- Vista agregada por región y mes
CREATE OR REPLACE VIEW interrupciones_por_region_mes AS
SELECT 
    anho_int,
    mes_int,
    region,
    COUNT(*) as total_interrupciones,
    SUM(clientes_afectados) as total_clientes_afectados,
    AVG(clientes_afectados) as promedio_clientes_afectados
FROM interrupciones
GROUP BY anho_int, mes_int, region
ORDER BY anho_int DESC, mes_int DESC, total_interrupciones DESC;

-- Función para insertar datos en batch
CREATE OR REPLACE FUNCTION insert_interrupciones_batch(
    p_data JSONB
) RETURNS INTEGER AS $$
DECLARE
    v_inserted INTEGER := 0;
    v_record JSONB;
BEGIN
    FOR v_record IN SELECT * FROM jsonb_array_elements(p_data)
    LOOP
        INSERT INTO interrupciones (
            dia_int,
            mes_int,
            anho_int,
            hora_interrupcion,
            fecha_interrupcion,
            region,
            comuna,
            empresa,
            clientes_afectados,
            actualizado_hace,
            fecha_int_str
        ) VALUES (
            (v_record->>'DIA_INT')::INTEGER,
            (v_record->>'MES_INT')::INTEGER,
            (v_record->>'ANHO_INT')::INTEGER,
            (v_record->>'HORA')::INTEGER,
            make_date(
                (v_record->>'ANHO_INT')::INTEGER,
                (v_record->>'MES_INT')::INTEGER,
                (v_record->>'DIA_INT')::INTEGER
            ),
            v_record->>'NOMBRE_REGION',
            v_record->>'NOMBRE_COMUNA',
            v_record->>'NOMBRE_EMPRESA',
            (v_record->>'CLIENTES_AFECTADOS')::INTEGER,
            v_record->>'ACTUALIZADO_HACE',
            v_record->>'FECHA_INT_STR'
        )
        ON CONFLICT (fecha_interrupcion, hora_interrupcion, region, comuna, empresa)
        DO UPDATE SET
            clientes_afectados = EXCLUDED.clientes_afectados,
            actualizado_hace = EXCLUDED.actualizado_hace,
            scraped_at = NOW();
        
        v_inserted := v_inserted + 1;
    END LOOP;
    
    RETURN v_inserted;
END;
$$ LANGUAGE plpgsql;

-- Comentarios para documentación
COMMENT ON TABLE interrupciones IS 'Registro histórico de interrupciones eléctricas en Chile desde 2017';
COMMENT ON TABLE scraping_snapshots IS 'Metadata de cada ejecución de scraping';
COMMENT ON COLUMN interrupciones.clientes_afectados IS 'Número de clientes sin servicio eléctrico';
COMMENT ON COLUMN interrupciones.scraped_at IS 'Timestamp de cuando se capturó este dato';
