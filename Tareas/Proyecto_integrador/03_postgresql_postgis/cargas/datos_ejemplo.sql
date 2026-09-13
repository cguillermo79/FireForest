-- longitud/latitud se conservan tal como llegan del origen, en grados
-- EPSG:4326. La columna "epsg" no se fuerza a 4326 aqui: describe el
-- sistema de referencia de "geom" (columna espacial autoritativa de la
-- celda), que el schema define en EPSG:32717 (DEFAULT de la tabla).
INSERT INTO dim_celda
    (celda_id, longitud, latitud, area_km2)
VALUES
    ('LJ_04521', -79.241, -4.082, 0.25),
    ('LJ_04522', -79.236, -4.079, 0.25)
ON CONFLICT (celda_id) DO NOTHING;

-- Geometria real de cada celda (poligono de 500 x 500 m = 0.25 km2,
-- coherente con area_km2) en EPSG:32717, tal como exige dim_celda.geom.
-- No se etiqueta el punto en grados directamente como si ya estuviera
-- en 32717: primero se fija su SRID real (4326, WGS84) con
-- ST_SetSRID(ST_MakePoint(...), 4326) y luego se reproyecta con
-- ST_Transform(..., 32717); recien sobre ese punto ya reproyectado
-- (en metros) se construye el cuadrado de 500 m de lado, centrado en
-- el punto, mediante ST_MakeEnvelope.
UPDATE dim_celda AS dc
SET epsg = 32717,
    geom = ST_MakeEnvelope(
        ST_X(t.punto_utm) - 250, ST_Y(t.punto_utm) - 250,
        ST_X(t.punto_utm) + 250, ST_Y(t.punto_utm) + 250,
        32717
    )
FROM (
    SELECT celda_id,
           ST_Transform(
               ST_SetSRID(ST_MakePoint(longitud, latitud), 4326),
               32717
           ) AS punto_utm
    FROM dim_celda
    WHERE celda_id IN ('LJ_04521', 'LJ_04522')
) AS t
WHERE dc.celda_id = t.celda_id;

INSERT INTO dim_fecha
    (fecha_id, fecha, anio, mes)
VALUES
    (20230815, '2023-08-15', 2023, 8),
    (20230820, '2023-08-20', 2023, 8)
ON CONFLICT (fecha_id) DO NOTHING;

INSERT INTO fact_clima
    (
        celda_id,
        fecha_id,
        precipitacion_diaria_mm
    )
VALUES
    ('LJ_04521', 20230815, 12.5),
    ('LJ_04522', 20230820, 8.7)
ON CONFLICT (celda_id, fecha_id) DO NOTHING;

INSERT INTO fact_incendio
    (
        incendio_id,
        celda_id,
        fecha_id,
        fuente,
        numero_detecciones,
        frp_suma_mw,
        frp_maxima_mw,
        fire_mask_maximo,
        incendio_observado
    )
VALUES
    ('V_2023_0001', 'LJ_04521', 20230815, 'VIIRS', 1, 18.4, 18.4, 7, TRUE),
    ('V_2023_0002', 'LJ_04522', 20230820, 'VIIRS', 1, 9.7, 9.7, 8, TRUE)
ON CONFLICT (incendio_id) DO NOTHING;