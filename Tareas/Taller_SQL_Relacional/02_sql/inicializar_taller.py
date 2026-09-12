"""Crea/reinicializa la base 'taller_sql_fireforest' y ejecuta schema + datos + consultas.

Reutiliza el host/usuario/password de PostgreSQL ya configurado en el .env de la
raiz de FireForest (mismo servidor local), pero usa una base de datos propia e
independiente ('taller_sql_fireforest'), sin tocar la base 'fireforest' del
Proyecto Integrador. Practica independiente: Taller SQL (Practica 2, M1721).
"""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent   # Taller_SQL_Relacional/
ROOT_ENV = BASE_DIR.parent.parent / ".env"           # FireForest/.env (compartido: host/usuario)

load_dotenv(dotenv_path=ROOT_ENV)

PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = os.getenv("PGPORT", "5432")
PGUSER = os.getenv("PGUSER", "postgres")
PGPASSWORD = os.getenv("PGPASSWORD", "")

TALLER_DB = "taller_sql_fireforest"   # base independiente de "fireforest"

SCHEMA_SQL = BASE_DIR / "02_sql" / "schema.sql"
DATOS_SQL = BASE_DIR / "03_datos" / "datos_ejemplo.sql"
CONSULTAS_DIR = BASE_DIR / "04_consultas"
RESULTADOS_MD = BASE_DIR / "05_resultados" / "resultados_consultas.md"
VALIDACIONES_MD = BASE_DIR / "05_resultados" / "validaciones.md"


def conectar(dbname, autocommit=False):
    return psycopg.connect(
        host=PGHOST, port=PGPORT, dbname=dbname,
        user=PGUSER, password=PGPASSWORD, autocommit=autocommit,
    )


def reinicializar_base():
    with conectar("postgres", autocommit=True) as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid();",
                (TALLER_DB,),
            )
            cursor.execute(f'DROP DATABASE IF EXISTS "{TALLER_DB}"')
            cursor.execute(f'CREATE DATABASE "{TALLER_DB}"')
    print(f"Base '{TALLER_DB}' (re)creada desde cero.")


def ejecutar_archivo(conexion, archivo: Path):
    with conexion.cursor() as cursor:
        cursor.execute(archivo.read_text(encoding="utf-8"))
    conexion.commit()
    print(f"Ejecutado: {archivo.relative_to(BASE_DIR)}")


def formatear_tabla(columnas, filas):
    if not filas:
        return "_(sin filas)_\n"
    encabezado = "| " + " | ".join(columnas) + " |"
    separador = "|" + "|".join(["---"] * len(columnas)) + "|"
    cuerpo = "\n".join(
        "| " + " | ".join("" if v is None else str(v) for v in fila) + " |"
        for fila in filas
    )
    return f"{encabezado}\n{separador}\n{cuerpo}\n"


def ejecutar_consultas_y_guardar():
    archivos = sorted(CONSULTAS_DIR.glob("*.sql"))
    partes = ["# Resultados de las consultas — Taller SQL (Practica 2, M1721)\n"]
    with conectar(TALLER_DB) as conexion:
        for archivo in archivos:
            sql = archivo.read_text(encoding="utf-8")
            with conexion.cursor() as cursor:
                cursor.execute(sql)
                columnas = [d.name for d in cursor.description]
                filas = cursor.fetchall()
            partes.append(f"## {archivo.name}\n")
            partes.append(f"```sql\n{sql.strip()}\n```\n")
            partes.append(f"**Filas devueltas:** {len(filas)}\n")
            partes.append(formatear_tabla(columnas, filas))
    RESULTADOS_MD.parent.mkdir(parents=True, exist_ok=True)
    RESULTADOS_MD.write_text("\n".join(partes), encoding="utf-8")
    print(f"Resultados guardados en {RESULTADOS_MD.relative_to(BASE_DIR)}")


def validar():
    lineas = ["# Validaciones — Taller SQL (Practica 2, M1721)\n"]
    with conectar(TALLER_DB) as conexion:
        with conexion.cursor() as cursor:
            # 1) Conteo de filas por tabla
            lineas.append("## Conteo de filas por tabla\n")
            for tabla in (
                "dim_celda", "dim_fecha", "dim_cobertura_vegetal",
                "celda_cobertura", "fact_incendio", "fact_clima",
            ):
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                total = cursor.fetchone()[0]
                lineas.append(f"- `{tabla}`: {total} filas")

            # 2) PK sin duplicados (por construccion de PostgreSQL, se confirma
            #    contando filas distintas vs totales en cada clave)
            lineas.append("\n## PK sin duplicados\n")
            cursor.execute(
                "SELECT COUNT(*) = COUNT(DISTINCT incendio_id) FROM fact_incendio"
            )
            lineas.append(f"- `fact_incendio.incendio_id` unico: {cursor.fetchone()[0]}")
            cursor.execute(
                "SELECT COUNT(*) = COUNT(DISTINCT clima_id) FROM fact_clima"
            )
            lineas.append(f"- `fact_clima.clima_id` unico: {cursor.fetchone()[0]}")

            # 3) FK validas (todo celda_id/fecha_id referenciado existe)
            lineas.append("\n## Integridad referencial (FK)\n")
            cursor.execute(
                "SELECT COUNT(*) FROM fact_incendio fi "
                "LEFT JOIN dim_celda dc ON dc.celda_id = fi.celda_id "
                "WHERE dc.celda_id IS NULL"
            )
            lineas.append(f"- `fact_incendio` con celda inexistente: {cursor.fetchone()[0]} (debe ser 0)")
            cursor.execute(
                "SELECT COUNT(*) FROM fact_clima fc "
                "LEFT JOIN dim_fecha df ON df.fecha_id = fc.fecha_id "
                "WHERE df.fecha_id IS NULL"
            )
            lineas.append(f"- `fact_clima` con fecha inexistente: {cursor.fetchone()[0]} (debe ser 0)")

            # 4) UNIQUE (celda_id, fecha_id) respetado
            lineas.append("\n## UNIQUE(celda_id, fecha_id)\n")
            cursor.execute(
                "SELECT celda_id, fecha_id, COUNT(*) FROM fact_incendio "
                "GROUP BY celda_id, fecha_id HAVING COUNT(*) > 1"
            )
            lineas.append(f"- Duplicados logicos en `fact_incendio`: {len(cursor.fetchall())} (debe ser 0)")

            # 5) Coherencia de valores
            lineas.append("\n## Coherencia de valores\n")
            cursor.execute("SELECT COUNT(*) FROM fact_clima WHERE precipitacion_diaria_mm < 0")
            lineas.append(f"- Precipitaciones negativas: {cursor.fetchone()[0]} (debe ser 0)")
            cursor.execute("SELECT COUNT(*) FROM fact_incendio WHERE frp_maxima_mw < 0")
            lineas.append(f"- FRP negativos: {cursor.fetchone()[0]} (debe ser 0)")
            cursor.execute(
                "SELECT celda_id, anio, SUM(porcentaje_cobertura) FROM celda_cobertura "
                "GROUP BY celda_id, anio HAVING SUM(porcentaje_cobertura) > 100"
            )
            excedidos = cursor.fetchall()
            lineas.append(f"- Celdas con cobertura > 100% en un anio: {len(excedidos)} (debe ser 0) {excedidos if excedidos else ''}")

        # 6) CHECK rechaza valores no permitidos (se prueba en una transaccion
        #    que se revierte, para no dejar la base en estado invalido)
        lineas.append("\n## CHECK rechaza valores no permitidos\n")
        pruebas = [
            ("mes fuera de rango (13)",
             "INSERT INTO dim_fecha (fecha_id, fecha, anio, mes) VALUES (20240101, '2024-01-01', 2024, 13)"),
            ("precipitacion negativa",
             "INSERT INTO fact_clima (celda_id, fecha_id, precipitacion_diaria_mm) VALUES ('LJ_001', 20230705, -5)"),
            ("porcentaje de cobertura > 100",
             "INSERT INTO celda_cobertura (celda_id, cobertura_id, anio, porcentaje_cobertura) VALUES ('LJ_001', 1, 2099, 150)"),
        ]
        for descripcion, sentencia in pruebas:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(sentencia)
                conexion.rollback()
                lineas.append(f"- {descripcion}: **NO fue rechazado (revisar CHECK)**")
            except psycopg.errors.CheckViolation:
                conexion.rollback()
                lineas.append(f"- {descripcion}: rechazado correctamente por CHECK")

    VALIDACIONES_MD.parent.mkdir(parents=True, exist_ok=True)
    VALIDACIONES_MD.write_text("\n".join(lineas), encoding="utf-8")
    print(f"Validaciones guardadas en {VALIDACIONES_MD.relative_to(BASE_DIR)}")


def main():
    reinicializar_base()
    with conectar(TALLER_DB) as conexion:
        ejecutar_archivo(conexion, SCHEMA_SQL)
        ejecutar_archivo(conexion, DATOS_SQL)
    ejecutar_consultas_y_guardar()
    validar()


if __name__ == "__main__":
    main()
