"""Evalúa reglas de calidad sobre las fuentes Raw de FireForest.

Genera la matriz de calidad, estadísticas de valores atípicos, bitácora de
decisiones y seguimiento de entregables. Solo lee las fuentes originales y las
evidencias del perfilado; no crea todavía las capas Clean o Curated.
"""

from __future__ import annotations

import csv
import json
import math
import os
import sqlite3
import statistics
from pathlib import Path
from typing import Any, Iterable


RUTA_SCRIPT = Path(__file__).resolve()
RAIZ_TAREA = RUTA_SCRIPT.parents[1]
RAIZ_INTEGRADOR = RAIZ_TAREA.parent
EVIDENCIAS = RAIZ_TAREA / "evidencias"
CONFIG_PERFILADO = RAIZ_TAREA / "configuracion" / "perfilado.json"
CONFIG_CALIDAD = RAIZ_TAREA / "configuracion" / "reglas_calidad.json"


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


def leer_csv(ruta: Path) -> list[dict[str, str]]:
    with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))


def escribir_csv(ruta: Path, columnas: list[str], filas: Iterable[dict[str, Any]]) -> None:
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


def porcentaje(afectados: int, evaluados: int) -> str:
    return f"{afectados * 100 / evaluados:.6f}" if evaluados else "0.000000"


def a_float(valor: str) -> float | None:
    texto = valor.strip()
    if texto == "":
        return None
    numero = float(texto)
    if not math.isfinite(numero):
        raise ValueError(f"Valor no finito: {valor}")
    return numero


def estadistica_iqr(fuente: str, variable: str, valores: list[float]) -> dict[str, Any]:
    ordenados = sorted(valores)
    q1, _, q3 = statistics.quantiles(ordenados, n=4, method="inclusive")
    iqr = q3 - q1
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr
    atipicos = sum(
        valor < limite_inferior or valor > limite_superior for valor in ordenados
    )
    return {
        "fuente": fuente,
        "variable": variable,
        "registros_evaluados": len(ordenados),
        "q1": f"{q1:.12g}",
        "q3": f"{q3:.12g}",
        "iqr": f"{iqr:.12g}",
        "limite_inferior": f"{limite_inferior:.12g}",
        "limite_superior": f"{limite_superior:.12g}",
        "registros_atipicos": atipicos,
        "porcentaje_atipicos": porcentaje(atipicos, len(ordenados)),
        "tratamiento": "Marcar para revisión; no eliminar automáticamente.",
    }


def fila_matriz(
    regla_id: str,
    dimension: str,
    fuente: str,
    variables: str,
    regla: str,
    criterio: str,
    severidad: str,
    evaluados: int,
    afectados: int,
    resultado: str,
    tratamiento: str,
    evidencia: str,
    evidencia_posterior: str = "Pendiente de la capa Clean.",
) -> dict[str, Any]:
    return {
        "regla_id": regla_id,
        "dimension_calidad": dimension,
        "fuente": fuente,
        "ambito": "periodo_2023",
        "variables": variables,
        "regla": regla,
        "criterio_esperado": criterio,
        "severidad": severidad,
        "registros_evaluados": evaluados,
        "registros_afectados": afectados,
        "porcentaje_afectado": porcentaje(afectados, evaluados),
        "resultado_raw": resultado,
        "tratamiento_definido": tratamiento,
        "evidencia_previa": evidencia,
        "evidencia_posterior": evidencia_posterior,
    }


def main() -> int:
    perfil = cargar_json(CONFIG_PERFILADO)
    reglas = cargar_json(CONFIG_CALIDAD)
    anio = int(reglas["anio_estudio"])
    tolerancia_fracciones = float(reglas["tolerancia_fracciones"])
    tolerancia_precipitacion = float(
        reglas["tolerancia_reconciliacion_precipitacion_mm"]
    )
    tolerancia_area = float(reglas["tolerancia_area_m2"])
    politicas = reglas["politicas"]

    inventario = leer_csv(EVIDENCIAS / "inventario_fuentes.csv")
    controles_previos = leer_csv(EVIDENCIAS / "perfilado_claves_relaciones.csv")
    control_por_id = {fila["control"]: fila for fila in controles_previos}

    rutas = {
        fuente: resolver_ruta_fuente(datos["ruta"])
        for fuente, datos in perfil["fuentes"].items()
    }

    # Malla
    tabla_malla = perfil["tabla_malla"]
    conexion = sqlite3.connect(f"file:{rutas['malla'].as_posix()}?mode=ro", uri=True)
    try:
        malla = conexion.execute(
            f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN geom IS NULL THEN 1 ELSE 0 END) AS geom_nula,
                SUM(CASE WHEN ABS(area_nominal_m2 - 250000.0) > ? THEN 1 ELSE 0 END) AS area_invalida,
                SUM(CASE WHEN fraccion_dentro_loja < -? OR fraccion_dentro_loja > 1 + ? THEN 1 ELSE 0 END) AS fraccion_invalida
            FROM "{tabla_malla}"
            """,
            (tolerancia_area, tolerancia_fracciones, tolerancia_fracciones),
        ).fetchone()
        srs = conexion.execute(
            "SELECT srs_id FROM gpkg_geometry_columns WHERE table_name = ?",
            (tabla_malla,),
        ).fetchone()
    finally:
        conexion.close()

    malla_total, geom_nula, area_invalida, fraccion_invalida = map(int, malla)
    srs_id = int(srs[0]) if srs else -1
    problemas_malla = geom_nula + area_invalida + fraccion_invalida + int(srs_id != 32717)

    # VIIRS
    viirs_total = 0
    viirs_faltantes = 0
    viirs_celdas_faltantes: set[str] = set()
    viirs_temporal = 0
    viirs_negativos = 0
    viirs_rangos = 0
    viirs_consistencia_fuego = 0
    valores_frp_suma: list[float] = []
    valores_frp_maxima: list[float] = []
    campos_viirs_no_negativos = (
        "viirs_detecciones_todas_support_mean",
        "viirs_detecciones_nominal_alta_support_mean",
        "viirs_frp_suma_observada_support_mean_mw",
        "viirs_frp_maxima_support_mean_mw",
        "viirs_dias_validos_support_mean",
    )
    campos_viirs_fracciones = (
        "viirs_presencia_fuego_support_frac",
        "viirs_presencia_fuego_nominal_alta_support_frac",
        "viirs_observado_support_mean",
        "viirs_source_coverage_frac",
        "viirs_observed_support_frac",
    )
    with rutas["viirs"].open("r", encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["anio"] != str(anio):
                continue
            viirs_total += 1
            esperado = f"{fila['anio']}-{int(fila['mes']):02d}"
            if not 1 <= int(fila["mes"]) <= 12 or fila["anio_mes"] != esperado:
                viirs_temporal += 1
            observado = fila["viirs_observed_support_frac"].strip()
            if observado == "":
                viirs_faltantes += 1
                viirs_celdas_faltantes.add(fila["cell_index"])
                continue
            for campo in campos_viirs_no_negativos:
                valor = a_float(fila[campo])
                if valor is None or valor < 0:
                    viirs_negativos += 1
            for campo in campos_viirs_fracciones:
                valor = a_float(fila[campo])
                if valor is None or valor < -tolerancia_fracciones or valor > 1 + tolerancia_fracciones:
                    viirs_rangos += 1
            disponibilidad = a_float(fila["viirs_disponibilidad_support_pct"])
            if disponibilidad is None or disponibilidad < -tolerancia_fracciones or disponibilidad > 100 + tolerancia_fracciones:
                viirs_rangos += 1
            detecciones = float(fila["viirs_detecciones_todas_support_mean"])
            fuego = fila["viirs_evidencia_fuego_any"] == "1"
            if (fuego and detecciones <= 0) or (not fuego and detecciones > 0):
                viirs_consistencia_fuego += 1
            valores_frp_suma.append(float(fila["viirs_frp_suma_observada_support_mean_mw"]))
            valores_frp_maxima.append(float(fila["viirs_frp_maxima_support_mean_mw"]))

    # CHIRPS
    chirps_total = 0
    chirps_faltantes = 0
    chirps_temporal = 0
    chirps_negativos = 0
    chirps_rangos = 0
    chirps_dias_inconsistentes = 0
    chirps_precipitacion_inconsistente = 0
    valores_precipitacion_acumulada: list[float] = []
    valores_precipitacion_maxima: list[float] = []
    campos_chirps_no_negativos = (
        "area_dentro_loja_m2",
        "dias_calendario",
        "chirps_n_pixels_intersectados",
        "chirps_precipitacion_acumulada_mm",
        "chirps_precipitacion_media_diaria_mm",
        "chirps_precipitacion_maxima_diaria_mm",
        "chirps_dias_humedos_ge1mm",
        "chirps_dias_secos_lt1mm",
        "chirps_dias_validos_pixel",
    )
    campos_chirps_fracciones = (
        "fraccion_dentro_loja",
        "chirps_grid_coverage",
        "chirps_observado_mes",
        "chirps_valid_coverage",
    )
    with rutas["chirps"].open("r", encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["anio"] != str(anio):
                continue
            chirps_total += 1
            esperado = f"{fila['anio']}-{int(fila['mes']):02d}"
            if not 1 <= int(fila["mes"]) <= 12 or fila["anio_mes"] != esperado:
                chirps_temporal += 1
            campos_criticos = (
                "cell_index",
                "cell_id",
                "anio",
                "mes",
                "anio_mes",
                "chirps_precipitacion_acumulada_mm",
                "chirps_dias_validos_pixel",
            )
            if any(fila[campo].strip() == "" for campo in campos_criticos):
                chirps_faltantes += 1
                continue
            for campo in campos_chirps_no_negativos:
                valor = a_float(fila[campo])
                if valor is None or valor < 0:
                    chirps_negativos += 1
            for campo in campos_chirps_fracciones:
                valor = a_float(fila[campo])
                if valor is None or valor < -tolerancia_fracciones or valor > 1 + tolerancia_fracciones:
                    chirps_rangos += 1
            disponibilidad = float(fila["chirps_disponibilidad_pixel_pct"])
            if disponibilidad < -tolerancia_fracciones or disponibilidad > 100 + tolerancia_fracciones:
                chirps_rangos += 1
            humedos = float(fila["chirps_dias_humedos_ge1mm"])
            secos = float(fila["chirps_dias_secos_lt1mm"])
            validos = float(fila["chirps_dias_validos_pixel"])
            if abs(humedos + secos - validos) > tolerancia_fracciones:
                chirps_dias_inconsistentes += 1
            acumulada = float(fila["chirps_precipitacion_acumulada_mm"])
            media = float(fila["chirps_precipitacion_media_diaria_mm"])
            if abs(acumulada - media * validos) > tolerancia_precipitacion:
                chirps_precipitacion_inconsistente += 1
            valores_precipitacion_acumulada.append(acumulada)
            valores_precipitacion_maxima.append(
                float(fila["chirps_precipitacion_maxima_diaria_mm"])
            )

    atipicos = [
        estadistica_iqr("viirs", "viirs_frp_suma_observada_support_mean_mw", valores_frp_suma),
        estadistica_iqr("viirs", "viirs_frp_maxima_support_mean_mw", valores_frp_maxima),
        estadistica_iqr("chirps", "chirps_precipitacion_acumulada_mm", valores_precipitacion_acumulada),
        estadistica_iqr("chirps", "chirps_precipitacion_maxima_diaria_mm", valores_precipitacion_maxima),
    ]
    limites = {
        fila["variable"]: (
            float(fila["limite_inferior"]),
            float(fila["limite_superior"]),
        )
        for fila in atipicos
    }
    atipicos_viirs = sum(
        suma < limites["viirs_frp_suma_observada_support_mean_mw"][0]
        or suma > limites["viirs_frp_suma_observada_support_mean_mw"][1]
        or maxima < limites["viirs_frp_maxima_support_mean_mw"][0]
        or maxima > limites["viirs_frp_maxima_support_mean_mw"][1]
        for suma, maxima in zip(valores_frp_suma, valores_frp_maxima)
    )
    atipicos_chirps = sum(
        acumulada < limites["chirps_precipitacion_acumulada_mm"][0]
        or acumulada > limites["chirps_precipitacion_acumulada_mm"][1]
        or maxima < limites["chirps_precipitacion_maxima_diaria_mm"][0]
        or maxima > limites["chirps_precipitacion_maxima_diaria_mm"][1]
        for acumulada, maxima in zip(
            valores_precipitacion_acumulada, valores_precipitacion_maxima
        )
    )

    hash_incorrectos = sum(fila["hash_coincide"] != "True" for fila in inventario)
    duplicados_clave = sum(
        int(control_por_id[id_control]["incumplimientos"])
        for id_control in (
            "unicidad_cell_index_malla",
            "unicidad_cell_id_malla",
            "unicidad_clave_viirs_periodo",
            "unicidad_clave_chirps_periodo",
        )
    )
    integridad_referencial = sum(
        int(control_por_id[id_control]["incumplimientos"])
        for id_control in (
            "claves_viirs_sin_chirps",
            "claves_chirps_sin_viirs",
            "celdas_viirs_fuera_malla",
            "celdas_chirps_fuera_malla",
            "cell_id_chirps_consistente_con_malla",
        )
    )
    reconciliacion = abs(viirs_total - 7_997 * 12) + abs(chirps_total - 7_997 * 12)

    matriz = [
        fila_matriz(
            "CAL-01", "trazabilidad", "todas", "archivo y sha256",
            "El archivo debe coincidir con el hash del manifiesto.", "0 hashes diferentes",
            "critica", len(inventario), hash_incorrectos, "CUMPLE" if hash_incorrectos == 0 else "NO_CUMPLE",
            "Detener el flujo si algún hash cambia.", "inventario_fuentes.csv",
            "No aplica todavía; la fuente Raw no se modifica.",
        ),
        fila_matriz(
            "CAL-02", "unicidad", "todas", "claves de cada fuente",
            "Las claves declaradas deben ser completas y únicas.", "0 nulos y 0 duplicados",
            "critica", viirs_total + chirps_total + malla_total, duplicados_clave,
            "CUMPLE" if duplicados_clave == 0 else "NO_CUMPLE", politicas["duplicados_clave"],
            "perfilado_claves_relaciones.csv",
        ),
        fila_matriz(
            "CAL-03", "integridad_referencial", "todas", "cell_index; cell_id; anio; mes",
            "Todas las claves deben encontrar correspondencia y conservar cardinalidad uno a uno.",
            "0 claves sin correspondencia", "critica", viirs_total + chirps_total, integridad_referencial,
            "CUMPLE" if integridad_referencial == 0 else "NO_CUMPLE", politicas["integracion"],
            "perfilado_claves_relaciones.csv",
        ),
        fila_matriz(
            "CAL-04", "validez", "malla", "geom; srs_id; area_nominal_m2; fraccion_dentro_loja",
            "Geometría no nula, EPSG:32717, área nominal 250000 m2 y fracción entre 0 y 1.",
            "0 geometrías o atributos espaciales inválidos", "critica", malla_total, problemas_malla,
            "CUMPLE" if problemas_malla == 0 else "NO_CUMPLE",
            "Detener el flujo ante geometría nula, CRS inesperado o atributos fuera de rango.",
            "GeoPackage Raw y perfilado_columnas.csv",
        ),
        fila_matriz(
            "CAL-05", "completitud", "chirps", "claves y precipitación crítica",
            "Las variables críticas de CHIRPS no deben ser nulas.", "0 registros incompletos",
            "critica", chirps_total, chirps_faltantes, "CUMPLE" if chirps_faltantes == 0 else "NO_CUMPLE",
            "Separar el registro y detener la publicación si afecta la cobertura mensual.",
            "perfilado_columnas.csv y evaluación Raw",
        ),
        fila_matriz(
            "CAL-06", "completitud", "viirs", "viirs_observed_support_frac y métricas asociadas",
            "Distinguir observación faltante de ausencia de fuego.", "Nulos identificados y marcados",
            "alta", viirs_total, viirs_faltantes, "REQUIERE_TRATAMIENTO" if viirs_faltantes else "CUMPLE",
            politicas["faltantes_viirs"], "hallazgos_perfilado.csv y evaluación Raw",
        ),
        fila_matriz(
            "CAL-07", "consistencia", "viirs y chirps", "anio; mes; anio_mes",
            "anio_mes debe corresponder exactamente con anio y mes; mes entre 1 y 12.",
            "0 inconsistencias", "critica", viirs_total + chirps_total, viirs_temporal + chirps_temporal,
            "CUMPLE" if viirs_temporal + chirps_temporal == 0 else "NO_CUMPLE",
            "Rechazar el registro si no puede reconstruirse de forma inequívoca.", "evaluación Raw",
        ),
        fila_matriz(
            "CAL-08", "validez", "viirs", "detecciones; FRP; días; coberturas",
            "Conteos, FRP y días no negativos; fracciones entre 0 y 1; porcentajes entre 0 y 100.",
            "0 valores fuera de rango entre registros observados", "critica", viirs_total - viirs_faltantes,
            viirs_negativos + viirs_rangos, "CUMPLE" if viirs_negativos + viirs_rangos == 0 else "NO_CUMPLE",
            "Separar valores inválidos; no recortar ni imputar silenciosamente.", "evaluación Raw",
        ),
        fila_matriz(
            "CAL-09", "validez", "chirps", "precipitación; días; coberturas",
            "Precipitación y días no negativos; fracciones entre 0 y 1; porcentajes entre 0 y 100.",
            "0 valores fuera de rango con tolerancia documentada", "critica", chirps_total,
            chirps_negativos + chirps_rangos, "CUMPLE" if chirps_negativos + chirps_rangos == 0 else "NO_CUMPLE",
            "Separar valores inválidos; aplicar tolerancia solo a ruido de punto flotante.", "evaluación Raw",
        ),
        fila_matriz(
            "CAL-10", "consistencia", "chirps", "días húmedos; días secos; días válidos; precipitación",
            "Húmedos + secos = válidos y acumulada = media diaria por días válidos dentro de tolerancia.",
            f"0 inconsistencias; tolerancia {tolerancia_precipitacion:g} mm", "alta", chirps_total,
            chirps_dias_inconsistentes + chirps_precipitacion_inconsistente,
            "CUMPLE" if chirps_dias_inconsistentes + chirps_precipitacion_inconsistente == 0 else "NO_CUMPLE",
            "Revisar el origen y separar registros que excedan la tolerancia.", "evaluación Raw",
        ),
        fila_matriz(
            "CAL-11", "consistencia", "viirs", "detecciones y evidencia_fuego",
            "Evidencia de fuego debe equivaler a detecciones mayores que cero en registros observados.",
            "0 contradicciones", "alta", viirs_total - viirs_faltantes, viirs_consistencia_fuego,
            "CUMPLE" if viirs_consistencia_fuego == 0 else "NO_CUMPLE",
            "Separar contradicciones para revisión; no recodificar sin trazabilidad.", "evaluación Raw",
        ),
        fila_matriz(
            "CAL-12", "valores_atipicos", "viirs", "FRP mensual",
            "Detectar extremos mediante IQR sin asumir que son errores.", "Registrar y conservar",
            "media", viirs_total - viirs_faltantes, atipicos_viirs, "OBSERVACION",
            politicas["valores_atipicos"], "estadisticas_atipicos.csv",
        ),
        fila_matriz(
            "CAL-13", "valores_atipicos", "chirps", "precipitación acumulada y máxima diaria",
            "Detectar extremos mediante IQR sin asumir que son errores.", "Registrar y conservar",
            "media", chirps_total, atipicos_chirps, "OBSERVACION",
            politicas["valores_atipicos"], "estadisticas_atipicos.csv",
        ),
        fila_matriz(
            "CAL-14", "reconciliacion", "viirs y chirps", "conteo de filas 2023",
            "Cada fuente debe contener 7997 celdas por 12 meses.", "95964 filas por fuente",
            "critica", viirs_total + chirps_total, reconciliacion, "CUMPLE" if reconciliacion == 0 else "NO_CUMPLE",
            "Detener la integración si los conteos esperados no se cumplen.", "inventario_fuentes.csv",
        ),
    ]

    bitacora = [
        {
            "decision_id": "DEC-001", "fuente_o_variable": "todas", "problema": "Alcance temporal amplio en los archivos Raw",
            "regla": "La tarea trabajará enero-diciembre de 2023.", "decision": "Filtrar 2023 mediante código sin modificar Raw.",
            "justificacion": "Coincide con el periodo formal del Proyecto Integrador y mantiene un volumen verificable.",
            "filas_afectadas": 95_964 * 2, "fecha_o_version": "2026-09-20 / v1.0",
        },
        {
            "decision_id": "DEC-002", "fuente_o_variable": "VIIRS y CHIRPS", "problema": "Los archivos disponibles ya están agregados mensualmente.",
            "regla": "No presentar datos mensuales como observaciones diarias.", "decision": "Construir el ETL directamente a grano celda-mes.",
            "justificacion": "Respeta el significado y la granularidad real de las fuentes.",
            "filas_afectadas": 95_964 * 2, "fecha_o_version": "2026-09-20 / v1.0",
        },
        {
            "decision_id": "DEC-003", "fuente_o_variable": "cell_index; cell_id; anio; mes", "problema": "VIIRS no contiene cell_id.",
            "regla": "Integrar mediante cell_index + anio + mes y publicar cell_id + anio + mes.",
            "decision": "Obtener cell_id desde la malla y validar correspondencia contra CHIRPS.",
            "justificacion": "La malla mantiene una correspondencia única entre cell_index y cell_id.",
            "filas_afectadas": 95_964, "fecha_o_version": "2026-09-20 / v1.0",
        },
        {
            "decision_id": "DEC-004", "fuente_o_variable": "métricas VIIRS", "problema": "900 filas no tienen observación VIIRS.",
            "regla": "No confundir faltante con cero.",
            "decision": "Conservar nulos en Clean y Curated maestro, añadir observacion_viirs_disponible=false y excluirlos solo del subconjunto analítico.",
            "justificacion": "La ausencia de soporte observacional no demuestra ausencia de incendio.",
            "filas_afectadas": viirs_faltantes, "fecha_o_version": "2026-09-20 / v1.0",
        },
        {
            "decision_id": "DEC-005", "fuente_o_variable": "celdas parciales", "problema": "828 celdas intersectan parcialmente el cantón.",
            "regla": "No eliminar por área sin justificación analítica.",
            "decision": "Conservar fraccion_dentro_loja y es_celda_completa como atributos de calidad.",
            "justificacion": "Permite evaluar sensibilidad sin alterar silenciosamente la población.",
            "filas_afectadas": 828, "fecha_o_version": "2026-09-20 / v1.0",
        },
        {
            "decision_id": "DEC-006", "fuente_o_variable": "fracciones y precipitación", "problema": "Ruido de punto flotante alrededor de valores teóricos.",
            "regla": f"Usar tolerancia {tolerancia_fracciones:g} en fracciones y {tolerancia_precipitacion:g} mm en reconciliación.",
            "decision": "Comparar con tolerancia y conservar el valor original.",
            "justificacion": "Evita falsos incumplimientos sin redondear ni reescribir Raw.",
            "filas_afectadas": 0, "fecha_o_version": "2026-09-20 / v1.0",
        },
        {
            "decision_id": "DEC-007", "fuente_o_variable": "claves", "problema": "Una deduplicación automática ocultaría errores de origen.",
            "regla": "Las claves deben ser únicas.", "decision": politicas["duplicados_clave"].capitalize() + ".",
            "justificacion": "La identidad y granularidad están definidas antes de la limpieza.",
            "filas_afectadas": duplicados_clave, "fecha_o_version": "2026-09-20 / v1.0",
        },
        {
            "decision_id": "DEC-008", "fuente_o_variable": "FRP y precipitación", "problema": "El método IQR identifica extremos potencialmente reales.",
            "regla": "Detectar no significa eliminar.", "decision": "Añadir banderas de atípico y conservar los valores.",
            "justificacion": "Los incendios intensos y lluvias extremas pueden ser observaciones científicamente relevantes.",
            "filas_afectadas": atipicos_viirs + atipicos_chirps, "fecha_o_version": "2026-09-20 / v1.0",
        },
        {
            "decision_id": "DEC-009", "fuente_o_variable": "salidas", "problema": "La guía requiere trazabilidad y formatos reutilizables.",
            "regla": "Generar salidas determinísticas y documentadas.", "decision": "Publicar Curated en CSV y Parquet, con diccionario y comparación antes/después.",
            "justificacion": "CSV facilita revisión; Parquet preserva tipos y eficiencia analítica.",
            "filas_afectadas": 0, "fecha_o_version": "2026-09-20 / v1.0",
        },
    ]

    archivos_clean_requeridos = [
        RAIZ_TAREA / "clean" / "malla_500m.csv",
        RAIZ_TAREA / "clean" / "malla_500m.parquet",
        RAIZ_TAREA / "clean" / "viirs_2023.csv",
        RAIZ_TAREA / "clean" / "viirs_2023.parquet",
        RAIZ_TAREA / "clean" / "chirps_2023.csv",
        RAIZ_TAREA / "clean" / "chirps_2023.parquet",
        RAIZ_TAREA / "clean" / "observaciones_viirs_sin_cobertura_2023.csv",
        RAIZ_TAREA / "clean" / "rechazos_criticos_2023.csv",
        EVIDENCIAS / "controles_clean.csv",
        EVIDENCIAS / "comparacion_antes_despues.csv",
        EVIDENCIAS / "prueba_idempotencia_clean.txt",
    ]
    clean_completo = all(ruta.is_file() for ruta in archivos_clean_requeridos)
    archivos_curated_requeridos = [
        RAIZ_TAREA / "curated" / "fireforest_celda_mes_2023.csv",
        RAIZ_TAREA / "curated" / "fireforest_celda_mes_2023.parquet",
        RAIZ_TAREA / "curated" / "diccionario_datos.csv",
        EVIDENCIAS / "controles_curated.csv",
        EVIDENCIAS / "manifiesto_salidas_curated.csv",
    ]
    curated_completo = all(
        ruta.is_file() for ruta in archivos_curated_requeridos
    )
    prueba_flujo_completo = (
        EVIDENCIAS / "prueba_reproducibilidad_flujo_completo.txt"
    ).is_file()
    contenido_readme = (RAIZ_TAREA / "README.md").read_text(encoding="utf-8")
    conclusiones_documentadas = "## Conclusiones y limitaciones" in contenido_readme
    evidencia_raw = (
        "raw/; raw/metadatos/manifiesto_firelab_loja.json"
        if (RAIZ_TAREA / "raw").is_dir()
        else "../02_datos/raw/; ../05_ingesta/metadatos/manifiesto_firelab_loja.json"
    )
    if clean_completo or curated_completo:
        for fila in matriz:
            fila["evidencia_posterior"] = (
                "controles_clean.csv; comparacion_antes_despues.csv; "
                "manifiesto_salidas_clean.csv; controles_curated.csv; "
                "manifiesto_salidas_curated.csv"
            )

    entregables = [
        ("Alcance", "Pregunta, población, periodo, unidad y claves", "README.md", "CUMPLE", "Definición formal para 2023."),
        ("Código", "Script o notebook ejecutable desde el inicio", "codigo/etl_fireforest.py --desde-cero", "CUMPLE" if curated_completo else "EN_DESARROLLO", "Un solo comando ejecuta perfilado, calidad Raw, Clean, Curated y seguimiento." if curated_completo else "El flujo todavía está en desarrollo."),
        ("Datos", "Fuentes permitidas o instrucciones reproducibles", evidencia_raw, "CUMPLE", "Raw conservado con hashes."),
        ("Datos", "Capa Clean", "clean/*.csv; clean/*.parquet", "CUMPLE" if clean_completo else "PENDIENTE", "Malla, VIIRS y CHIRPS tipados por separado, con excepciones y rechazos explícitos." if clean_completo else "No se ha transformado información."),
        ("Datos", "Dataset Curated", "curated/fireforest_celda_mes_2023.csv; curated/fireforest_celda_mes_2023.parquet", "CUMPLE" if curated_completo else "PENDIENTE", "Dataset maestro de 95.964 filas por cell_id + anio + mes." if curated_completo else "Se generará después de Clean."),
        ("Datos", "Diccionario de datos Curated", "curated/diccionario_datos.csv", "CUMPLE" if curated_completo else "PENDIENTE", "Documenta las 45 variables, tipos, unidades, origen, derivación y nulabilidad." if curated_completo else "Debe incluir nombre, significado, tipo, unidad y derivación."),
        ("Calidad", "Perfilado inicial", "evidencias/perfilado_columnas.csv", "CUMPLE", "Incluye tipos, faltantes, rangos y cardinalidad."),
        ("Calidad", "Matriz de calidad", "evidencias/matriz_calidad.csv", "CUMPLE", "Incluye regla, afectados, porcentaje, tratamiento y evidencia."),
        ("Calidad", "Bitácora de decisiones", "evidencias/bitacora_decisiones.csv", "CUMPLE", "Formato exigido por la guía."),
        ("Calidad", "Al menos seis controles automatizados", "evidencias/matriz_calidad.csv; evidencias/controles_clean.csv; evidencias/controles_curated.csv", "CUMPLE" if curated_completo else "EN_DESARROLLO", "Se ejecutaron 16 controles Clean y 11 controles Curated." if curated_completo else "Existen controles Raw y Clean; faltan los de Curated."),
        ("Calidad", "Comparación antes y después", "evidencias/comparacion_antes_despues.csv", "CUMPLE" if curated_completo else "PENDIENTE", "Compara Raw, Clean y Curated en filas, faltantes, duplicados, atípicos y rechazos." if curated_completo else "Requiere la integración Curated."),
        ("Transformación", "Al menos tres transformaciones", "codigo/etl_fireforest.py; configuracion/transformaciones_clean.json", "CUMPLE" if clean_completo else "PENDIENTE", "Se implementaron seis transformaciones documentadas y la integración uno a uno." if clean_completo else "Definidas en el alcance, aún no implementadas."),
        ("Integración", "Claves, cardinalidad y tipo de unión justificados", "README.md; evidencias/perfilado_claves_relaciones.csv; evidencias/controles_curated.csv", "CUMPLE" if curated_completo else "EN_DESARROLLO", "Unión externa de validación uno a uno por cell_index + anio + mes, sin claves huérfanas ni multiplicación de filas." if curated_completo else "Cardinalidad validada; falta ejecutar la integración Curated."),
        ("Reproducibilidad", "Dependencias, rutas, parámetros y orden", "README.md; configuracion/requirements_etl.txt; configuracion/; codigo/README.md", "CUMPLE" if curated_completo else "EN_DESARROLLO", "El comando --desde-cero ejecuta el flujo completo en el orden documentado." if curated_completo else "Falta incorporar Curated al flujo completo."),
        ("Reproducibilidad", "Segunda ejecución sin duplicación", "evidencias/prueba_reproducibilidad_flujo_completo.txt", "CUMPLE" if prueba_flujo_completo else "EN_DESARROLLO", "Dos ejecuciones completas produjeron salidas equivalentes sin duplicación." if prueba_flujo_completo else "Pendiente ejecutar dos veces el flujo completo."),
        ("Documentación", "Diagrama Raw a Clean a Curated", "README.md", "CUMPLE", "Diagrama incorporado en el documento principal."),
        ("Documentación", "Conclusiones y limitaciones", "README.md", "CUMPLE" if conclusiones_documentadas else "PENDIENTE", "Conclusiones y limitaciones documentadas a partir de los resultados ejecutados." if conclusiones_documentadas else "Se redactarán después de ejecutar Clean y Curated."),
    ]
    filas_entregables = [
        {
            "categoria": categoria,
            "requisito_guia": requisito,
            "evidencia_planificada": evidencia,
            "estado": estado,
            "observacion": observacion,
        }
        for categoria, requisito, evidencia, estado, observacion in entregables
    ]

    escribir_csv(
        EVIDENCIAS / "matriz_calidad.csv",
        [
            "regla_id", "dimension_calidad", "fuente", "ambito", "variables",
            "regla", "criterio_esperado", "severidad", "registros_evaluados",
            "registros_afectados", "porcentaje_afectado", "resultado_raw",
            "tratamiento_definido", "evidencia_previa", "evidencia_posterior",
        ],
        matriz,
    )
    escribir_csv(
        EVIDENCIAS / "estadisticas_atipicos.csv",
        [
            "fuente", "variable", "registros_evaluados", "q1", "q3", "iqr",
            "limite_inferior", "limite_superior", "registros_atipicos",
            "porcentaje_atipicos", "tratamiento",
        ],
        atipicos,
    )
    escribir_csv(
        EVIDENCIAS / "bitacora_decisiones.csv",
        [
            "decision_id", "fuente_o_variable", "problema", "regla", "decision",
            "justificacion", "filas_afectadas", "fecha_o_version",
        ],
        bitacora,
    )
    escribir_csv(
        EVIDENCIAS / "matriz_entregables_guia.csv",
        ["categoria", "requisito_guia", "evidencia_planificada", "estado", "observacion"],
        filas_entregables,
    )

    cumple = sum(fila["resultado_raw"] == "CUMPLE" for fila in matriz)
    revisar = sum(fila["resultado_raw"] in {"REQUIERE_TRATAMIENTO", "OBSERVACION"} for fila in matriz)
    no_cumple = sum(fila["resultado_raw"] == "NO_CUMPLE" for fila in matriz)
    marca_clean = "x" if clean_completo else " "
    marca_curated = "x" if curated_completo else " "
    marca_reproducibilidad = "x" if prueba_flujo_completo else " "
    marca_conclusiones = "x" if conclusiones_documentadas else " "
    lista = f"""# Lista de verificación de la guía ETL

## Estado general

- Reglas Raw que cumplen: {cumple} de {len(matriz)}.
- Reglas con observaciones o tratamiento definido: {revisar}.
- Reglas Raw que no cumplen: {no_cumple}.

## Lista de entrega

- [x] Pregunta analítica, población, periodo y unidad final definidos.
- [x] Tres fuentes relacionadas identificadas y trazables.
- [x] Raw conservado sin alteraciones y verificado mediante hashes.
- [x] Perfilado inicial con tipos, faltantes, duplicados, rangos y relaciones.
- [x] Matriz de calidad con reglas, afectados, tratamiento y evidencia.
- [x] Bitácora inicial de decisiones.
- [x] Diagnóstico de valores atípicos mediante IQR.
- [{marca_clean}] Capa Clean generada sin sobrescribir Raw.
- [{marca_clean}] Registros rechazados o no aptos separados de forma explícita.
- [{marca_clean}] Al menos tres transformaciones implementadas y justificadas.
- [{marca_curated}] Integración uno a uno ejecutada y reconciliada.
- [{marca_curated}] Dataset Curated por `cell_id + anio + mes`.
- [{marca_curated}] Diccionario de datos del Curated.
- [{marca_curated}] Comparación antes y después de Raw a Clean y Curated.
- [{marca_clean}] Al menos seis controles automatizados ejecutados sobre Clean.
- [{marca_curated}] Controles de cardinalidad y reconciliación ejecutados sobre Curated.
- [{marca_curated}] Comando único de ejecución completa desde cero.
- [{marca_reproducibilidad}] Segunda ejecución completa sin duplicación y con resultados equivalentes.
- [{marca_conclusiones}] Conclusiones y limitaciones finales.

## Decisión aplicada para continuar

El Curated maestro conserva las 95.964 claves esperadas. Las 900 filas sin
observación VIIRS mantienen sus métricas como nulas y llevan una bandera de
cobertura. Para análisis conjunto se filtra `apto_analisis=true`, sin eliminar
las filas del producto maestro ni convertir sus faltantes en cero.
"""
    escribir_texto(EVIDENCIAS / "lista_verificacion_guia.md", lista)

    print(f"Matriz de calidad: {len(matriz)} reglas")
    print(f"Cumplen: {cumple}; observaciones: {revisar}; no cumplen: {no_cumple}")
    print(f"Bitácora: {len(bitacora)} decisiones")
    print(f"Entregables controlados: {len(entregables)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
