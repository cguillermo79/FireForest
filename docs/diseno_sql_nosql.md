# Diseño comparativo SQL–NoSQL

## Unidad de análisis

La unidad de análisis será una celda espacial de 500 m × 500 m observada durante un mes.

La clave analítica que conecta la parte SQL y la parte NoSQL será:

```text
celda_id + anio + mes
```

La granularidad real tiene tres niveles: (1) MongoDB guarda la detección individual (`celda_id + fecha`, día y hora exactos); (2) PostgreSQL carga un registro diario por celda en `fact_incendio`/`fact_clima` (`dim_fecha` es un calendario **diario**, con `anio`/`mes` derivados de cada fecha); (3) el dataset analítico celda-mes se obtiene agregando esos registros diarios mediante `GROUP BY anio, mes` (ver `consultas/consulta_01_incendios_clima_mensual.sql`). No existen filas pre-agregadas por mes en las tablas base.

## Entidades

**Lado SQL (PostgreSQL/PostGIS):**

- `dim_celda`: malla espacial de referencia (una fila por celda del cantón Loja).
- `dim_fecha`: calendario diario del periodo analizado (una fila por fecha, con `anio`/`mes` derivados).
- `fact_incendio`: registro diario de detecciones de incendio por celda (agregable a mes).
- `fact_clima`: registro diario de precipitación por celda (`precipitacion_diaria_mm`, un único valor por celda-día; acumulada/media/máxima solo tienen sentido al agregar estos valores por mes, no se almacenan como columnas separadas a grano diario).

**Lado NoSQL (MongoDB):**

- Colección `detecciones_viirs`: detecciones satelitales individuales de incendio, tal como las entrega el producto VIIRS, antes de resumirlas por celda-mes.

## Relaciones

- `fact_incendio.celda_id → dim_celda.celda_id` (FK) y `fact_incendio.fecha_id → dim_fecha.fecha_id` (FK).
- `fact_clima.celda_id → dim_celda.celda_id` (FK) y `fact_clima.fecha_id → dim_fecha.fecha_id` (FK), con `UNIQUE (celda_id, fecha_id)` para evitar duplicar el clima de una misma celda-día.
- `fact_incendio` y `fact_clima` se relacionan entre sí de forma implícita (no por FK directa) al compartir `celda_id` y `fecha_id`: se cruzan mediante `JOIN` cuando se necesita comparar incendio y clima.
- La colección `detecciones_viirs` (NoSQL) no tiene FK hacia PostgreSQL; cada documento trae `celda_id` + `fecha` (día), y ese detalle diario se agrega por `celda_id` + `anio` + `mes` para poblar `fact_incendio`.
- Esta integración MongoDB → PostgreSQL no es automática: se realiza mediante un proceso ETL/ELT (script de transformación) que lee las detecciones individuales de `detecciones_viirs`, las agrupa por `celda_id` + `fecha` y escribe un registro diario resumido en `fact_incendio`. `celda_id + fecha` es la clave que usa ese proceso para decidir qué filas corresponden a qué detecciones.

## Qué datos son estables y relacionales (SQL)

- La malla espacial (`dim_celda`): la geometría y ubicación de cada celda no cambian en el periodo de estudio.
- El calendario (`dim_fecha`): estructura fija y conocida de antemano.
- Los registros diarios de incendio y clima por celda (`fact_incendio`, `fact_clima`): son numéricos, tienen una estructura homogénea y se benefician de integridad referencial (PK/FK) y de operaciones `JOIN` / `GROUP BY` para agregarlos a celda-mes.

## Qué datos son flexibles o anidados (NoSQL)

- Las detecciones individuales VIIRS: cada documento trae coordenadas anidadas (`coordenadas.longitud`, `coordenadas.latitud`) y un objeto de calidad (`calidad.valida`) que puede ganar o perder campos según la versión del producto satelital, sin romper un esquema fijo.
- Metadatos de captura no uniformes entre fuentes (por ejemplo, atributos adicionales que solo trae cierto sensor o cierta versión de archivo).

## Justificación del uso de cada tecnología

**¿Por qué PostgreSQL/PostGIS para determinados datos?**
Porque la malla espacial y los hechos diarios de incendio/clima tienen una estructura estable y relaciones claras entre celda, fecha y hecho. Esto se beneficia de claves primarias/foráneas que garantizan integridad (no se puede registrar clima o incendio de una celda que no existe), de tipos numéricos con restricciones (`CHECK`), y de las capacidades geoespaciales de PostGIS para almacenar y consultar la geometría de cada celda. Además, las preguntas analíticas del proyecto (comparar incendio y clima por celda-mes) requieren `JOIN` y agregación, algo natural en SQL.

**¿Por qué MongoDB para otros datos?**
Porque las detecciones satelitales individuales llegan en formato JSON semi-estructurado y anidado, y su forma exacta puede variar entre versiones del producto VIIRS sin que eso deba obligar a migrar un esquema relacional. MongoDB permite conservar el detalle crudo y trazable de cada detección (para auditoría y control de calidad) y ejecutar agregaciones documentales previas, antes de resumir la información hacia PostgreSQL.

## Consultas que se espera resolver

**En SQL:**

- Número de detecciones, FRP total y FRP máxima de incendio por celda y mes (`JOIN` entre `fact_incendio`, `dim_celda`, `dim_fecha`).
- Precipitación acumulada, media y máxima por celda y mes, cruzada con la ocurrencia de incendio (`JOIN` entre `fact_incendio` y `fact_clima` por `celda_id` + `fecha_id`).
- Ranking de celdas con `incendio_observado = TRUE` y menor precipitación acumulada del mes.

**En MongoDB (agregación documental):**

- Conteo de detecciones válidas por `celda_id` (`$match` sobre `calidad.valida: true`, `$group` por `celda_id`).
- FRP promedio y máximo por `celda_id` y mes (`$group` usando el mes extraído de `fecha`).
- Filtrado de detecciones según un umbral mínimo de `fire_mask` (criterio de calidad del sensor).

## Tabla comparativa (síntesis)

| Elemento | Pregunta | Decisión para FireForest |
|---|---|---|
| Entidades | ¿Cuáles son los objetos principales del problema? | `dim_celda`, `dim_fecha`, `fact_incendio`, `fact_clima` (tablas) y `detecciones_viirs` (colección) |
| Relaciones | ¿Qué vínculos importan? | FK celda/fecha en las tablas de hechos; clave analítica `celda_id + anio + mes` entre SQL y NoSQL (la fecha diaria solo vive en MongoDB) |
| SQL | ¿Qué datos son estables y relacionales? | Malla espacial, calendario diario y registros diarios de incendio/clima (agregables a mes) |
| NoSQL | ¿Qué datos son flexibles o anidados? | Detecciones VIIRS individuales, con coordenadas y calidad anidadas |
| Consulta | ¿Qué preguntas deberá responder el sistema? | Agregados por celda-mes en SQL; conteos/filtrados de detecciones en MongoDB |
| ML | ¿Cuál será la unidad de análisis? | Celda espacial–mes, dataset final reproducible |
