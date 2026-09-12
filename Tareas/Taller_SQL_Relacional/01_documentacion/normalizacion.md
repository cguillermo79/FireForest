# Normalización — Taller SQL (Práctica 2, M1721)

Notación: `A → B` significa "A determina funcionalmente a B" (dado un valor de A, B queda
determinado de forma única). PK = clave primaria de la tabla.

## Modelo inicial (desnormalizado)

Antes de dividir en tablas, toda la información cabría en una sola tabla plana tipo:

```
registro_diario(
  celda_id, longitud, latitud, area_km2,
  fecha, anio, mes,
  cobertura_1, pct_1, cobertura_2, pct_2,   -- grupo repetitivo: cobertura vegetal
  numero_detecciones, frp_suma_mw, frp_maxima_mw, incendio_observado,
  precipitacion_diaria_mm
)
```

Problemas evidentes: la ubicación de la celda (`longitud`, `latitud`, `area_km2`) se repite en
cada fila diaria; `anio`/`mes` se repiten por cada fecha; y la cobertura vegetal aparece como
columnas repetidas (`cobertura_1`, `cobertura_2`, ...) porque una celda puede tener más de un
tipo de cobertura — un grupo repetitivo de longitud variable, no soportable en columnas fijas.

## 1FN — Primera Forma Normal

**Requisito:** atributos atómicos, sin grupos repetidos, e identificación única de cada fila.

- **Grupos repetidos eliminados:** las columnas `cobertura_1/pct_1`, `cobertura_2/pct_2`, ...
  se extraen a una tabla propia (`celda_cobertura`), con una fila por combinación
  `(celda_id, cobertura_id, anio)` en lugar de columnas repetidas.
- **Atomicidad:** ningún atributo del esquema final contiene listas ni valores compuestos
  (`longitud`/`latitud` son valores numéricos simples; `fecha` es un único valor `DATE`, no un
  rango ni una lista de fechas).
- **Identificación única:** cada tabla del esquema final tiene una PK declarada explícitamente
  (`celda_id`; `fecha_id`; `cobertura_id`; `(celda_id, cobertura_id, anio)`; `incendio_id`;
  `clima_id`), por lo que no puede haber dos filas idénticas sin distinguirse por clave.

Conclusión: el esquema final (`dim_celda`, `dim_fecha`, `dim_cobertura_vegetal`,
`celda_cobertura`, `fact_incendio`, `fact_clima`) cumple 1FN.

## 2FN — Segunda Forma Normal

**Requisito:** cumplir 1FN y no tener dependencias parciales de atributos no clave respecto de
una parte de una clave primaria compuesta (solo aplica cuando la PK es compuesta).

Tablas con PK simple (`dim_celda`, `dim_fecha`, `dim_cobertura_vegetal`, `fact_incendio` con
`incendio_id`, `fact_clima` con `clima_id`) **no pueden tener dependencia parcial por
definición**, porque no hay "parte" de una clave de un solo atributo. Esta es precisamente la
razón de diseño para usar PK surrogates (`incendio_id`, `clima_id`) en lugar de la clave natural
compuesta `(celda_id, fecha_id)`: se evita la discusión de dependencia parcial y la integridad se
resguarda igual mediante `UNIQUE(celda_id, fecha_id)`.

La única tabla con **PK realmente compuesta** es `celda_cobertura(celda_id, cobertura_id, anio)`.
Dependencias funcionales de su único atributo no clave:

```
(celda_id, cobertura_id, anio) → porcentaje_cobertura
```

`porcentaje_cobertura` (el porcentaje de esa cobertura en esa celda, en ese año) no puede
determinarse con solo `celda_id`, ni solo con `cobertura_id`, ni solo con `anio`, ni con ninguna
pareja de ellos: necesita los tres a la vez (el mismo tipo de cobertura puede tener un porcentaje
distinto en otra celda, o en otro año, en la misma celda). No existe dependencia parcial.

Conclusión: el esquema cumple 2FN.

## 3FN — Tercera Forma Normal

**Requisito:** cumplir 2FN y no tener dependencias transitivas de atributos no clave a través de
otro atributo no clave (A → B → C, con A la PK).

Dependencias funcionales por tabla:

- `dim_celda`: `celda_id → nombre_referencia, longitud, latitud, area_km2`. Ningún atributo no
  clave determina a otro (p. ej. `longitud` no determina `area_km2`). Cumple 3FN.
- `dim_cobertura_vegetal`: `cobertura_id → nombre, descripcion`. Sin dependencias transitivas.
  Cumple 3FN.
- `fact_incendio`: `incendio_id → celda_id, fecha_id, fuente, numero_detecciones, frp_suma_mw,
  frp_maxima_mw, fire_mask_maximo, incendio_observado`. `incendio_observado` está relacionado con
  `numero_detecciones` (se refuerza con el `CHECK chk_incendio_coherente`, no con una dependencia
  transitiva vía otro atributo no clave independiente), y ambos dependen directamente de la PK.
  Cumple 3FN.
- `fact_clima`: `clima_id → celda_id, fecha_id, precipitacion_diaria_mm`. Sin dependencias
  transitivas. Cumple 3FN.
- `celda_cobertura`: único atributo no clave (`porcentaje_cobertura`), no hay otro atributo no
  clave por el cual pueda haber transitividad. Cumple 3FN trivialmente.

### Excepción deliberada: `dim_fecha`

```
fecha_id → fecha → anio, mes
```

`anio` y `mes` dependen funcionalmente de `fecha` (una fecha calendario determina de forma única
su año y su mes), y no directamente de la PK `fecha_id` sin pasar por `fecha`. Estrictamente,
esto **es una dependencia transitiva** y viola la letra de 3FN.

**Justificación de la desnormalización:** se conserva de forma deliberada porque:

1. `dim_fecha` es una dimensión de tiempo, un patrón estándar en modelado dimensional donde se
   materializan columnas derivadas (`anio`, `mes`) para evitar recalcular `EXTRACT(YEAR FROM
   fecha)` / `EXTRACT(MONTH FROM fecha)` en cada consulta de agregación mensual (requisito
   central de este taller: `GROUP BY anio, mes`).
2. El riesgo de inconsistencia (que `anio`/`mes` no coincidan con `fecha`) se controla con la
   restricción `chk_fecha_id_consistente` en `schema.sql`, que ata `fecha_id` a `fecha` de forma
   verificable por la base de datos.
3. `fecha` es `UNIQUE NOT NULL`, por lo que no hay riesgo de anomalías de actualización en la
   práctica: cada fecha aparece en una sola fila.

Se documenta explícitamente esta excepción, tal como permite la guía de la práctica
("si el grupo decide conservar alguna desnormalización, deberá explicarla").

## Conclusión

El esquema final cumple 1FN y 2FN sin excepciones, y 3FN en todas las tablas salvo `dim_fecha`,
donde se acepta y justifica una dependencia transitiva controlada (`fecha → anio, mes`) por
razones de modelado dimensional y de rendimiento en las consultas analíticas del taller.
