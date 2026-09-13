# 3. Diccionario de datos

Colección: `taller_nosql_fireforest.evidencia_viirs_celda_mes` (105 documentos).

| Campo | Tipo BSON | Rango / valores observados | Descripción |
|---|---|---|---|
| `_id` | string | `VCM_0001`…`VCM_0105` | Identificador del registro de muestra. |
| `celda.cell_index` | int32 | entero positivo (id de celda de 500 m) | Identificador de la celda espacial. |
| `celda.unidad_espacial` | string | `"celda_500m"` (constante) | Unidad espacial de referencia. |
| `periodo.anio` | int32 | 2019–2025 | Año calendario. |
| `periodo.mes` | int32 | 1–12 | Mes calendario. |
| `periodo.anio_mes` | string | `"2019-01"`…`"2025-12"` | Clave legible año-mes. |
| `periodo.fecha_inicio` | date | primer día de cada mes, 00:00 UTC | Fecha BSON del periodo. |
| `fuente_satelital.fuente_primaria` | string | `"NASA FIRMS - VIIRS"` (constante) | Fuente satelital primaria. |
| `fuente_satelital.asset_gee` | string | `"VIIRS_PREP_AAAA_MM"` (identificador genérico por año-mes) | Identificador del activo de procesamiento asociado al periodo; no expone rutas ni cuentas internas. |
| `fuente_satelital.soporte_nativo_m` | double | ≈ 375–930 | Resolución nativa aproximada del sensor, en metros. |
| `fuente_satelital.procedencia` | string | `"registros_previamente_procesados"` (constante) | Indica que son registros reales de VIIRS procesados previamente, provenientes de una fuente externa de solo lectura. |
| `fuente_satelital.version_origen` | string | `"v1.0.3"` (constante) | Versión del producto de origen. |
| `metricas.detecciones.media_todas` | double | ≥ 0 | Promedio de detecciones de fuego (todas las confianzas). |
| `metricas.detecciones.media_nominal_alta` | double | ≥ 0 | Promedio de detecciones de confianza nominal/alta. |
| `metricas.presencia.fraccion_todas` | double | 0–1 | Fracción de presencia de fuego (todas). |
| `metricas.presencia.fraccion_nominal_alta` | double | 0–1 | Fracción de presencia de fuego (nominal/alta). |
| `metricas.frp.suma_observada_media_mw` | double | 0–188,27 (observado) | FRP acumulada observada, en MW. |
| `metricas.frp.maxima_media_mw` | double | 0–122,3162 (observado) | FRP máxima observada, en MW. **Variable objetivo candidata.** |
| `calidad_observacion.dias_validos_media` | double | 0–31 | Días válidos de observación en el mes. |
| `calidad_observacion.disponibilidad_pct` | double | 0–100 | Porcentaje de disponibilidad de observación satelital. |
| `calidad_observacion.observado_media` | double | 0–1 | Fracción media observada. |
| `calidad_observacion.cobertura_fuente_fraccion` | double | 0–1 | Fracción de cobertura de la fuente. |
| `calidad_observacion.soporte_observado_fraccion` | double | 0–1 | Fracción de soporte observado. |
| `evidencias[].categoria` | string | `"todas"` \| `"nominal_alta"` | Criterio de confianza de la evidencia. |
| `evidencias[].detecciones_media` | double | ≥ 0 | Detecciones medias para esa categoría. |
| `evidencias[].presencia_fraccion` | double | 0–1 | Presencia fraccional para esa categoría. |
| `evidencias[].evidencia_fuego` | bool | `true` / `false` | Indicador booleano de evidencia de fuego. |
| `muestreo.estrato` | string | `"con_fuego"` \| `"sin_fuego"` | Estrato de muestreo asignado. |
| `muestreo.metodo` | string | `"estratificado_por_anio_y_evidencia"` (constante) | Método de muestreo. |
| `muestreo.semilla` | int32 | `2026` (constante) | Semilla base del muestreo aleatorio. |
| `metadatos.unidad_analisis` | string | `"celda_mes_500m"` (constante) | Unidad de análisis declarada. |
| `metadatos.datos_simulados` | bool | `false` (constante, 105/105) | Indica que **no** son datos simulados. |
| `metadatos.uso` | string | `"Laboratorio NoSQL MongoDB - M1721"` (constante) | Uso declarado del dato. |
| `metadatos.estado_revision` | string (opcional) | `"revisado_taller_nosql"` en 70/105 | **Metadato operativo** agregado por `updateMany()` (no es observación satelital). |
| `revisado_manualmente` | bool (opcional) | `true` en 1/105 | **Metadato operativo** agregado por `updateOne()`. |
| `bitacora_laboratorio[]` | array de object (opcional) | 1 entrada en 105/105 tras la carga | **Metadatos operativos** de trazabilidad (`accion`, `responsable`, `fecha_procesamiento`). |

## Notas de calidad de datos

- Ningún campo satelital contiene valores nulos: el script de extracción
  (`02_mongodb/01_extraer_muestra_viirs.py`) descarta filas con valores
  ausentes en los campos esenciales antes de muestrear.
- La unicidad de `celda.cell_index + periodo.anio + periodo.mes` está
  garantizada por diseño del muestreo (no hay dos registros de la misma
  celda en el mismo mes) y reforzada por el índice único
  `ux_celda_anio_mes` en la base `taller_nosql_fireforest`.
- Todos los valores numéricos y booleanos provienen directamente de
  registros reales de VIIRS procesados previamente (fuente externa de
  solo lectura, versión `v1.0.3`); no se inventaron ubicaciones,
  coordenadas, parroquias, coberturas ni variables climáticas.
