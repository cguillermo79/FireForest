-- ============================================================
-- Taller SQL (Practica 2, M1721) - Esquema relacional
-- Base de datos independiente: taller_sql_fireforest
-- Practica independiente del Proyecto Integrador FireForest.
-- No reutiliza archivos de FIRELAB_Loja ni modifica la base "fireforest".
-- ============================================================

-- ------------------------------------------------------------
-- dim_celda: unidad territorial de referencia (500 m x 500 m).
-- PK natural (celda_id). Auditoria: se retira el tipo GEOMETRY/PostGIS
-- usado en FireForest porque este taller es estrictamente relacional
-- y la guia no exige capacidades geoespaciales; se conservan las
-- coordenadas como NUMERIC para mantener el taller autocontenido
-- (no requiere la extension PostGIS).
-- ------------------------------------------------------------
CREATE TABLE dim_celda (
    celda_id            VARCHAR(20) PRIMARY KEY,
    nombre_referencia   VARCHAR(60) NOT NULL,
    longitud            NUMERIC(9,6) NOT NULL,
    latitud             NUMERIC(9,6) NOT NULL,
    area_km2            NUMERIC(6,3) NOT NULL DEFAULT 0.25 CHECK (area_km2 > 0),
    CONSTRAINT uq_celda_coordenadas UNIQUE (longitud, latitud)
);

-- ------------------------------------------------------------
-- dim_fecha: calendario diario del periodo de estudio.
-- Nota de normalizacion (ver 01_documentacion/normalizacion.md):
-- anio y mes se derivan funcionalmente de "fecha" (no de fecha_id
-- directamente). Es una dependencia transitiva deliberada, tipica
-- de una dimension de tiempo, que se mantiene para permitir agregar
-- por anio/mes sin recalcular EXTRACT() en cada consulta.
-- ------------------------------------------------------------
CREATE TABLE dim_fecha (
    fecha_id    INTEGER PRIMARY KEY,          -- formato AAAAMMDD
    fecha       DATE NOT NULL UNIQUE,
    anio        SMALLINT NOT NULL,
    mes         SMALLINT NOT NULL CHECK (mes BETWEEN 1 AND 12),
    CONSTRAINT chk_fecha_id_consistente CHECK (fecha_id = (EXTRACT(YEAR FROM fecha)::INT * 10000
                                                          + EXTRACT(MONTH FROM fecha)::INT * 100
                                                          + EXTRACT(DAY FROM fecha)::INT))
);

-- ------------------------------------------------------------
-- dim_cobertura_vegetal: catalogo de tipos de cobertura del suelo.
-- ------------------------------------------------------------
CREATE TABLE dim_cobertura_vegetal (
    cobertura_id    SMALLSERIAL PRIMARY KEY,
    nombre          VARCHAR(40) NOT NULL UNIQUE,
    descripcion     VARCHAR(120)
);

-- ------------------------------------------------------------
-- celda_cobertura: relacion N:M entre dim_celda y dim_cobertura_vegetal.
-- Una celda puede registrar mas de un tipo de cobertura por anio
-- (mosaico de uso de suelo); un tipo de cobertura aplica a muchas celdas.
-- PK compuesta (celda_id, cobertura_id, anio): porcentaje_cobertura
-- depende de los TRES atributos de la clave a la vez (no hay dependencia
-- parcial), lo que se documenta como evidencia de 2FN en normalizacion.md.
-- ------------------------------------------------------------
CREATE TABLE celda_cobertura (
    celda_id                VARCHAR(20) NOT NULL REFERENCES dim_celda(celda_id),
    cobertura_id            SMALLINT NOT NULL REFERENCES dim_cobertura_vegetal(cobertura_id),
    anio                    SMALLINT NOT NULL,
    porcentaje_cobertura    NUMERIC(5,2) NOT NULL CHECK (porcentaje_cobertura > 0 AND porcentaje_cobertura <= 100),
    PRIMARY KEY (celda_id, cobertura_id, anio)
);

-- ------------------------------------------------------------
-- fact_incendio: registro diario de deteccion de incendio por celda.
-- PK surrogate (incendio_id) + UNIQUE(celda_id, fecha_id): evita
-- depender de una clave compuesta como PK y con ello cualquier
-- dependencia parcial (ver normalizacion.md, seccion 2FN).
-- ------------------------------------------------------------
CREATE TABLE fact_incendio (
    incendio_id         VARCHAR(20) PRIMARY KEY,
    celda_id            VARCHAR(20) NOT NULL REFERENCES dim_celda(celda_id),
    fecha_id            INTEGER NOT NULL REFERENCES dim_fecha(fecha_id),
    fuente              VARCHAR(20) NOT NULL DEFAULT 'VIIRS',
    numero_detecciones  INTEGER NOT NULL DEFAULT 0 CHECK (numero_detecciones >= 0),
    frp_suma_mw         NUMERIC(10,3) CHECK (frp_suma_mw >= 0),
    frp_maxima_mw       NUMERIC(10,3) CHECK (frp_maxima_mw >= 0),
    fire_mask_maximo    SMALLINT CHECK (fire_mask_maximo BETWEEN 0 AND 9),
    incendio_observado  BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_incendio_celda_fecha UNIQUE (celda_id, fecha_id),
    CONSTRAINT chk_incendio_coherente CHECK (
        (incendio_observado = FALSE AND numero_detecciones = 0)
        OR (incendio_observado = TRUE AND numero_detecciones >= 1)
    )
);

-- ------------------------------------------------------------
-- fact_clima: registro diario de precipitacion por celda.
-- ------------------------------------------------------------
CREATE TABLE fact_clima (
    clima_id                    SERIAL PRIMARY KEY,
    celda_id                    VARCHAR(20) NOT NULL REFERENCES dim_celda(celda_id),
    fecha_id                    INTEGER NOT NULL REFERENCES dim_fecha(fecha_id),
    precipitacion_diaria_mm     NUMERIC(6,2) NOT NULL CHECK (precipitacion_diaria_mm >= 0),
    CONSTRAINT uq_clima_celda_fecha UNIQUE (celda_id, fecha_id)
);

-- ------------------------------------------------------------
-- Verificacion rapida de creacion (control basico, ver tambien 05_resultados/)
-- ------------------------------------------------------------
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
      'dim_celda', 'dim_fecha', 'dim_cobertura_vegetal',
      'celda_cobertura', 'fact_incendio', 'fact_clima'
  )
ORDER BY table_name;
