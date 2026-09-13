# 2. Diseño documental (Parte A de la guía)

## Colección principal

- **Nombre:** `evidencia_viirs_celda_mes`.
- **Base de datos de la entrega:** `taller_nosql_fireforest` (base
  independiente del taller; ver advertencia de independencia en el
  `README.md` raíz de `Taller_NoSQL`).
- **Propósito:** almacenar, para cada combinación única de celda espacial
  y mes calendario, la evidencia satelital VIIRS de fuego junto con sus
  metadatos de calidad, muestreo y procesamiento del laboratorio.

## Documento

Cada documento representa **una celda espacial de 500 m observada
durante un mes calendario** (unidad "celda-mes"), consistente con la
unidad de análisis declarada en `AGENTS.md` del Proyecto Integrador
FireForest.

## Campos obligatorios, opcionales y variables

| Campo (ruta) | Tipo BSON | Obligatorio | Descripción |
|---|---|---|---|
| `_id` | string | sí | Identificador del registro de muestra (`VCM_0001`…`VCM_0105`). |
| `celda.cell_index` | int | sí | Identificador de la celda espacial de 500 m. |
| `celda.unidad_espacial` | string | sí | Etiqueta fija `"celda_500m"`. |
| `periodo.anio`, `periodo.mes` | int | sí | Año y mes calendario. |
| `periodo.anio_mes` | string | sí | Clave legible `"AAAA-MM"`. |
| `periodo.fecha_inicio` | date (BSON) | sí | Primer día del mes, en UTC. |
| `fuente_satelital.*` | object | sí | Fuente primaria, activo de Google Earth Engine, soporte nativo (m), proyecto y versión de origen. |
| `metricas.detecciones.*` | double | sí | Promedio de detecciones (todas / nominal-alta). |
| `metricas.presencia.*` | double | sí | Fracción de presencia de fuego (todas / nominal-alta). |
| `metricas.frp.*` | double | sí | FRP acumulada observada y FRP máxima, en MW. |
| `calidad_observacion.*` | double | sí | Días válidos, % de disponibilidad, cobertura y soporte observado. |
| `evidencias` | array de object | sí (2 elementos) | Evidencia de fuego por criterio de confianza (`todas`, `nominal_alta`). |
| `muestreo.*` | object | sí | Estrato, método y semilla del muestreo. |
| `metadatos.unidad_analisis`, `metadatos.datos_simulados`, `metadatos.uso` | mixed | sí | Metadatos de procedencia fijados en la carga. |
| `metadatos.estado_revision` | string | **opcional/variable** | Se agrega después de la carga mediante `updateMany()` (Parte D, actualización 2); solo existe en los documentos con evidencia de fuego. |
| `revisado_manualmente` | bool | **opcional/variable** | Se agrega solo al documento de mayor FRP (actualización 1). |
| `bitacora_laboratorio` | array de object | **variable, crece con el tiempo** | Se incorpora con `$push` (actualización 3); puede crecer en cada reprocesamiento. |

## Anidamiento — qué datos pertenecen naturalmente al mismo objeto

- `celda`, `periodo`, `fuente_satelital`, `metricas`, `calidad_observacion`
  y `muestreo` se anidan como **objetos embebidos** porque siempre se
  leen junto con el documento principal, no cambian de cardinalidad
  independientemente del documento, y se actualizan (si acaso) en bloque
  durante la carga, no de forma individual y frecuente.
- `evidencias` se modela como **arreglo embebido de exactamente 2
  elementos por documento** (uno por criterio de confianza: `todas` y
  `nominal_alta`), consultado con `$elemMatch` cuando se necesita filtrar
  por categoría y valor de evidencia simultáneamente (consultas 2 y 6), y
  transformado con `$unwind` cuando se necesita comparar ambas categorías
  como filas independientes (consulta 9).
- `bitacora_laboratorio` es un **arreglo que crece con el tiempo**
  (`$push`), distinto de `evidencias`: mientras `evidencias` es un dato
  satelital fijo desde la carga, `bitacora_laboratorio` es una traza
  operativa que se espera que aumente en futuros reprocesamientos.

## Referencias

Este taller **no requiere colecciones adicionales ni referencias por
`$lookup`**: la unidad celda-mes concentra toda la información necesaria
para las 10 consultas exigidas dentro de un único documento
autocontenido. Se documenta explícitamente esta decisión (ver
`04_embebido_vs_referencia.md`) porque la guía exige justificar tanto el
embebido como la ausencia de referencias cuando corresponda.

## Metadatos

- **Procedencia:** `fuente_satelital.procedencia` (registros reales
  de VIIRS procesados previamente), `fuente_satelital.version_origen`
  (`v1.0.3`), `muestreo.metodo` y `muestreo.semilla`.
- **Estado/versión operativa:** `metadatos.estado_revision`,
  `revisado_manualmente`, `bitacora_laboratorio` — todos ellos metadatos
  **del proceso del laboratorio**, nunca observaciones satelitales; se
  distinguen deliberadamente de `metricas`, `calidad_observacion` y
  `evidencias`, que sí son datos satelitales reales.

## Esquema resumido del documento

```text
evidencia_viirs_celda_mes
├── _id                         string
├── celda            { cell_index, unidad_espacial }
├── periodo          { anio, mes, anio_mes, fecha_inicio: Date }
├── fuente_satelital { fuente_primaria, asset_gee, soporte_nativo_m,
│                      procedencia, version_origen }
├── metricas
│   ├── detecciones  { media_todas, media_nominal_alta }
│   ├── presencia    { fraccion_todas, fraccion_nominal_alta }
│   └── frp          { suma_observada_media_mw, maxima_media_mw }
├── calidad_observacion { dias_validos_media, disponibilidad_pct,
│                         observado_media, cobertura_fuente_fraccion,
│                         soporte_observado_fraccion }
├── evidencias [ { categoria, detecciones_media, presencia_fraccion,
│                  evidencia_fuego: bool }, ... ]  (2 elementos)
├── muestreo         { estrato, metodo, semilla }
├── metadatos        { unidad_analisis, datos_simulados, uso,
│                      estado_revision? }
├── revisado_manualmente?        bool
└── bitacora_laboratorio? [ { accion, responsable, fecha_procesamiento: Date }, ... ]
```
