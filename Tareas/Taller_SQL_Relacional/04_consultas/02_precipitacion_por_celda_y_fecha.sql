-- Consulta 2 (Operativa | SELECT + WHERE)
-- Pregunta: ¿Cuál fue la precipitación diaria registrada en la celda LJ_003
-- durante septiembre de 2023?
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
