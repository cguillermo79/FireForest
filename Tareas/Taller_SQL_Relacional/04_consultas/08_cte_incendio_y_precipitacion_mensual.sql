-- Consulta 8 (Analítica | CTE)
-- Pregunta: ¿Qué combinaciones celda-mes presentan a la vez detecciones de
-- incendio y precipitación mensual acumulada baja (< 20 mm)?
-- Es una asociación descriptiva observada en los datos de ejemplo, no una
-- relación causal.
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
