"""Crea la base 'fireforest' (si no existe) y aplica schema.sql + datos_ejemplo.sql.

Requiere un archivo .env en la raiz de FireForest (ver .env.example, compartido
con el resto del repositorio) con las variables PGHOST, PGPORT, PGDATABASE,
PGUSER, PGPASSWORD. Ejecutable desde cualquier directorio.
"""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

RUTA_SCRIPT = Path(__file__).resolve()
RAIZ_FIREFOREST = RUTA_SCRIPT.parents[4]

load_dotenv(RAIZ_FIREFOREST / ".env")

PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = os.getenv("PGPORT", "5432")
PGDATABASE = os.getenv("PGDATABASE", "fireforest")
PGUSER = os.getenv("PGUSER", "postgres")
PGPASSWORD = os.getenv("PGPASSWORD", "")

SCHEMA_SQL = RUTA_SCRIPT.parent / "schema.sql"
DATOS_SQL = RUTA_SCRIPT.parent / "datos_ejemplo.sql"


def crear_base_si_no_existe():
    conexion = psycopg.connect(
        host=PGHOST, port=PGPORT, dbname="postgres",
        user=PGUSER, password=PGPASSWORD, autocommit=True,
    )
    with conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (PGDATABASE,)
            )
            if cursor.fetchone() is None:
                cursor.execute(f'CREATE DATABASE "{PGDATABASE}"')
                print(f"Base '{PGDATABASE}' creada.")
            else:
                print(f"Base '{PGDATABASE}' ya existe.")


def aplicar_sql(conexion, archivo: Path):
    with conexion.cursor() as cursor:
        cursor.execute(archivo.read_text(encoding="utf-8"))
    conexion.commit()
    print(f"Aplicado: {archivo}")


def main():
    crear_base_si_no_existe()

    conexion = psycopg.connect(
        host=PGHOST, port=PGPORT, dbname=PGDATABASE,
        user=PGUSER, password=PGPASSWORD,
    )
    with conexion:
        aplicar_sql(conexion, SCHEMA_SQL)
        aplicar_sql(conexion, DATOS_SQL)

    with psycopg.connect(
        host=PGHOST, port=PGPORT, dbname=PGDATABASE,
        user=PGUSER, password=PGPASSWORD,
    ) as conexion, conexion.cursor() as cursor:
        for tabla in ("dim_celda", "dim_fecha", "fact_incendio", "fact_clima"):
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            print(f"{tabla}: {cursor.fetchone()[0]} filas")


if __name__ == "__main__":
    main()
