# Resultados de las consultas — Taller SQL (Practica 2, M1721)

## 01_detecciones_por_celda_y_periodo.sql

```sql
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
```

**Filas devueltas:** 2

| incendio_id | celda_id | fecha | numero_detecciones | frp_maxima_mw | incendio_observado |
|---|---|---|---|---|---|
| INC_0001 | LJ_001 | 2023-07-05 | 2 | 15.200 | True |
| INC_0002 | LJ_001 | 2023-08-15 | 1 | 10.100 | True |

## 02_precipitacion_por_celda_y_fecha.sql

```sql
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
```

**Filas devueltas:** 1

| celda_id | fecha | precipitacion_diaria_mm |
|---|---|---|
| LJ_003 | 2023-09-20 | 6.40 |

## 03_top5_detecciones_por_frp.sql

```sql
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
```

**Filas devueltas:** 5

| incendio_id | celda_id | fecha | frp_maxima_mw | numero_detecciones |
|---|---|---|---|---|
| INC_0014 | LJ_005 | 2023-08-15 | 25.600 | 5 |
| INC_0007 | LJ_003 | 2023-07-25 | 22.100 | 4 |
| INC_0005 | LJ_002 | 2023-08-20 | 20.300 | 3 |
| INC_0001 | LJ_001 | 2023-07-05 | 15.200 | 2 |
| INC_0016 | LJ_006 | 2023-07-15 | 14.500 | 2 |

## 04_incendios_sin_precipitacion_registrada.sql

```sql
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
```

**Filas devueltas:** 1

| celda_id | fecha | numero_detecciones | precipitacion_diaria_mm |
|---|---|---|---|
| LJ_001 | 2023-07-05 | 2 |  |

## 05_detalle_incendios_tres_tablas.sql

```sql
-- Consulta 5 (Operativa | INNER JOIN entre 3 tablas)
-- Pregunta: ¿Cuál es el listado completo y legible de detecciones de
-- incendio observadas, con el nombre de referencia de la celda y la fecha
-- calendario (no solo los identificadores numéricos)?
SELECT
    dc.nombre_referencia,
    df.fecha,
    df.mes,
    fi.numero_detecciones,
    fi.frp_maxima_mw,
    fi.fire_mask_maximo
FROM fact_incendio AS fi
JOIN dim_celda AS dc ON dc.celda_id = fi.celda_id
JOIN dim_fecha AS df ON df.fecha_id = fi.fecha_id
WHERE fi.incendio_observado = TRUE
ORDER BY df.fecha, dc.nombre_referencia;
```

**Filas devueltas:** 10

| nombre_referencia | fecha | mes | numero_detecciones | frp_maxima_mw | fire_mask_maximo |
|---|---|---|---|---|---|
| Sector La Toma | 2023-07-05 | 7 | 2 | 15.200 | 8 |
| Sector Zamora Huayco | 2023-07-15 | 7 | 2 | 14.500 | 7 |
| Sector El Pedestal | 2023-07-25 | 7 | 4 | 22.100 | 8 |
| Sector Amable Maria | 2023-08-10 | 8 | 1 | 9.300 | 6 |
| Sector La Toma | 2023-08-15 | 8 | 1 | 10.100 | 7 |
| Sector San Cayetano | 2023-08-15 | 8 | 5 | 25.600 | 9 |
| Sector Landangui | 2023-08-20 | 8 | 3 | 20.300 | 9 |
| Sector San Cayetano | 2023-09-05 | 9 | 1 | 7.200 | 5 |
| Sector Landangui | 2023-09-15 | 9 | 1 | 8.700 | 6 |
| Sector El Pedestal | 2023-09-20 | 9 | 2 | 12.000 | 7 |

## 06_frp_y_detecciones_por_celda.sql

```sql
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
```

**Filas devueltas:** 6

| celda_id | nombre_referencia | dias_con_registro | detecciones_totales | frp_promedio_mw | frp_maxima_mw |
|---|---|---|---|---|---|
| LJ_003 | Sector El Pedestal | 3 | 6 | 17.05 | 22.100 |
| LJ_005 | Sector San Cayetano | 3 | 6 | 16.40 | 25.600 |
| LJ_002 | Sector Landangui | 3 | 4 | 14.50 | 20.300 |
| LJ_001 | Sector La Toma | 3 | 3 | 12.65 | 15.200 |
| LJ_006 | Sector Zamora Huayco | 3 | 2 | 14.50 | 14.500 |
| LJ_004 | Sector Amable Maria | 3 | 1 | 9.30 | 9.300 |

## 07_meses_con_precipitacion_baja.sql

```sql
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
```

**Filas devueltas:** 9

| celda_id | anio | mes | precipitacion_acumulada_mm | precipitacion_minima_mm | dias_con_registro |
|---|---|---|---|---|---|
| LJ_002 | 2023 | 7 | 0.00 | 0.00 | 1 |
| LJ_005 | 2023 | 7 | 0.50 | 0.50 | 1 |
| LJ_003 | 2023 | 7 | 2.10 | 0.00 | 2 |
| LJ_005 | 2023 | 8 | 4.50 | 0.50 | 2 |
| LJ_003 | 2023 | 9 | 6.40 | 6.40 | 1 |
| LJ_006 | 2023 | 8 | 10.00 | 10.00 | 1 |
| LJ_004 | 2023 | 8 | 14.40 | 5.50 | 2 |
| LJ_001 | 2023 | 9 | 14.70 | 0.00 | 2 |
| LJ_001 | 2023 | 7 | 18.40 | 18.40 | 1 |

## 08_cte_incendio_y_precipitacion_mensual.sql

```sql
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
```

**Filas devueltas:** 5

| celda_id | anio | mes | detecciones_totales | precipitacion_acumulada_mm |
|---|---|---|---|---|
| LJ_003 | 2023 | 7 | 4 | 2.10 |
| LJ_005 | 2023 | 8 | 5 | 4.50 |
| LJ_003 | 2023 | 9 | 2 | 6.40 |
| LJ_004 | 2023 | 8 | 1 | 14.40 |
| LJ_001 | 2023 | 7 | 2 | 18.40 |

## 09_extra_cobertura_vegetal_y_detecciones.sql

```sql
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
```

**Filas devueltas:** 5

| cobertura_vegetal | celdas_con_esta_cobertura | detecciones_totales |
|---|---|---|
| Matorral | 2 | 10 |
| Pastizal | 4 | 10 |
| Bosque nativo | 2 | 9 |
| Cultivo | 2 | 7 |
| Area urbana | 1 | 2 |
