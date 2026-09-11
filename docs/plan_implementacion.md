# Plan preliminar de implementación

Plan de trabajo para el desarrollo del proyecto FireForest durante el curso. Es preliminar y podrá ajustarse conforme se conozcan mejor los datos y las restricciones técnicas.

| Etapa | Actividad | Resultado esperado | Estado en este avance |
|---|---|---|---|
| 1 | Identificación de fuentes | Fuentes disponibles (malla espacial, VIIRS, CHIRPS) documentadas | Completado — ver `docs/inventario_fuentes.md` |
| 2 | Diseño relacional (SQL) | Esquema `dim_celda`, `dim_fecha`, `fact_incendio`, `fact_clima` con PK/FK | Completado — ver `sql/schema.sql` |
| 3 | Diseño NoSQL | Colección `detecciones_viirs` con documento de ejemplo | Completado — ver `nosql/detecciones_viirs.json` |
| 4 | Ingesta | Carga de datos de ejemplo en PostgreSQL y MongoDB | Completado con datos de ejemplo — ver "Proceso de acceso e importación" abajo |
| 5 | Limpieza y validación | Datos consistentes (sin duplicados, geometría y fechas válidas) | Pendiente |
| 6 | Integración | Dataset consolidado por celda–mes (SQL + NoSQL) | Pendiente |
| 7 | Análisis | Indicadores y/o modelos (relación incendio–precipitación) | Pendiente |
| 8 | Producto final | Reporte, dashboard o modelo reproducible | Pendiente |

## Relación con las entregas del curso

- **Avance 1 (este documento):** etapas 1 a 4 completas con datos de ejemplo.
- **Avance 2 (siguiente entrega):** etapa 5 (limpieza y validación); avanzar etapa 6 (integración del dataset celda–mes); evaluar incorporación de datos reales exportados de GEE (VIIRS/CHIRPS) como copias controladas, sin tocar archivos ni scripts de FIRELAB_Loja.
- **Informe final:** etapas 7 y 8, con el dataset integrado, el análisis de la pregunta analítica y el producto final (reporte o dashboard).

## Proceso de acceso e importación de las bases de datos

Requiere PostgreSQL y MongoDB instalados y corriendo localmente (servicios `postgresql-x64-18` y `MongoDB` en Windows).

1. Copiar `.env.example` a `.env` y completar `PGUSER`/`PGPASSWORD` con las credenciales locales de Postgres. `.env` no se sube a git.
2. Activar el entorno virtual: `.venv\Scripts\activate`.
3. PostgreSQL/PostGIS: `python scripts/cargar_postgres.py` — crea la base `fireforest` si no existe, aplica `sql/schema.sql` y carga `sql/datos_ejemplo.sql`. Requiere la extensión PostGIS disponible en el servidor.
4. MongoDB: `python scripts/cargar_mongodb.py` — carga `nosql/detecciones_viirs.json` en la base `fireforest`, colección `detecciones_viirs` (no requiere autenticación en la instalación local por defecto).
5. Verificación: ambos scripts imprimen el conteo de filas/documentos cargados al finalizar; también puede verificarse con `psql -U <usuario> -d fireforest -c "SELECT COUNT(*) FROM fact_incendio;"` y `mongosh fireforest --eval "db.detecciones_viirs.countDocuments()"`.

Los datos usados en este avance son de ejemplo y controlados (ver restricciones en `CLAUDE.md` y `docs/inventario_fuentes.md`). La incorporación de datos reales de GEE se documentará como copias independientes en `datos/raw/`, sin acceder a los archivos del proyecto FIRELAB_Loja.
