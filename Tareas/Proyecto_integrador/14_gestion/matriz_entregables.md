# Matriz de entregables — Proyecto Integrador FireForest

| Requisito académico | Archivo que lo demuestra | Ubicación | Estado | Observaciones |
|---|---|---|---|---|
| Definición del problema | `problema.md` | `../00_documentacion_inicial/` | Completado | Reubicado desde `docs/` sin cambios de contenido |
| Objetivos del proyecto | `objetivos.md` | `../00_documentacion_inicial/` | Pendiente | *Stub* con referencias al contenido disperso existente |
| Inventario de fuentes | `inventario_fuentes.md` | `../00_documentacion_inicial/` | Completado | Reubicado desde `docs/`; rutas internas actualizadas |
| Arquitectura del proyecto | `arquitectura.md` | `../00_documentacion_inicial/` | Pendiente | *Stub* |
| Diseño SQL–NoSQL | `diseno_sql_nosql.md` | `../00_documentacion_inicial/` | Completado | Reubicado desde `docs/`; rutas internas actualizadas |
| Diccionario de datos | `diccionario_datos.md` | `../00_documentacion_inicial/` | Pendiente | *Stub* |
| Presentación del proyecto | `presentacion_fireforest.pdf` (+ `.tex`) | `../00_documentacion_inicial/` | Completado | Reubicado desde `Presentacion/` (raíz), contenido idéntico verificado por hash |
| Artículo de referencia citado | `s42408-026-00470-y.pdf` | `../00_documentacion_inicial/referencias/` | Completado | Reubicado desde `Presentacion/` (raíz) con `git mv`; contenido idéntico verificado por hash (`0d26f556...`) |
| Guía del Avance 1 | `Guia_Avance_Proyecto_Integrador.pdf` | `../01_avance_1/guia/` | Completado | Reubicado desde `Tareas/Guia_Avance_Proyecto_Integrador.pdf` |
| Fuente del Avance 1 | `avance1.tex` | `../01_avance_1/fuente/` | Completado | Reubicado desde `Tareas/Avance1/`; contenido **sin modificar** (incluye menciones de ruta anteriores a esta reorganización, intencionalmente preservadas) |
| Entrega del Avance 1 | `Grupo04_AvanceProyectoIntegrador.pdf` | `../01_avance_1/entrega/` | Completado | Reubicado; idéntico por hash al `avance1.pdf` que existía duplicado en el repositorio (no se perdió contenido) |
| Esquema relacional | `schema.sql` | `../03_postgresql_postgis/cargas/` | Completado | Reubicado desde `sql/` |
| Datos de ejemplo SQL | `datos_ejemplo.sql` | `../03_postgresql_postgis/cargas/` | Completado | Reubicado desde `sql/` |
| Script de carga PostgreSQL | `cargar_postgres.py` | `../03_postgresql_postgis/cargas/` | Completado | Reubicado desde `scripts/`; rutas internas y carga de `.env` corregidas para funcionar desde cualquier directorio |
| Consulta analítica SQL | `consulta_01_incendios_clima_mensual.sql` | `../03_postgresql_postgis/consultas/` | Completado | Reubicado desde `consultas/`; corregido el `JOIN` final (`INNER`→`LEFT` desde clima) el 2026-09-13, ver `decisiones_metodologicas.md` |
| Documento de ejemplo MongoDB | `detecciones_viirs.json` | `../04_mongodb/cargas/` | Completado | Reubicado desde `nosql/` |
| Script de carga MongoDB | `cargar_mongodb.py` | `../04_mongodb/cargas/` | Completado | Reubicado desde `scripts/`; ruta interna corregida |
| Consultas MongoDB | `consultas_mongodb.js` | `../04_mongodb/consultas/` | Completado | Reubicado desde `nosql/` |
| Automatización (DAGs) | `fireforest_prueba.py`, `fireforest_validar_viirs.py` | `../08_airflow/dags/` | En desarrollo | Reubicados desde `airflow/dags/`; `docker-compose.override.yaml` corregido para montar el nuevo `04_mongodb/cargas/` |
| Plan de trabajo | `plan_implementacion.md` | `./` (14_gestion) | Completado | Reubicado desde `docs/`; cumple la función de "plan de trabajo" de la estructura objetivo (no se creó un `plan_trabajo.md` adicional para no duplicar contenido) |
| Control de avance | `tareas_pendientes.md` | `./` (14_gestion) | Completado | Este mismo control |
| Matriz de entregables | `matriz_entregables.md` | `./` (14_gestion) | Completado | Este documento |
| Bitácora de la reorganización | `bitacora.md` | `./` (14_gestion) | Completado | Registra esta reorganización |
| Lista de verificación | `lista_verificacion.md` | `./` (14_gestion) | Completado | Checklist de la validación final |
| Dataset integrado celda-mes | — | `../02_datos/final/` | Pendiente | Carpeta creada, sin contenido |
| Automatización Spark/PySpark | — | `../09_spark_pyspark/` | Pendiente | Carpeta creada, sin contenido |
| Análisis estadístico | — | `../10_analisis/` | Pendiente | Carpeta creada, sin contenido |
| Avance 2 | — | `../12_avance_2/` | Pendiente | Carpeta creada, sin contenido |
| Entrega final | — | `../13_entrega_final/` | Pendiente | Carpeta creada, sin contenido |

## Cumplimiento de la guía del Avance 1

Evaluación detallada punto por punto en
`../01_avance_1/evidencias/evaluacion_cumplimiento_guia.md`. Tabla
resumen por criterio de la guía (`../01_avance_1/guia/Guia_Avance_Proyecto_Integrador.pdf`):

| Criterio de la guía | Evidencia | Archivo | Ubicación | Estado | Observaciones | Acción requerida |
|---|---|---|---|---|---|---|
| Requisitos formales (modalidad, 1 PDF, nombre de archivo) | Portada con 3 integrantes; archivo único; nombre exacto `GrupoXX_...` | `Grupo04_AvanceProyectoIntegrador.pdf` | `../01_avance_1/entrega/` | CUMPLE | — | Ninguna |
| Extensión (5–8 páginas sin portada) | 9 páginas totales = 1 portada + 8 de contenido | Ídem | Ídem | CUMPLE | En el límite superior del rango | Ninguna |
| Definición del problema | Secciones 1.1–1.5 (contexto, población, objetivo, usuarios, preguntas) | Ídem | Ídem | CUMPLE | — | Ninguna |
| Inventario de 3 fuentes | Secciones 2.1–2.3 (malla, VIIRS, CHIRPS) con los 7 atributos exigidos | Ídem | Ídem | CUMPLE PARCIALMENTE | Fuente institucional de la malla y producto/campo de calidad VIIRS declarados como pendientes por el propio equipo | Confirmar en Avance 2 (ver `decisiones_metodologicas.md` §4) — **sin evidencia técnica todavía, no marcar como resuelto** |
| Diseño SQL vs. NoSQL | Secciones 3.1–3.5 | Ídem | Ídem | CUMPLE | Organización en subsecciones en vez de la tabla sugerida (solo forma) | Ninguna obligatoria |
| Modelo preliminar (tablas PK/FK + JSON) | Secciones 4.1–4.3 | Ídem | Ídem | CUMPLE | — | Ninguna |
| Arquitectura preliminar (diagrama) | Sección 5, Figura 1 | Ídem | Ídem | CUMPLE | — | Ninguna |
| Pregunta analítica y unidad de análisis | Sección 6 | Ídem | Ídem | CUMPLE | — | Ninguna |
| Dataset esperado | Sección 6 (párrafo final) | Ídem | Ídem | CUMPLE | — | Ninguna |
| Plan de implementación | Sección 7 | Ídem | Ídem | CUMPLE | — | Ninguna |
| Lista de comprobación (8 ítems) | Ver evaluación detallada §11 | Ídem | Ídem | CUMPLE (8/8) | — | Ninguna |
| Consistencia de la consulta SQL ilustrativa (sección 3.5) con el archivo técnico completo | Fragmento en el PDF vs. `consulta_01_incendios_clima_mensual.sql` | PDF + `.sql` | `../01_avance_1/entrega/` y `../03_postgresql_postgis/consultas/` | CUMPLE PARCIALMENTE | El `.sql` tenía un `INNER JOIN` que descartaba clima sin incendio; **ya corregido en el archivo técnico** (no en el PDF, que se conserva intacto) | **Corregido** en esta auditoría (2026-09-13); pendiente solo replicar el mismo patrón en el futuro pipeline de integración celda-mes |

**Nota:** ninguna observación de esta tabla se marcó como "resuelta"
sin evidencia técnica verificable; los pendientes de fuentes (malla,
VIIRS) permanecen en `CUMPLE PARCIALMENTE` hasta que exista un archivo,
ejecución o documento que los confirme.
