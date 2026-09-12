-- Consulta 9 (Extra, más allá del mínimo de 8 | JOIN a través de la relación N:M)
-- Pregunta: ¿Qué tipo de cobertura vegetal concentra más detecciones de
-- incendio? Usa explícitamente la relación muchos-a-muchos
-- dim_celda <-> dim_cobertura_vegetal resuelta por celda_cobertura.
-- Nota: no se afirma causalidad entre cobertura vegetal e incendios, solo
-- se describe la concentración observada en los datos de ejemplo.
SELECT
    cv.nombre                          AS cobertura_vegetal,
    COUNT(DISTINCT cc.celda_id)        AS celdas_con_esta_cobertura,
    SUM(fi.numero_detecciones)         AS detecciones_totales
FROM dim_cobertura_vegetal AS cv
JOIN celda_cobertura AS cc ON cc.cobertura_id = cv.cobertura_id
JOIN fact_incendio AS fi ON fi.celda_id = cc.celda_id
GROUP BY cv.nombre
ORDER BY detecciones_totales DESC;
