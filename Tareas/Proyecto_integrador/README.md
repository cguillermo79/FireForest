# Proyecto Integrador FireForest

## Propósito

Diseñar e implementar una arquitectura híbrida SQL–NoSQL que integre
detecciones satelitales de incendios (VIIRS) y datos climáticos de
precipitación (CHIRPS) sobre una malla espacial del cantón Loja, para
construir un dataset analítico por celda espacial y mes que permita
estudiar la relación entre condiciones climáticas y ocurrencia de
incendios. Ver el detalle completo en
`00_documentacion_inicial/problema.md`.

## Pregunta principal

¿Existe relación entre la precipitación acumulada mensual (CHIRPS) y la
ocurrencia/intensidad de incendios (VIIRS) en una misma celda espacial
del cantón Loja? (ver `00_documentacion_inicial/problema.md`, sección
"Preguntas que podrían responderse con los datos").

## Unidad de análisis: celda–mes

La unidad de análisis es una celda espacial de 500 m × 500 m observada
durante un mes (`celda_id + anio + mes`). La granularidad real tiene
tres niveles (ver `00_documentacion_inicial/diseno_sql_nosql.md`):

1. **MongoDB** guarda la detección individual VIIRS (`celda_id + fecha`,
   día y hora exactos).
2. **PostgreSQL** carga un registro **diario** por celda en
   `fact_incendio`/`fact_clima`.
3. El **dataset analítico celda-mes** se obtiene agregando esos
   registros diarios mediante `GROUP BY anio, mes` — no existen filas
   pre-agregadas por mes en las tablas base.

## Fuentes de datos

Malla espacial de referencia, VIIRS (NASA FIRMS, detección de fuego
activo) y CHIRPS (Climate Hazards Center, precipitación). Ficha técnica,
matriz de inventario y riesgos identificados en
`00_documentacion_inicial/inventario_fuentes.md`. **Los datos usados
actualmente son de ejemplo, controlados o simulados**, conforme a la
restricción del proyecto (`CLAUDE.md`, `AGENTS.md`): no se accede a
archivos del proyecto externo FIRELAB_Loja.

## Arquitectura SQL–NoSQL

- **PostgreSQL/PostGIS:** `dim_celda`, `dim_fecha`, `fact_incendio`,
  `fact_clima` — datos estables, relacionales, con integridad
  referencial y capacidades geoespaciales.
- **MongoDB:** colección `detecciones_viirs` — detecciones individuales
  en JSON semi-estructurado y anidado (coordenadas, calidad), antes de
  resumirlas por celda-mes.
- Justificación completa de cada tecnología y consultas que se espera
  resolver en `00_documentacion_inicial/diseno_sql_nosql.md`.

## Estructura de carpetas

```
Proyecto_integrador/
├── 00_documentacion_inicial/  Caso, objetivos*, inventario de fuentes, arquitectura*,
│                              diseño SQL-NoSQL, diccionario de datos*, presentación,
│                              referencias/ (artículos citados)
│                              (* pendientes de redactar, ver 14_gestion/tareas_pendientes.md)
├── 01_avance_1/               Guía, fuente (.tex) y entrega del Avance 1 (ya presentado)
├── 02_datos/                  raw/{malla,viirs,chirps}, interim, processed, final
├── 03_postgresql_postgis/     cargas/ (schema.sql, datos_ejemplo.sql, cargar_postgres.py),
│                              consultas/, evidencias/
├── 04_mongodb/                validacion_json/, cargas/ (detecciones_viirs.json,
│                              cargar_mongodb.py), consultas/, evidencias/
├── 05_ingesta/                malla/, viirs/, chirps/, metadatos/ (pendiente: Avance 2)
├── 06_calidad_datos/          validacion_malla/, validacion_viirs/, validacion_chirps/, reportes/
├── 07_etl_integracion/        extraccion/, transformacion/, carga/, integracion_celda_mes/
├── 08_airflow/                dags/, config/, evidencias/, docker-compose*.yaml
├── 09_spark_pyspark/          scripts/, notebooks/, resultados/ (pendiente)
├── 10_analisis/                notebooks/, consultas/, tablas/, figuras/ (pendiente)
├── 11_resultados/             calidad/, indicadores/, dataset_final/, logs/ (pendiente)
├── 12_avance_2/                guia/, fuente/, evidencias/, entrega/ (pendiente)
├── 13_entrega_final/          informe/, presentacion/, anexos/, entrega/ (pendiente)
├── 14_gestion/                plan_implementacion.md, tareas_pendientes.md,
│                              bitacora.md, matriz_entregables.md, lista_verificacion.md
├── README.md                  Este archivo
├── requirements.txt            Copia de referencia del entorno compartido (ver Requisitos)
└── .env.example                Copia de referencia de las variables compartidas
```

## Requisitos

- **Entorno virtual compartido**: `FireForest/.venv` (raíz del
  repositorio), con las dependencias de `requirements.txt`. El
  `requirements.txt` de esta carpeta es una **copia de referencia** del
  mismo archivo de la raíz; el entorno real que se activa y usa es
  siempre el de la raíz de FireForest (`.venv\Scripts\activate`), para
  no duplicar ni desincronizar entornos entre tareas.
- **`.env` compartido**: el archivo real `.env` que usan los scripts de
  este proyecto es el de la **raíz de FireForest**
  (`FireForest\.env`, no versionado), el mismo que reutiliza
  `Tareas/Taller_SQL_Relacional` para conectarse al servidor local de
  PostgreSQL (cada tarea usa su propia base de datos:
  `fireforest` para este proyecto). El `.env.example` de esta carpeta es
  una copia de referencia de las mismas variables.
- PostgreSQL 13+ con la extensión PostGIS disponible localmente.
- MongoDB corriendo localmente en `localhost:27017`.
- Docker (opcional) para levantar Airflow vía `08_airflow/docker-compose.yaml`.

## Orden de ejecución / desarrollo

Ver el detalle completo, con estado por etapa, en
`14_gestion/plan_implementacion.md` y `14_gestion/tareas_pendientes.md`.
Resumen de las 17 etapas (guía del proyecto):

1. Definición del problema, objetivo y pregunta — **completado**.
2. Inventario de malla espacial, VIIRS y CHIRPS — **completado**.
3. Definición de la unidad de análisis celda-mes — **completado**.
4. Diseño de PostgreSQL/PostGIS — **completado**.
5. Diseño documental en MongoDB — **completado**.
6. Adquisición y conservación de datos originales — **pendiente** (Avance 2).
7. Validación individual de cada fuente — **pendiente**.
8. Limpieza y estandarización — **pendiente**.
9. Carga en MongoDB y PostgreSQL/PostGIS — **completado con datos de ejemplo**.
10. Integración temporal y espacial — **pendiente**.
11. Construcción del dataset celda-mes — **pendiente**.
12. Controles de calidad del dataset integrado — **pendiente**.
13. Automatización mediante Airflow — **en desarrollo** (2 DAGs de prueba/validación ya operativos, ver `08_airflow/`).
14. Procesamiento o demostración de escalabilidad con Spark/PySpark — **pendiente**.
15. Análisis estadístico y visualización — **pendiente**.
16. Elaboración del Avance 2 — **pendiente**.
17. Elaboración del informe y presentación final — **pendiente**.

## Reproducción (carga de datos de ejemplo)

Todos los comandos se ejecutan **desde la raíz de FireForest**:

```bash
.venv\Scripts\activate
python Tareas\Proyecto_integrador\03_postgresql_postgis\cargas\cargar_postgres.py
python Tareas\Proyecto_integrador\04_mongodb\cargas\cargar_mongodb.py
```

Verificación:

```bash
psql -U <usuario> -d fireforest -c "SELECT COUNT(*) FROM fact_incendio;"
mongosh fireforest --eval "db.detecciones_viirs.countDocuments()"
```

Airflow (opcional, requiere Docker):

```bash
cd Tareas\Proyecto_integrador\08_airflow
docker-compose up airflow-init
docker-compose up
```

## Estado actual

Avance 1 presentado (etapas 1–5 y 9, con datos de ejemplo). Ver
`01_avance_1/entrega/Grupo04_AvanceProyectoIntegrador.pdf`. El resto de
etapas (6–8, 10–12, 14–17) están pendientes; la 13 (Airflow) está en
desarrollo. Detalle completo en `14_gestion/tareas_pendientes.md` y
`14_gestion/matriz_entregables.md`.

## Pendientes

- Redactar `00_documentacion_inicial/objetivos.md`,
  `arquitectura.md` y `diccionario_datos.md` (actualmente son *stubs*
  que documentan explícitamente qué falta; ver su contenido).
- Incorporar datos reales de GEE (VIIRS/CHIRPS) como copias
  independientes en `02_datos/raw/`, sin acceder a archivos de
  FIRELAB_Loja (ver `14_gestion/plan_implementacion.md`).
- Completar 05_ingesta, 06_calidad_datos, 07_etl_integracion,
  09_spark_pyspark, 10_analisis, 11_resultados, 12_avance_2 y
  13_entrega_final (carpetas creadas con `.gitkeep`, sin contenido aún).
- ~~`Presentacion/s42408-026-00470-y.pdf` de origen ambiguo~~ — resuelto:
  reubicado en `00_documentacion_inicial/referencias/` (artículo
  científico citado como referencia en la presentación de FireForest).

## Advertencia de independencia

Este proyecto y `Tareas/Taller_NoSQL`/`Tareas/Taller_SQL_Relacional` son
componentes distintos del mismo repositorio FireForest: los talleres son
actividades académicas independientes con sus propias bases de datos
(`taller_nosql_fireforest`, `taller_sql_fireforest`) y **no fueron
modificados** por esta reorganización. Este proyecto usa la base
`fireforest` (PostgreSQL y MongoDB). Ninguno de los tres componentes
accede a archivos del proyecto externo FIRELAB_Loja.
