-- Consulta 4 (Operativa | LEFT JOIN entre 2 tablas)
-- Pregunta: ¿Qué celdas tienen incendio observado en una fecha para la que
-- NO existe registro de precipitación (sin correspondencia válida)?
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
