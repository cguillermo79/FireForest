# Decisiones metodológicas — registro para el Avance 2

Este documento registra decisiones y correcciones metodológicas
detectadas durante la auditoría técnica del 2026-09-13, posteriores a la
entrega del Avance 1. **No modifica** `01_avance_1/entrega/Grupo04_AvanceProyectoIntegrador.pdf`
ni `01_avance_1/fuente/avance1.tex` (documentos académicos ya
entregados y conservados exactamente como fueron presentados); las
correcciones se aplican únicamente a los archivos técnicos activos del
proyecto (`03_postgresql_postgis/consultas/`, documentación de
`00_documentacion_inicial/` y de gestión en `14_gestion/`).

## 1. Corrección de la consulta mensual (ausencia de incendio vs. dato faltante)

**Problema detectado:** `03_postgresql_postgis/consultas/consulta_01_incendios_clima_mensual.sql`
usaba `incendio_mes` (la agregación de `fact_incendio`) como base del
`JOIN` final, con `INNER JOIN` hacia `clima_mes`. Como resultado, un
celda-mes con precipitación registrada en CHIRPS pero **sin ninguna
fila en `fact_incendio` ese mes** (es decir, sin incendio, no por falta
de dato) desaparecía completamente del resultado. Esto trataba
implícitamente "ausencia de incendio" como si fuera "dato faltante",
lo cual es metodológicamente incorrecto: CHIRPS puede tener cobertura
completa del mes mientras VIIRS legítimamente no detectó fuego.

**Corrección aplicada:** se invirtió el rol de las CTE en el `JOIN`
final: ahora `clima_mes` es la base y se usa `LEFT JOIN` hacia
`incendio_mes`, con `COALESCE(..., 0)` en `detecciones_totales`,
`frp_total_mw`, `frp_maxima_mw` y `numero_dias_con_incendio`. Un mes
sin incendio ahora aparece con estos valores en `0` (fuego con
intensidad cero, es decir, ausencia confirmada), en lugar de no
aparecer en absoluto.

**Validación realizada** (sin alterar datos, ver `01_avance_1/evidencias/evaluacion_cumplimiento_guia.md`
para el detalle completo):

- `EXPLAIN` sobre la consulta corregida: sintaxis válida, plan de
  ejecución confirma un `Hash Left Join` entre `clima_mes` e
  `incendio_mes`.
- Ejecución real sobre los datos de ejemplo actuales (2 celda-mes,
  ambos con incendio): resultado idéntico al esperado, sin regresión.
- Prueba del caso crítico dentro de una **transacción revertida
  (`ROLLBACK`)**: se insertó temporalmente un registro de clima de
  septiembre de 2023 sin ningún incendio asociado; la consulta
  corregida devolvió esa fila con `detecciones_totales = 0`,
  `frp_total_mw = 0`, `frp_maxima_mw = 0` y la precipitación real
  registrada. Tras el `ROLLBACK`, se confirmó que no quedó ningún dato
  de prueba en la base (`fireforest`).

## 2. Distinción formal: ausencia de incendio ≠ dato faltante

Para la construcción del dataset analítico celda-mes (etapa 6 del
plan, `07_etl_integracion/integracion_celda_mes/`), debe respetarse
esta regla:

| Situación | Representación correcta |
|---|---|
| CHIRPS tiene el mes completo y VIIRS no detectó fuego en esa celda-mes | `detecciones_totales = 0`, `frp_total_mw = 0`, `frp_maxima_mw = 0` (fuego con intensidad cero, **no** `NULL`) |
| Falta realmente el dato de origen (p. ej. VIIRS no tiene cobertura ese periodo, o la fuente no fue consultada) | `NULL` únicamente en ese caso, y debe documentarse la causa (ver `06_calidad_datos/`) |

**Implicación para el diseño futuro del dataset integrado (etapa 6):**
la construcción del panel celda-mes debe partir de una base completa
—ya sea el producto cartesiano celda × mes del periodo de estudio, o
la tabla de clima (más completa por diseño, ya que CHIRPS es un
producto de cobertura continua) — e incorporar los incendios mediante
`LEFT JOIN`, nunca `INNER JOIN` sobre `fact_incendio`. Este mismo
patrón debe reutilizarse en `07_etl_integracion/integracion_celda_mes/`
cuando se construya en Avance 2.

## 3. Auditoría de consistencia de granularidad documental

Se revisaron `00_documentacion_inicial/diseno_sql_nosql.md`,
`README.md` (raíz de `Proyecto_integrador`) y `14_gestion/plan_implementacion.md`
en busca de contradicciones entre los tres niveles de granularidad.
**No se encontraron contradicciones**: los tres documentos ya
describían de forma consistente:

1. **MongoDB** conserva cada detección VIIRS individual
   (`celda_id + fecha`, día y hora exactos).
2. Las detecciones se agregan por **celda y día** (vía un proceso
   ETL/ELT, no automático ni por FK) para poblar `fact_incendio`
   (`PostgreSQL`, grano diario, `UNIQUE(celda_id, fecha_id)`).
3. Los registros diarios de incendio y clima se agregan posteriormente
   por `celda_id + anio + mes` (mediante `GROUP BY` en consultas SQL,
   como la corregida en la sección 1) para construir el dataset
   analítico.
4. El dataset final tiene **una fila por celda-mes**; no existen filas
   pre-agregadas por mes en las tablas base (`fact_incendio`,
   `fact_clima` permanecen a grano diario).

Se agregó una referencia cruzada a esta corrección en
`00_documentacion_inicial/diseno_sql_nosql.md` (sección "Consultas que
se espera resolver").

## 4. Pendientes metodológicos — VIIRS y malla espacial

Registrados como pendientes explícitos (no se inventó ni asumió
ninguna respuesta):

| Pendiente | Detalle |
|---|---|
| Fuente institucional del límite del cantón Loja | Por confirmar entre las candidatas mencionadas en `inventario_fuentes.md` (Instituto Geográfico Militar, GAD Provincial de Loja); documentar fecha de descarga, versión y EPSG definitivos en la fase de ingesta (Avance 2) |
| Producto VIIRS definitivo | El Avance 1 referencia VIIRS Active Fire ~375 m (NASA FIRMS); debe confirmarse la colección exacta (p. ej. VNP14IMG vs. VJ114IMG, NRT vs. Standard) antes de la ingesta real, y evitar mezclar campos de productos/versiones distintas en un mismo dataset |
| Campo de calidad VIIRS | El documento de ejemplo usa `fire_mask`; **no se debe asumir automáticamente** que ese sea el campo definitivo — algunos productos VIIRS usan `confidence` (categórico: low/nominal/high) en lugar de o además de `fire_mask` (numérico). Debe verificarse contra la estructura real del producto elegido antes de fijar el criterio de filtrado de calidad |
| Criterio de filtrado de calidad | Pendiente de documentar de forma exacta (p. ej. `fire_mask >= 7` o `confidence IN ('nominal','high')`) una vez confirmado el producto y el campo |

Ninguno de estos pendientes se resolvió por suposición; se dejan
registrados también en `14_gestion/tareas_pendientes.md`.

## 5. Versión corregida del informe del Avance 1 (2026-09-13, pendiente de aprobación)

Se generó `01_avance_1/fuente/avance1_corregido.tex` y
`01_avance_1/entrega/Grupo04_AvanceProyectoIntegrador_corregido.pdf`,
que incorporan al documento del Avance 1 las correcciones 1–5 de este
registro (malla/EPSG, producto y campo de calidad VIIRS pendientes,
granularidad temporal corregida en el ejemplo JSON, consulta SQL
corregida con `LEFT JOIN`, y la aclaración de ausencia de incendio vs.
dato faltante). **No se modificaron** `avance1.tex` ni
`Grupo04_AvanceProyectoIntegrador.pdf` (originales, verificados por
hash). La versión corregida se mantiene como propuesta, sin sustituir
la entrega original, hasta su revisión y aprobación. Detalle completo
en `01_avance_1/evidencias/evaluacion_cumplimiento_guia.md`.
