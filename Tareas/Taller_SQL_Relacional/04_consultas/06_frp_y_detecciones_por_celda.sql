-- Consulta 6 (Analítica | GROUP BY + COUNT/SUM/AVG/MAX)
-- Pregunta: ¿Cuántas detecciones totales y qué FRP promedio y máximo
-- presenta cada celda en todo el periodo?
SELECT
    dc.celda_id,
    dc.nombre_referencia,
    COUNT(fi.incendio_id)             AS dias_con_registro,
    SUM(fi.numero_detecciones)        AS detecciones_totales,
    ROUND(AVG(fi.frp_maxima_mw), 2)   AS frp_promedio_mw,
    MAX(fi.frp_maxima_mw)             AS frp_maxima_mw
FROM dim_celda AS dc
JOIN fact_incendio AS fi ON fi.celda_id = dc.celda_id
GROUP BY dc.celda_id, dc.nombre_referencia
ORDER BY detecciones_totales DESC;
