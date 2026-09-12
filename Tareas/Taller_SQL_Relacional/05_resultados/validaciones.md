# Validaciones — Taller SQL (Practica 2, M1721)

## Conteo de filas por tabla

- `dim_celda`: 6 filas
- `dim_fecha`: 12 filas
- `dim_cobertura_vegetal`: 5 filas
- `celda_cobertura`: 11 filas
- `fact_incendio`: 18 filas
- `fact_clima`: 30 filas

## PK sin duplicados

- `fact_incendio.incendio_id` unico: True
- `fact_clima.clima_id` unico: True

## Integridad referencial (FK)

- `fact_incendio` con celda inexistente: 0 (debe ser 0)
- `fact_clima` con fecha inexistente: 0 (debe ser 0)

## UNIQUE(celda_id, fecha_id)

- Duplicados logicos en `fact_incendio`: 0 (debe ser 0)

## Coherencia de valores

- Precipitaciones negativas: 0 (debe ser 0)
- FRP negativos: 0 (debe ser 0)
- Celdas con cobertura > 100% en un anio: 0 (debe ser 0) 

## CHECK rechaza valores no permitidos

- mes fuera de rango (13): rechazado correctamente por CHECK
- precipitacion negativa: rechazado correctamente por CHECK
- porcentaje de cobertura > 100: rechazado correctamente por CHECK

## Coherencia de fechas (dim_fecha)

No basta con que exista el `CHECK chk_fecha_id_consistente`: se ejecuta una consulta explícita
que compara cada fila de `dim_fecha` contra los componentes reales de su columna `fecha`, para
comprobar que `fecha_id`, `anio` y `mes` sean coherentes con `fecha`.

```sql
SELECT fecha_id, fecha, anio, mes
FROM dim_fecha
WHERE fecha_id <> (EXTRACT(YEAR FROM fecha)::INT * 10000
                  + EXTRACT(MONTH FROM fecha)::INT * 100
                  + EXTRACT(DAY FROM fecha)::INT)
   OR anio <> EXTRACT(YEAR FROM fecha)::INT
   OR mes  <> EXTRACT(MONTH FROM fecha)::INT;
```

**Resultado real (ejecutado contra `taller_sql_fireforest`):**

- Total de filas en `dim_fecha`: 12
- Filas incoherentes encontradas: **0** (consulta devolvió 0 filas)

Conclusión: para las 12 fechas cargadas, `fecha_id` coincide exactamente con `fecha` en formato
`AAAAMMDD`, y `anio`/`mes` coinciden exactamente con el año y el mes calendario de `fecha`. No es
solo una garantía estructural del `CHECK`: se verificó dato por dato.