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