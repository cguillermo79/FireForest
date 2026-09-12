-- Consulta 5 (Operativa | INNER JOIN entre 3 tablas)
-- Pregunta: ¿Cuál es el listado completo y legible de detecciones de
-- incendio observadas, con el nombre de referencia de la celda y la fecha
-- calendario (no solo los identificadores numéricos)?
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
