# Tareas pendientes — Proyecto Integrador FireForest

Estado por etapa (ver `plan_implementacion.md` para el detalle original
del Avance 1). Ninguna actividad se declara "completado" sin un
archivo, ejecución o evidencia comprobable en el repositorio.

| Etapa | Actividad | Estado | Evidencia / justificación |
|---|---|---|---|
| 1 | Identificación de fuentes | **Completado** | `../00_documentacion_inicial/inventario_fuentes.md` |
| 2 | Diseño relacional (SQL) | **Completado** | `../03_postgresql_postgis/cargas/schema.sql` |
| 3 | Diseño NoSQL | **Completado** | `../04_mongodb/cargas/detecciones_viirs.json` |
| 4 | Diseño comparativo SQL–NoSQL | **Completado** | `../00_documentacion_inicial/diseno_sql_nosql.md` |
| 5 | Ingesta (datos de ejemplo) | **Completado con datos de ejemplo** | `cargar_postgres.py` y `cargar_mongodb.py` ejecutables; ver `README.md` raíz del proyecto |
| 6 | Adquisición y conservación de datos originales (reales, GEE) | **Pendiente** | Sin archivos en `../02_datos/raw/` más allá de `.gitkeep` |
| 7 | Validación individual de cada fuente | **Pendiente** | `../06_calidad_datos/` sin contenido |
| 8 | Limpieza y estandarización | **Pendiente** | `../07_etl_integracion/transformacion/` sin contenido |
| 9 | Carga en MongoDB y PostgreSQL/PostGIS | **Completado con datos de ejemplo** | Igual que etapa 5 |
| 10 | Integración temporal y espacial | **Pendiente** | `../07_etl_integracion/integracion_celda_mes/` sin contenido |
| 11 | Construcción del dataset celda-mes | **Pendiente** | `../02_datos/final/` sin contenido |
| 12 | Controles de calidad del dataset integrado | **Pendiente** | `../06_calidad_datos/reportes/` sin contenido |
| 13 | Automatización mediante Airflow | **En desarrollo** | 2 DAGs operativos: `../08_airflow/dags/fireforest_prueba.py` (flujo de prueba) y `fireforest_validar_viirs.py` (valida `detecciones_viirs.json`); falta integrarlos con las etapas 6-12 |
| 14 | Procesamiento/escalabilidad con Spark o PySpark | **Pendiente** | `../09_spark_pyspark/` sin contenido |
| 15 | Análisis estadístico y visualización | **Pendiente** | `../10_analisis/` sin contenido |
| 16 | Elaboración del Avance 2 | **Pendiente** | `../12_avance_2/` sin contenido |
| 17 | Informe y presentación final | **Pendiente** | `../13_entrega_final/` sin contenido |

## Documentación pendiente de redactar

| Documento | Estado | Nota |
|---|---|---|
| `../00_documentacion_inicial/objetivos.md` | **Pendiente** | Creado como *stub* que referencia dónde vive el contenido disperso actual |
| `../00_documentacion_inicial/arquitectura.md` | **Pendiente** | Ídem |
| `../00_documentacion_inicial/diccionario_datos.md` | **Pendiente** | Ídem |

## Hallazgos técnicos pendientes (no bloqueantes para el commit de la reorganización)

| Hallazgo | Detalle | Impacto |
|---|---|---|
| `cargar_postgres.py` no es idempotente | `schema.sql` no usa `CREATE TABLE IF NOT EXISTS`; al re-ejecutar el script sobre una base ya inicializada falla con `psycopg.errors.DuplicateTable`. Comportamiento preexistente a esta reorganización (no se modificó `schema.sql` ni la lógica del script, solo sus rutas). | Bajo: no afecta la reorganización de carpetas; sí conviene corregirlo antes de automatizarlo con Airflow (etapa 13) |

## Actividades registradas tras la auditoría de cumplimiento (2026-09-13)

Ver el detalle completo en `decisiones_metodologicas.md` y
`../01_avance_1/evidencias/evaluacion_cumplimiento_guia.md`.

| Actividad | Estado | Evidencia real |
|---|---|---|
| Corregir y validar la consulta mensual (`consulta_01_incendios_clima_mensual.sql`) | **Completado** | `JOIN` corregido (`INNER`→`LEFT` desde clima) + `COALESCE(...,0)`; validado con `EXPLAIN` (sintaxis correcta, plan confirma `Hash Left Join`), ejecución real sobre los datos de ejemplo (resultado sin regresión) y prueba del caso crítico en una transacción revertida (`ROLLBACK`, sin alterar datos) que demostró que un mes con clima sin incendio ahora aparece con ceros en vez de desaparecer |
| Construir el panel completo celda-mes (`07_etl_integracion/integracion_celda_mes/`) | **Pendiente** | Carpeta creada, sin contenido; la decisión de usar `LEFT JOIN` desde una base completa quedó documentada, pero el pipeline en sí no se ha construido |
| Diferenciar ausencia de incendio y dato faltante en el diseño del dataset integrado | **En desarrollo** | Regla documentada formalmente en `decisiones_metodologicas.md` §2 (en la prueba controlada, un valor de 0 representa que `LEFT JOIN`/`COALESCE` conservaron el mes climático sin fila coincidente de incendio; `NULL` representa dato realmente faltante) y ya aplicada en la consulta corregida; falta aplicarla en el futuro pipeline de integración (etapa 10). En datos reales, 0 solo podrá leerse como ausencia de detecciones tras verificar independientemente la cobertura e ingesta VIIRS |
| Confirmar fuente oficial de la malla espacial del cantón Loja | **En desarrollo** | Identificada y usada para verificación: INEC, Marco Geoestadístico Nacional (`zon_a`, EPSG:31992→32717). Permitió detectar que `LJ_04521`/`LJ_04522` estaban fuera del cantón Loja y generar `LJ_TEST_001`/`LJ_TEST_002` (parroquia El Cisne) — ver `decisiones_metodologicas.md` §6. Sigue pendiente generar la malla completa de producción para todo el cantón |
| Validar y aplicar en PostgreSQL/PostGIS real la sustitución de celdas (`LJ_TEST_001`/`LJ_TEST_002`) | **Completado — migración permanente aplicada** | Tres etapas diferenciadas: (a) prueba transaccional inicial con `ROLLBACK` (`validar_celdas_postgis.py`, `salida_validacion_postgis_celdas.txt`), que solo confirmó que la migración era funcional sin persistirla; (b) migración permanente con `COMMIT`, ejecutada localmente por el usuario el 2026-09-14 con `../03_postgresql_postgis/validacion/aplicar_celdas_postgis.py` (respaldo previo de `LJ_04521`/`LJ_04522` en `respaldo_celdas_anteriores.json`; log completo en `../03_postgresql_postgis/evidencias/salida_aplicacion_postgis_celdas.txt`); (c) verificación del estado ya persistido en una conexión nueva de solo lectura, dentro del mismo log, y una reejecución adicional de cierre en `../03_postgresql_postgis/evidencias/salida_reejecucion_cierre_postgis_mongodb.txt`. Confirmado en la base real: `LJ_04521`/`LJ_04522` ausentes, `LJ_TEST_001`/`LJ_TEST_002` presentes, SRID 32717, geometría válida, área 250 000 m², dentro del cantón Loja y de la parroquia El Cisne, distancia al límite 1085,00 m y 1066,01 m, sin huérfanos ni duplicados, integración celda-mes con 2 filas correctas. MongoDB ya estaba actualizado de forma permanente desde una fase anterior |
| Confirmar producto VIIRS y campo de calidad (`fire_mask` vs. `confidence`) | **Pendiente** | Sin evidencia técnica; no debe asumirse el campo sin verificar la estructura real del producto elegido (ver `decisiones_metodologicas.md` §4) |
| Comprobar que Airflow reconoce el DAG de FireForest cuando Docker Desktop esté activo | **Pendiente** | `docker compose config -q` validado sin errores (2026-09-13), pero el daemon de Docker Desktop no estaba activo durante la auditoría; no se pudo verificar el reconocimiento del DAG en un Airflow en ejecución |
| Mejorar la idempotencia de `cargar_postgres.py` | **Pendiente** | Ver hallazgo técnico arriba; requiere modificar `schema.sql` (`CREATE TABLE IF NOT EXISTS` o `DROP ... IF EXISTS` previo), fuera del alcance de esta auditoría por tratarse de contenido técnico ya existente que no se debía alterar sin instrucción explícita |

## Archivos registrados como pendientes por ambigüedad (no movidos)

Ninguno pendiente actualmente. `s42408-026-00470-y.pdf` (artículo de
referencia citado en la presentación de FireForest) se reubicó el
2026-09-13 en `../00_documentacion_inicial/referencias/` mediante
`git mv`, una vez confirmado su propósito (ver `bitacora.md`).

## No aplica

- Ninguna etapa fue marcada como "no aplica" en este avance.
