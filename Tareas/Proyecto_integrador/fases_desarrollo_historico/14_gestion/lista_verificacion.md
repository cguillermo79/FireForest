# Lista de verificación final — reorganización 2026-09-13

| # | Verificación | Resultado |
|---|---|---|
| 1 | `git status --short` ejecutado antes y después de mover archivos | Sí, ver `bitacora.md` |
| 2 | Inventario recursivo de la raíz de FireForest antes de mover | Sí |
| 3 | Lectura de `README.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore` | Sí |
| 4 | `Taller_NoSQL` y `Taller_SQL_Relacional` sin modificar | Confirmado: `git status --short` sobre ambas carpetas no devuelve ningún cambio |
| 5 | `.git`, `.venv` no movidos ni modificados | Confirmado |
| 6 | `.env` no copiado, mostrado ni expuesto | Confirmado: solo se movió de ubicación (`airflow/.env` → `08_airflow/.env`) sin leer ni imprimir su contenido; sigue ignorado por git |
| 7 | Ningún archivo eliminado (solo directorios vacíos) | Confirmado: `sql/`, `nosql/`, `scripts/`, `docs/`, `consultas/`, `datos/{raw,processed}/`, `notebooks/`, `resultados/`, `logs/` estaban vacíos antes de eliminarlos (verificado con `find` antes de cada `rmdir`) |
| 8 | `git mv` usado para archivos versionados | Confirmado: `git status` muestra 13 renombres (`R`/`RM`) detectados por git |
| 9 | Los 4 documentos del Avance 1 continúan presentes o su ausencia está justificada | 3 archivos únicos presentes en `../01_avance_1/`; el cuarto (`avance1.pdf`) era un duplicado exacto por hash de `Grupo04_AvanceProyectoIntegrador.pdf` (ambos blobs `090fc876...` en el historial de git) — no hay pérdida de contenido |
| 10 | Contenido de `avance1.tex` sin modificar | Confirmado: `git hash-object` sobre el archivo actual coincide exactamente con el blob de `HEAD` (`ce9e8134...`) |
| 11 | Rutas internas actualizadas tras mover archivos | `cargar_mongodb.py`, `cargar_postgres.py`, `docker-compose.override.yaml`, `diseno_sql_nosql.md`, `inventario_fuentes.md`, `plan_implementacion.md` |
| 12 | Búsqueda de rutas rotas en `.py`, `.sql`, `.js`, `.md`, `.tex`, YAML y Docker | Sin coincidencias fuera de las menciones históricas intencionales en `bitacora.md` y las de `avance1.tex` (preservado a propósito) |
| 13 | Sintaxis Python válida en los 4 scripts reubicados | `py_compile` sin errores en `cargar_postgres.py`, `cargar_mongodb.py`, `fireforest_prueba.py`, `fireforest_validar_viirs.py` |
| 14 | JSON válido tras el traslado | `detecciones_viirs.json`: 2 documentos, carga correctamente con `json.load` |
| 15 | YAML válido tras el traslado | `docker-compose.yaml` y `docker-compose.override.yaml`: cargan correctamente con `yaml.safe_load` |
| 16 | No se generaron copias innecesarias de archivos pesados | `requirements.txt` y `.env.example` (livianos) se copiaron deliberadamente como referencia, documentado en el README; el duplicado `presentacion_fireforest.pdf` que ya existía se resolvió eliminando la copia sin seguimiento de git y conservando la versión con historial |
| 17 | Archivos ambiguos no movidos, registrados como pendientes | `Presentacion/s42408-026-00470-y.pdf` — ver `tareas_pendientes.md` |
| 18 | Sin `git commit`, `git push`, `git reset` ni `git clean` | Confirmado, ninguno de estos comandos se ejecutó |
| 19 | `.gitignore` de la raíz actualizado (rutas de `airflow/` obsoletas retiradas) | Confirmado |
| 20 | `.gitignore` propio de `Proyecto_integrador` creado y verificado con `git check-ignore` | Confirmado: `08_airflow/.env`, `08_airflow/logs/`, `**/__pycache__/`, `08_airflow/config/airflow.cfg`, `02_datos/raw/**`, `09_spark_pyspark/resultados/**`, `11_resultados/logs/**` se ignoran correctamente; se corrigió un caso donde `02_datos/raw/**` bloqueaba también sus propios `.gitkeep` anidados (se añadió `!02_datos/raw/**/` para permitir a git descender a las subcarpetas) |
| 21 | `s42408-026-00470-y.pdf` reubicado a `00_documentacion_inicial/referencias/` | `git mv` ejecutado; git lo detecta como renombre; hash idéntico (`0d26f556...`) antes y después |
| 22 | 43 carpetas con `.gitkeep` auditadas de forma recursiva | Ninguna contenía otro archivo además de `.gitkeep`; no se retiró ningún `.gitkeep` ni se eliminó ninguna carpeta |
| 23 | `docker compose config -q` desde `08_airflow/` | Configuración válida, sin errores (Docker Engine 29.7.2, Compose v5.5.0). El daemon de Docker Desktop no está activo (sin contenedores en ejecución), por lo que no se pudo comprobar el reconocimiento del DAG en un Airflow ya corriendo; no se inició Docker ni se descargaron/reconstruyeron imágenes |
| 24 | Volúmenes resueltos por `docker compose config` (solo rutas, sin volcar variables de entorno/secretos) | `../04_mongodb/cargas` → `/opt/airflow/fireforest/nosql` (antes `../nosql`); `dags`, `logs`, `config`, `plugins` resueltos correctamente a la nueva ubicación de `08_airflow/` |
| 25 | `requirements.txt` cubre las dependencias importadas por los scripts | Confirmado: `psycopg`, `python-dotenv` y `pymongo` presentes (usados por `cargar_postgres.py` y `cargar_mongodb.py`) |
| 26 | `.env.example` (raíz, `Proyecto_integrador/` y `08_airflow/`) sin credenciales reales | Confirmado: solo placeholders (`PGPASSWORD=` vacío, `FERNET_KEY=COLOCAR_AQUI_UNA_CLAVE_GENERADA_LOCALMENTE`) |
| 27 | `cargar_mongodb.py` resuelve rutas y ejecuta correctamente desde la nueva estructura | Ejecución real desde la raíz de FireForest: `Documentos insertados: 2`, `Documentos en la colección: 2` (base `fireforest`, colección `detecciones_viirs`) |
| 28 | `cargar_postgres.py` resuelve rutas y `.env` correctamente desde la nueva estructura | Ejecución real: conecta a PostgreSQL, confirma `Base 'fireforest' ya existe` y localiza `schema.sql` en su nueva ruta; falla con `DuplicateTable: la relación "dim_celda" ya existe` porque el script **no es idempotente por diseño** (no usa `CREATE TABLE IF NOT EXISTS`) y las tablas ya habían sido creadas en una carga anterior — este comportamiento es preexistente y no depende de la reorganización; la transacción se revirtió limpiamente (`with conexion:`), sin dejar la base en estado inconsistente |
