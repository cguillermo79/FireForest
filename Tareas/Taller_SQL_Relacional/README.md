# Taller SQL Relacional — Práctica 2 (M1721)

## Advertencia importante

**Esta es una tarea independiente del Proyecto Integrador FireForest.** Comparte el mismo
dominio temático (incendios forestales, cantón Loja) y adapta ideas conceptuales del esquema
relacional de FireForest, pero:

- usa su **propia base de datos PostgreSQL** (`taller_sql_fireforest`, distinta de `fireforest`);
- usa su **propio esquema y datos de ejemplo** (no copiados automáticamente del Proyecto
  Integrador);
- **no depende de MongoDB** ni de ningún componente NoSQL;
- puede ejecutarse y revisarse sin tocar ningún archivo del Proyecto Integrador ni del proyecto
  FIRELAB_Loja.

## Propósito

Diseñar e implementar una base de datos relacional para un caso aplicado (detecciones de
incendio, precipitación y cobertura vegetal por celda espacial y fecha), justificar su
normalización hasta 3FN y construir consultas SQL que respondan preguntas operativas y
analíticas. Ver la guía en `00_guia/` y el caso en `01_documentacion/caso_aplicado.md`.

## Estructura de carpetas

```
Taller_SQL_Relacional/
├── 00_guia/                 Guía de la práctica (copia, sin modificar el original)
├── 01_documentacion/        caso_aplicado.md, normalizacion.md, modelo_relacional.md
├── 02_sql/                  schema.sql (DDL) + inicializar_taller.py (script reproducible)
├── 03_datos/                datos_ejemplo.sql (datos de ejemplo controlados, INSERT)
├── 04_consultas/            9 consultas SQL (mínimo 8 exigido + 1 extra), una por archivo
├── 05_resultados/           resultados_consultas.md y validaciones.md (evidencia de ejecución)
└── README.md                Este archivo
```

## Requisitos

- PostgreSQL 13+ corriendo localmente (ya disponible en este equipo).
- Python 3.10+ con el entorno virtual de FireForest (`../../.venv`), que ya incluye `psycopg` y
  `python-dotenv` (ver `../../requirements.txt`).
- Un archivo `.env` en la raíz de FireForest (`FireForest/.env`, no versionado) con
  `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD` — el mismo que usa el Proyecto Integrador para
  conectarse al servidor local de PostgreSQL (se reutiliza la conexión al servidor, **no** la
  base de datos `fireforest`).

## Procedimiento para crear la base y cargar los datos

Reproducible con un solo comando, desde la raíz de FireForest:

```bash
.venv\Scripts\activate
python Tareas/Taller_SQL_Relacional/02_sql/inicializar_taller.py
```

Este script:

1. Recrea desde cero la base `taller_sql_fireforest` (la elimina si ya existe y la vuelve a
   crear), sin tocar `fireforest`.
2. Ejecuta `02_sql/schema.sql` (tablas, PK, FK, restricciones).
3. Ejecuta `03_datos/datos_ejemplo.sql` (datos de ejemplo controlados).
4. Ejecuta las 9 consultas de `04_consultas/` y guarda pregunta + SQL + resultado en
   `05_resultados/resultados_consultas.md`.
5. Ejecuta controles de integridad (PK, FK, UNIQUE, CHECK, coherencia de valores, conteo de
   filas) y guarda la evidencia en `05_resultados/validaciones.md`.

## Procedimiento manual alternativo (solo SQL, sin Python)

```bash
psql -U <usuario> -h localhost -c "DROP DATABASE IF EXISTS taller_sql_fireforest;"
psql -U <usuario> -h localhost -c "CREATE DATABASE taller_sql_fireforest;"
psql -U <usuario> -h localhost -d taller_sql_fireforest -f 02_sql/schema.sql
psql -U <usuario> -h localhost -d taller_sql_fireforest -f 03_datos/datos_ejemplo.sql
psql -U <usuario> -h localhost -d taller_sql_fireforest -f 04_consultas/01_detecciones_por_celda_y_periodo.sql
-- (repetir para cada archivo de 04_consultas/)
```

## Datos

Todos los datos son de ejemplo, controlados y generados específicamente para este taller: 6
celdas, 12 fechas (jul–sep 2023), 5 tipos de cobertura vegetal, 82 filas en total distribuidas en
6 tablas. No son datos reales de VIIRS/CHIRPS ni provienen de archivos del proyecto
FIRELAB_Loja. Ver el detalle en `01_documentacion/caso_aplicado.md`.
