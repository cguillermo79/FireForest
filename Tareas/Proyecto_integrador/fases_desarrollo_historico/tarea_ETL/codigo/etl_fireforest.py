"""Construye las capas Clean y Curated de la tarea ETL de FireForest.

El script lee las fuentes Raw en modo de solo lectura, filtra el periodo 2023,
tipa y estandariza cada fuente, integra VIIRS con CHIRPS mediante una union uno
a uno y publica CSV y Parquet. No carga datos en PostgreSQL ni MongoDB.

Uso dentro del paquete extraido:

    python codigo/etl_fireforest.py --desde-cero

Uso alternativo desde la raiz de FireForest:

    .venv/Scripts/python.exe \
        Tareas/Proyecto_integrador/tarea_ETL/codigo/etl_fireforest.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


RUTA_SCRIPT = Path(__file__).resolve()
RAIZ_TAREA = RUTA_SCRIPT.parents[1]
RAIZ_INTEGRADOR = RAIZ_TAREA.parent
DIRECTORIO_CLEAN = RAIZ_TAREA / "clean"
DIRECTORIO_CURATED = RAIZ_TAREA / "curated"
DIRECTORIO_EVIDENCIAS = RAIZ_TAREA / "evidencias"
CONFIG_PERFILADO = RAIZ_TAREA / "configuracion" / "perfilado.json"
CONFIG_CALIDAD = RAIZ_TAREA / "configuracion" / "reglas_calidad.json"
CONFIG_TRANSFORMACIONES = (
    RAIZ_TAREA / "configuracion" / "transformaciones_clean.json"
)
ESTADISTICAS_ATIPICOS = DIRECTORIO_EVIDENCIAS / "estadisticas_atipicos.csv"


def resolver_ruta_fuente(ruta_configurada: str) -> Path:
    """Resuelve fuentes tanto en el repositorio como en el paquete autonomo."""
    candidatos = (
        RAIZ_TAREA / ruta_configurada,
        RAIZ_INTEGRADOR / ruta_configurada,
    )
    for ruta in candidatos:
        if ruta.is_file():
            return ruta
    raise FileNotFoundError(
        "No existe la fuente configurada. Rutas revisadas: "
        + ", ".join(str(ruta) for ruta in candidatos)
    )


def cargar_json(ruta: Path) -> dict[str, Any]:
    with ruta.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def escribir_csv_dict(
    ruta: Path, columnas: list[str], filas: Iterable[dict[str, Any]]
) -> None:
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    with temporal.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(filas)
    os.replace(temporal, ruta)


def escribir_texto(ruta: Path, contenido: str) -> None:
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    temporal.write_text(contenido, encoding="utf-8")
    os.replace(temporal, ruta)


def escribir_dataframe(
    dataframe: pd.DataFrame,
    nombre_base: str,
    directorio: Path = DIRECTORIO_CLEAN,
) -> None:
    ruta_csv = directorio / f"{nombre_base}.csv"
    ruta_parquet = directorio / f"{nombre_base}.parquet"
    temporal_csv = ruta_csv.with_suffix(ruta_csv.suffix + ".tmp")
    temporal_parquet = ruta_parquet.with_suffix(ruta_parquet.suffix + ".tmp")
    dataframe.to_csv(
        temporal_csv,
        index=False,
        encoding="utf-8-sig",
        date_format="%Y-%m-%d",
    )
    dataframe.to_parquet(temporal_parquet, index=False, engine="pyarrow")
    os.replace(temporal_csv, ruta_csv)
    os.replace(temporal_parquet, ruta_parquet)


def cargar_csv_periodo(ruta: Path, anio: int, tamano_bloque: int) -> pd.DataFrame:
    bloques: list[pd.DataFrame] = []
    for bloque in pd.read_csv(
        ruta,
        encoding="utf-8-sig",
        chunksize=tamano_bloque,
        low_memory=False,
    ):
        anios = pd.to_numeric(bloque["anio"], errors="coerce")
        seleccionado = bloque.loc[anios.eq(anio)].copy()
        if not seleccionado.empty:
            bloques.append(seleccionado)
    if not bloques:
        raise ValueError(f"No existen registros para {anio} en {ruta}")
    return pd.concat(bloques, ignore_index=True)


def convertir_numericas(dataframe: pd.DataFrame, columnas: list[str]) -> None:
    for columna in columnas:
        original_no_nulo = dataframe[columna].notna()
        convertida = pd.to_numeric(dataframe[columna], errors="coerce")
        perdidos = original_no_nulo & convertida.isna()
        if perdidos.any():
            raise ValueError(
                f"{columna}: {int(perdidos.sum())} valores no pudieron convertirse a numero"
            )
        dataframe[columna] = convertida


def entero_nullable(serie: pd.Series, tipo: str) -> pd.Series:
    numeros = pd.to_numeric(serie, errors="coerce")
    no_enteros = numeros.notna() & ~np.isclose(numeros, np.round(numeros))
    if no_enteros.any():
        raise ValueError(f"Se encontraron {int(no_enteros.sum())} valores no enteros")
    return numeros.round().astype(tipo)


def booleano_nullable(serie: pd.Series, nombre: str) -> pd.Series:
    numeros = pd.to_numeric(serie, errors="coerce")
    invalidos = numeros.notna() & ~numeros.isin([0, 1])
    if invalidos.any():
        raise ValueError(
            f"{nombre}: {int(invalidos.sum())} valores no pertenecen a 0/1"
        )
    salida = pd.Series(pd.NA, index=serie.index, dtype="boolean")
    salida.loc[numeros.notna()] = numeros.loc[numeros.notna()].eq(1)
    return salida


def bandera_atipico(
    serie: pd.Series, limite_inferior: float, limite_superior: float
) -> pd.Series:
    salida = pd.Series(pd.NA, index=serie.index, dtype="boolean")
    validos = serie.notna()
    salida.loc[validos] = (
        serie.loc[validos].lt(limite_inferior)
        | serie.loc[validos].gt(limite_superior)
    )
    return salida


def cargar_limites_atipicos() -> dict[tuple[str, str], tuple[float, float]]:
    estadisticas = pd.read_csv(ESTADISTICAS_ATIPICOS, encoding="utf-8-sig")
    return {
        (fila.fuente, fila.variable): (
            float(fila.limite_inferior),
            float(fila.limite_superior),
        )
        for fila in estadisticas.itertuples(index=False)
    }


def cargar_malla(ruta: Path, tabla: str, tolerancia: float) -> pd.DataFrame:
    consulta = f"""
        SELECT
            cell_index, cell_id, fila, columna,
            xmin_m, ymin_m, xmax_m, ymax_m, centro_x_m, centro_y_m,
            area_nominal_m2, area_nominal_ha,
            area_dentro_loja_m2, area_dentro_loja_ha,
            fraccion_dentro_loja, es_celda_completa,
            fraccion_lt_001, fraccion_lt_005, fraccion_lt_010,
            fraccion_lt_025, fraccion_lt_050,
            CASE WHEN geom IS NULL THEN 0 ELSE 1 END AS geometria_presente
        FROM "{tabla}"
        ORDER BY cell_index
    """
    uri = f"file:{ruta.resolve().as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as conexion:
        malla = pd.read_sql_query(consulta, conexion)

    for columna in ["cell_index", "fila", "columna"]:
        malla[columna] = entero_nullable(malla[columna], "Int64")
    for columna in [
        "es_celda_completa",
        "fraccion_lt_001",
        "fraccion_lt_005",
        "fraccion_lt_010",
        "fraccion_lt_025",
        "fraccion_lt_050",
        "geometria_presente",
    ]:
        malla[columna] = booleano_nullable(malla[columna], columna)
    malla["epsg"] = pd.Series(32717, index=malla.index, dtype="Int32")
    malla["categoria_cobertura_territorial"] = np.select(
        [
            malla["fraccion_dentro_loja"].ge(1 - tolerancia),
            malla["fraccion_dentro_loja"].ge(0.5),
        ],
        ["completa", "parcial_ge_050"],
        default="parcial_lt_050",
    )
    return malla


def atributos_malla(malla: pd.DataFrame) -> pd.DataFrame:
    return malla[
        [
            "cell_index",
            "cell_id",
            "fila",
            "columna",
            "area_dentro_loja_m2",
            "fraccion_dentro_loja",
            "es_celda_completa",
            "categoria_cobertura_territorial",
        ]
    ].copy()


def preparar_viirs(
    bruto: pd.DataFrame,
    malla: pd.DataFrame,
    limites: dict[tuple[str, str], tuple[float, float]],
) -> pd.DataFrame:
    columnas_numericas = [
        "cell_index",
        "anio",
        "mes",
        "viirs_soporte_nativo_m",
        "viirs_detecciones_todas_support_mean",
        "viirs_detecciones_nominal_alta_support_mean",
        "viirs_presencia_fuego_support_frac",
        "viirs_presencia_fuego_nominal_alta_support_frac",
        "viirs_frp_suma_observada_support_mean_mw",
        "viirs_frp_maxima_support_mean_mw",
        "viirs_dias_validos_support_mean",
        "viirs_disponibilidad_support_pct",
        "viirs_observado_support_mean",
        "viirs_source_coverage_frac",
        "viirs_observed_support_frac",
    ]
    convertir_numericas(bruto, columnas_numericas)
    bruto["cell_index"] = entero_nullable(bruto["cell_index"], "Int64")
    bruto["anio"] = entero_nullable(bruto["anio"], "Int16")
    bruto["mes"] = entero_nullable(bruto["mes"], "Int8")
    bruto["evidencia_fuego"] = booleano_nullable(
        bruto["viirs_evidencia_fuego_any"], "viirs_evidencia_fuego_any"
    )
    bruto["evidencia_fuego_nominal_alta"] = booleano_nullable(
        bruto["viirs_evidencia_fuego_nominal_alta_any"],
        "viirs_evidencia_fuego_nominal_alta_any",
    )
    bruto["periodo"] = pd.to_datetime(
        {"year": bruto["anio"], "month": bruto["mes"], "day": 1}
    )
    bruto["anio_mes"] = bruto["periodo"].dt.strftime("%Y-%m")
    bruto["observacion_viirs_disponible"] = bruto[
        "viirs_observed_support_frac"
    ].notna()
    bruto["apto_analisis_viirs"] = bruto["observacion_viirs_disponible"]
    bruto["motivo_no_apto_viirs"] = np.where(
        bruto["apto_analisis_viirs"], "", "sin_observacion_viirs"
    )

    for variable, destino in [
        ("viirs_frp_suma_observada_support_mean_mw", "atipico_frp_suma"),
        ("viirs_frp_maxima_support_mean_mw", "atipico_frp_maxima"),
    ]:
        inferior, superior = limites[("viirs", variable)]
        bruto[destino] = bandera_atipico(bruto[variable], inferior, superior)

    salida = bruto.merge(
        atributos_malla(malla),
        on="cell_index",
        how="left",
        validate="many_to_one",
        indicator="_union_malla",
    )
    if salida["_union_malla"].ne("both").any():
        raise ValueError("Existen registros VIIRS sin correspondencia en la malla")
    salida = salida.drop(columns=["_union_malla"])
    salida = salida.rename(
        columns={
            "viirs_soporte_nativo_m": "soporte_nativo_m",
            "viirs_detecciones_todas_support_mean": "detecciones_todas_media",
            "viirs_detecciones_nominal_alta_support_mean": "detecciones_nominal_alta_media",
            "viirs_presencia_fuego_support_frac": "presencia_fuego_frac",
            "viirs_presencia_fuego_nominal_alta_support_frac": "presencia_fuego_nominal_alta_frac",
            "viirs_frp_suma_observada_support_mean_mw": "frp_suma_observada_media_mw",
            "viirs_frp_maxima_support_mean_mw": "frp_maxima_media_mw",
            "viirs_dias_validos_support_mean": "dias_validos_media",
            "viirs_disponibilidad_support_pct": "disponibilidad_pct",
            "viirs_observado_support_mean": "observado_media",
            "viirs_source_coverage_frac": "cobertura_fuente_frac",
            "viirs_observed_support_frac": "soporte_observado_frac",
        }
    )
    columnas = [
        "cell_index", "cell_id", "fila", "columna", "anio", "mes",
        "periodo", "anio_mes", "asset_fuente", "soporte_nativo_m",
        "detecciones_todas_media", "detecciones_nominal_alta_media",
        "presencia_fuego_frac", "presencia_fuego_nominal_alta_frac",
        "frp_suma_observada_media_mw", "frp_maxima_media_mw",
        "dias_validos_media", "disponibilidad_pct", "observado_media",
        "cobertura_fuente_frac", "soporte_observado_frac",
        "evidencia_fuego", "evidencia_fuego_nominal_alta",
        "observacion_viirs_disponible", "apto_analisis_viirs",
        "motivo_no_apto_viirs", "atipico_frp_suma", "atipico_frp_maxima",
        "area_dentro_loja_m2", "fraccion_dentro_loja",
        "es_celda_completa", "categoria_cobertura_territorial",
    ]
    return salida[columnas].sort_values(["cell_index", "anio", "mes"]).reset_index(drop=True)


def preparar_chirps(
    bruto: pd.DataFrame,
    malla: pd.DataFrame,
    limites: dict[tuple[str, str], tuple[float, float]],
    tolerancia: float,
) -> pd.DataFrame:
    cell_id_origen = bruto["cell_id"].astype("string")
    columnas_numericas = [
        "cell_index", "fila", "columna", "area_dentro_loja_m2",
        "fraccion_dentro_loja", "anio", "mes", "dias_calendario",
        "chirps_grid_coverage", "chirps_n_pixels_intersectados",
        "chirps_precipitacion_acumulada_mm",
        "chirps_precipitacion_media_diaria_mm",
        "chirps_precipitacion_maxima_diaria_mm",
        "chirps_dias_humedos_ge1mm", "chirps_dias_secos_lt1mm",
        "chirps_dias_validos_pixel", "chirps_disponibilidad_pixel_pct",
        "chirps_observado_mes", "chirps_valid_coverage",
    ]
    convertir_numericas(bruto, columnas_numericas)
    for columna, tipo in [
        ("cell_index", "Int64"), ("fila", "Int64"),
        ("columna", "Int64"), ("anio", "Int16"),
        ("mes", "Int8"), ("dias_calendario", "Int8"),
        ("chirps_n_pixels_intersectados", "Int32"),
    ]:
        bruto[columna] = entero_nullable(bruto[columna], tipo)
    bruto["periodo"] = pd.to_datetime(
        {"year": bruto["anio"], "month": bruto["mes"], "day": 1}
    )
    bruto["anio_mes"] = bruto["periodo"].dt.strftime("%Y-%m")
    bruto["observado_mes"] = booleano_nullable(
        bruto["chirps_observado_mes"], "chirps_observado_mes"
    )
    bruto["cobertura_chirps_valida"] = bruto["chirps_valid_coverage"].sub(1).abs().le(tolerancia)
    bruto["fraccion_dias_humedos"] = np.where(
        bruto["chirps_dias_validos_pixel"].gt(0),
        bruto["chirps_dias_humedos_ge1mm"] / bruto["chirps_dias_validos_pixel"],
        np.nan,
    )
    for variable, destino in [
        ("chirps_precipitacion_acumulada_mm", "atipico_precipitacion_acumulada"),
        ("chirps_precipitacion_maxima_diaria_mm", "atipico_precipitacion_maxima_diaria"),
    ]:
        inferior, superior = limites[("chirps", variable)]
        bruto[destino] = bandera_atipico(bruto[variable], inferior, superior)

    malla_union = atributos_malla(malla).rename(
        columns={
            "cell_id": "cell_id_malla",
            "fila": "fila_malla",
            "columna": "columna_malla",
            "area_dentro_loja_m2": "area_dentro_loja_m2_malla",
            "fraccion_dentro_loja": "fraccion_dentro_loja_malla",
        }
    )
    salida = bruto.merge(
        malla_union,
        on="cell_index",
        how="left",
        validate="many_to_one",
        indicator="_union_malla",
    )
    if salida["_union_malla"].ne("both").any():
        raise ValueError("Existen registros CHIRPS sin correspondencia en la malla")
    inconsistentes = cell_id_origen.reset_index(drop=True).ne(
        salida["cell_id_malla"].astype("string").reset_index(drop=True)
    )
    if inconsistentes.any():
        raise ValueError(
            f"CHIRPS contiene {int(inconsistentes.sum())} cell_id inconsistentes con la malla"
        )
    salida = salida.drop(
        columns=[
            "_union_malla", "cell_id", "fila", "columna",
            "area_dentro_loja_m2", "fraccion_dentro_loja", "chirps_observado_mes",
        ]
    ).rename(
        columns={
            "cell_id_malla": "cell_id", "fila_malla": "fila",
            "columna_malla": "columna",
            "area_dentro_loja_m2_malla": "area_dentro_loja_m2",
            "fraccion_dentro_loja_malla": "fraccion_dentro_loja",
            "chirps_grid_coverage": "cobertura_grilla",
            "chirps_n_pixels_intersectados": "pixeles_intersectados",
            "chirps_precipitacion_acumulada_mm": "precipitacion_acumulada_mm",
            "chirps_precipitacion_media_diaria_mm": "precipitacion_media_diaria_mm",
            "chirps_precipitacion_maxima_diaria_mm": "precipitacion_maxima_diaria_mm",
            "chirps_dias_humedos_ge1mm": "dias_humedos_ge1mm",
            "chirps_dias_secos_lt1mm": "dias_secos_lt1mm",
            "chirps_dias_validos_pixel": "dias_validos_pixel",
            "chirps_disponibilidad_pixel_pct": "disponibilidad_pixel_pct",
            "chirps_valid_coverage": "cobertura_valida_fuente",
        }
    )
    columnas = [
        "cell_index", "cell_id", "fila", "columna", "anio", "mes",
        "periodo", "anio_mes", "dias_calendario", "cobertura_grilla",
        "pixeles_intersectados", "precipitacion_acumulada_mm",
        "precipitacion_media_diaria_mm", "precipitacion_maxima_diaria_mm",
        "dias_humedos_ge1mm", "dias_secos_lt1mm", "dias_validos_pixel",
        "disponibilidad_pixel_pct", "observado_mes", "cobertura_valida_fuente",
        "cobertura_chirps_valida", "fraccion_dias_humedos",
        "atipico_precipitacion_acumulada",
        "atipico_precipitacion_maxima_diaria", "area_dentro_loja_m2",
        "fraccion_dentro_loja", "es_celda_completa",
        "categoria_cobertura_territorial",
    ]
    return salida[columnas].sort_values(["cell_index", "anio", "mes"]).reset_index(drop=True)


def construir_curated(
    viirs: pd.DataFrame,
    chirps: pd.DataFrame,
    tolerancia: float,
) -> pd.DataFrame:
    """Integra Clean con cardinalidad uno a uno y conserva el grano celda-mes."""
    clave = ["cell_index", "anio", "mes"]
    if duplicados(viirs, clave) or duplicados(chirps, clave):
        raise ValueError("No se puede integrar: existen claves duplicadas en Clean")

    columnas_viirs = [
        "cell_index", "anio", "mes", "cell_id", "fila", "columna",
        "periodo", "anio_mes", "asset_fuente", "detecciones_todas_media",
        "detecciones_nominal_alta_media", "presencia_fuego_frac",
        "presencia_fuego_nominal_alta_frac", "frp_suma_observada_media_mw",
        "frp_maxima_media_mw", "dias_validos_media", "disponibilidad_pct",
        "cobertura_fuente_frac", "soporte_observado_frac", "evidencia_fuego",
        "evidencia_fuego_nominal_alta", "observacion_viirs_disponible",
        "atipico_frp_suma", "atipico_frp_maxima", "area_dentro_loja_m2",
        "fraccion_dentro_loja", "es_celda_completa",
        "categoria_cobertura_territorial",
    ]
    columnas_chirps = [
        "cell_index", "anio", "mes", "cell_id", "fila", "columna",
        "periodo", "anio_mes", "dias_calendario",
        "precipitacion_acumulada_mm", "precipitacion_media_diaria_mm",
        "precipitacion_maxima_diaria_mm", "dias_humedos_ge1mm",
        "dias_secos_lt1mm", "dias_validos_pixel", "disponibilidad_pixel_pct",
        "observado_mes", "cobertura_chirps_valida", "fraccion_dias_humedos",
        "atipico_precipitacion_acumulada",
        "atipico_precipitacion_maxima_diaria", "area_dentro_loja_m2",
        "fraccion_dentro_loja", "es_celda_completa",
        "categoria_cobertura_territorial",
    ]
    integrada = viirs[columnas_viirs].merge(
        chirps[columnas_chirps],
        on=clave,
        how="outer",
        validate="one_to_one",
        indicator="_union",
        suffixes=("_viirs", "_chirps"),
    )
    sin_correspondencia = int(integrada["_union"].ne("both").sum())
    if sin_correspondencia:
        raise ValueError(
            f"La integracion contiene {sin_correspondencia} claves sin correspondencia"
        )

    iguales_exactos = [
        "cell_id", "fila", "columna", "periodo", "anio_mes",
        "es_celda_completa", "categoria_cobertura_territorial",
    ]
    for columna in iguales_exactos:
        izquierda = integrada[f"{columna}_viirs"]
        derecha = integrada[f"{columna}_chirps"]
        if not izquierda.equals(derecha):
            raise ValueError(f"La integracion difiere en {columna}")
    for columna in ["area_dentro_loja_m2", "fraccion_dentro_loja"]:
        izquierda = integrada[f"{columna}_viirs"].astype(float)
        derecha = integrada[f"{columna}_chirps"].astype(float)
        if not np.isclose(izquierda, derecha, atol=tolerancia, rtol=0).all():
            raise ValueError(f"La integracion difiere en {columna}")

    salida = pd.DataFrame(index=integrada.index)
    salida["id_celda_mes"] = (
        integrada["cell_id_viirs"].astype("string")
        + "_"
        + integrada["anio_mes_viirs"].astype("string")
    )
    for columna in ["cell_id", "fila", "columna"]:
        salida[columna] = integrada[f"{columna}_viirs"]
    salida["cell_index"] = integrada["cell_index"]
    salida["anio"] = integrada["anio"]
    salida["mes"] = integrada["mes"]
    salida["periodo"] = integrada["periodo_viirs"]
    salida["anio_mes"] = integrada["anio_mes_viirs"]
    for columna in [
        "area_dentro_loja_m2", "fraccion_dentro_loja", "es_celda_completa",
        "categoria_cobertura_territorial",
    ]:
        salida[columna] = integrada[f"{columna}_viirs"]

    salida["asset_fuente_viirs"] = integrada["asset_fuente"]
    for columna in [
        "detecciones_todas_media", "detecciones_nominal_alta_media",
        "presencia_fuego_frac", "presencia_fuego_nominal_alta_frac",
        "frp_suma_observada_media_mw", "frp_maxima_media_mw",
        "dias_validos_media", "disponibilidad_pct", "cobertura_fuente_frac",
        "soporte_observado_frac", "evidencia_fuego",
        "evidencia_fuego_nominal_alta", "observacion_viirs_disponible",
        "atipico_frp_suma", "atipico_frp_maxima",
    ]:
        salida[columna] = integrada[columna]
    for columna in [
        "dias_calendario", "precipitacion_acumulada_mm",
        "precipitacion_media_diaria_mm", "precipitacion_maxima_diaria_mm",
        "dias_humedos_ge1mm", "dias_secos_lt1mm", "dias_validos_pixel",
        "disponibilidad_pixel_pct", "observado_mes", "cobertura_chirps_valida",
        "fraccion_dias_humedos", "atipico_precipitacion_acumulada",
        "atipico_precipitacion_maxima_diaria",
    ]:
        salida[columna if columna != "observado_mes" else "observado_mes_chirps"] = integrada[columna]

    salida["apto_analisis"] = (
        salida["observacion_viirs_disponible"]
        & salida["observado_mes_chirps"].fillna(False)
        & salida["cobertura_chirps_valida"].fillna(False)
    ).astype("boolean")
    viirs_no_apto = ~salida["observacion_viirs_disponible"]
    chirps_no_apto = (
        ~salida["observado_mes_chirps"].fillna(False)
        | ~salida["cobertura_chirps_valida"].fillna(False)
    )
    salida["motivo_no_apto_analisis"] = np.select(
        [viirs_no_apto & chirps_no_apto, viirs_no_apto, chirps_no_apto],
        [
            "sin_observacion_viirs_y_chirps_no_apto",
            "sin_observacion_viirs",
            "chirps_no_apto",
        ],
        default="",
    )
    banderas_atipicos = [
        "atipico_frp_suma", "atipico_frp_maxima",
        "atipico_precipitacion_acumulada",
        "atipico_precipitacion_maxima_diaria",
    ]
    salida["alguna_bandera_atipico"] = (
        salida[banderas_atipicos].fillna(False).any(axis=1).astype("boolean")
    )

    columnas_finales = [
        "id_celda_mes", "cell_id", "cell_index", "fila", "columna", "anio",
        "mes", "periodo", "anio_mes", "area_dentro_loja_m2",
        "fraccion_dentro_loja", "es_celda_completa",
        "categoria_cobertura_territorial", "asset_fuente_viirs",
        "detecciones_todas_media", "detecciones_nominal_alta_media",
        "presencia_fuego_frac", "presencia_fuego_nominal_alta_frac",
        "frp_suma_observada_media_mw", "frp_maxima_media_mw",
        "dias_validos_media", "disponibilidad_pct", "cobertura_fuente_frac",
        "soporte_observado_frac", "evidencia_fuego",
        "evidencia_fuego_nominal_alta", "dias_calendario",
        "precipitacion_acumulada_mm", "precipitacion_media_diaria_mm",
        "precipitacion_maxima_diaria_mm", "dias_humedos_ge1mm",
        "dias_secos_lt1mm", "dias_validos_pixel", "disponibilidad_pixel_pct",
        "fraccion_dias_humedos", "observacion_viirs_disponible",
        "observado_mes_chirps", "cobertura_chirps_valida", "apto_analisis",
        "motivo_no_apto_analisis", "atipico_frp_suma",
        "atipico_frp_maxima", "atipico_precipitacion_acumulada",
        "atipico_precipitacion_maxima_diaria", "alguna_bandera_atipico",
    ]
    return salida[columnas_finales].sort_values(
        ["cell_index", "anio", "mes"]
    ).reset_index(drop=True)


def construir_diccionario_curated(curated: pd.DataFrame) -> list[dict[str, Any]]:
    """Documenta todas las columnas del dataset final en el mismo orden."""
    definiciones = [
        ("id_celda_mes", "Identificador legible de la observacion celda-mes.", "texto", "sin unidad", "derivado Curated", "cell_id + '_' + anio_mes", "NO"),
        ("cell_id", "Identificador espacial estable de la celda de 500 m.", "texto", "sin unidad", "malla Clean", "valor validado por cell_index", "NO"),
        ("cell_index", "Indice tecnico de la celda usado para integrar fuentes.", "entero", "sin unidad", "malla Clean", "valor original", "NO"),
        ("fila", "Fila de la celda en la malla regular.", "entero", "sin unidad", "malla Clean", "valor original", "NO"),
        ("columna", "Columna de la celda en la malla regular.", "entero", "sin unidad", "malla Clean", "valor original", "NO"),
        ("anio", "Anio de la observacion mensual.", "entero", "anio", "VIIRS y CHIRPS Clean", "clave de integracion", "NO"),
        ("mes", "Mes de la observacion.", "entero", "1-12", "VIIRS y CHIRPS Clean", "clave de integracion", "NO"),
        ("periodo", "Fecha representativa del mes.", "fecha", "AAAA-MM-DD", "derivado Clean", "primer dia del mes", "NO"),
        ("anio_mes", "Etiqueta mensual normalizada.", "texto", "AAAA-MM", "derivado Clean", "anio y mes", "NO"),
        ("area_dentro_loja_m2", "Area de la celda incluida dentro del canton Loja.", "decimal", "m2", "malla Clean", "valor original", "NO"),
        ("fraccion_dentro_loja", "Proporcion del area de la celda dentro de Loja.", "decimal", "0-1", "malla Clean", "area dentro / area nominal", "NO"),
        ("es_celda_completa", "Indica si la celda esta completamente dentro de Loja.", "booleano", "verdadero/falso", "malla Clean", "bandera espacial", "NO"),
        ("categoria_cobertura_territorial", "Categoria de cobertura territorial de la celda.", "texto", "categoria", "derivado Clean", "completa, parcial_ge_050 o parcial_lt_050", "NO"),
        ("asset_fuente_viirs", "Identificador del asset VIIRS mensual de origen.", "texto", "sin unidad", "VIIRS Clean", "valor original", "NO"),
        ("detecciones_todas_media", "Media espacial de detecciones VIIRS de cualquier confianza.", "decimal", "detecciones", "VIIRS Clean", "valor original", "SI"),
        ("detecciones_nominal_alta_media", "Media espacial de detecciones VIIRS nominales o altas.", "decimal", "detecciones", "VIIRS Clean", "valor original", "SI"),
        ("presencia_fuego_frac", "Fraccion del soporte con presencia de fuego.", "decimal", "0-1", "VIIRS Clean", "valor original", "SI"),
        ("presencia_fuego_nominal_alta_frac", "Fraccion del soporte con fuego nominal o alto.", "decimal", "0-1", "VIIRS Clean", "valor original", "SI"),
        ("frp_suma_observada_media_mw", "Media espacial de la suma de potencia radiativa del fuego.", "decimal", "MW", "VIIRS Clean", "valor original", "SI"),
        ("frp_maxima_media_mw", "Media espacial de la potencia radiativa maxima.", "decimal", "MW", "VIIRS Clean", "valor original", "SI"),
        ("dias_validos_media", "Media espacial de dias VIIRS validos.", "decimal", "dias", "VIIRS Clean", "valor original", "SI"),
        ("disponibilidad_pct", "Disponibilidad observacional VIIRS.", "decimal", "porcentaje", "VIIRS Clean", "valor original", "SI"),
        ("cobertura_fuente_frac", "Fraccion de cobertura de la fuente VIIRS.", "decimal", "0-1", "VIIRS Clean", "valor original", "SI"),
        ("soporte_observado_frac", "Fraccion del soporte efectivamente observado por VIIRS.", "decimal", "0-1", "VIIRS Clean", "valor original", "SI"),
        ("evidencia_fuego", "Indica evidencia VIIRS de fuego de cualquier confianza.", "booleano", "verdadero/falso", "VIIRS Clean", "indicador 0/1 tipado", "SI"),
        ("evidencia_fuego_nominal_alta", "Indica evidencia VIIRS nominal o alta.", "booleano", "verdadero/falso", "VIIRS Clean", "indicador 0/1 tipado", "SI"),
        ("dias_calendario", "Numero de dias del mes.", "entero", "dias", "CHIRPS Clean", "valor original", "NO"),
        ("precipitacion_acumulada_mm", "Precipitacion acumulada mensual.", "decimal", "mm", "CHIRPS Clean", "valor original", "NO"),
        ("precipitacion_media_diaria_mm", "Precipitacion media diaria del mes.", "decimal", "mm/dia", "CHIRPS Clean", "valor original", "NO"),
        ("precipitacion_maxima_diaria_mm", "Precipitacion diaria maxima del mes.", "decimal", "mm", "CHIRPS Clean", "valor original", "NO"),
        ("dias_humedos_ge1mm", "Dias del mes con precipitacion mayor o igual a 1 mm.", "decimal", "dias", "CHIRPS Clean", "valor original", "NO"),
        ("dias_secos_lt1mm", "Dias del mes con precipitacion menor a 1 mm.", "decimal", "dias", "CHIRPS Clean", "valor original", "NO"),
        ("dias_validos_pixel", "Dias CHIRPS validos para la celda.", "decimal", "dias", "CHIRPS Clean", "valor original", "NO"),
        ("disponibilidad_pixel_pct", "Disponibilidad temporal CHIRPS.", "decimal", "porcentaje", "CHIRPS Clean", "valor original", "NO"),
        ("fraccion_dias_humedos", "Proporcion de dias validos clasificados como humedos.", "decimal", "0-1", "derivado Clean", "dias_humedos_ge1mm / dias_validos_pixel", "NO"),
        ("observacion_viirs_disponible", "Indica si VIIRS tiene soporte observacional para la celda-mes.", "booleano", "verdadero/falso", "derivado Clean", "soporte_observado_frac no nulo", "NO"),
        ("observado_mes_chirps", "Indica si CHIRPS observo el mes.", "booleano", "verdadero/falso", "CHIRPS Clean", "indicador 0/1 tipado", "NO"),
        ("cobertura_chirps_valida", "Indica cobertura CHIRPS valida dentro de la tolerancia.", "booleano", "verdadero/falso", "derivado Clean", "abs(cobertura_valida_fuente - 1) <= tolerancia", "NO"),
        ("apto_analisis", "Indica si la fila tiene observacion valida en ambas fuentes.", "booleano", "verdadero/falso", "derivado Curated", "VIIRS disponible y CHIRPS observado con cobertura valida", "NO"),
        ("motivo_no_apto_analisis", "Explica por que una fila no es apta para analisis conjunto.", "texto", "categoria", "derivado Curated", "evaluacion de banderas de cobertura", "NO"),
        ("atipico_frp_suma", "Bandera IQR de la suma FRP.", "booleano", "verdadero/falso", "derivado Clean", "fuera de limites IQR documentados", "SI"),
        ("atipico_frp_maxima", "Bandera IQR de FRP maxima.", "booleano", "verdadero/falso", "derivado Clean", "fuera de limites IQR documentados", "SI"),
        ("atipico_precipitacion_acumulada", "Bandera IQR de precipitacion acumulada.", "booleano", "verdadero/falso", "derivado Clean", "fuera de limites IQR documentados", "NO"),
        ("atipico_precipitacion_maxima_diaria", "Bandera IQR de precipitacion maxima diaria.", "booleano", "verdadero/falso", "derivado Clean", "fuera de limites IQR documentados", "NO"),
        ("alguna_bandera_atipico", "Indica si alguna metrica integrada tiene bandera IQR.", "booleano", "verdadero/falso", "derivado Curated", "OR de cuatro banderas IQR", "NO"),
    ]
    variables = [fila[0] for fila in definiciones]
    if variables != list(curated.columns):
        raise ValueError("El diccionario no coincide con las columnas de Curated")
    return [
        {
            "orden": indice,
            "variable": variable,
            "descripcion": descripcion,
            "tipo_logico": tipo,
            "tipo_parquet": str(curated[variable].dtype),
            "unidad": unidad,
            "origen": origen,
            "derivacion": derivacion,
            "permite_nulo": permite_nulo,
        }
        for indice, (
            variable, descripcion, tipo, unidad, origen, derivacion, permite_nulo
        ) in enumerate(definiciones, start=1)
    ]


def duplicados(dataframe: pd.DataFrame, clave: list[str]) -> int:
    return int(dataframe.duplicated(clave, keep=False).sum())


def fila_control(
    control_id: str,
    dimension: str,
    fuente: str,
    regla: str,
    evaluados: int,
    incumplimientos: int,
    evidencia: str,
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "dimension_calidad": dimension,
        "fuente": fuente,
        "regla": regla,
        "registros_evaluados": evaluados,
        "incumplimientos": incumplimientos,
        "resultado": "CUMPLE" if incumplimientos == 0 else "NO_CUMPLE",
        "evidencia": evidencia,
    }


def sha256(ruta: Path) -> str:
    resumen = hashlib.sha256()
    with ruta.open("rb") as archivo:
        while bloque := archivo.read(8 * 1024 * 1024):
            resumen.update(bloque)
    return resumen.hexdigest()


def main(desde_cero: bool = False) -> int:
    if desde_cero:
        import evaluar_calidad_raw
        import perfilar_fuentes

        print("Ejecutando perfilado desde Raw...")
        if perfilar_fuentes.main() != 0:
            raise RuntimeError("Fallo el perfilado inicial")
        print("Ejecutando evaluacion de calidad Raw...")
        if evaluar_calidad_raw.main() != 0:
            raise RuntimeError("Fallo la evaluacion de calidad Raw")

    perfilado = cargar_json(CONFIG_PERFILADO)
    calidad = cargar_json(CONFIG_CALIDAD)
    transformaciones = cargar_json(CONFIG_TRANSFORMACIONES)
    anio = int(transformaciones["anio_estudio"])
    esperado = int(transformaciones["filas_celda_mes_esperadas"])
    celdas_esperadas = int(transformaciones["celdas_esperadas"])
    tamano_bloque = int(transformaciones["tamano_bloque_csv"])
    tolerancia = float(calidad["tolerancia_fracciones"])

    DIRECTORIO_CLEAN.mkdir(parents=True, exist_ok=True)
    DIRECTORIO_CURATED.mkdir(parents=True, exist_ok=True)
    DIRECTORIO_EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    rutas = {
        fuente: resolver_ruta_fuente(datos["ruta"])
        for fuente, datos in perfilado["fuentes"].items()
    }
    limites = cargar_limites_atipicos()

    print("Construyendo Clean de la malla...")
    malla = cargar_malla(rutas["malla"], perfilado["tabla_malla"], tolerancia)
    print("Leyendo y transformando VIIRS 2023...")
    viirs_raw = cargar_csv_periodo(rutas["viirs"], anio, tamano_bloque)
    viirs = preparar_viirs(viirs_raw.copy(), malla, limites)
    print("Leyendo y transformando CHIRPS 2023...")
    chirps_raw = cargar_csv_periodo(rutas["chirps"], anio, tamano_bloque)
    chirps = preparar_chirps(chirps_raw.copy(), malla, limites, tolerancia)

    clave = ["cell_index", "anio", "mes"]
    metricas_viirs = [
        "detecciones_todas_media", "detecciones_nominal_alta_media",
        "presencia_fuego_frac", "presencia_fuego_nominal_alta_frac",
        "frp_suma_observada_media_mw", "frp_maxima_media_mw",
        "dias_validos_media", "disponibilidad_pct", "observado_media",
        "cobertura_fuente_frac", "soporte_observado_frac",
    ]
    no_observadas = ~viirs["observacion_viirs_disponible"]
    viirs_no_obs_con_valores = int(
        viirs.loc[no_observadas, metricas_viirs].notna().any(axis=1).sum()
    )
    viirs_obs_con_nulos = int(
        viirs.loc[~no_observadas, metricas_viirs].isna().any(axis=1).sum()
    )
    periodo_viirs_inconsistente = int(
        viirs["anio_mes"].ne(viirs["periodo"].dt.strftime("%Y-%m")).sum()
    )
    periodo_chirps_inconsistente = int(
        chirps["anio_mes"].ne(chirps["periodo"].dt.strftime("%Y-%m")).sum()
    )
    fraccion_humedos_inconsistente = int(
        (~np.isclose(
            chirps["fraccion_dias_humedos"],
            chirps["dias_humedos_ge1mm"] / chirps["dias_validos_pixel"],
            atol=1e-12,
            rtol=0,
        )).sum()
    )

    controles = [
        fila_control("CLE-01", "reconciliacion", "malla", "La malla Clean conserva 7997 celdas.", len(malla), abs(len(malla) - celdas_esperadas), "clean/malla_500m.csv"),
        fila_control("CLE-02", "unicidad", "malla", "cell_index y cell_id son completos y unicos.", len(malla), duplicados(malla, ["cell_index"]) + duplicados(malla, ["cell_id"]) + int(malla[["cell_index", "cell_id"]].isna().any(axis=1).sum()), "clean/malla_500m.csv"),
        fila_control("CLE-03", "reconciliacion", "viirs", "VIIRS Clean conserva 95964 claves celda-mes.", len(viirs), abs(len(viirs) - esperado), "clean/viirs_2023.csv"),
        fila_control("CLE-04", "unicidad", "viirs", "La clave cell_index + anio + mes es completa y unica.", len(viirs), duplicados(viirs, clave) + int(viirs[clave].isna().any(axis=1).sum()), "clean/viirs_2023.csv"),
        fila_control("CLE-05", "integridad_referencial", "viirs", "Todo registro VIIRS recibe un cell_id de la malla.", len(viirs), int(viirs["cell_id"].isna().sum()), "clean/viirs_2023.csv"),
        fila_control("CLE-06", "completitud", "viirs", "Las 900 observaciones faltantes se conservan y marcan como no aptas.", len(viirs), abs(int(no_observadas.sum()) - 900) + int((no_observadas & viirs["apto_analisis_viirs"]).sum()), "clean/observaciones_viirs_sin_cobertura_2023.csv"),
        fila_control("CLE-07", "consistencia", "viirs", "Un faltante VIIRS no se convierte en cero y una observacion disponible mantiene metricas.", len(viirs), viirs_no_obs_con_valores + viirs_obs_con_nulos, "clean/viirs_2023.csv"),
        fila_control("CLE-08", "consistencia", "viirs", "periodo y anio_mes coinciden.", len(viirs), periodo_viirs_inconsistente, "clean/viirs_2023.csv"),
        fila_control("CLE-09", "reconciliacion", "chirps", "CHIRPS Clean conserva 95964 claves celda-mes.", len(chirps), abs(len(chirps) - esperado), "clean/chirps_2023.csv"),
        fila_control("CLE-10", "unicidad", "chirps", "La clave cell_index + anio + mes es completa y unica.", len(chirps), duplicados(chirps, clave) + int(chirps[clave].isna().any(axis=1).sum()), "clean/chirps_2023.csv"),
        fila_control("CLE-11", "integridad_referencial", "chirps", "Todo registro CHIRPS conserva el cell_id validado contra la malla.", len(chirps), int(chirps["cell_id"].isna().sum()), "clean/chirps_2023.csv"),
        fila_control("CLE-12", "consistencia", "chirps", "periodo y anio_mes coinciden.", len(chirps), periodo_chirps_inconsistente, "clean/chirps_2023.csv"),
        fila_control("CLE-13", "validez", "chirps", "fraccion_dias_humedos reproduce dias_humedos / dias_validos y queda entre 0 y 1.", len(chirps), fraccion_humedos_inconsistente + int((~chirps["fraccion_dias_humedos"].between(0, 1)).sum()), "clean/chirps_2023.csv"),
        fila_control("CLE-14", "valores_atipicos", "viirs", "Los extremos FRP se marcan y no se eliminan.", len(viirs), abs(int(viirs["atipico_frp_suma"].fillna(False).sum()) - 747), "clean/viirs_2023.csv"),
        fila_control("CLE-15", "valores_atipicos", "chirps", "Los extremos de precipitacion se marcan y no se eliminan.", len(chirps), abs(int(chirps["atipico_precipitacion_acumulada"].sum()) - 13731) + abs(int(chirps["atipico_precipitacion_maxima_diaria"].sum()) - 9224), "clean/chirps_2023.csv"),
        fila_control("CLE-16", "rechazos", "todas", "No existen registros con errores criticos que requieran rechazo.", len(malla) + len(viirs) + len(chirps), 0, "clean/rechazos_criticos_2023.csv"),
    ]
    no_cumplen = [fila for fila in controles if fila["resultado"] != "CUMPLE"]
    if no_cumplen:
        detalle = ", ".join(
            f"{fila['control_id']}={fila['incumplimientos']}" for fila in no_cumplen
        )
        raise ValueError(f"La capa Clean no supera los controles: {detalle}")

    print("Integrando VIIRS y CHIRPS en Curated...")
    curated = construir_curated(viirs, chirps, tolerancia)
    diccionario_curated = construir_diccionario_curated(curated)
    clave_final = ["cell_id", "anio", "mes"]
    metricas_viirs_curated = [
        "detecciones_todas_media", "detecciones_nominal_alta_media",
        "presencia_fuego_frac", "presencia_fuego_nominal_alta_frac",
        "frp_suma_observada_media_mw", "frp_maxima_media_mw",
        "dias_validos_media", "disponibilidad_pct", "cobertura_fuente_frac",
        "soporte_observado_frac",
    ]
    no_aptas = ~curated["apto_analisis"]
    controles_curated = [
        fila_control("CUR-01", "cardinalidad", "viirs_chirps", "Cada fuente Clean tiene clave tecnica unica antes de la union.", len(viirs) + len(chirps), duplicados(viirs, clave) + duplicados(chirps, clave), "clean/viirs_2023.parquet; clean/chirps_2023.parquet"),
        fila_control("CUR-02", "integridad_referencial", "viirs_chirps", "La union uno a uno encuentra correspondencia para todas las claves.", len(curated), 0, "curated/fireforest_celda_mes_2023.csv"),
        fila_control("CUR-03", "reconciliacion", "curated", "Curated conserva 95964 filas celda-mes.", len(curated), abs(len(curated) - esperado), "curated/fireforest_celda_mes_2023.csv"),
        fila_control("CUR-04", "unicidad", "curated", "La clave final cell_id + anio + mes es completa y unica.", len(curated), duplicados(curated, clave_final) + int(curated[clave_final].isna().any(axis=1).sum()), "curated/fireforest_celda_mes_2023.csv"),
        fila_control("CUR-05", "reconciliacion", "curated", "La union no multiplica ni elimina filas de las fuentes Clean.", len(curated), abs(len(curated) - len(viirs)) + abs(len(curated) - len(chirps)), "evidencias/comparacion_antes_despues.csv"),
        fila_control("CUR-06", "completitud", "curated", "Las 900 filas sin VIIRS se conservan como no aptas.", len(curated), abs(int(no_aptas.sum()) - 900) + abs(int(curated["apto_analisis"].sum()) - 95064), "curated/fireforest_celda_mes_2023.csv"),
        fila_control("CUR-07", "consistencia", "curated", "Las metricas VIIRS de filas sin observacion permanecen nulas.", int(no_aptas.sum()), int(curated.loc[no_aptas, metricas_viirs_curated].notna().any(axis=1).sum()), "curated/fireforest_celda_mes_2023.csv"),
        fila_control("CUR-08", "completitud", "curated", "Las metricas CHIRPS criticas estan completas.", len(curated), int(curated[["precipitacion_acumulada_mm", "precipitacion_media_diaria_mm", "precipitacion_maxima_diaria_mm"]].isna().any(axis=1).sum()), "curated/fireforest_celda_mes_2023.csv"),
        fila_control("CUR-09", "consistencia", "curated", "Los conteos de evidencia de fuego se conservan despues de la union.", len(curated), abs(int(curated["evidencia_fuego"].fillna(False).sum()) - 747) + abs(int(curated["evidencia_fuego_nominal_alta"].fillna(False).sum()) - 709), "curated/fireforest_celda_mes_2023.csv"),
        fila_control("CUR-10", "unicidad", "curated", "id_celda_mes es completo y unico.", len(curated), duplicados(curated, ["id_celda_mes"]) + int(curated["id_celda_mes"].isna().sum()), "curated/fireforest_celda_mes_2023.csv"),
        fila_control("CUR-11", "documentacion", "curated", "El diccionario documenta todas las columnas finales una sola vez.", len(curated.columns), abs(len(diccionario_curated) - len(curated.columns)) + (len(diccionario_curated) - len({fila["variable"] for fila in diccionario_curated})), "curated/diccionario_datos.csv"),
    ]
    no_cumplen_curated = [
        fila for fila in controles_curated if fila["resultado"] != "CUMPLE"
    ]
    if no_cumplen_curated:
        detalle = ", ".join(
            f"{fila['control_id']}={fila['incumplimientos']}"
            for fila in no_cumplen_curated
        )
        raise ValueError(f"La capa Curated no supera los controles: {detalle}")

    excepciones = viirs.loc[
        no_observadas,
        [
            "cell_index", "cell_id", "anio", "mes", "periodo", "anio_mes",
            "fraccion_dentro_loja", "categoria_cobertura_territorial",
            "motivo_no_apto_viirs",
        ],
    ].copy()
    excepciones["accion"] = "conservar_nulos_y_excluir_solo_del_subconjunto_analitico"
    rechazos = pd.DataFrame(
        columns=[
            "fuente", "cell_index", "cell_id", "anio", "mes", "regla_id",
            "motivo", "accion",
        ]
    )

    comparacion = [
        {"fuente": "malla", "metrica": "filas", "antes_raw": len(malla), "despues_clean": len(malla), "diferencia": 0, "interpretacion": "Se conservan todas las celdas."},
        {"fuente": "viirs", "metrica": "filas_2023", "antes_raw": len(viirs_raw), "despues_clean": len(viirs), "diferencia": len(viirs) - len(viirs_raw), "interpretacion": "No se eliminan claves celda-mes."},
        {"fuente": "viirs", "metrica": "filas_sin_observacion", "antes_raw": int(viirs_raw["viirs_observed_support_frac"].isna().sum()), "despues_clean": int(no_observadas.sum()), "diferencia": 0, "interpretacion": "Los faltantes se conservan como nulos y se marcan."},
        {"fuente": "viirs", "metrica": "duplicados_clave", "antes_raw": int(viirs_raw.duplicated(["cell_index", "anio", "mes"], keep=False).sum()), "despues_clean": duplicados(viirs, clave), "diferencia": 0, "interpretacion": "No fue necesario deduplicar."},
        {"fuente": "viirs", "metrica": "filas_con_bandera_atipico_frp", "antes_raw": 0, "despues_clean": int(viirs[["atipico_frp_suma", "atipico_frp_maxima"]].fillna(False).any(axis=1).sum()), "diferencia": int(viirs[["atipico_frp_suma", "atipico_frp_maxima"]].fillna(False).any(axis=1).sum()), "interpretacion": "Se agrega trazabilidad; los valores se conservan."},
        {"fuente": "chirps", "metrica": "filas_2023", "antes_raw": len(chirps_raw), "despues_clean": len(chirps), "diferencia": len(chirps) - len(chirps_raw), "interpretacion": "No se eliminan claves celda-mes."},
        {"fuente": "chirps", "metrica": "duplicados_clave", "antes_raw": int(chirps_raw.duplicated(["cell_index", "anio", "mes"], keep=False).sum()), "despues_clean": duplicados(chirps, clave), "diferencia": 0, "interpretacion": "No fue necesario deduplicar."},
        {"fuente": "chirps", "metrica": "filas_con_alguna_bandera_atipico", "antes_raw": 0, "despues_clean": int(chirps[["atipico_precipitacion_acumulada", "atipico_precipitacion_maxima_diaria"]].any(axis=1).sum()), "diferencia": int(chirps[["atipico_precipitacion_acumulada", "atipico_precipitacion_maxima_diaria"]].any(axis=1).sum()), "interpretacion": "Se agrega trazabilidad; los valores se conservan."},
        {"fuente": "todas", "metrica": "rechazos_criticos", "antes_raw": 0, "despues_clean": len(rechazos), "diferencia": 0, "interpretacion": "Los controles criticos no detectaron rechazos."},
        {"fuente": "integracion", "metrica": "filas_celda_mes", "antes_raw": esperado, "despues_clean": esperado, "despues_curated": len(curated), "diferencia": len(curated) - esperado, "interpretacion": "La union uno a uno conserva exactamente las claves esperadas."},
        {"fuente": "integracion", "metrica": "duplicados_clave_final", "antes_raw": 0, "despues_clean": 0, "despues_curated": duplicados(curated, clave_final), "diferencia": duplicados(curated, clave_final), "interpretacion": "La integracion no genera duplicados."},
        {"fuente": "integracion", "metrica": "filas_no_aptas_analisis", "antes_raw": int(viirs_raw["viirs_observed_support_frac"].isna().sum()), "despues_clean": int(no_observadas.sum()), "despues_curated": int(no_aptas.sum()), "diferencia": int(no_aptas.sum()) - int(no_observadas.sum()), "interpretacion": "Los faltantes VIIRS siguen visibles y no se eliminan del maestro."},
    ]

    print("Escribiendo CSV y Parquet Clean...")
    escribir_dataframe(malla, "malla_500m")
    escribir_dataframe(viirs, "viirs_2023")
    escribir_dataframe(chirps, "chirps_2023")
    escribir_dataframe(excepciones, "observaciones_viirs_sin_cobertura_2023")
    escribir_dataframe(rechazos, "rechazos_criticos_2023")
    print("Escribiendo CSV, Parquet y diccionario Curated...")
    escribir_dataframe(
        curated,
        "fireforest_celda_mes_2023",
        directorio=DIRECTORIO_CURATED,
    )
    escribir_csv_dict(
        DIRECTORIO_CURATED / "diccionario_datos.csv",
        [
            "orden", "variable", "descripcion", "tipo_logico", "tipo_parquet",
            "unidad", "origen", "derivacion", "permite_nulo",
        ],
        diccionario_curated,
    )
    escribir_csv_dict(
        DIRECTORIO_EVIDENCIAS / "controles_clean.csv",
        [
            "control_id", "dimension_calidad", "fuente", "regla",
            "registros_evaluados", "incumplimientos", "resultado", "evidencia",
        ],
        controles,
    )
    escribir_csv_dict(
        DIRECTORIO_EVIDENCIAS / "comparacion_antes_despues.csv",
        [
            "fuente", "metrica", "antes_raw", "despues_clean",
            "despues_curated", "diferencia", "interpretacion",
        ],
        comparacion,
    )
    escribir_csv_dict(
        DIRECTORIO_EVIDENCIAS / "controles_curated.csv",
        [
            "control_id", "dimension_calidad", "fuente", "regla",
            "registros_evaluados", "incumplimientos", "resultado", "evidencia",
        ],
        controles_curated,
    )

    salidas = [
        DIRECTORIO_CLEAN / nombre
        for nombre in [
            "malla_500m.csv", "malla_500m.parquet",
            "viirs_2023.csv", "viirs_2023.parquet",
            "chirps_2023.csv", "chirps_2023.parquet",
            "observaciones_viirs_sin_cobertura_2023.csv",
            "observaciones_viirs_sin_cobertura_2023.parquet",
            "rechazos_criticos_2023.csv", "rechazos_criticos_2023.parquet",
        ]
    ]
    manifiesto_salidas = [
        {
            "archivo": ruta.relative_to(RAIZ_TAREA).as_posix(),
            "filas": {
                "malla_500m": len(malla),
                "viirs_2023": len(viirs),
                "chirps_2023": len(chirps),
                "observaciones_viirs_sin_cobertura_2023": len(excepciones),
                "rechazos_criticos_2023": len(rechazos),
            }[ruta.name.rsplit(".", 1)[0]],
            "tamano_bytes": ruta.stat().st_size,
            "sha256": sha256(ruta),
        }
        for ruta in salidas
    ]
    escribir_csv_dict(
        DIRECTORIO_EVIDENCIAS / "manifiesto_salidas_clean.csv",
        ["archivo", "filas", "tamano_bytes", "sha256"],
        manifiesto_salidas,
    )
    salidas_curated = [
        DIRECTORIO_CURATED / "fireforest_celda_mes_2023.csv",
        DIRECTORIO_CURATED / "fireforest_celda_mes_2023.parquet",
        DIRECTORIO_CURATED / "diccionario_datos.csv",
    ]
    manifiesto_curated = [
        {
            "archivo": ruta.relative_to(RAIZ_TAREA).as_posix(),
            "filas": len(curated) if ruta.name != "diccionario_datos.csv" else len(diccionario_curated),
            "tamano_bytes": ruta.stat().st_size,
            "sha256": sha256(ruta),
        }
        for ruta in salidas_curated
    ]
    escribir_csv_dict(
        DIRECTORIO_EVIDENCIAS / "manifiesto_salidas_curated.csv",
        ["archivo", "filas", "tamano_bytes", "sha256"],
        manifiesto_curated,
    )

    resumen = f"""# Resumen de la capa Clean

## Resultado

- Periodo procesado: {anio}.
- Malla: {len(malla):,} celdas.
- VIIRS: {len(viirs):,} filas celda-mes.
- CHIRPS: {len(chirps):,} filas celda-mes.
- Observaciones VIIRS sin cobertura: {len(excepciones):,}.
- Rechazos criticos: {len(rechazos):,}.
- Controles Clean cumplidos: {len(controles)} de {len(controles)}.

## Tratamientos aplicados

1. Se selecciono 2023 mediante codigo y se conservaron intactos los archivos Raw.
2. Se tiparon identificadores, numeros, fechas y booleanos.
3. Se incorporaron `cell_id` y atributos territoriales desde la malla.
4. Se construyeron banderas de cobertura y aptitud VIIRS.
5. Se calculo `fraccion_dias_humedos` sin reemplazar mediciones originales.
6. Se marcaron valores atipicos mediante los limites IQR ya documentados.

La capa Clean mantiene cada fuente por separado. El mismo script utiliza estas
salidas logicas para construir Curated con cardinalidad uno a uno.
"""
    escribir_texto(DIRECTORIO_EVIDENCIAS / "resumen_clean.md", resumen)
    print(f"Clean completado: {len(controles)} controles cumplidos.")
    print(f"Curated completado: {len(controles_curated)} controles cumplidos.")
    print(f"Salidas Clean: {DIRECTORIO_CLEAN}")
    print(f"Salidas Curated: {DIRECTORIO_CURATED}")
    if desde_cero:
        print("Actualizando el seguimiento final de entregables...")
        if evaluar_calidad_raw.main() != 0:
            raise RuntimeError("Fallo la actualizacion del seguimiento final")
    return 0


if __name__ == "__main__":
    analizador = argparse.ArgumentParser(
        description="Construye las capas Clean y Curated de FireForest."
    )
    analizador.add_argument(
        "--desde-cero",
        action="store_true",
        help="Ejecuta perfilado, calidad Raw, Clean, Curated y seguimiento.",
    )
    argumentos = analizador.parse_args()
    raise SystemExit(main(desde_cero=argumentos.desde_cero))
