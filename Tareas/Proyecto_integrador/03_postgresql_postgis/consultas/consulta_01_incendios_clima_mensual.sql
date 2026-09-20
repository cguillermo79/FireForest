-- Consulta 01: ranking mensual de celdas con mayor actividad de incendios
-- y comparación con la precipitación acumulada y media del mismo mes.
--
-- Objetivo: identificar qué celdas presentan más detecciones y severidad
-- de incendios en relación con el clima del periodo analizado.
--
-- Correccion metodologica (2026-09-13): la version anterior usaba
-- incendio_mes como base del JOIN final (INNER JOIN contra clima_mes),
-- por lo que un celda-mes con precipitacion pero sin ninguna fila en
-- fact_incendio (es decir, sin incendio ese mes) desaparecia por completo
-- del resultado. Eso equivalia a tratar "ausencia de incendio" como si
-- fuera "dato faltante", cuando en realidad CHIRPS puede tener el mes
-- completo mientras VIIRS legitimamente no registro ninguna deteccion.
-- Ahora clima_mes es la base (LEFT JOIN hacia incendio_mes) y las metricas
-- de incendio se representan con COALESCE(...,0) cuando no hay fila en
-- incendio_mes, preservando todos los meses con clima registrado.

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
    -- CHIRPS es un producto diario: precipitacion_diaria_mm guarda un unico
    -- valor por celda-dia. Acumulada/media/maxima solo tienen sentido al
    -- agregar esos valores diarios por mes, aqui mismo.
    SELECT
        df.anio,
        df.mes,
        fc.celda_id,
        SUM(fc.precipitacion_diaria_mm) AS precipitacion_acumulada_mensual_mm,
        AVG(fc.precipitacion_diaria_mm) AS precipitacion_media_diaria_mm,
        MAX(fc.precipitacion_diaria_mm) AS precipitacion_maxima_diaria_mm
    FROM fact_clima AS fc
    INNER JOIN dim_fecha AS df
        ON df.fecha_id = fc.fecha_id
    GROUP BY df.anio, df.mes, fc.celda_id
)
SELECT
    c.anio,
    c.mes,
    c.celda_id,
    dc.longitud,
    dc.latitud,
    COALESCE(i.detecciones_totales, 0) AS detecciones_totales,
    COALESCE(i.frp_total_mw, 0) AS frp_total_mw,
    COALESCE(i.frp_maxima_mw, 0) AS frp_maxima_mw,
    COALESCE(i.numero_dias_con_incendio, 0) AS numero_dias_con_incendio,
    c.precipitacion_acumulada_mensual_mm,
    c.precipitacion_media_diaria_mm,
    c.precipitacion_maxima_diaria_mm
FROM clima_mes AS c
LEFT JOIN incendio_mes AS i
    ON i.anio = c.anio
   AND i.mes = c.mes
   AND i.celda_id = c.celda_id
INNER JOIN dim_celda AS dc
    ON dc.celda_id = c.celda_id
ORDER BY c.anio, c.mes, COALESCE(i.detecciones_totales, 0) DESC,
         c.precipitacion_acumulada_mensual_mm DESC, c.celda_id;
