CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE dim_celda (
    celda_id VARCHAR(30) PRIMARY KEY,
    longitud DOUBLE PRECISION NOT NULL,
    latitud DOUBLE PRECISION NOT NULL,
    area_km2 NUMERIC(10,4),
    epsg INTEGER NOT NULL DEFAULT 32717,
    geom GEOMETRY(Polygon, 32717)
);

CREATE TABLE dim_fecha (
    fecha_id INTEGER PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12)
);

CREATE TABLE fact_incendio (
    incendio_id VARCHAR(40) PRIMARY KEY,
    celda_id VARCHAR(30) NOT NULL,
    fecha_id INTEGER NOT NULL,
    fuente VARCHAR(30) NOT NULL,
    numero_detecciones INTEGER DEFAULT 0 CHECK (numero_detecciones >= 0),
    frp_suma_mw NUMERIC(12,3),
    frp_maxima_mw NUMERIC(12,3),
    fire_mask_maximo INTEGER,
    incendio_observado BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_incendio_celda
        FOREIGN KEY (celda_id) REFERENCES dim_celda(celda_id),

    CONSTRAINT fk_incendio_fecha
        FOREIGN KEY (fecha_id) REFERENCES dim_fecha(fecha_id),

    CONSTRAINT uq_incendio_celda_fecha
        UNIQUE (celda_id, fecha_id)
);

CREATE TABLE fact_clima (
    clima_id BIGSERIAL PRIMARY KEY,
    celda_id VARCHAR(30) NOT NULL,
    fecha_id INTEGER NOT NULL,
    precipitacion_diaria_mm NUMERIC(12,3),

    CONSTRAINT fk_clima_celda
        FOREIGN KEY (celda_id) REFERENCES dim_celda(celda_id),

    CONSTRAINT fk_clima_fecha
        FOREIGN KEY (fecha_id) REFERENCES dim_fecha(fecha_id),

    CONSTRAINT uq_clima_celda_fecha
        UNIQUE (celda_id, fecha_id)
);

COMMENT ON COLUMN fact_incendio.frp_suma_mw IS
    'Suma descriptiva de los valores de FRP de las detecciones del dia; no representa energia acumulada ni potencia continua.';

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
      'dim_celda',
      'dim_fecha',
      'fact_incendio',
      'fact_clima'
  )
ORDER BY table_name;