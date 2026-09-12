-- Consulta 1 (Operativa | SELECT + WHERE)
-- Pregunta: ¿Qué detecciones de incendio existen para la celda LJ_001 entre
-- julio y agosto de 2023?
SELECT
    fi.incendio_id,
    fi.celda_id,
    df.fecha,
    fi.numero_detecciones,
    fi.frp_maxima_mw,
    fi.incendio_observado
FROM fact_incendio AS fi
JOIN dim_fecha AS df ON df.fecha_id = fi.fecha_id
WHERE fi.celda_id = 'LJ_001'
  AND df.fecha BETWEEN '2023-07-01' AND '2023-08-31'
ORDER BY df.fecha;
