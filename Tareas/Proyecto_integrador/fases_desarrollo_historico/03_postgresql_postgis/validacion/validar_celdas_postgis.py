"""Validacion PostGIS de la sustitucion de celdas controladas (Fase F,
pendiente de aprobacion). NO aplica cambios permanentes: toda la ejecucion
ocurre dentro de una unica transaccion que termina siempre en ROLLBACK,
sin importar el resultado.

Que valida, en orden:

 1. Sustitucion de las celdas antiguas: LJ_04521/LJ_04522 no existen tras
    la migracion; LJ_TEST_001/LJ_TEST_002 si existen.
 2. Integridad de claves foraneas: ninguna fila de fact_incendio/fact_clima
    queda huerfana (sin dim_celda/dim_fecha correspondiente).
 3. SRID de dim_celda.geom = 32717 para las celdas nuevas.
 4. Geometria valida (ST_IsValid).
 5. Area = 250 000 m2 (ST_Area).
 6. Pertenencia COMPLETA al canton Loja (ST_Within del poligono completo,
    no solo del centroide) contra el limite reconstruido desde la capa
    oficial del INEC (02_datos/raw/malla/).
 7. Pertenencia a la parroquia El Cisne (mismo procedimiento).
 8. Distancia minima al limite cantonal >= 1000 m (ST_Distance).
 9. La consulta de integracion celda-mes (consulta_01_incendios_clima_
    mensual.sql) sigue funcionando con los nuevos identificadores.
10. Caso "clima sin deteccion": una fila de fact_clima sin fila
    correspondiente en fact_incendio debe aparecer en el resultado con
    detecciones_totales = 0 (no ausente), y se documenta la diferencia
    frente a un valor NULL real.

No se solicitan ni se almacenan credenciales en este script: se leen de
las variables ya existentes en `.env` (python-dotenv), el mismo archivo
que ya usan cargar_postgres.py y cargar_mongodb.py. No se escribe en
`.env` en ningun momento. No hay rutas personales: todo es relativo a la
ubicacion de este archivo.

Uso (ver instrucciones completas de PowerShell en el informe de cierre):

    python 03_postgresql_postgis/validacion/validar_celdas_postgis.py

Salida: se imprime en pantalla y se guarda tambien en
03_postgresql_postgis/evidencias/salida_validacion_postgis_celdas.txt
"""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

from dotenv import load_dotenv
import os

# ---------------------------------------------------------------------------
# Rutas relativas (sin rutas personales)
# ---------------------------------------------------------------------------
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]              # .../Proyecto_integrador
PRESENTACION_SCRIPTS = REPO_ROOT / "01_avance_1" / "presentacion" / "scripts"
EVIDENCIAS_DIR = REPO_ROOT / "03_postgresql_postgis" / "evidencias"
CARGAS_DIR = REPO_ROOT / "03_postgresql_postgis" / "cargas"
CONSULTAS_DIR = REPO_ROOT / "03_postgresql_postgis" / "consultas"
ENV_PATH = REPO_ROOT / ".env"

sys.path.insert(0, str(PRESENTACION_SCRIPTS))
from verificacion_territorial_y_malla import construir_limites  # noqa: E402


def _log(*args):
    print(*args)


def main():
    load_dotenv(ENV_PATH)  # solo LEE .env; nunca lo modifica ni lo imprime

    import psycopg

    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    dbname = os.getenv("PGDATABASE", "fireforest")
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "")

    if not password:
        _log("ERROR: PGPASSWORD no esta definido en .env (o .env no existe).")
        _log("Este script no solicita la contrasena por otro medio; "
             "cree su propio .env local a partir de .env.example y "
             "complete PGPASSWORD antes de ejecutar.")
        sys.exit(1)

    conninfo = f"host={host} port={port} dbname={dbname} user={user} password={password}"

    _log("=" * 78)
    _log("VALIDACION POSTGIS DE LA SUSTITUCION DE CELDAS (transaccion de prueba)")
    _log("=" * 78)
    _log(f"Conectando a {user}@{host}:{port}/{dbname} (credenciales tomadas de .env)")

    canton_loja, canton_catamayo, parroquias = construir_limites()
    el_cisne = parroquias["110153"]

    with psycopg.connect(conninfo, autocommit=False) as conn:
        with conn.cursor() as cur:
            _ejecutar_migracion(cur)
            _log("\n--- 1) Sustitucion de las celdas antiguas ---")
            _check_sustitucion(cur)

            _log("\n--- 2) Integridad de claves foraneas (sin filas huerfanas) ---")
            _check_fk_integrity(cur)

            _log("\n--- 3-5) SRID, geometria valida, area ---")
            _check_srid_validez_area(cur)

            _log("\n--- 6) Pertenencia completa al canton Loja (poligono, no solo centroide) ---")
            _check_within_canton(cur, canton_loja, "canton_loja_tmp")

            _log("\n--- 7) Pertenencia a la parroquia El Cisne ---")
            _check_within_canton(cur, el_cisne, "parroquia_el_cisne_tmp",
                                  etiqueta="parroquia El Cisne")

            _log("\n--- 8) Distancia minima al limite cantonal (>= 1000 m) ---")
            _check_distancia(cur, canton_loja)

            _log("\n--- 9) Consulta de integracion celda-mes ---")
            _check_integracion_celda_mes(cur)

            _log("\n--- 10) Caso clima sin deteccion (0 vs NULL) ---")
            _check_clima_sin_deteccion(cur)

        conn.rollback()
        _log("\n" + "=" * 78)
        _log("ROLLBACK ejecutado. Ningun cambio quedo persistido en la base de datos.")
        _log("=" * 78)


def _strip_sql_comments(text: str) -> str:
    """Elimina comentarios de linea '-- ...' ANTES de partir por ';', para
    que un ';' dentro de una frase en un comentario (prosa) no se confunda
    con el separador de sentencias SQL."""
    out_lines = []
    for line in text.splitlines():
        idx = line.find("--")
        out_lines.append(line[:idx] if idx != -1 else line)
    return "\n".join(out_lines)


def _run_sql_file(cur, path: Path, stop_before: str | None = None):
    text = path.read_text(encoding="utf-8")
    if stop_before:
        text = text.split(stop_before)[0]
    text = _strip_sql_comments(text)
    # quitar BEGIN/ROLLBACK propios del archivo: la transaccion la controla
    # este script (psycopg ya abre una transaccion implicita)
    statements = []
    for raw in text.split(";"):
        stmt = raw.strip()
        if not stmt:
            continue
        upper = stmt.upper()
        if upper in ("BEGIN", "ROLLBACK", "COMMIT"):
            continue
        statements.append(stmt)
    for stmt in statements:
        cur.execute(stmt)


def _ejecutar_migracion(cur):
    _log("\n--- 0) Aplicando actualizacion_celdas_prueba.sql (dentro de la transaccion) ---")
    sql_path = CARGAS_DIR / "actualizacion_celdas_prueba.sql"
    _run_sql_file(cur, sql_path, stop_before="-- 3) Verificaciones")
    _log(f"Migracion aplicada desde: {sql_path.relative_to(REPO_ROOT)}")


def _check_sustitucion(cur):
    cur.execute("SELECT celda_id FROM dim_celda WHERE celda_id IN ('LJ_04521','LJ_04522')")
    antiguas = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT celda_id FROM dim_celda WHERE celda_id IN ('LJ_TEST_001','LJ_TEST_002') ORDER BY celda_id")
    nuevas = [r[0] for r in cur.fetchall()]
    _log(f"Celdas antiguas remanentes (esperado: []): {antiguas}")
    _log(f"Celdas nuevas presentes (esperado: ['LJ_TEST_001','LJ_TEST_002']): {nuevas}")
    assert antiguas == [], "Las celdas antiguas NO deberian existir tras la migracion"
    assert nuevas == ["LJ_TEST_001", "LJ_TEST_002"], "Faltan celdas nuevas"


def _check_fk_integrity(cur):
    cur.execute("""
        SELECT fi.incendio_id, fi.celda_id FROM fact_incendio fi
        LEFT JOIN dim_celda dc ON dc.celda_id = fi.celda_id
        WHERE dc.celda_id IS NULL
    """)
    huerfanos_incendio = cur.fetchall()
    cur.execute("""
        SELECT fc.celda_id, fc.fecha_id FROM fact_clima fc
        LEFT JOIN dim_celda dc ON dc.celda_id = fc.celda_id
        WHERE dc.celda_id IS NULL
    """)
    huerfanos_clima = cur.fetchall()
    cur.execute("""
        SELECT fi.incendio_id FROM fact_incendio fi
        LEFT JOIN dim_fecha df ON df.fecha_id = fi.fecha_id
        WHERE df.fecha_id IS NULL
    """)
    huerfanos_fecha = cur.fetchall()
    _log(f"fact_incendio sin dim_celda (esperado []): {huerfanos_incendio}")
    _log(f"fact_clima sin dim_celda (esperado []): {huerfanos_clima}")
    _log(f"fact_incendio sin dim_fecha (esperado []): {huerfanos_fecha}")
    assert not huerfanos_incendio and not huerfanos_clima and not huerfanos_fecha, \
        "Se encontraron filas huerfanas"

    # duplicados celda-fecha (violarian la restriccion UNIQUE, pero se
    # verifica explicitamente igual, como pide el punto 6 del pedido)
    cur.execute("""
        SELECT celda_id, fecha_id, COUNT(*) FROM fact_incendio
        WHERE celda_id IN ('LJ_TEST_001','LJ_TEST_002')
        GROUP BY celda_id, fecha_id HAVING COUNT(*) > 1
    """)
    dup_incendio = cur.fetchall()
    cur.execute("""
        SELECT celda_id, fecha_id, COUNT(*) FROM fact_clima
        WHERE celda_id IN ('LJ_TEST_001','LJ_TEST_002')
        GROUP BY celda_id, fecha_id HAVING COUNT(*) > 1
    """)
    dup_clima = cur.fetchall()
    _log(f"Duplicados celda-fecha en fact_incendio (esperado []): {dup_incendio}")
    _log(f"Duplicados celda-fecha en fact_clima (esperado []): {dup_clima}")
    assert not dup_incendio and not dup_clima, "Se encontraron combinaciones celda-fecha duplicadas"


def _check_srid_validez_area(cur):
    cur.execute("""
        SELECT celda_id, ST_SRID(geom), ST_IsValid(geom), ST_Area(geom)
        FROM dim_celda
        WHERE celda_id IN ('LJ_TEST_001','LJ_TEST_002')
        ORDER BY celda_id
    """)
    for celda_id, srid, valido, area in cur.fetchall():
        _log(f"{celda_id}: SRID={srid} valido={valido} area_m2={area}")
        assert srid == 32717, f"SRID inesperado para {celda_id}: {srid}"
        assert valido, f"Geometria invalida para {celda_id}"
        assert abs(float(area) - 250000.0) < 0.01, f"Area inesperada para {celda_id}: {area}"


def _check_within_canton(cur, geom_shapely, tmp_table, etiqueta="canton Loja"):
    cur.execute(f"CREATE TEMP TABLE {tmp_table} (geom geometry(Polygon,32717)) ON COMMIT DROP")
    cur.execute(
        f"INSERT INTO {tmp_table} (geom) VALUES (ST_GeomFromWKB(%s, 32717))",
        (geom_shapely.wkb,),
    )
    cur.execute(f"""
        SELECT dc.celda_id,
               ST_Within(ST_Centroid(dc.geom), t.geom) AS centroide_dentro,
               ST_Within(dc.geom, t.geom)               AS poligono_dentro
        FROM dim_celda dc
        CROSS JOIN {tmp_table} t
        WHERE dc.celda_id IN ('LJ_TEST_001','LJ_TEST_002')
        ORDER BY dc.celda_id
    """)
    for celda_id, centroide_dentro, poligono_dentro in cur.fetchall():
        _log(f"{celda_id}: dentro de {etiqueta} (centroide)={centroide_dentro} "
             f"(poligono completo)={poligono_dentro}")
        assert centroide_dentro and poligono_dentro, \
            f"{celda_id} no quedo completamente dentro de {etiqueta}"


def _check_distancia(cur, canton_loja_shapely):
    cur.execute("CREATE TEMP TABLE canton_loja_dist_tmp (geom geometry(Polygon,32717)) ON COMMIT DROP")
    cur.execute(
        "INSERT INTO canton_loja_dist_tmp (geom) VALUES (ST_GeomFromWKB(%s, 32717))",
        (canton_loja_shapely.wkb,),
    )
    cur.execute("""
        SELECT dc.celda_id, ST_Distance(dc.geom, ST_Boundary(t.geom)) AS distancia_m
        FROM dim_celda dc
        CROSS JOIN canton_loja_dist_tmp t
        WHERE dc.celda_id IN ('LJ_TEST_001','LJ_TEST_002')
        ORDER BY dc.celda_id
    """)
    for celda_id, dist in cur.fetchall():
        _log(f"{celda_id}: distancia al limite = {dist:.2f} m")
        assert float(dist) >= 1000.0, f"{celda_id} no cumple el margen de 1000 m"


def _check_integracion_celda_mes(cur):
    consulta_path = CONSULTAS_DIR / "consulta_01_incendios_clima_mensual.sql"
    sql = consulta_path.read_text(encoding="utf-8")
    cur.execute(sql)
    filas = cur.fetchall()
    cols = [d.name for d in cur.description]
    _log(f"Filas devueltas por la consulta de integracion (todas las celdas cargadas): {len(filas)}")
    for fila in filas:
        _log(dict(zip(cols, fila)))
    ids_en_resultado = {fila[cols.index("celda_id")] for fila in filas}
    assert {"LJ_TEST_001", "LJ_TEST_002"}.issubset(ids_en_resultado), \
        "Las celdas nuevas no aparecen en la consulta de integracion"


def _check_clima_sin_deteccion(cur):
    cur.execute("SAVEPOINT clima_sin_deteccion")
    try:
        # dia sintetico de septiembre 2023 sin ninguna fila en fact_incendio
        cur.execute("""
            INSERT INTO dim_fecha (fecha_id, fecha, anio, mes)
            VALUES (20230901, '2023-09-01', 2023, 9)
            ON CONFLICT (fecha_id) DO NOTHING
        """)
        cur.execute("""
            INSERT INTO fact_clima (celda_id, fecha_id, precipitacion_diaria_mm)
            VALUES ('LJ_TEST_001', 20230901, 15.2)
            ON CONFLICT (celda_id, fecha_id) DO NOTHING
        """)
        consulta_path = CONSULTAS_DIR / "consulta_01_incendios_clima_mensual.sql"
        cur.execute(consulta_path.read_text(encoding="utf-8"))
        filas = cur.fetchall()
        cols = [d.name for d in cur.description]
        fila_sep = [dict(zip(cols, f)) for f in filas
                    if f[cols.index("celda_id")] == "LJ_TEST_001" and f[cols.index("mes")] == 9]
        _log(f"Fila celda-mes sintetica (LJ_TEST_001, 2023-09): {fila_sep}")
        assert len(fila_sep) == 1, "No aparecio la fila celda-mes sintetica de septiembre"
        f = fila_sep[0]
        assert f["detecciones_totales"] == 0, \
            "detecciones_totales deberia ser 0 (no ausente) cuando no hay fila en fact_incendio"
        assert float(f["precipitacion_acumulada_mensual_mm"]) == 15.2, \
            "La precipitacion real deberia conservarse"
        _log("Confirmado: LEFT JOIN + COALESCE produce 0 (no NULL, no ausencia de fila) "
             "para detecciones_totales cuando el mes tiene clima pero ninguna deteccion.")
        _log("En la prueba controlada, LEFT JOIN conservo la fila climatica y COALESCE "
             "represento con cero la ausencia de una fila coincidente de incendio. En datos "
             "reales, el cero solo podra interpretarse como ausencia de detecciones despues "
             "de verificar independientemente la cobertura e ingesta VIIRS.")
    finally:
        cur.execute("ROLLBACK TO SAVEPOINT clima_sin_deteccion")


if __name__ == "__main__":
    buf = io.StringIO()
    exit_code = 0
    try:
        with redirect_stdout(buf):
            main()
    except AssertionError as e:
        with redirect_stdout(buf):
            print(f"\nFALLO DE VALIDACION: {e}")
        exit_code = 2
    except Exception as e:  # conexion, etc.
        with redirect_stdout(buf):
            print(f"\nERROR: {type(e).__name__}: {e}")
        exit_code = 1
    finally:
        output = buf.getvalue()
        print(output)
        EVIDENCIAS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = EVIDENCIAS_DIR / "salida_validacion_postgis_celdas.txt"
        out_path.write_text(output, encoding="utf-8")
        print(f"\nSalida guardada en: {out_path}")
    sys.exit(exit_code)
