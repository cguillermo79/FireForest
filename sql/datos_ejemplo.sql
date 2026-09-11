INSERT INTO dim_celda
    (celda_id, longitud, latitud, area_km2, epsg)
VALUES
    ('LJ_04521', -79.241, -4.082, 0.25, 4326),
    ('LJ_04522', -79.236, -4.079, 0.25, 4326)
ON CONFLICT (celda_id) DO NOTHING;

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