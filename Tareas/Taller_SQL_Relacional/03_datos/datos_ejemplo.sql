-- ============================================================
-- Taller SQL (Practica 2, M1721) - Datos de ejemplo controlados
-- NO son datos reales de VIIRS/CHIRPS ni provienen de FIRELAB_Loja.
-- Suficientes para producir resultados no triviales en las consultas
-- de 04_consultas/ (>= 30 filas distribuidas en 6 tablas).
-- ============================================================

-- ------------------------------------------------------------
-- dim_celda (6 celdas)
-- ------------------------------------------------------------
INSERT INTO dim_celda (celda_id, nombre_referencia, longitud, latitud, area_km2) VALUES
    ('LJ_001', 'Sector La Toma',        -79.2010, -4.0350, 0.25),
    ('LJ_002', 'Sector Landangui',      -79.1950, -4.0410, 0.25),
    ('LJ_003', 'Sector El Pedestal',    -79.2100, -4.0280, 0.25),
    ('LJ_004', 'Sector Amable Maria',   -79.1880, -4.0500, 0.25),
    ('LJ_005', 'Sector San Cayetano',   -79.2200, -4.0150, 0.25),
    ('LJ_006', 'Sector Zamora Huayco',  -79.1800, -4.0600, 0.25);

-- ------------------------------------------------------------
-- dim_fecha (12 fechas, jul-sep 2023)
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- dim_cobertura_vegetal (5 tipos)
-- ------------------------------------------------------------
INSERT INTO dim_cobertura_vegetal (nombre, descripcion) VALUES
    ('Bosque nativo', 'Vegetacion arborea natural'),
    ('Pastizal',       'Pastos para ganaderia'),
    ('Matorral',       'Vegetacion arbustiva baja'),
    ('Cultivo',        'Areas agricolas'),
    ('Area urbana',    'Suelo urbano o construido');

-- ------------------------------------------------------------
-- celda_cobertura (relacion N:M, 11 filas; referencia por nombre
-- para no depender del valor autogenerado de cobertura_id)
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- fact_incendio (18 filas; mezcla de dias con y sin deteccion,
-- distintos niveles de FRP)
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- fact_clima (30 filas; incluye una fecha con incendio observado
-- SIN precipitacion registrada a proposito: LJ_001 / 2023-07-05,
-- para poder ejercitar la consulta operativa de "sin correspondencia")
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- Conteo de filas por tabla (control basico, ver tambien 05_resultados/)
-- ------------------------------------------------------------
SELECT 'dim_celda' AS tabla, COUNT(*) AS filas FROM dim_celda
UNION ALL SELECT 'dim_fecha', COUNT(*) FROM dim_fecha
UNION ALL SELECT 'dim_cobertura_vegetal', COUNT(*) FROM dim_cobertura_vegetal
UNION ALL SELECT 'celda_cobertura', COUNT(*) FROM celda_cobertura
UNION ALL SELECT 'fact_incendio', COUNT(*) FROM fact_incendio
UNION ALL SELECT 'fact_clima', COUNT(*) FROM fact_clima;
