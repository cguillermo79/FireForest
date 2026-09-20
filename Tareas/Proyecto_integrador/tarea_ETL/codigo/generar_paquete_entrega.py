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
import tempfile
import zipfile
from pathlib import Path


ETL_DIR = Path(__file__).resolve().parents[1]
PROYECTO_DIR = ETL_DIR.parent
NOMBRE_RAIZ = "FireForest_Tarea_ETL_entrega_completa"
SALIDA_PREDETERMINADA = ETL_DIR / "FireForest_Tarea_ETL_entrega_completa_2026-09-20.zip"
FECHA_ZIP = (2026, 9, 20, 0, 0, 0)


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

    seleccion["raw/malla/malla_500m_loja_maestra.gpkg"] = malla
    seleccion["raw/metadatos/manifiesto_firelab_loja.json"] = (
        PROYECTO_DIR / "05_ingesta/metadatos/manifiesto_firelab_loja.json"
    )
    return [(ruta, relativa) for relativa, ruta in sorted(seleccion.items())]


def texto_readme(resultados: dict[str, dict[str, int]], hash_malla: str) -> str:
    return rf"""# Tarea ETL - FireForest

## Objetivo y alcance

Construir un flujo ETL reproducible que integre la malla espacial, la evidencia
mensual de incendios VIIRS y la precipitacion CHIRPS para estudiar su relacion
en el canton Loja durante 2023. La poblacion comprende 7.997 celdas de 500 m x
500 m observadas durante 12 meses. La unidad final es una celda-mes y su clave
es `cell_id + anio + mes`.

El flujo conserva Raw, estandariza cada fuente en Clean y realiza una union uno
a uno por `cell_index + anio + mes` para construir Curated.

## Contenido de la entrega

- `raw/malla/malla_500m_loja_maestra.gpkg`: geometria de 7.997 celdas.
- `clean/`: fuentes 2023 tipadas, excepciones y rechazos.
- `curated/fireforest_celda_mes_2023.csv`: dataset integrado de 45 variables.
- `curated/diccionario_datos.csv`: significado, tipo, unidad y derivacion.
- `codigo/`: scripts del perfilado, calidad y ETL completo.
- `configuracion/`: parametros, reglas, transformaciones y dependencias.
- `evidencias/`: diagnostico, controles, comparacion y bitacora exigidos.

## Fuentes Raw y procedencia

La malla GeoPackage se incluye porque es pequena y permite inspeccionar la
geometria. Los CSV Raw historicos 2019-2025 de VIIRS y CHIRPS superan los 100 MB
cada uno y no se duplican en esta entrega. Su procedencia, ruta controlada,
tamano y SHA-256 constan en `raw/metadatos/manifiesto_firelab_loja.json`.

Los resultados Clean y Curated de 2023 incluidos permiten revisar el flujo. La
reproduccion desde Raw requiere obtener las dos fuentes historicas registradas
en el manifiesto y ubicarlas en las rutas indicadas por
`configuracion/perfilado.json`.

## Ejecucion

Dependencias:

```powershell
python -m pip install -r configuracion/requirements_etl.txt
```

Desde la raiz del repositorio FireForest, con las fuentes Raw disponibles:

```powershell
.venv\Scripts\python.exe Tareas\Proyecto_integrador\tarea_ETL\codigo\etl_fireforest.py --desde-cero
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
    archivos = archivos_para_paquete(malla)

    salida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f"{salida.stem}_", suffix=".tmp", dir=salida.parent, delete=False
    ) as temporal:
        ruta_temporal = Path(temporal.name)

    try:
        with zipfile.ZipFile(
            ruta_temporal, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as paquete:
            readme = texto_readme(resultados, hash_malla).encode("utf-8")
            escribir_bytes(paquete, f"{NOMBRE_RAIZ}/README.md", readme)

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
