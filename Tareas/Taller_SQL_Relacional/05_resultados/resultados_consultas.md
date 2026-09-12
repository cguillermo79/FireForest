# Resultados de las consultas — Taller SQL (Práctica 2, M1721)

Ejecutadas contra la base `taller_sql_fireforest` (datos de ejemplo controlados). Las
interpretaciones se basan únicamente en los valores mostrados en la tabla de resultado de cada
consulta; no establecen causalidad ni proyectan comportamiento futuro.

## Consulta 1 — 01_detecciones_por_celda_y_periodo.sql

### 1. Pregunta
¿Qué detecciones de incendio existen para la celda LJ_001 entre julio y agosto de 2023?

### 2. SQL
```sql
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

### 3. Resultado real
**Filas devueltas:** 2

| incendio_id | celda_id | fecha | numero_detecciones | frp_maxima_mw | incendio_observado |
|---|---|---|---|---|---|
| INC_0001 | LJ_001 | 2023-07-05 | 2 | 15.200 | True |
| INC_0002 | LJ_001 | 2023-08-15 | 1 | 10.100 | True |

### 4. Interpretación
En el periodo julio–agosto de 2023, la celda LJ_001 registra dos detecciones: 2 el 5 de julio
(FRP máxima 15.2 MW) y 1 el 15 de agosto (FRP máxima 10.1 MW). Ambas fechas quedaron marcadas
como incendio observado; no hay otras fechas con registro para esta celda en el rango consultado.

---

## Consulta 2 — 02_precipitacion_por_celda_y_fecha.sql

### 1. Pregunta
¿Cuál fue la precipitación diaria registrada en la celda LJ_003 durante septiembre de 2023?

### 2. SQL
```sql
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

### 3. Resultado real
**Filas devueltas:** 1

| celda_id | fecha | precipitacion_diaria_mm |
|---|---|---|
| LJ_003 | 2023-09-20 | 6.40 |

### 4. Interpretación
Para LJ_003, septiembre de 2023 tiene un único registro de precipitación cargado: 6.40 mm el día
20. No existen otros días de ese mes con dato de precipitación para esta celda en la base.

---

## Consulta 3 — 03_top5_detecciones_por_frp.sql

### 1. Pregunta
¿Cuáles son las 5 detecciones individuales con mayor intensidad (FRP máxima) registrada en todo
el periodo?

### 2. SQL
```sql
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

### 3. Resultado real
**Filas devueltas:** 5

| incendio_id | celda_id | fecha | frp_maxima_mw | numero_detecciones |
|---|---|---|---|---|
| INC_0014 | LJ_005 | 2023-08-15 | 25.600 | 5 |
| INC_0007 | LJ_003 | 2023-07-25 | 22.100 | 4 |
| INC_0005 | LJ_002 | 2023-08-20 | 20.300 | 3 |
| INC_0001 | LJ_001 | 2023-07-05 | 15.200 | 2 |
| INC_0016 | LJ_006 | 2023-07-15 | 14.500 | 2 |

### 4. Interpretación
Las cinco detecciones de mayor FRP máxima van de 25.6 MW (LJ_005, 15-ago) a 14.5 MW (LJ_006,
15-jul) y corresponden a cinco celdas distintas, sin que ninguna concentre más de un evento en
este top 5. El número de detecciones asociado a cada evento varía entre 2 y 5.

---

## Consulta 4 — 04_incendios_sin_precipitacion_registrada.sql

### 1. Pregunta
¿Qué celdas tienen incendio observado en una fecha para la que NO existe registro de
precipitación (sin correspondencia válida)?

### 2. SQL
```sql
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

### 3. Resultado real
**Filas devueltas:** 1

| celda_id | fecha | numero_detecciones | precipitacion_diaria_mm |
|---|---|---|---|
| LJ_001 | 2023-07-05 | 2 |  |

### 4. Interpretación
Se identifica un único caso sin correspondencia: LJ_001 tiene incendio observado el 5 de julio de
2023 (2 detecciones) pero no cuenta con registro de precipitación para esa misma fecha. En el
resto de fechas con incendio observado sí existe un registro de precipitación asociado.

---

## Consulta 5 — 05_detalle_incendios_tres_tablas.sql

### 1. Pregunta
¿Cuál es el listado completo y legible de detecciones de incendio observadas, con el nombre de
referencia de la celda y la fecha calendario (no solo los identificadores numéricos)?

### 2. SQL
```sql
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

### 3. Resultado real
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

### 4. Interpretación
Las 10 fechas con incendio observado se reparten en los tres meses del periodo (julio, agosto y
septiembre), sin que un solo mes concentre la mayoría de los casos. El valor de
`fire_mask_maximo` va de 5 a 9 y el número de detecciones por fecha entre 1 y 5, mostrando
variedad tanto en calidad de detección como en magnitud del evento.

---

## Consulta 6 — 06_frp_y_detecciones_por_celda.sql

### 1. Pregunta
¿Cuántas detecciones totales y qué FRP promedio y máximo presenta cada celda en todo el periodo?

### 2. SQL
```sql
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

### 3. Resultado real
**Filas devueltas:** 6

| celda_id | nombre_referencia | dias_con_registro | detecciones_totales | frp_promedio_mw | frp_maxima_mw |
|---|---|---|---|---|---|
| LJ_003 | Sector El Pedestal | 3 | 6 | 17.05 | 22.100 |
| LJ_005 | Sector San Cayetano | 3 | 6 | 16.40 | 25.600 |
| LJ_002 | Sector Landangui | 3 | 4 | 14.50 | 20.300 |
| LJ_001 | Sector La Toma | 3 | 3 | 12.65 | 15.200 |
| LJ_006 | Sector Zamora Huayco | 3 | 2 | 14.50 | 14.500 |
| LJ_004 | Sector Amable Maria | 3 | 1 | 9.30 | 9.300 |

### 4. Interpretación (analítica)
LJ_003 y LJ_005 concentran el mayor número de detecciones acumuladas del periodo (6 cada una),
mientras que LJ_004 registra solo 1. Comparando intensidad: LJ_005 tiene el FRP máximo más alto
de las seis celdas (25.6 MW), pero su FRP promedio (16.40 MW) es ligeramente menor al de LJ_003
(17.05 MW); es decir, LJ_003 mantiene una intensidad promedio algo más alta pese a no tener el
pico máximo absoluto. Esto es una comparación entre celdas, no una tendencia temporal.

---

## Consulta 7 — 07_meses_con_precipitacion_baja.sql

### 1. Pregunta
¿Qué celdas y meses acumulan una precipitación total por debajo de 20 mm (posible déficit
hídrico del mes)?

### 2. SQL
```sql
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

### 3. Resultado real
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

### 4. Interpretación (analítica)
Nueve combinaciones celda-mes acumulan menos de 20 mm de precipitación en los datos cargados.
LJ_002 en julio es el caso extremo, con 0.00 mm sobre un único día registrado, mientras que LJ_001
en julio es el más cercano al umbral (18.40 mm). La mayoría de estos casos (7 de 9) tienen solo 1
o 2 días con registro de precipitación en el mes, por lo que el acumulado bajo también puede
reflejar cobertura de datos incompleta y no únicamente ausencia real de lluvia.

---

## Consulta 8 — 08_cte_incendio_y_precipitacion_mensual.sql

### 1. Pregunta
¿Qué combinaciones celda-mes presentan a la vez detecciones de incendio y precipitación mensual
acumulada baja (< 20 mm)? Es una asociación descriptiva observada en los datos de ejemplo, no una
relación causal.

### 2. SQL
```sql
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

### 3. Resultado real
**Filas devueltas:** 5

| celda_id | anio | mes | detecciones_totales | precipitacion_acumulada_mm |
|---|---|---|---|---|
| LJ_003 | 2023 | 7 | 4 | 2.10 |
| LJ_005 | 2023 | 8 | 5 | 4.50 |
| LJ_003 | 2023 | 9 | 2 | 6.40 |
| LJ_004 | 2023 | 8 | 1 | 14.40 |
| LJ_001 | 2023 | 7 | 2 | 18.40 |

### 4. Interpretación (analítica)
En 5 de las combinaciones celda-mes del periodo coexisten detecciones de incendio y una
precipitación mensual acumulada baja; el caso más marcado es LJ_003 en julio (4 detecciones con
solo 2.10 mm) y LJ_005 en agosto (5 detecciones con 4.50 mm). Esto describe una asociación
observada entre ambas variables en los datos de ejemplo, sin que constituya evidencia de
causalidad ni deba extrapolarse a otros periodos o celdas no incluidos en esta muestra.

---

## Consulta 9 — 09_extra_cobertura_vegetal_y_detecciones.sql

**Consulta adicional — fuera del mínimo exigido por la guía.**

### 1. Pregunta
¿Qué tipo de cobertura vegetal concentra más detecciones de incendio? Usa explícitamente la
relación muchos-a-muchos `dim_celda` ↔ `dim_cobertura_vegetal` resuelta por `celda_cobertura`.

### 2. SQL
```sql
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

### 3. Resultado real
**Filas devueltas:** 5

| cobertura_vegetal | celdas_con_esta_cobertura | detecciones_totales |
|---|---|---|
| Matorral | 2 | 10 |
| Pastizal | 4 | 10 |
| Bosque nativo | 2 | 9 |
| Cultivo | 2 | 7 |
| Area urbana | 1 | 2 |

### 4. Interpretación (analítica)
Matorral y Pastizal concentran el mayor número de detecciones acumuladas (10 cada una), aunque
Pastizal está presente en el doble de celdas (4) que Matorral (2), por lo que su detección
promedio por celda es menor. Área urbana es la cobertura con menos detecciones asociadas (2) y
también la que aparece en una sola celda. Esta es una concentración descriptiva observada en los
datos de ejemplo; no implica que el tipo de cobertura vegetal sea causa de la ocurrencia de
incendios.
