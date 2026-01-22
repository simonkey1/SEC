CREATE TABLE dim_geografia (
    -- Aquí define las columnas con sus tipos
    -- Recuerda: 1 PK, 4 columnas de texto para los nombres

    id_geografia SERIAL PRIMARY KEY,
    nombre_comuna VARCHAR(100) NOT NULL,
    nombre_region VARCHAR(100) NOT NULL,
    nombre_provincia VARCHAR(100) DEFAULT '',
    codigo_comuna INT DEFAULT 0

);

CREATE TABLE dim_empresa(
    id_empresa SERIAL PRIMARY KEY,
    nombre_empresa VARCHAR(100) NOT NULL UNIQUE,
    rut_empresa VARCHAR(100) DEFAULT NULL
);

CREATE TABLE dim_tiempo(
    id_tiempo BIGINT PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    año SMALLINT NOT NULL,
    mes SMALLINT NOT NULL,
    dia SMALLINT NOT NULL
);

CREATE TABLE fact_interrupciones(
    id_fact BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_tiempo BIGINT NOT NULL,
    id_geografia INT NOT NULL,
    id_empresa INT NOT NULL,
    clientes_afectados INT NOT NULL,
    hash_id VARCHAR(100) NOT NULL UNIQUE,

    FOREIGN KEY (id_tiempo) REFERENCES dim_tiempo(id_tiempo),
    FOREIGN KEY (id_geografia) REFERENCES dim_geografia(id_geografia)
    FOREIGN KEY (id_empresa) REFERENCES dim_empresa(id_empresa)
);

CREATE INDEX idx_tiempo ON fact_interrupciones(id_tiempo DESC);
CREATE INDEX idx_geografia ON fact_interrupciones(id_geografia);
CREATE INDEX idx_empresa ON fact_interrupciones(id_empresa);
CREATE INDEX inx_created_at ON fact_interrupciones(created_at DESC);