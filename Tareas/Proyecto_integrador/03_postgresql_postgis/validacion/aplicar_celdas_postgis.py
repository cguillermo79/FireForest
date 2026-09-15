"""Ejecutor de la migracion PERMANENTE de celdas controladas (Fase F,
COMMIT real). A diferencia de `validar_celdas_postgis.py` (que este
script NO modifica y que sigue terminando siempre en ROLLBACK), este
ejecutor aplica el cambio de verdad contra la base de desarrollo
`fireforest`.

Que hace, en orden:

 0. Localiza la raiz del proyecto de forma relativa (sin rutas
    personales) y carga `Tareas/Proyecto_integrador/.env`.
 1. Comprueba que PGHOST, PGPORT, PGDATABASE, PGUSER y PGPASSWORD estan
    definidos. Nunca solicita, imprime ni guarda la contrasena: si
    falta, el script se detiene con un mensaje claro.
 2. Se conecta con psycopg (autocommit=False: la conexion abre una
    transaccion real).
 3. RESPALDO PREVIO: consulta las filas de `dim_celda`, `fact_incendio`
    y `fact_clima` relacionadas con LJ_04521/LJ_04522 y las guarda en
    `03_postgresql_postgis/evidencias/respaldo_celdas_anteriores.json`
    (geometria como ST_AsEWKT + SRID + area; sin variables de entorno
    ni cadenas de conexion). Esto ocurre ANTES de cualquier escritura,
    dentro de la misma transaccion (son solo lecturas).
 4. Lee `cargas/aplicar_actualizacion_celdas_prueba.sql` y ejecuta,
    dentro de la transaccion ya abierta, todas sus sentencias EXCEPTO
    `BEGIN`/`COMMIT` propios del archivo (la transaccion la controla
    este script). El parser de sentencias respeta bloques `DO $$ ... $$`
    (no corta por los `;` internos de esos bloques).
 5. Si cualquier sentencia falla (incluida una `RAISE EXCEPTION` de
    precondicion o postcondicion dentro de un bloque `DO`), se captura
    la excepcion, se hace ROLLBACK y el script termina con codigo de
    salida distinto de cero. Si todas las sentencias terminan bien, se
    hace COMMIT real.
 6. Cierra esa conexion y abre una conexion NUEVA, exclusivamente de
    lectura, para verificar el estado ya persistido (no queda ninguna
    escritura pendiente en esa segunda conexion).
 7. Guarda toda la salida en
    `03_postgresql_postgis/evidencias/salida_aplicacion_postgis_celdas.txt`
    (nunca en `salida_validacion_postgis_celdas.txt`, que conserva la
    prueba anterior con ROLLBACK).

Precision sobre 0 y NULL (ver verificacion del caso "clima sin
deteccion"): en la prueba controlada, LEFT JOIN conserva la fila
climatica y COALESCE representa con cero la ausencia de una fila
coincidente de incendio. En datos reales, el cero solo podra
interpretarse como ausencia de detecciones despues de verificar
independientemente la cobertura e ingesta VIIRS.

Uso:
    & ".venv\\Scripts\\python.exe" `
      ".\\Tareas\\Proyecto_integrador\\03_postgresql_postgis\\validacion\\aplicar_celdas_postgis.py"
"""

from __future__ import annotations

import datetime
import decimal
import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas relativas (sin rutas personales)
# ---------------------------------------------------------------------------
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]  # .../Proyecto_integrador
PRESENTACION_SCRIPTS = REPO_ROOT / "01_avance_1" / "presentacion" / "scripts"
EVIDENCIAS_DIR = REPO_ROOT / "03_postgresql_postgis" / "evidencias"
CARGAS_DIR = REPO_ROOT / "03_postgresql_postgis" / "cargas"
CONSULTAS_DIR = REPO_ROOT / "03_postgresql_postgis" / "consultas"
ENV_PATH = REPO_ROOT / ".env"
MIGRACION_SQL = CARGAS_DIR / "aplicar_actualizacion_celdas_prueba.sql"
RESPALDO_JSON = EVIDENCIAS_DIR / "respaldo_celdas_anteriores.json"
SALIDA_TXT = EVIDENCIAS_DIR / "salida_aplicacion_postgis_celdas.txt"

sys.path.insert(0, str(PRESENTACION_SCRIPTS))
from verificacion_territorial_y_malla import construir_limites  # noqa: E402

CELDAS_ANTIGUAS = ["LJ_04521", "LJ_04522"]
CELDAS_NUEVAS = ["LJ_TEST_001", "LJ_TEST_002"]
# psycopg3 no expande un parametro tupla en "IN %s" como hacia psycopg2;
# se usa "= ANY(%s)" con una lista, que es la forma correcta en psycopg3.
DISTANCIAS_ESPERADAS = {"LJ_TEST_001": 1085.00, "LJ_TEST_002": 1066.01}
TOLERANCIA_DISTANCIA_M = 0.5  # margen numerico razonable sobre la cifra reportada


def _log(*args):
    print(*args)


# ---------------------------------------------------------------------------
# 0-1) Credenciales: solo lectura de .env, nunca se piden ni se imprimen
# ---------------------------------------------------------------------------

def _cargar_credenciales():
    from dotenv import load_dotenv

    load_dotenv(ENV_PATH)
    campos = ["PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD"]
    valores = {c: os.getenv(c) for c in campos}
    faltantes = [c for c, v in valores.items() if not v]
    if faltantes:
        _log(f"ERROR: faltan variables en {ENV_PATH}: {', '.join(faltantes)}")
        _log("Este script no solicita la contrasena por otro medio. Complete su "
             "propio .env local (copiado de .env.example) antes de ejecutar.")
        sys.exit(1)
    _log(f"Variables de conexion encontradas en {ENV_PATH.relative_to(REPO_ROOT.parent)}: "
         f"PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD (valor no mostrado).")
    return valores


def _conninfo(cred):
    return (f"host={cred['PGHOST']} port={cred['PGPORT']} "
            f"dbname={cred['PGDATABASE']} user={cred['PGUSER']} "
            f"password={cred['PGPASSWORD']}")


# ---------------------------------------------------------------------------
# Serializacion segura a JSON (Decimal, fechas, memoryview, etc.)
# ---------------------------------------------------------------------------

def _json_default(o):
    if isinstance(o, decimal.Decimal):
        return str(o)
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, (bytes, bytearray, memoryview)):
        return bytes(o).hex()
    return str(o)


# ---------------------------------------------------------------------------
# 3) Respaldo previo (solo lectura; se ejecuta antes de cualquier escritura)
# ---------------------------------------------------------------------------

def _respaldar_celdas_antiguas(cur):
    respaldo = {
        "generado": datetime.datetime.now().isoformat(),
        "nota": "Respaldo de las filas de LJ_04521/LJ_04522 tomado justo antes de "
                "aplicar la migracion permanente (COMMIT). No contiene credenciales "
                "ni cadenas de conexion.",
        "dim_celda": [],
        "fact_incendio": [],
        "fact_clima": [],
    }

    cur.execute("""
        SELECT celda_id, longitud, latitud, area_km2, epsg,
               ST_AsEWKT(geom) AS geom_ewkt, ST_SRID(geom) AS srid,
               ST_Area(geom) AS area_m2
        FROM dim_celda
        WHERE celda_id = ANY(%s)
        ORDER BY celda_id
    """, (CELDAS_ANTIGUAS,))
    cols = [d.name for d in cur.description]
    respaldo["dim_celda"] = [dict(zip(cols, row)) for row in cur.fetchall()]

    cur.execute("SELECT * FROM fact_incendio WHERE celda_id = ANY(%s) ORDER BY incendio_id",
                (CELDAS_ANTIGUAS,))
    cols = [d.name for d in cur.description]
    respaldo["fact_incendio"] = [dict(zip(cols, row)) for row in cur.fetchall()]

    cur.execute("SELECT * FROM fact_clima WHERE celda_id = ANY(%s) ORDER BY clima_id",
                (CELDAS_ANTIGUAS,))
    cols = [d.name for d in cur.description]
    respaldo["fact_clima"] = [dict(zip(cols, row)) for row in cur.fetchall()]

    EVIDENCIAS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESPALDO_JSON, "w", encoding="utf-8") as f:
        json.dump(respaldo, f, ensure_ascii=False, indent=2, default=_json_default)

    _log(f"Respaldo creado: {RESPALDO_JSON.relative_to(REPO_ROOT.parent)}")
    _log(f"  dim_celda: {len(respaldo['dim_celda'])} fila(s)")
    _log(f"  fact_incendio: {len(respaldo['fact_incendio'])} fila(s)")
    _log(f"  fact_clima: {len(respaldo['fact_clima'])} fila(s)")
    return respaldo


# ---------------------------------------------------------------------------
# 4) Parser de sentencias SQL, respetando bloques DO $$ ... $$
# ---------------------------------------------------------------------------

def _parse_sql_statements(text: str):
    statements = []
    buf = []
    i, n = 0, len(text)
    in_dollar = False
    dollar_tag = None
    while i < n:
        ch = text[i]
        if not in_dollar and text[i:i + 2] == "--":
            j = text.find("\n", i)
            if j == -1:
                break
            i = j + 1
            continue
        if ch == "$":
            j = i + 1
            while j < n and (text[j].isalnum() or text[j] == "_"):
                j += 1
            if j < n and text[j] == "$":
                tag = text[i:j + 1]
                if not in_dollar:
                    in_dollar = True
                    dollar_tag = tag
                    buf.append(tag)
                    i = j + 1
                    continue
                if tag == dollar_tag:
                    in_dollar = False
                    dollar_tag = None
                    buf.append(tag)
                    i = j + 1
                    continue
        if not in_dollar and ch == ";":
            buf.append(ch)
            stmt = "".join(buf).strip()
            if stmt and stmt != ";":
                statements.append(stmt)
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements


def _resumen_accion(stmt: str) -> str:
    head = " ".join(stmt.split()[:3])
    return head


# ---------------------------------------------------------------------------
# 5) Ejecucion de la migracion (una sola transaccion, COMMIT o ROLLBACK)
# ---------------------------------------------------------------------------

def _ejecutar_migracion(cur):
    text = MIGRACION_SQL.read_text(encoding="utf-8")
    statements = _parse_sql_statements(text)

    filas_por_tabla = {}
    ejecutadas = 0
    for stmt in statements:
        upper = stmt.upper().rstrip(";").strip()
        if upper in ("BEGIN", "COMMIT"):
            continue  # la transaccion la controla este script, no el archivo
        cur.execute(stmt)
        ejecutadas += 1
        rowcount = cur.rowcount
        accion = _resumen_accion(stmt)
        if rowcount is not None and rowcount >= 0 and not stmt.upper().startswith("DO"):
            filas_por_tabla[accion] = rowcount
            _log(f"  {accion} -> {rowcount} fila(s) afectada(s)")
        elif stmt.upper().startswith("DO"):
            _log(f"  {accion[:40]}... -> comprobacion superada")
    _log(f"Sentencias ejecutadas dentro de la migracion: {ejecutadas}")
    return filas_por_tabla


# ---------------------------------------------------------------------------
# 6) Verificacion posterior en conexion NUEVA, exclusivamente de lectura
# ---------------------------------------------------------------------------

def _verificar_estado_persistido(conninfo):
    import psycopg

    canton_loja, canton_catamayo, parroquias = construir_limites()
    el_cisne = parroquias["110153"]

    ok = True
    with psycopg.connect(conninfo, autocommit=False) as conn:
        with conn.cursor() as cur:
            _log("\n--- Verificacion posterior (conexion nueva, solo lectura) ---")

            cur.execute("SELECT celda_id FROM dim_celda WHERE celda_id = ANY(%s)", (CELDAS_ANTIGUAS,))
            antiguas = [r[0] for r in cur.fetchall()]
            _log(f"Celdas antiguas ausentes (esperado []): {antiguas}")
            ok &= (antiguas == [])

            cur.execute("SELECT celda_id FROM dim_celda WHERE celda_id = ANY(%s) ORDER BY celda_id",
                        (CELDAS_NUEVAS,))
            nuevas = [r[0] for r in cur.fetchall()]
            _log(f"Celdas nuevas presentes (esperado {list(CELDAS_NUEVAS)}): {nuevas}")
            ok &= (nuevas == list(CELDAS_NUEVAS))

            cur.execute("""
                SELECT fi.incendio_id FROM fact_incendio fi
                LEFT JOIN dim_celda dc ON dc.celda_id = fi.celda_id
                WHERE dc.celda_id IS NULL
            """)
            huerfanos_i = cur.fetchall()
            cur.execute("""
                SELECT fc.celda_id, fc.fecha_id FROM fact_clima fc
                LEFT JOIN dim_celda dc ON dc.celda_id = fc.celda_id
                WHERE dc.celda_id IS NULL
            """)
            huerfanos_c = cur.fetchall()
            _log(f"Huerfanos fact_incendio (esperado []): {huerfanos_i}")
            _log(f"Huerfanos fact_clima (esperado []): {huerfanos_c}")
            ok &= (not huerfanos_i and not huerfanos_c)

            cur.execute("""
                SELECT celda_id, fecha_id, COUNT(*) FROM fact_incendio
                WHERE celda_id = ANY(%s) GROUP BY celda_id, fecha_id HAVING COUNT(*) > 1
            """, (CELDAS_NUEVAS,))
            dup_i = cur.fetchall()
            cur.execute("""
                SELECT celda_id, fecha_id, COUNT(*) FROM fact_clima
                WHERE celda_id = ANY(%s) GROUP BY celda_id, fecha_id HAVING COUNT(*) > 1
            """, (CELDAS_NUEVAS,))
            dup_c = cur.fetchall()
            _log(f"Duplicados fact_incendio (esperado []): {dup_i}")
            _log(f"Duplicados fact_clima (esperado []): {dup_c}")
            ok &= (not dup_i and not dup_c)

            cur.execute("""
                SELECT celda_id, ST_SRID(geom), ST_IsValid(geom), ST_Area(geom)
                FROM dim_celda WHERE celda_id = ANY(%s) ORDER BY celda_id
            """, (CELDAS_NUEVAS,))
            for celda_id, srid, valido, area in cur.fetchall():
                _log(f"{celda_id}: SRID={srid} valido={valido} area_m2={area}")
                ok &= (srid == 32717 and bool(valido) and abs(float(area) - 250000.0) < 0.01)

            for tabla, geom, etiqueta in (
                (canton_loja, "geom_tmp_canton", "canton Loja"),
                (el_cisne, "geom_tmp_parroquia", "parroquia El Cisne"),
            ):
                cur.execute(f"CREATE TEMP TABLE {geom} (g geometry(Polygon,32717)) ON COMMIT DROP")
                cur.execute(f"INSERT INTO {geom} (g) VALUES (ST_GeomFromWKB(%s, 32717))",
                            (tabla.wkb,))
                cur.execute(f"""
                    SELECT dc.celda_id,
                           ST_Within(ST_Centroid(dc.geom), t.g) AS centroide_dentro,
                           ST_Within(dc.geom, t.g) AS poligono_dentro
                    FROM dim_celda dc CROSS JOIN {geom} t
                    WHERE dc.celda_id = ANY(%s) ORDER BY dc.celda_id
                """, (CELDAS_NUEVAS,))
                for celda_id, c_dentro, p_dentro in cur.fetchall():
                    _log(f"{celda_id}: dentro de {etiqueta} (centroide)={c_dentro} "
                         f"(poligono)={p_dentro}")
                    ok &= bool(c_dentro) and bool(p_dentro)

            cur.execute("CREATE TEMP TABLE geom_tmp_dist (g geometry(Polygon,32717)) ON COMMIT DROP")
            cur.execute("INSERT INTO geom_tmp_dist (g) VALUES (ST_GeomFromWKB(%s, 32717))",
                        (canton_loja.wkb,))
            cur.execute("""
                SELECT dc.celda_id, ST_Distance(dc.geom, ST_Boundary(t.g)) AS dist_m
                FROM dim_celda dc CROSS JOIN geom_tmp_dist t
                WHERE dc.celda_id = ANY(%s) ORDER BY dc.celda_id
            """, (CELDAS_NUEVAS,))
            for celda_id, dist in cur.fetchall():
                esperado = DISTANCIAS_ESPERADAS[celda_id]
                diff = abs(float(dist) - esperado)
                _log(f"{celda_id}: distancia al limite = {dist:.2f} m "
                     f"(esperado {esperado:.2f} m, diferencia {diff:.3f} m)")
                ok &= (diff <= TOLERANCIA_DISTANCIA_M)

            consulta_sql = (CONSULTAS_DIR / "consulta_01_incendios_clima_mensual.sql").read_text(encoding="utf-8")
            cur.execute(consulta_sql)
            filas = cur.fetchall()
            cols = [d.name for d in cur.description]
            filas_nuevas = [dict(zip(cols, f)) for f in filas
                             if f[cols.index("celda_id")] in CELDAS_NUEVAS]
            _log(f"Consulta celda-mes: {len(filas_nuevas)} fila(s) para las celdas nuevas "
                 f"(esperado 2)")
            for fila in filas_nuevas:
                _log(f"  {fila}")
            ok &= (len(filas_nuevas) == 2)
            esperado_valores = {
                "LJ_TEST_001": {"frp_total_mw": 18.4, "precipitacion_acumulada_mensual_mm": 12.5},
                "LJ_TEST_002": {"frp_total_mw": 9.7, "precipitacion_acumulada_mensual_mm": 8.7},
            }
            for fila in filas_nuevas:
                esp = esperado_valores.get(fila["celda_id"], {})
                for campo, val_esp in esp.items():
                    val = float(fila[campo])
                    ok &= (abs(val - val_esp) < 0.01)

        conn.rollback()  # ninguna escritura ocurrio; se cierra limpio de todas formas
    return ok


# ---------------------------------------------------------------------------
# Ejecucion principal
# ---------------------------------------------------------------------------

def main():
    import psycopg

    cred = _cargar_credenciales()
    conninfo = _conninfo(cred)

    _log("=" * 78)
    _log("MIGRACION PERMANENTE DE CELDAS CONTROLADAS (COMMIT real)")
    _log("=" * 78)
    _log(f"Conectando a {cred['PGUSER']}@{cred['PGHOST']}:{cred['PGPORT']}/{cred['PGDATABASE']}")

    with psycopg.connect(conninfo, autocommit=False) as conn:
        with conn.cursor() as cur:
            _log("\n--- 1) Respaldo previo ---")
            _respaldar_celdas_antiguas(cur)

            _log("\n--- 2) Ejecucion de la migracion (transaccion unica) ---")
            try:
                filas_por_tabla = _ejecutar_migracion(cur)
            except Exception as exc:
                conn.rollback()
                _log(f"\nFALLO: {type(exc).__name__}: {exc}")
                _log("ROLLBACK ejecutado. No se persistio ningun cambio.")
                return 1

            conn.commit()
            _log("\nCOMMIT ejecutado. La migracion quedo persistida en la base de datos.")
            _log("Resumen de filas afectadas por tabla:")
            for accion, n in filas_por_tabla.items():
                _log(f"  {accion}: {n} fila(s)")

    _log("\n--- 3) Verificacion en conexion nueva (solo lectura) ---")
    ok = _verificar_estado_persistido(conninfo)
    if not ok:
        _log("\nATENCION: una o mas verificaciones posteriores NO se cumplieron. "
             "La migracion ya fue confirmada (COMMIT), revisar manualmente.")
        return 1

    _log("\nTodas las verificaciones posteriores se cumplieron.")
    _log(f"Log completo guardado en: {SALIDA_TXT.relative_to(REPO_ROOT.parent)}")
    return 0


if __name__ == "__main__":
    buf = io.StringIO()
    code = 0
    try:
        with redirect_stdout(buf):
            code = main()
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
    except Exception as exc:
        with redirect_stdout(buf):
            print(f"\nERROR NO CONTROLADO: {type(exc).__name__}: {exc}")
        code = 1
    finally:
        output = buf.getvalue()
        print(output)
        EVIDENCIAS_DIR.mkdir(parents=True, exist_ok=True)
        SALIDA_TXT.write_text(output, encoding="utf-8")
        print(f"\nSalida guardada en: {SALIDA_TXT}")
    sys.exit(code)
