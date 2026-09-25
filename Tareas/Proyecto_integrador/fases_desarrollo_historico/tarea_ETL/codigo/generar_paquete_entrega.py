"""Genera el paquete minimo de revision para la entrega ETL.

Incluye solo los productos y evidencias que el docente necesita observar. No
incluye documentos administrativos, la guia ni los CSV Raw historicos.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


ETL_DIR = Path(__file__).resolve().parents[1]
PROYECTO_DIR = ETL_DIR.parent
NOMBRE_RAIZ = "tarea_ETL"
SALIDA_PREDETERMINADA = ETL_DIR / "FireForest_Tarea_ETL_entrega_completa_2026-09-20.zip"
FECHA_ZIP = (2026, 9, 20, 0, 0, 0)
ANIO_ESTUDIO = 2023
RUTA_MANIFIESTO_CONTROLADO = (
    PROYECTO_DIR / "05_ingesta/metadatos/manifiesto_firelab_loja.json"
)

SUBCONJUNTOS_RAW = {
    "viirs": {
        "origen": PROYECTO_DIR
        / "02_datos/raw/viirs/viirs_evidencia_500m_celda_mes_2019_2025_v1_0_3.csv",
        "destino_raw": "viirs/viirs_evidencia_500m_celda_mes_2023.csv",
    },
    "chirps": {
        "origen": PROYECTO_DIR
        / "02_datos/raw/chirps/chirps_500m_celda_mes_2019_2025.csv",
        "destino_raw": "chirps/chirps_500m_celda_mes_2023.csv",
    },
}


ARCHIVOS_ETL = [
    # Los tres scripts son necesarios: --desde-cero importa los dos primeros.
    "codigo/etl_fireforest.py",
    "codigo/evaluar_calidad_raw.py",
    "codigo/perfilar_fuentes.py",
    # Parametros, reglas y dependencias del flujo.
    "configuracion/perfilado.json",
    "configuracion/reglas_calidad.json",
    "configuracion/requirements_etl.txt",
    "configuracion/transformaciones_clean.json",
    # Productos Clean observables en CSV.
    "clean/malla_500m.csv",
    "clean/viirs_2023.csv",
    "clean/chirps_2023.csv",
    "clean/observaciones_viirs_sin_cobertura_2023.csv",
    "clean/rechazos_criticos_2023.csv",
    # Dataset analitico y diccionario.
    "curated/fireforest_celda_mes_2023.csv",
    "curated/diccionario_datos.csv",
    # Evidencias exigidas por la guia y la rubrica.
    "evidencias/perfilado_columnas.csv",
    "evidencias/perfilado_claves_relaciones.csv",
    "evidencias/estadisticas_atipicos.csv",
    "evidencias/matriz_calidad.csv",
    "evidencias/comparacion_antes_despues.csv",
    "evidencias/controles_clean.csv",
    "evidencias/controles_curated.csv",
    "evidencias/bitacora_decisiones.csv",
    "evidencias/prueba_reproducibilidad_flujo_completo.txt",
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
    datos = json.loads(RUTA_MANIFIESTO_CONTROLADO.read_text(encoding="utf-8"))
    registro = next(item for item in datos["archivos"] if item["fuente"] == "malla")
    ruta = PROYECTO_DIR / "02_datos/raw" / registro["destino_relativo_a_02_datos_raw"]
    hash_real = sha256(ruta)
    if hash_real != registro["sha256"]:
        raise ValueError("La malla GeoPackage no coincide con el manifiesto de procedencia")
    return ruta, hash_real


def crear_subconjunto_raw(
    fuente: str, origen: Path, destino: Path, hash_fuente_esperado: str
) -> dict[str, Any]:
    if sha256(origen) != hash_fuente_esperado:
        raise ValueError(f"La fuente controlada completa no coincide: {origen}")

    destino.parent.mkdir(parents=True, exist_ok=True)
    filas = 0
    claves: set[tuple[str, str, str]] = set()
    with origen.open("r", encoding="utf-8-sig", newline="") as entrada, destino.open(
        "w", encoding="utf-8-sig", newline=""
    ) as salida:
        lector = csv.DictReader(entrada)
        columnas = lector.fieldnames or []
        requeridas = {"cell_index", "anio", "mes"}
        if not requeridas.issubset(columnas):
            raise ValueError(f"{fuente}: faltan columnas {sorted(requeridas - set(columnas))}")
        escritor = csv.DictWriter(
            salida, fieldnames=columnas, extrasaction="raise", lineterminator="\n"
        )
        escritor.writeheader()
        for fila in lector:
            if int(fila["anio"]) != ANIO_ESTUDIO:
                continue
            clave = (fila["cell_index"], fila["anio"], fila["mes"])
            if clave in claves:
                raise ValueError(f"{fuente}: clave Raw duplicada {clave}")
            claves.add(clave)
            escritor.writerow(fila)
            filas += 1

    if filas != 95_964:
        raise ValueError(f"{fuente}: se esperaban 95.964 filas Raw y se obtuvieron {filas}")
    return {
        "fuente": fuente,
        "ruta": destino,
        "destino_raw": SUBCONJUNTOS_RAW[fuente]["destino_raw"],
        "filas": filas,
        "columnas": len(columnas),
        "tamano_bytes": destino.stat().st_size,
        "sha256": sha256(destino),
        "sha256_fuente_completa": hash_fuente_esperado,
    }


def crear_configuracion_paquete(directorio_temporal: Path) -> Path:
    configuracion = json.loads(
        (ETL_DIR / "configuracion/perfilado.json").read_text(encoding="utf-8")
    )
    configuracion["fuentes"]["malla"]["ruta"] = (
        "raw/malla/malla_500m_loja_maestra.gpkg"
    )
    for fuente, datos in SUBCONJUNTOS_RAW.items():
        configuracion["fuentes"][fuente]["ruta"] = "raw/" + datos["destino_raw"]
    destino = directorio_temporal / "perfilado.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(configuracion, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return destino


def crear_manifiesto_paquete(
    directorio_temporal: Path,
    subconjuntos: dict[str, dict[str, Any]],
) -> Path:
    original = json.loads(RUTA_MANIFIESTO_CONTROLADO.read_text(encoding="utf-8"))
    por_fuente = {entrada["fuente"]: entrada for entrada in original["archivos"]}
    archivos = [dict(por_fuente["malla"], periodo="no aplica")]
    for fuente in ("viirs", "chirps"):
        base = por_fuente[fuente]
        derivado = subconjuntos[fuente]
        archivos.append(
            {
                "fuente": fuente,
                "uso": base["uso"],
                "origen_relativo_a_FIRELAB_Loja": base[
                    "origen_relativo_a_FIRELAB_Loja"
                ],
                "destino_relativo_a_02_datos_raw": derivado["destino_raw"],
                "periodo": str(ANIO_ESTUDIO),
                "filas": derivado["filas"],
                "tamano_bytes": derivado["tamano_bytes"],
                "sha256": derivado["sha256"],
                "derivacion": f"Seleccion exacta de filas con anio == {ANIO_ESTUDIO}",
                "sha256_fuente_completa": derivado["sha256_fuente_completa"],
                "modificado_origen_utc": base["modificado_origen_utc"],
            }
        )
    manifiesto = {
        "descripcion": (
            "Procedencia de la malla y de los subconjuntos Raw 2023 incluidos "
            "en el paquete ejecutable de FireForest."
        ),
        "verificado_utc": original["verificado_utc"],
        "archivos": archivos,
    }
    destino = directorio_temporal / "manifiesto_firelab_loja.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return destino


def generar_perfilado_paquete(tarea_temporal: Path) -> dict[str, Path]:
    codigo = tarea_temporal / "codigo"
    evidencias = tarea_temporal / "evidencias"
    codigo.mkdir(parents=True, exist_ok=True)
    evidencias.mkdir(parents=True, exist_ok=True)
    script = codigo / "perfilar_fuentes.py"
    shutil.copy2(ETL_DIR / "codigo/perfilar_fuentes.py", script)
    proceso = subprocess.run(
        [sys.executable, str(script)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proceso.returncode != 0:
        raise RuntimeError(
            "No se pudo generar el perfilado del paquete:\n"
            + proceso.stdout
            + proceso.stderr
        )
    return {
        "evidencias/perfilado_columnas.csv": evidencias / "perfilado_columnas.csv",
        "evidencias/perfilado_claves_relaciones.csv": (
            evidencias / "perfilado_claves_relaciones.csv"
        ),
    }


def archivos_para_paquete(
    malla: Path,
    subconjuntos: dict[str, dict[str, Any]],
    configuracion_paquete: Path,
    manifiesto_paquete: Path,
    perfilado_paquete: dict[str, Path],
) -> list[tuple[Path, str]]:
    seleccion: dict[str, Path] = {}
    for relativa in ARCHIVOS_ETL:
        ruta = (
            configuracion_paquete
            if relativa == "configuracion/perfilado.json"
            else perfilado_paquete.get(relativa, ETL_DIR / relativa)
        )
        seleccion[relativa] = ruta

    seleccion["raw/malla/malla_500m_loja_maestra.gpkg"] = malla
    for fuente in ("viirs", "chirps"):
        seleccion["raw/" + subconjuntos[fuente]["destino_raw"]] = subconjuntos[
            fuente
        ]["ruta"]
    seleccion["raw/metadatos/manifiesto_firelab_loja.json"] = manifiesto_paquete
    return [(ruta, relativa) for relativa, ruta in sorted(seleccion.items())]


def texto_readme(
    resultados: dict[str, dict[str, int]],
    hash_malla: str,
    subconjuntos: dict[str, dict[str, Any]],
) -> str:
    return rf"""# Tarea ETL - FireForest

## Objetivo y alcance

Construir un flujo ETL reproducible que integre la malla espacial, la evidencia
mensual de incendios VIIRS y la precipitacion CHIRPS para estudiar su relacion
en el canton Loja durante 2023. La poblacion comprende 7.997 celdas de 500 m x
500 m observadas durante 12 meses. La unidad final es una celda-mes y su clave
es `cell_id + anio + mes`.

El flujo conserva Raw, estandariza cada fuente en Clean y realiza una union uno
a uno por `cell_index + anio + mes` para construir Curated.

## Contenido ejecutable de la entrega

- `raw/`: malla, subconjuntos VIIRS/CHIRPS 2023 y manifiesto.
- `clean/`: bases limpias ya generadas, fuentes tipadas y excepciones.
- `curated/`: dataset final ya generado y diccionario.
- `codigo/`: los tres scripts del flujo completo.
- `configuracion/`: parametros y dependencias.
- `evidencias/`: pruebas exigidas por la guia.

`raw/` contiene las entradas sin transformar. `clean/` contiene las bases
resultantes despues de aplicar las reglas de limpieza. Ambas capas ya vienen
incluidas y pueden revisarse sin ejecutar ningun comando.

## Fuentes Raw y procedencia

El paquete incluye la malla completa y las 95.964 filas Raw de 2023 de cada
fuente mensual. No duplica los historicos 2019-2025. Los subconjuntos conservan
las columnas y valores originales; solo aplican el filtro `anio == 2023`.

- VIIRS Raw 2023: {entero_es(subconjuntos['viirs']['filas'])} filas, SHA-256
  `{subconjuntos['viirs']['sha256']}`.
- CHIRPS Raw 2023: {entero_es(subconjuntos['chirps']['filas'])} filas, SHA-256
  `{subconjuntos['chirps']['sha256']}`.

La procedencia, el hash de cada fuente historica y el hash de cada subconjunto
se registran en `raw/metadatos/manifiesto_firelab_loja.json`.

## Reproduccion opcional

No es necesario ejecutar el ETL para revisar la entrega. Si se desea comprobar
que los resultados pueden regenerarse, abra una terminal en la carpeta donde
se extrajo el ZIP y ejecute:

```powershell
cd tarea_ETL
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r configuracion\requirements_etl.txt
.venv\Scripts\python.exe codigo\etl_fireforest.py --desde-cero
```

`etl_fireforest.py --desde-cero` ejecuta en orden
`perfilar_fuentes.py`, `evaluar_calidad_raw.py` y la construccion de Clean y
Curated. Una regla critica detiene el flujo; los registros no aptos se separan
o se conservan con una bandera explicita.

## Transformaciones e integracion

1. Seleccion reproducible del periodo 2023.
2. Tipado de identificadores, numeros, fechas y booleanos.
3. Normalizacion espacial mediante `cell_index` y `cell_id`.
4. Banderas de cobertura y aptitud analitica.
5. Calculo de la fraccion de dias humedos.
6. Marcado IQR de valores atipicos sin eliminarlos.

La integracion valida una cardinalidad uno a uno antes de unir VIIRS y CHIRPS.
Se conservan las claves esperadas y los faltantes VIIRS no se convierten en
cero.

## Resultados y controles

- Malla CSV: {entero_es(resultados['clean/malla_500m.csv']['filas'])} filas.
- VIIRS Clean: {entero_es(resultados['clean/viirs_2023.csv']['filas'])} filas.
- CHIRPS Clean: {entero_es(resultados['clean/chirps_2023.csv']['filas'])} filas.
- Curated: {entero_es(resultados['curated/fireforest_celda_mes_2023.csv']['filas'])} filas.
- 95.064 filas aptas para analisis y 900 sin observacion VIIRS.
- 16 controles Clean y 11 controles Curated cumplidos.
- Cero duplicados en la clave final.
- SHA-256 de la malla GeoPackage: `{hash_malla}`.

La evidencia se concentra en nueve archivos: perfilado de columnas y claves,
estadisticas de atipicos, matriz de calidad, comparacion antes y despues,
controles Clean y Curated, bitacora de decisiones y prueba de reproducibilidad.

## Conclusiones y limitaciones

- La union conserva 95.964 observaciones celda-mes sin multiplicar registros.
- Los valores atipicos se marcan y conservan porque pueden representar eventos
  ambientales reales.
- Las 900 filas sin VIIRS permanecen como nulas y no se interpretan como
  ausencia de incendio.
- VIIRS y CHIRPS llegan agregados por mes; no permiten reconstruir eventos
  diarios ni establecer causalidad entre lluvia y fuego.
"""


def crear_paquete(salida: Path) -> None:
    resultados = validar_productos()
    malla, hash_malla = validar_malla()

    salida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f"{salida.stem}_", suffix=".tmp", dir=salida.parent, delete=False
    ) as temporal:
        ruta_temporal = Path(temporal.name)

    try:
        with tempfile.TemporaryDirectory(
            prefix="paquete_raw_2023_", dir=ETL_DIR
        ) as temporal_raw:
            directorio_temporal = Path(temporal_raw)
            tarea_temporal = directorio_temporal / "tarea_ETL"
            manifiesto_original = json.loads(
                RUTA_MANIFIESTO_CONTROLADO.read_text(encoding="utf-8")
            )
            manifiesto_por_fuente = {
                entrada["fuente"]: entrada
                for entrada in manifiesto_original["archivos"]
            }
            subconjuntos: dict[str, dict[str, Any]] = {}
            for fuente, datos in SUBCONJUNTOS_RAW.items():
                destino = tarea_temporal / "raw" / datos["destino_raw"]
                subconjuntos[fuente] = crear_subconjunto_raw(
                    fuente,
                    datos["origen"],
                    destino,
                    manifiesto_por_fuente[fuente]["sha256"],
                )

            malla_temporal = (
                tarea_temporal / "raw/malla/malla_500m_loja_maestra.gpkg"
            )
            malla_temporal.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(malla, malla_temporal)

            configuracion_paquete = crear_configuracion_paquete(
                tarea_temporal / "configuracion"
            )
            manifiesto_paquete = crear_manifiesto_paquete(
                tarea_temporal / "raw/metadatos", subconjuntos
            )
            perfilado_paquete = generar_perfilado_paquete(tarea_temporal)
            archivos = archivos_para_paquete(
                malla_temporal,
                subconjuntos,
                configuracion_paquete,
                manifiesto_paquete,
                perfilado_paquete,
            )

            with zipfile.ZipFile(
                ruta_temporal, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
            ) as paquete:
                readme = texto_readme(
                    resultados, hash_malla, subconjuntos
                ).encode("utf-8")
                escribir_bytes(
                    paquete,
                    f"{NOMBRE_RAIZ}/README.md",
                    readme,
                )

                for ruta, relativa in archivos:
                    if not ruta.exists():
                        raise FileNotFoundError(f"Falta el archivo requerido: {ruta}")
                    destino = f"{NOMBRE_RAIZ}/{relativa}"
                    escribir_archivo(paquete, destino, ruta)
            os.replace(ruta_temporal, salida)
    finally:
        ruta_temporal.unlink(missing_ok=True)

    print(f"Paquete creado: {salida}")
    print(f"Archivos incluidos: {len(archivos) + 1}")
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
