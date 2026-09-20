# Bitácora

## 2026-09-13 — Reorganización integral del Proyecto Integrador FireForest

**Contexto:** antes de esta sesión ya existía un traslado parcial y sin
seguimiento de git de los documentos del Avance 1
(`Tareas/Proyecto_integrador/Avance1/` con 3 archivos, más una copia
suelta de `presentacion_fireforest.pdf`). Se verificó por hash de git
que ningún contenido se había perdido en ese traslado previo (los
blobs de `avance1.pdf`/`Grupo04_AvanceProyectoIntegrador.pdf`,
`Guia_Avance_Proyecto_Integrador.pdf`, `avance1.tex` y
`presentacion_fireforest.pdf` coinciden exactamente con las versiones
registradas en el historial de git).

**Acciones realizadas:**

1. Inventario recursivo de la raíz de FireForest y lectura de
   `README.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore` y `.env.example`.
2. Creación de la estructura objetivo completa dentro de
   `Tareas/Proyecto_integrador/` (00 a 14), con `.gitkeep` en las
   carpetas que aún no tienen contenido.
3. Reubicación de los 3 documentos del Avance 1 (ya trasladados
   previamente) a `01_avance_1/{guia,fuente,entrega}/`.
4. `git mv` de los archivos con seguimiento de git: `docs/*.md` →
   `00_documentacion_inicial/` y `14_gestion/plan_implementacion.md`;
   `Presentacion/presentacion_fireforest.{pdf,tex}` →
   `00_documentacion_inicial/`; `sql/*.sql` + `consultas/*.sql` →
   `03_postgresql_postgis/`; `nosql/*` → `04_mongodb/`;
   `scripts/cargar_*.py` → `03_postgresql_postgis/cargas/` y
   `04_mongodb/cargas/` respectivamente. Git detectó todos estos
   movimientos como renombres (contenido sin modificar).
5. Traslado de `airflow/` (sin seguimiento de git) a `08_airflow/`.
6. Corrección de rutas internas afectadas por el traslado:
   `cargar_mongodb.py`, `cargar_postgres.py` (rutas y carga de `.env`
   ahora robustas frente al directorio de trabajo),
   `08_airflow/docker-compose.override.yaml` (monta
   `../04_mongodb/cargas` en lugar de `../nosql`, sin cambiar la ruta
   dentro del contenedor ni el código de los DAGs),
   `diseno_sql_nosql.md` e `inventario_fuentes.md` (referencias a
   rutas). **No se modificó** `avance1.tex` (documento académico ya
   entregado): conserva intencionalmente sus menciones a las rutas
   anteriores a esta reorganización.
7. Eliminación de las carpetas vacías que quedaron en la raíz tras los
   traslados (`sql/`, `nosql/`, `scripts/`, `docs/`, `consultas/`,
   `datos/` con sus subcarpetas, `notebooks/`, `resultados/`, `logs/`).
   No se eliminó ningún archivo, solo directorios vacíos.
8. Creación de `README.md`, `requirements.txt` y `.env.example` (copias
   de referencia del entorno compartido) y `.gitignore` propio dentro de
   `Tareas/Proyecto_integrador/`.
9. Actualización del `.gitignore` de la raíz de FireForest: se
   retiraron las 4 líneas específicas de `airflow/` (rutas que ya no
   existen en la raíz) y se dejó una nota apuntando al `.gitignore` de
   `Tareas/Proyecto_integrador/`.
10. Creación de los 3 documentos pendientes de `00_documentacion_inicial/`
    (`objetivos.md`, `arquitectura.md`, `diccionario_datos.md`) como
    *stubs* transparentes que señalan qué falta redactar, sin fabricar
    contenido académico.
11. Creación de `14_gestion/tareas_pendientes.md`,
    `matriz_entregables.md`, `bitacora.md` (este archivo) y
    `lista_verificacion.md`.
12. Actualización del `README.md` raíz de FireForest para señalar que
    el proyecto principal vive en `Tareas/Proyecto_integrador`.

**No se ejecutó** `git commit`, `git push`, `git reset` ni `git clean`
en ningún momento. `Tareas/Taller_NoSQL` y `Tareas/Taller_SQL_Relacional`
no fueron tocados.

## 2026-09-13 — Auditoría final previa al commit

1. Se ejecutaron `git status --short`, `git diff --summary`,
   `git diff --stat` y `git diff -- .gitignore README.md` para revisar
   el estado completo antes de cualquier commit.
2. Se auditaron individualmente los 4 archivos marcados como
   eliminados en `Tareas/Avance1/` y `Tareas/Guia_Avance_Proyecto_Integrador.pdf`.
   Se confirmó por hash (`git rev-parse HEAD:<ruta>` vs.
   `git hash-object <ruta nueva>`) que 3 de los 4 tienen contenido
   idéntico en su nueva ubicación dentro de `01_avance_1/`. El cuarto
   (`avance1.pdf`) no tiene una ruta nueva propia porque era un
   duplicado exacto (mismo blob) de `Grupo04_AvanceProyectoIntegrador.pdf`,
   cuyo contenido sí se conserva. Se verificó además, con una prueba no
   destructiva (`git add -N` + `git diff -M` + `git reset` sobre esas
   3 rutas exclusivamente), que git sí reconoce esas 3 reubicaciones
   como renombres al 100% de similitud una vez indexadas; el estado del
   repositorio se restauró exactamente a como estaba antes de la
   prueba.
3. Se reubicó `Presentacion/s42408-026-00470-y.pdf` (artículo científico
   citado como referencia en la presentación de FireForest) a
   `00_documentacion_inicial/referencias/s42408-026-00470-y.pdf`
   mediante `git mv`; git lo detecta como renombre. Contenido verificado
   idéntico por hash (`0d26f556...`). La carpeta `Presentacion/` quedó
   vacía y se eliminó (no contenía más archivos).
4. Se revisaron las 43 carpetas con `.gitkeep` (verificación recursiva,
   no solo del primer nivel): ninguna contenía otro archivo además de
   `.gitkeep` (las carpetas que sí recibieron contenido real —
   `01_avance_1/entrega`, `fuente` y `guia` — nunca llegaron a tener
   `.gitkeep`, porque ya no estaban vacías en el momento en que se
   generaron los marcadores). No se retiró ningún `.gitkeep` ni se
   eliminó ninguna carpeta.
5. Se ejecutó `docker compose config -q` desde `08_airflow/` (sin
   descargar imágenes ni reconstruir contenedores): configuración
   válida. El daemon de Docker Desktop no estaba activo (sin
   contenedores en ejecución), por lo que no se pudo verificar el
   reconocimiento del DAG en un Airflow ya corriendo; no se intentó
   iniciar Docker para no incumplir la restricción de no
   descargar/reconstruir imágenes innecesariamente. Se confirmó, sin
   volcar variables de entorno (para no exponer `FERNET_KEY` u otros
   secretos), que los volúmenes se resuelven correctamente a la nueva
   ubicación, en particular `../04_mongodb/cargas` →
   `/opt/airflow/fireforest/nosql` (antes `../nosql`).
6. Se verificó que `requirements.txt` incluye `psycopg`,
   `python-dotenv` y `pymongo` (las dependencias que importan
   `cargar_postgres.py` y `cargar_mongodb.py`); que los tres
   `.env.example` (raíz, `Proyecto_integrador/` y `08_airflow/`) solo
   contienen placeholders, sin credenciales reales; y que
   `cargar_mongodb.py`/`cargar_postgres.py` resuelven correctamente sus
   rutas desde la nueva estructura mediante **ejecución real**:
   `cargar_mongodb.py` insertó 2 documentos en `fireforest.detecciones_viirs`
   sin error; `cargar_postgres.py` conectó a PostgreSQL, confirmó que la
   base `fireforest` ya existe y localizó `schema.sql` en su nueva ruta,
   pero falló con `DuplicateTable` porque el script no es idempotente
   por diseño (no usa `CREATE TABLE IF NOT EXISTS`) y las tablas ya
   existían de una carga previa — comportamiento preexistente, no
   causado por la reorganización; la transacción se revirtió
   limpiamente. También se detectó y corrigió un problema real en
   `Tareas/Proyecto_integrador/.gitignore`: el patrón `02_datos/raw/**`
   impedía que la negación `!02_datos/raw/**/.gitkeep` tuviera efecto
   sobre los `.gitkeep` anidados en `malla/`, `viirs/` y `chirps/`
   (limitación conocida de git al excluir directorios completos); se
   añadió `!02_datos/raw/**/` para que git descienda a esas carpetas y
   la negación de `.gitkeep` funcione, verificado con `git check-ignore`.
