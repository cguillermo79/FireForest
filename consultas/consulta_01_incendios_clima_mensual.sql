-- Consulta 01: ranking mensual de celdas con mayor actividad de incendios
-- y comparación con la precipitación acumulada y media del mismo mes.
--
-- Objetivo: identificar qué celdas presentan más detecciones y severidad
-- de incendios en relación con el clima del periodo analizado.

WITH incendio_mes AS (
    SELECT
        df.anio,
        df.mes,
        fi.celda_id,
        SUM(fi.numero_detecciones) AS detecciones_totales,
        SUM(COALESCE(fi.frp_suma_mw, 0)) AS frp_total_mw,
        MAX(fi.frp_maxima_mw) AS frp_maxima_mw,
        COUNT(*) AS numero_dias_con_incendio
    FROM fact_incendio AS fi
    INNER JOIN dim_fecha AS df
        ON df.fecha_id = fi.fecha_id
    GROUP BY df.anio, df.mes, fi.celda_id
),
clima_mes AS (
    SELECT
        df.anio,
        df.mes,
        fc.celda_id,
        AVG(fc.precipitacion_acumulada_mm) AS precipitacion_promedio_mm,
        SUM(fc.precipitacion_acumulada_mm) AS precipitacion_total_mm,
        MAX(fc.precipitacion_maxima_diaria_mm) AS precipitacion_maxima_diaria_mm
    FROM fact_clima AS fc
    INNER JOIN dim_fecha AS df
        ON df.fecha_id = fc.fecha_id
    GROUP BY df.anio, df.mes, fc.celda_id
)
SELECT
    i.anio,
    i.mes,
    i.celda_id,
    dc.longitud,
    dc.latitud,
    i.detecciones_totales,
    i.frp_total_mw,
    i.frp_maxima_mw,
    c.precipitacion_promedio_mm,
    c.precipitacion_total_mm,
    c.precipitacion_maxima_diaria_mm
FROM incendio_mes AS i
INNER JOIN clima_mes AS c
    ON c.anio = i.anio
   AND c.mes = i.mes
   AND c.celda_id = i.celda_id
INNER JOIN dim_celda AS dc
    ON dc.celda_id = i.celda_id
ORDER BY i.anio, i.mes, i.detecciones_totales DESC, i.frp_total_mw DESC;
