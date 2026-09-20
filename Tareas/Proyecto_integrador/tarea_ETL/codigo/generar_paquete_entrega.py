"""Genera el paquete autocontenido de revision para la entrega ETL.

El paquete incluye los productos Clean y Curated de 2023 y la copia controlada
de la malla GeoPackage. No incluye los CSV Raw historicos de VIIRS y CHIRPS.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path


ETL_DIR = Path(__file__).resolve().parents[1]
PROYECTO_DIR = ETL_DIR.parent
NOMBRE_RAIZ = "FireForest_Tarea_ETL_entrega_completa"
SALIDA_PREDETERMINADA = ETL_DIR / "FireForest_Tarea_ETL_entrega_completa_2026-09-20.zip"
FECHA_ZIP = (2026, 9, 20, 0, 0, 0)


ARCHIVOS_ETL = [
    "README.md",
    "ENTREGA_PROFESOR.md",
    "Guia_Tarea_ETL_Calidad_Integracion_1_5_puntos.pdf",
]

PATRONES_ETL = [
    "codigo/*.py",
    "configuracion/*",
    "clean/*",
    "curated/*",
    "evidencias/*",
]


def sha256(ruta: Path) -> str:
    resumen = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            resumen.update(bloque)
    return resumen.hexdigest()


def entero_es(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def escribir_bytes(paquete: zipfile.ZipFile, destino: str, contenido: bytes) -> None:
    info = zipfile.ZipInfo(destino, FECHA_ZIP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    paquete.writestr(info, contenido, compresslevel=9)


def escribir_archivo(paquete: zipfile.ZipFile, destino: str, origen: Path) -> None:
    info = zipfile.ZipInfo(destino, FECHA_ZIP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    with origen.open("rb") as entrada, paquete.open(info, "w", force_zip64=True) as salida:
        shutil.copyfileobj(entrada, salida, length=1024 * 1024)


def contar_csv(ruta: Path, clave: tuple[str, ...]) -> tuple[int, int]:
    filas = 0
    valores_clave: set[tuple[str, ...]] = set()
    with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        columnas = lector.fieldnames or []
        faltantes = [columna for columna in clave if columna not in columnas]
        if faltantes:
            raise ValueError(f"{ruta.name}: faltan columnas clave {faltantes}")
        for fila in lector:
            filas += 1
            valor = tuple(fila[columna] for columna in clave)
            if valor in valores_clave:
                raise ValueError(f"{ruta.name}: clave duplicada {valor}")
            valores_clave.add(valor)
    return filas, len(columnas)


def validar_productos() -> dict[str, dict[str, int]]:
    controles = {
        "clean/malla_500m.csv": (("cell_id",), 7_997),
        "clean/viirs_2023.csv": (("cell_index", "anio", "mes"), 95_964),
        "clean/chirps_2023.csv": (("cell_index", "anio", "mes"), 95_964),
        "curated/fireforest_celda_mes_2023.csv": (
            ("cell_id", "anio", "mes"),
            95_964,
        ),
    }
    resultados: dict[str, dict[str, int]] = {}
    for relativa, (clave, filas_esperadas) in controles.items():
        ruta = ETL_DIR / relativa
        filas, columnas = contar_csv(ruta, clave)
        if filas != filas_esperadas:
            raise ValueError(
                f"{relativa}: se esperaban {filas_esperadas} filas y se encontraron {filas}"
            )
        resultados[relativa] = {"filas": filas, "columnas": columnas}
    return resultados


def validar_malla() -> tuple[Path, str]:
    manifiesto = PROYECTO_DIR / "05_ingesta/metadatos/manifiesto_firelab_loja.json"
    datos = json.loads(manifiesto.read_text(encoding="utf-8"))
    registro = next(item for item in datos["archivos"] if item["fuente"] == "malla")
    ruta = PROYECTO_DIR / "02_datos/raw" / registro["destino_relativo_a_02_datos_raw"]
    hash_real = sha256(ruta)
    if hash_real != registro["sha256"]:
        raise ValueError("La malla GeoPackage no coincide con el manifiesto de procedencia")
    return ruta, hash_real


def archivos_para_paquete(malla: Path) -> list[tuple[Path, str]]:
    seleccion: dict[str, Path] = {}
    for relativa in ARCHIVOS_ETL:
        ruta = ETL_DIR / relativa
        seleccion[relativa] = ruta
    for patron in PATRONES_ETL:
        for ruta in ETL_DIR.glob(patron):
            if ruta.is_file() and ruta.suffix.lower() != ".zip":
                relativa = ruta.relative_to(ETL_DIR).as_posix()
                seleccion[relativa] = ruta

    seleccion["raw/malla/malla_500m_loja_maestra.gpkg"] = malla
    seleccion["raw/metadatos/manifiesto_firelab_loja.json"] = (
        PROYECTO_DIR / "05_ingesta/metadatos/manifiesto_firelab_loja.json"
    )
    return [(ruta, relativa) for relativa, ruta in sorted(seleccion.items())]


def texto_leeme(resultados: dict[str, dict[str, int]], hash_malla: str) -> str:
    return f"""# LEEME PRIMERO

Este paquete permite revisar la entrega ETL de FireForest sin depender de las
carpetas locales del equipo.

## Archivos principales

- `raw/malla/malla_500m_loja_maestra.gpkg`: geometria de 7.997 celdas.
- `clean/malla_500m.csv`: atributos tabulares de la malla.
- `clean/viirs_2023.csv`: VIIRS Clean de 2023.
- `clean/chirps_2023.csv`: CHIRPS Clean de 2023.
- `curated/fireforest_celda_mes_2023.csv`: dataset analitico integrado.
- `curated/diccionario_datos.csv`: definicion de las variables.

Los mismos productos tambien se incluyen en Parquet cuando existe esa salida.

## Verificaciones realizadas antes de crear el ZIP

- Malla CSV: {entero_es(resultados['clean/malla_500m.csv']['filas'])} filas.
- VIIRS Clean: {entero_es(resultados['clean/viirs_2023.csv']['filas'])} filas.
- CHIRPS Clean: {entero_es(resultados['clean/chirps_2023.csv']['filas'])} filas.
- Curated: {entero_es(resultados['curated/fireforest_celda_mes_2023.csv']['filas'])} filas.
- No existen claves duplicadas en los cuatro productos anteriores.
- SHA-256 de la malla GeoPackage: `{hash_malla}`.

## Alcance de Raw

Los CSV Raw historicos 2019-2025 de VIIRS y CHIRPS no se duplican en este ZIP.
El paquete contiene sus productos Clean de 2023, el dataset Curated y las
evidencias necesarias para evaluarlos. La procedencia y los hashes de los Raw
se documentan en `raw/metadatos/manifiesto_firelab_loja.json`.

Por esta razon, el ZIP es autocontenido para revision y analisis de los
resultados, pero la reproduccion desde Raw requiere acceso controlado a las
fuentes originales descritas en el manifiesto.
"""


def crear_paquete(salida: Path) -> None:
    resultados = validar_productos()
    malla, hash_malla = validar_malla()
    archivos = archivos_para_paquete(malla)

    salida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f"{salida.stem}_", suffix=".tmp", dir=salida.parent, delete=False
    ) as temporal:
        ruta_temporal = Path(temporal.name)

    try:
        sumas: list[str] = []
        with zipfile.ZipFile(
            ruta_temporal, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as paquete:
            leeme = texto_leeme(resultados, hash_malla).encode("utf-8")
            escribir_bytes(paquete, f"{NOMBRE_RAIZ}/LEEME_PRIMERO.md", leeme)
            sumas.append(f"{hashlib.sha256(leeme).hexdigest()}  LEEME_PRIMERO.md")

            for ruta, relativa in archivos:
                if not ruta.exists():
                    raise FileNotFoundError(f"Falta el archivo requerido: {ruta}")
                destino = f"{NOMBRE_RAIZ}/{relativa}"
                escribir_archivo(paquete, destino, ruta)
                sumas.append(f"{sha256(ruta)}  {relativa}")

            escribir_bytes(
                paquete,
                f"{NOMBRE_RAIZ}/SHA256SUMS.txt",
                ("\n".join(sumas) + "\n").encode("utf-8"),
            )
        os.replace(ruta_temporal, salida)
    finally:
        ruta_temporal.unlink(missing_ok=True)

    print(f"Paquete creado: {salida}")
    print(f"Archivos incluidos: {len(archivos) + 2}")
    print(f"Tamano: {salida.stat().st_size / (1024 * 1024):.2f} MB")
    print(f"SHA-256: {sha256(salida)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--salida",
        type=Path,
        default=SALIDA_PREDETERMINADA,
        help="Ruta del ZIP de salida",
    )
    argumentos = parser.parse_args()
    crear_paquete(argumentos.salida.resolve())


if __name__ == "__main__":
    main()
