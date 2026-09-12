-- Consulta 3 (Operativa/Analítica | ORDER BY + LIMIT)
-- Pregunta: ¿Cuáles son las 5 detecciones individuales con mayor intensidad
-- (FRP máxima) registrada en todo el periodo?
SELECT
    fi.incendio_id,
    fi.celda_id,
    df.fecha,
    fi.frp_maxima_mw,
    fi.numero_detecciones
FROM fact_incendio AS fi
JOIN dim_fecha AS df ON df.fecha_id = fi.fecha_id
WHERE fi.incendio_observado = TRUE
ORDER BY fi.frp_maxima_mw DESC
LIMIT 5;
