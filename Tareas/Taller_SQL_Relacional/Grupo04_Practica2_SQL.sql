-- ============================================================================
-- Practica 2 -- Taller SQL Relacional (M1721)
-- Grupo 04
--
-- Integrantes:
--   MALAN MULLO MARCO VINICIO
--   PUJOS CULQUE VIVIANA ISABEL
--   Carlos Guillermo Chuncho M.
--
-- Caso aplicado:
--   Deteccion de incendios forestales, precipitacion diaria y cobertura
--   vegetal por celda espacial y fecha, en el canton Loja. El objetivo es
--   integrar estas tres dimensiones en un esquema relacional que permita
--   responder preguntas operativas (consultar detecciones/precipitacion de
--   una celda y periodo) y analiticas (comparar celdas, meses y tipos de
--   cobertura vegetal segun numero de detecciones, FRP y precipitacion).
--
-- IMPORTANTE: todos los datos de este script son DE EJEMPLO Y CONTROLADOS,
-- generados especificamente para este taller. No son datos reales de VIIRS
-- ni de CHIRPS, y no provienen de archivos del proyecto FIRELAB_Loja.
--
-- Practica independiente del Proyecto Integrador FireForest: usa su propia
-- base de datos (recomendado: taller_sql_fireforest), separada de la base
-- "fireforest" del Proyecto Integrador. No requiere PostGIS ni MongoDB.
--
-- Este archivo es autocontenido: puede ejecutarse de principio a fin sobre
-- una base vacia, sin editar nada manualmente ni depender de otros archivos.
-- ============================================================================


-- ============================================================================
-- 1. DEFINICION DE TABLAS (CREATE TABLE, PK, FK, UNIQUE, CHECK, NOT NULL, DEFAULT)
-- ============================================================================

-- ------------------------------------------------------------
-- dim_celda: unidad territorial de referencia (500 m x 500 m).
-- PK natural (celda_id). No se usa PostGIS: este taller es estrictamente
-- relacional y la guia no exige capacidades geoespaciales; las coordenadas
-- se registran como NUMERIC para mantener el taller autocontenido.
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
-- anio y mes se derivan funcionalmente de "fecha" (dependencia transitiva
-- deliberada, tipica de una dimension de tiempo; ver normalizacion.md).
-- Se controla su coherencia con el CHECK chk_fecha_id_consistente y,
-- ademas, con una validacion explicita por consulta (ver seccion 5).
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
-- Una celda puede registrar mas de un tipo de cobertura por anio (mosaico
-- de uso de suelo); un tipo de cobertura aplica a muchas celdas.
-- PK compuesta (celda_id, cobertura_id, anio): porcentaje_cobertura
-- depende de los TRES atributos de la clave a la vez (sin dependencia
-- parcial; ver normalizacion.md, seccion 2FN).
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
-- PK surrogate (incendio_id) + UNIQUE(celda_id, fecha_id): evita depender
-- de una clave compuesta como PK, sin perder la integridad (ver 2FN).
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


-- ============================================================================
-- 2. CARGA DE DATOS DE EJEMPLO (INSERT) -- controlados, no reales
-- ============================================================================

-- dim_celda (6 celdas)
INSERT INTO dim_celda (celda_id, nombre_referencia, longitud, latitud, area_km2) VALUES
    ('LJ_001', 'Sector La Toma',        -79.2010, -4.0350, 0.25),
    ('LJ_002', 'Sector Landangui',      -79.1950, -4.0410, 0.25),
    ('LJ_003', 'Sector El Pedestal',    -79.2100, -4.0280, 0.25),
    ('LJ_004', 'Sector Amable Maria',   -79.1880, -4.0500, 0.25),
    ('LJ_005', 'Sector San Cayetano',   -79.2200, -4.0150, 0.25),
    ('LJ_006', 'Sector Zamora Huayco',  -79.1800, -4.0600, 0.25);

-- dim_fecha (12 fechas, jul-sep 2023)
INSERT INTO dim_fecha (fecha_id, fecha, anio, mes) VALUES
    (20230705, '2023-07-05', 2023, 7),
    (20230715, '2023-07-15', 2023, 7),
    (20230725, '2023-07-25', 2023, 7),
    (20230801, '2023-08-01', 2023, 8),
    (20230810, '2023-08-10', 2023, 8),
    (20230815, '2023-08-15', 2023, 8),
    (20230820, '2023-08-20', 2023, 8),
    (20230825, '2023-08-25', 2023, 8),
    (20230905, '2023-09-05', 2023, 9),
    (20230915, '2023-09-15', 2023, 9),
    (20230920, '2023-09-20', 2023, 9),
    (20230930, '2023-09-30', 2023, 9);

-- dim_cobertura_vegetal (5 tipos)
INSERT INTO dim_cobertura_vegetal (nombre, descripcion) VALUES
    ('Bosque nativo', 'Vegetacion arborea natural'),
    ('Pastizal',       'Pastos para ganaderia'),
    ('Matorral',       'Vegetacion arbustiva baja'),
    ('Cultivo',        'Areas agricolas'),
    ('Area urbana',    'Suelo urbano o construido');

-- celda_cobertura (relacion N:M, 11 filas; referencia por nombre para no
-- depender del valor autogenerado de cobertura_id)
INSERT INTO celda_cobertura (celda_id, cobertura_id, anio, porcentaje_cobertura)
SELECT 'LJ_001', cobertura_id, 2023, 70.00 FROM dim_cobertura_vegetal WHERE nombre = 'Bosque nativo'
UNION ALL SELECT 'LJ_001', cobertura_id, 2023, 30.00 FROM dim_cobertura_vegetal WHERE nombre = 'Pastizal'
UNION ALL SELECT 'LJ_002', cobertura_id, 2023, 60.00 FROM dim_cobertura_vegetal WHERE nombre = 'Pastizal'
UNION ALL SELECT 'LJ_002', cobertura_id, 2023, 40.00 FROM dim_cobertura_vegetal WHERE nombre = 'Matorral'
UNION ALL SELECT 'LJ_003', cobertura_id, 2023, 100.00 FROM dim_cobertura_vegetal WHERE nombre = 'Bosque nativo'
UNION ALL SELECT 'LJ_004', cobertura_id, 2023, 50.00 FROM dim_cobertura_vegetal WHERE nombre = 'Cultivo'
UNION ALL SELECT 'LJ_004', cobertura_id, 2023, 50.00 FROM dim_cobertura_vegetal WHERE nombre = 'Pastizal'
UNION ALL SELECT 'LJ_005', cobertura_id, 2023, 80.00 FROM dim_cobertura_vegetal WHERE nombre = 'Matorral'
UNION ALL SELECT 'LJ_005', cobertura_id, 2023, 20.00 FROM dim_cobertura_vegetal WHERE nombre = 'Cultivo'
UNION ALL SELECT 'LJ_006', cobertura_id, 2023, 40.00 FROM dim_cobertura_vegetal WHERE nombre = 'Area urbana'
UNION ALL SELECT 'LJ_006', cobertura_id, 2023, 60.00 FROM dim_cobertura_vegetal WHERE nombre = 'Pastizal';

-- fact_incendio (18 filas; mezcla de dias con y sin deteccion, distintos
-- niveles de FRP)
INSERT INTO fact_incendio
    (incendio_id, celda_id, fecha_id, fuente, numero_detecciones, frp_suma_mw, frp_maxima_mw, fire_mask_maximo, incendio_observado)
VALUES
    ('INC_0001', 'LJ_001', 20230705, 'VIIRS', 2, 25.4, 15.2, 8, TRUE),
    ('INC_0002', 'LJ_001', 20230815, 'VIIRS', 1, 10.1, 10.1, 7, TRUE),
    ('INC_0003', 'LJ_001', 20230905, 'VIIRS', 0, NULL, NULL, NULL, FALSE),
    ('INC_0004', 'LJ_002', 20230715, 'VIIRS', 0, NULL, NULL, NULL, FALSE),
    ('INC_0005', 'LJ_002', 20230820, 'VIIRS', 3, 45.6, 20.3, 9, TRUE),
    ('INC_0006', 'LJ_002', 20230915, 'VIIRS', 1, 8.7, 8.7, 6, TRUE),
    ('INC_0007', 'LJ_003', 20230725, 'VIIRS', 4, 60.2, 22.1, 8, TRUE),
    ('INC_0008', 'LJ_003', 20230825, 'VIIRS', 0, NULL, NULL, NULL, FALSE),
    ('INC_0009', 'LJ_003', 20230920, 'VIIRS', 2, 18.9, 12.0, 7, TRUE),
    ('INC_0010', 'LJ_004', 20230801, 'VIIRS', 0, NULL, NULL, NULL, FALSE),
    ('INC_0011', 'LJ_004', 20230810, 'VIIRS', 1, 9.3, 9.3, 6, TRUE),
    ('INC_0012', 'LJ_004', 20230930, 'VIIRS', 0, NULL, NULL, NULL, FALSE),
    ('INC_0013', 'LJ_005', 20230705, 'VIIRS', 0, NULL, NULL, NULL, FALSE),
    ('INC_0014', 'LJ_005', 20230815, 'VIIRS', 5, 80.5, 25.6, 9, TRUE),
    ('INC_0015', 'LJ_005', 20230905, 'VIIRS', 1, 7.2, 7.2, 5, TRUE),
    ('INC_0016', 'LJ_006', 20230715, 'VIIRS', 2, 22.0, 14.5, 7, TRUE),
    ('INC_0017', 'LJ_006', 20230820, 'VIIRS', 0, NULL, NULL, NULL, FALSE),
    ('INC_0018', 'LJ_006', 20230915, 'VIIRS', 0, NULL, NULL, NULL, FALSE);

-- fact_clima (30 filas; incluye una fecha con incendio observado SIN
-- precipitacion registrada a proposito: LJ_001 / 2023-07-05, para poder
-- ejercitar la consulta operativa de "sin correspondencia")
INSERT INTO fact_clima (celda_id, fecha_id, precipitacion_diaria_mm) VALUES
    ('LJ_001', 20230725, 18.4),
    ('LJ_001', 20230815, 3.2),
    ('LJ_001', 20230825, 22.0),
    ('LJ_001', 20230905, 0.0),
    ('LJ_001', 20230915, 14.7),

    ('LJ_002', 20230715, 0.0),
    ('LJ_002', 20230801, 30.5),
    ('LJ_002', 20230820, 1.5),
    ('LJ_002', 20230915, 9.8),
    ('LJ_002', 20230920, 40.2),

    ('LJ_003', 20230705, 2.1),
    ('LJ_003', 20230725, 0.0),
    ('LJ_003', 20230810, 12.3),
    ('LJ_003', 20230825, 55.0),
    ('LJ_003', 20230920, 6.4),

    ('LJ_004', 20230715, 20.0),
    ('LJ_004', 20230801, 8.9),
    ('LJ_004', 20230810, 5.5),
    ('LJ_004', 20230905, 33.1),
    ('LJ_004', 20230930, 0.0),

    ('LJ_005', 20230705, 0.5),
    ('LJ_005', 20230815, 0.5),
    ('LJ_005', 20230820, 4.0),
    ('LJ_005', 20230905, 1.2),
    ('LJ_005', 20230915, 60.7),

    ('LJ_006', 20230715, 5.0),
    ('LJ_006', 20230725, 65.3),
    ('LJ_006', 20230820, 10.0),
    ('LJ_006', 20230915, 0.0),
    ('LJ_006', 20230930, 28.6);


-- ============================================================================
-- 3. CONSULTAS OBLIGATORIAS (Consulta 1 a Consulta 8)
-- ============================================================================

-- ------------------------------------------------------------
-- Consulta 1 (Operativa | SELECT + WHERE)
-- Pregunta: ¿Qué detecciones de incendio existen para la celda LJ_001 entre
-- julio y agosto de 2023?
-- ------------------------------------------------------------
SELECT
    fi.incendio_id,
    fi.celda_id,
    df.fecha,
    fi.numero_detecciones,
    fi.frp_maxima_mw,
    fi.incendio_observado
FROM fact_incendio AS fi
JOIN dim_fecha AS df ON df.fecha_id = fi.fecha_id
WHERE fi.celda_id = 'LJ_001'
  AND df.fecha BETWEEN '2023-07-01' AND '2023-08-31'
ORDER BY df.fecha;

-- ------------------------------------------------------------
-- Consulta 2 (Operativa | SELECT + WHERE)
-- Pregunta: ¿Cuál fue la precipitación diaria registrada en la celda LJ_003
-- durante septiembre de 2023?
-- ------------------------------------------------------------
SELECT
    fc.celda_id,
    df.fecha,
    fc.precipitacion_diaria_mm
FROM fact_clima AS fc
JOIN dim_fecha AS df ON df.fecha_id = fc.fecha_id
WHERE fc.celda_id = 'LJ_003'
  AND df.anio = 2023
  AND df.mes = 9
ORDER BY df.fecha;

-- ------------------------------------------------------------
-- Consulta 3 (Operativa/Analítica | ORDER BY + LIMIT)
-- Pregunta: ¿Cuáles son las 5 detecciones individuales con mayor intensidad
-- (FRP máxima) registrada en todo el periodo?
-- ------------------------------------------------------------
SELECT
    fi.incendio_id,
    fi.celda_id,
    df.fecha,
    fi.frp_maxima_mw,
    fi.numero_detecciones
FROM fact_incendio AS fi
JOIN dim_fecha AS df ON df.fecha_id = fi.fecha_id
WHERE fi.incendio_observado = TRUE
ORDER BY fi.frp_maxima_mw DESC
LIMIT 5;

-- ------------------------------------------------------------
-- Consulta 4 (Operativa | LEFT JOIN, 3 tablas)
-- Pregunta: ¿Qué celdas tienen incendio observado en una fecha para la que
-- NO existe registro de precipitación (sin correspondencia válida)?
-- ------------------------------------------------------------
SELECT
    fi.celda_id,
    df.fecha,
    fi.numero_detecciones,
    fc.precipitacion_diaria_mm
FROM fact_incendio AS fi
JOIN dim_fecha AS df ON df.fecha_id = fi.fecha_id
LEFT JOIN fact_clima AS fc
       ON fc.celda_id = fi.celda_id
      AND fc.fecha_id = fi.fecha_id
WHERE fi.incendio_observado = TRUE
  AND fc.clima_id IS NULL
ORDER BY fi.celda_id, df.fecha;

-- ------------------------------------------------------------
-- Consulta 5 (Operativa | INNER JOIN entre 3 tablas)
-- Pregunta: ¿Cuál es el listado completo y legible de detecciones de
-- incendio observadas, con el nombre de referencia de la celda y la fecha
-- calendario (no solo los identificadores numéricos)?
-- ------------------------------------------------------------
SELECT
    dc.nombre_referencia,
    df.fecha,
    df.mes,
    fi.numero_detecciones,
    fi.frp_maxima_mw,
    fi.fire_mask_maximo
FROM fact_incendio AS fi
JOIN dim_celda AS dc ON dc.celda_id = fi.celda_id
JOIN dim_fecha AS df ON df.fecha_id = fi.fecha_id
WHERE fi.incendio_observado = TRUE
ORDER BY df.fecha, dc.nombre_referencia;

-- ------------------------------------------------------------
-- Consulta 6 (Analítica | GROUP BY + COUNT/SUM/AVG/MAX)
-- Pregunta: ¿Cuántas detecciones totales y qué FRP promedio y máximo
-- presenta cada celda en todo el periodo?
-- ------------------------------------------------------------
SELECT
    dc.celda_id,
    dc.nombre_referencia,
    COUNT(fi.incendio_id)             AS dias_con_registro,
    SUM(fi.numero_detecciones)        AS detecciones_totales,
    ROUND(AVG(fi.frp_maxima_mw), 2)   AS frp_promedio_mw,
    MAX(fi.frp_maxima_mw)             AS frp_maxima_mw
FROM dim_celda AS dc
JOIN fact_incendio AS fi ON fi.celda_id = dc.celda_id
GROUP BY dc.celda_id, dc.nombre_referencia
ORDER BY detecciones_totales DESC;

-- ------------------------------------------------------------
-- Consulta 7 (Analítica | GROUP BY + HAVING)
-- Pregunta: ¿Qué celdas y meses acumulan una precipitación total por debajo
-- de 20 mm (posible déficit hídrico del mes)?
-- ------------------------------------------------------------
SELECT
    fc.celda_id,
    df.anio,
    df.mes,
    SUM(fc.precipitacion_diaria_mm)  AS precipitacion_acumulada_mm,
    MIN(fc.precipitacion_diaria_mm)  AS precipitacion_minima_mm,
    COUNT(*)                          AS dias_con_registro
FROM fact_clima AS fc
JOIN dim_fecha AS df ON df.fecha_id = fc.fecha_id
GROUP BY fc.celda_id, df.anio, df.mes
HAVING SUM(fc.precipitacion_diaria_mm) < 20
ORDER BY precipitacion_acumulada_mm ASC;

-- ------------------------------------------------------------
-- Consulta 8 (Analítica | CTE)
-- Pregunta: ¿Qué combinaciones celda-mes presentan a la vez detecciones de
-- incendio y precipitación mensual acumulada baja (< 20 mm)?
-- Es una asociación descriptiva observada en los datos de ejemplo, no una
-- relación causal.
-- ------------------------------------------------------------
WITH detecciones_mes AS (
    SELECT
        fi.celda_id,
        df.anio,
        df.mes,
        SUM(fi.numero_detecciones) AS detecciones_totales
    FROM fact_incendio AS fi
    JOIN dim_fecha AS df ON df.fecha_id = fi.fecha_id
    GROUP BY fi.celda_id, df.anio, df.mes
),
clima_mes AS (
    SELECT
        fc.celda_id,
        df.anio,
        df.mes,
        SUM(fc.precipitacion_diaria_mm) AS precipitacion_acumulada_mm
    FROM fact_clima AS fc
    JOIN dim_fecha AS df ON df.fecha_id = fc.fecha_id
    GROUP BY fc.celda_id, df.anio, df.mes
)
SELECT
    d.celda_id,
    d.anio,
    d.mes,
    d.detecciones_totales,
    c.precipitacion_acumulada_mm
FROM detecciones_mes AS d
JOIN clima_mes AS c
  ON c.celda_id = d.celda_id AND c.anio = d.anio AND c.mes = d.mes
WHERE d.detecciones_totales > 0
  AND c.precipitacion_acumulada_mm < 20
ORDER BY c.precipitacion_acumulada_mm ASC;


-- ============================================================================
-- 4. CONSULTA ADICIONAL -- FUERA DEL MINIMO EXIGIDO POR LA GUIA
-- ============================================================================

-- ------------------------------------------------------------
-- Consulta adicional (JOIN a través de la relación N:M)
-- Pregunta: ¿Qué tipo de cobertura vegetal concentra más detecciones de
-- incendio? Usa explícitamente la relación muchos-a-muchos
-- dim_celda <-> dim_cobertura_vegetal resuelta por celda_cobertura.
-- Nota: no se afirma causalidad entre cobertura vegetal e incendios, solo
-- se describe la concentración observada en los datos de ejemplo.
-- ------------------------------------------------------------
SELECT
    cv.nombre                          AS cobertura_vegetal,
    COUNT(DISTINCT cc.celda_id)        AS celdas_con_esta_cobertura,
    SUM(fi.numero_detecciones)         AS detecciones_totales
FROM dim_cobertura_vegetal AS cv
JOIN celda_cobertura AS cc ON cc.cobertura_id = cv.cobertura_id
JOIN fact_incendio AS fi ON fi.celda_id = cc.celda_id
GROUP BY cv.nombre
ORDER BY detecciones_totales DESC;


-- ============================================================================
-- 5. VALIDACIONES
-- ============================================================================

-- ------------------------------------------------------------
-- 5.1 Conteo de filas por tabla (esperado: 6+12+5+11+18+30 = 82 filas)
-- ------------------------------------------------------------
SELECT 'dim_celda' AS tabla, COUNT(*) AS filas FROM dim_celda
UNION ALL SELECT 'dim_fecha', COUNT(*) FROM dim_fecha
UNION ALL SELECT 'dim_cobertura_vegetal', COUNT(*) FROM dim_cobertura_vegetal
UNION ALL SELECT 'celda_cobertura', COUNT(*) FROM celda_cobertura
UNION ALL SELECT 'fact_incendio', COUNT(*) FROM fact_incendio
UNION ALL SELECT 'fact_clima', COUNT(*) FROM fact_clima;

-- ------------------------------------------------------------
-- 5.2 PK sin duplicados (por construccion no pueden existir; se confirma
-- explicitamente comparando filas totales vs. valores distintos de PK)
-- ------------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM fact_incendio) = (SELECT COUNT(DISTINCT incendio_id) FROM fact_incendio) AS pk_incendio_unica,
    (SELECT COUNT(*) FROM fact_clima)    = (SELECT COUNT(DISTINCT clima_id)    FROM fact_clima)    AS pk_clima_unica;

-- ------------------------------------------------------------
-- 5.3 Integridad referencial (FK): filas huerfanas esperadas = 0
-- ------------------------------------------------------------
SELECT COUNT(*) AS incendios_con_celda_inexistente
FROM fact_incendio fi
LEFT JOIN dim_celda dc ON dc.celda_id = fi.celda_id
WHERE dc.celda_id IS NULL;

SELECT COUNT(*) AS clima_con_fecha_inexistente
FROM fact_clima fc
LEFT JOIN dim_fecha df ON df.fecha_id = fc.fecha_id
WHERE df.fecha_id IS NULL;

-- ------------------------------------------------------------
-- 5.4 Duplicados logicos por UNIQUE(celda_id, fecha_id): esperado = 0 filas
-- ------------------------------------------------------------
SELECT celda_id, fecha_id, COUNT(*)
FROM fact_incendio
GROUP BY celda_id, fecha_id
HAVING COUNT(*) > 1;

-- ------------------------------------------------------------
-- 5.5 Coherencia de valores: negativos y porcentaje de cobertura
-- ------------------------------------------------------------
SELECT COUNT(*) AS precipitaciones_negativas FROM fact_clima WHERE precipitacion_diaria_mm < 0;

SELECT COUNT(*) AS frp_negativos FROM fact_incendio WHERE frp_maxima_mw < 0;

SELECT celda_id, anio, SUM(porcentaje_cobertura) AS porcentaje_total
FROM celda_cobertura
GROUP BY celda_id, anio
HAVING SUM(porcentaje_cobertura) > 100;

-- ------------------------------------------------------------
-- 5.6 Coherencia de fechas (dim_fecha): fecha_id, anio y mes deben coincidir
-- con los componentes reales de "fecha". Esperado = 0 filas incoherentes.
-- ------------------------------------------------------------
SELECT fecha_id, fecha, anio, mes
FROM dim_fecha
WHERE fecha_id <> (EXTRACT(YEAR FROM fecha)::INT * 10000
                  + EXTRACT(MONTH FROM fecha)::INT * 100
                  + EXTRACT(DAY FROM fecha)::INT)
   OR anio <> EXTRACT(YEAR FROM fecha)::INT
   OR mes  <> EXTRACT(MONTH FROM fecha)::INT;

-- ------------------------------------------------------------
-- 5.7 CHECK rechaza valores no permitidos.
-- Se prueba dentro de bloques DO con manejo de excepcion (PL/pgSQL nativo
-- de PostgreSQL, no Python): cada intento de INSERT invalido se revierte
-- automaticamente al fallar y el resultado se reporta con RAISE NOTICE,
-- sin abortar la ejecucion del resto del script.
-- ------------------------------------------------------------
DO $$
BEGIN
    BEGIN
        INSERT INTO dim_fecha (fecha_id, fecha, anio, mes) VALUES (20240101, '2024-01-01', 2024, 13);
        RAISE NOTICE 'ADVERTENCIA: mes fuera de rango (13) NO fue rechazado';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'OK: mes fuera de rango (13) rechazado correctamente por CHECK';
    END;

    BEGIN
        INSERT INTO fact_clima (celda_id, fecha_id, precipitacion_diaria_mm) VALUES ('LJ_001', 20230705, -5);
        RAISE NOTICE 'ADVERTENCIA: precipitacion negativa NO fue rechazada';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'OK: precipitacion negativa rechazada correctamente por CHECK';
    END;

    BEGIN
        INSERT INTO celda_cobertura (celda_id, cobertura_id, anio, porcentaje_cobertura) VALUES ('LJ_001', 1, 2099, 150);
        RAISE NOTICE 'ADVERTENCIA: porcentaje de cobertura > 100 NO fue rechazado';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'OK: porcentaje de cobertura > 100 rechazado correctamente por CHECK';
    END;
END $$;

-- ============================================================================
-- Fin del script.
-- ============================================================================
