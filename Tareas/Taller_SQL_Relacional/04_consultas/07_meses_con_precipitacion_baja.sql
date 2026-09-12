-- Consulta 7 (Analítica | GROUP BY + HAVING)
-- Pregunta: ¿Qué celdas y meses acumulan una precipitación total por debajo
-- de 20 mm (posible déficit hídrico del mes)?
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
