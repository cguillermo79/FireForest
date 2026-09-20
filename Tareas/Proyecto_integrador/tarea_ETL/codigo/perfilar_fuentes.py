"""Inventaría y perfila las fuentes Raw de la tarea ETL de FireForest.

El script trabaja únicamente en modo de lectura sobre 02_datos/raw. Produce
evidencias determinísticas en tarea_ETL/evidencias y no limpia, transforma ni
carga registros en PostgreSQL o MongoDB.

Uso desde la raíz de FireForest:

    .venv/Scripts/python.exe \
        Tareas/Proyecto_integrador/tarea_ETL/codigo/perfilar_fuentes.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


RUTA_SCRIPT = Path(__file__).resolve()
RAIZ_TAREA = RUTA_SCRIPT.parents[1]
RAIZ_INTEGRADOR = RAIZ_TAREA.parent
RUTA_CONFIGURACION = RAIZ_TAREA / "configuracion" / "perfilado.json"
RUTA_MANIFIESTO = (
    RAIZ_INTEGRADOR
    / "05_ingesta"
    / "metadatos"
    / "manifiesto_firelab_loja.json"
)
DIRECTORIO_EVIDENCIAS = RAIZ_TAREA / "evidencias"

LIMITE_DISTINTOS = 10_000
LIMITE_CATEGORIAS = 100
BLOQUE_HASH = 8 * 1024 * 1024


@dataclass
class EstadisticaColumna:
    filas: int = 0
    nulos: int = 0
    enteros_validos: bool = True
    numeros_validos: bool = True
    minimo_numerico: float | None = None
    maximo_numerico: float | None = None
    distintos: set[str] = field(default_factory=set)
    distintos_truncados: bool = False
    categorias: Counter[str] = field(default_factory=Counter)
    categorias_truncadas: bool = False

    def agregar(self, valor: Any) -> None:
        self.filas += 1
        if valor is None or str(valor).strip() == "":
            self.nulos += 1
            return

        texto = str(valor).strip()

        if not self.distintos_truncados:
            self.distintos.add(texto)
            if len(self.distintos) > LIMITE_DISTINTOS:
                self.distintos_truncados = True
                self.distintos.clear()

        if texto in self.categorias:
            self.categorias[texto] += 1
        elif len(self.categorias) < LIMITE_CATEGORIAS:
            self.categorias[texto] = 1
        else:
            self.categorias_truncadas = True

        try:
            int(texto)
        except (TypeError, ValueError):
            self.enteros_validos = False

        try:
            numero = float(texto)
            if not math.isfinite(numero):
                raise ValueError("valor no finito")
            if self.minimo_numerico is None or numero < self.minimo_numerico:
                self.minimo_numerico = numero
            if self.maximo_numerico is None or numero > self.maximo_numerico:
                self.maximo_numerico = numero
        except (TypeError, ValueError):
            self.numeros_validos = False

    @property
    def no_nulos(self) -> int:
        return self.filas - self.nulos

    def tipo_inferido(self) -> str:
        if self.no_nulos == 0:
            return "sin_datos"
        if self.enteros_validos:
            return "entero"
        if self.numeros_validos:
            return "decimal"
        return "texto"

    def numero_distintos(self) -> str:
        if self.distintos_truncados:
            return f">{LIMITE_DISTINTOS}"
        return str(len(self.distintos))

    def valores_frecuentes(self) -> str:
        if self.categorias_truncadas:
            return "alta cardinalidad"
        pares = sorted(
            self.categorias.items(), key=lambda elemento: (-elemento[1], elemento[0])
        )[:10]
        return " | ".join(f"{valor}:{conteo}" for valor, conteo in pares)


def cargar_json(ruta: Path) -> dict[str, Any]:
    with ruta.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def sha256(ruta: Path) -> str:
    resumen = hashlib.sha256()
    with ruta.open("rb") as archivo:
        while bloque := archivo.read(BLOQUE_HASH):
            resumen.update(bloque)
    return resumen.hexdigest()


def formatear_numero(valor: float | None) -> str:
    if valor is None:
        return ""
    return format(valor, ".15g")


def escribir_csv(ruta: Path, columnas: list[str], filas: Iterable[dict[str, Any]]) -> None:
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    with temporal.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas, extrasaction="ignore")
        escritor.writeheader()
        for fila in filas:
            escritor.writerow(fila)
    os.replace(temporal, ruta)


def escribir_texto(ruta: Path, contenido: str) -> None:
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    temporal.write_text(contenido, encoding="utf-8")
    os.replace(temporal, ruta)


def fila_columna(
    fuente: str,
    ambito: str,
    variable: str,
    tipo_fuente: str,
    estadistica: EstadisticaColumna,
) -> dict[str, Any]:
    porcentaje = (
        estadistica.nulos * 100 / estadistica.filas if estadistica.filas else 0
    )
    numerica = estadistica.tipo_inferido() in {"entero", "decimal"}
    return {
        "fuente": fuente,
        "ambito": ambito,
        "variable": variable,
        "tipo_fuente": tipo_fuente,
        "tipo_inferido": estadistica.tipo_inferido(),
        "filas": estadistica.filas,
        "no_nulos": estadistica.no_nulos,
        "nulos": estadistica.nulos,
        "porcentaje_nulos": f"{porcentaje:.6f}",
        "valores_distintos": estadistica.numero_distintos(),
        "minimo": formatear_numero(estadistica.minimo_numerico) if numerica else "",
        "maximo": formatear_numero(estadistica.maximo_numerico) if numerica else "",
        "valores_frecuentes": estadistica.valores_frecuentes(),
    }


def codigo_clave(cell_index: str, anio: str, mes: str) -> int:
    return int(cell_index) * 1_000_000 + int(anio) * 100 + int(mes)


def perfilar_csv(
    fuente: str,
    ruta: Path,
    anio_estudio: int,
    tolerancia: float,
) -> dict[str, Any]:
    estadisticas_completas: dict[str, EstadisticaColumna] = {}
    estadisticas_periodo: dict[str, EstadisticaColumna] = {}
    claves_completas: set[int] = set()
    claves_periodo: set[int] = set()
    celdas_periodo: set[str] = set()
    periodos: set[str] = set()
    anios_encontrados: set[int] = set()
    nulos_clave_completo = 0
    nulos_clave_periodo = 0
    duplicados_completo = 0
    duplicados_periodo = 0
    filas_completas = 0
    filas_periodo = 0
    especiales: Counter[str] = Counter()
    celdas_viirs_sin_observacion: set[str] = set()
    pares_chirps: dict[str, str] = {}

    with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames is None:
            raise ValueError(f"El CSV no tiene encabezado: {ruta}")
        campos = list(lector.fieldnames)
        estadisticas_completas = {
            campo: EstadisticaColumna() for campo in campos
        }
        estadisticas_periodo = {
            campo: EstadisticaColumna() for campo in campos
        }

        for fila in lector:
            filas_completas += 1
            anio_fila = fila.get("anio", "").strip()
            if anio_fila:
                anios_encontrados.add(int(anio_fila))
            for campo in campos:
                estadisticas_completas[campo].agregar(fila.get(campo))

            valores_clave = (
                fila.get("cell_index", "").strip(),
                fila.get("anio", "").strip(),
                fila.get("mes", "").strip(),
            )
            if not all(valores_clave):
                nulos_clave_completo += 1
            else:
                clave = codigo_clave(*valores_clave)
                if clave in claves_completas:
                    duplicados_completo += 1
                else:
                    claves_completas.add(clave)
                periodos.add(fila.get("anio_mes", "").strip())

            if fila.get("anio", "").strip() != str(anio_estudio):
                continue

            filas_periodo += 1
            for campo in campos:
                estadisticas_periodo[campo].agregar(fila.get(campo))

            if not all(valores_clave):
                nulos_clave_periodo += 1
            else:
                clave = codigo_clave(*valores_clave)
                if clave in claves_periodo:
                    duplicados_periodo += 1
                else:
                    claves_periodo.add(clave)
                celdas_periodo.add(valores_clave[0])

            esperado_anio_mes = f"{fila.get('anio', '').strip()}-{int(fila.get('mes', '0')):02d}"
            if fila.get("anio_mes", "").strip() != esperado_anio_mes:
                especiales["anio_mes_inconsistente"] += 1

            if fuente == "viirs":
                observado = fila.get("viirs_observed_support_frac", "").strip()
                if observado == "":
                    especiales["filas_sin_observacion"] += 1
                    celdas_viirs_sin_observacion.add(valores_clave[0])
                if fila.get("viirs_evidencia_fuego_any", "").strip() == "1":
                    especiales["evidencia_fuego"] += 1
                if (
                    fila.get("viirs_evidencia_fuego_nominal_alta_any", "").strip()
                    == "1"
                ):
                    especiales["evidencia_fuego_nominal_alta"] += 1

            if fuente == "chirps":
                cobertura_texto = fila.get("chirps_valid_coverage", "").strip()
                if cobertura_texto:
                    cobertura = float(cobertura_texto)
                    if cobertura < 1:
                        especiales["cobertura_menor_que_uno"] += 1
                    if abs(cobertura - 1) > tolerancia:
                        especiales["cobertura_fuera_tolerancia"] += 1
                pares_chirps[valores_clave[0]] = fila.get("cell_id", "").strip()

    if not anios_encontrados:
        raise ValueError(f"{fuente}: no contiene años válidos")
    if len(anios_encontrados) == 1:
        ambito_completo = f"raw_{next(iter(anios_encontrados))}"
    else:
        ambito_completo = (
            f"completo_{min(anios_encontrados)}_{max(anios_encontrados)}"
        )

    filas_columnas: list[dict[str, Any]] = []
    for campo in campos:
        filas_columnas.append(
            fila_columna(
                fuente,
                ambito_completo,
                campo,
                "texto CSV",
                estadisticas_completas[campo],
            )
        )
        filas_columnas.append(
            fila_columna(
                fuente,
                f"periodo_{anio_estudio}",
                campo,
                "texto CSV",
                estadisticas_periodo[campo],
            )
        )

    return {
        "columnas": campos,
        "ambito_completo": ambito_completo,
        "filas_columnas": filas_columnas,
        "filas_completas": filas_completas,
        "filas_periodo": filas_periodo,
        "claves_unicas_completo": len(claves_completas),
        "claves_unicas_periodo": len(claves_periodo),
        "nulos_clave_completo": nulos_clave_completo,
        "nulos_clave_periodo": nulos_clave_periodo,
        "duplicados_completo": duplicados_completo,
        "duplicados_periodo": duplicados_periodo,
        "claves_periodo": claves_periodo,
        "celdas_periodo": celdas_periodo,
        "periodos": periodos,
        "especiales": especiales,
        "celdas_viirs_sin_observacion": celdas_viirs_sin_observacion,
        "pares_chirps": pares_chirps,
    }


def perfilar_malla(ruta: Path, tabla: str) -> dict[str, Any]:
    conexion = sqlite3.connect(f"file:{ruta.as_posix()}?mode=ro", uri=True)
    conexion.row_factory = sqlite3.Row
    try:
        contenido = conexion.execute(
            "SELECT table_name, data_type, identifier, srs_id "
            "FROM gpkg_contents WHERE table_name = ?",
            (tabla,),
        ).fetchone()
        geometria = conexion.execute(
            "SELECT column_name, geometry_type_name, srs_id "
            "FROM gpkg_geometry_columns WHERE table_name = ?",
            (tabla,),
        ).fetchone()
        if contenido is None or geometria is None:
            raise ValueError(f"No se encontró la capa {tabla} en {ruta}")

        definiciones = list(conexion.execute(f'PRAGMA table_info("{tabla}")'))
        columnas = [fila["name"] for fila in definiciones]
        tipos = {fila["name"]: fila["type"] for fila in definiciones}
        columna_geometria = geometria["column_name"]
        columnas_atributos = [c for c in columnas if c != columna_geometria]
        estadisticas = {c: EstadisticaColumna() for c in columnas_atributos}
        nulos_geometria = 0
        filas = 0
        mapeo: dict[str, str] = {}
        fracciones: dict[str, float] = {}
        duplicados_indice = 0
        duplicados_id = 0
        indices: set[str] = set()
        ids: set[str] = set()

        seleccion = ", ".join(f'"{c}"' for c in columnas_atributos)
        consulta = f'SELECT {seleccion}, "{columna_geometria}" IS NULL AS geom_nula FROM "{tabla}"'
        for fila in conexion.execute(consulta):
            filas += 1
            for columna in columnas_atributos:
                estadisticas[columna].agregar(fila[columna])
            nulos_geometria += int(fila["geom_nula"])
            indice = str(fila["cell_index"])
            cell_id = str(fila["cell_id"])
            if indice in indices:
                duplicados_indice += 1
            else:
                indices.add(indice)
            if cell_id in ids:
                duplicados_id += 1
            else:
                ids.add(cell_id)
            mapeo[indice] = cell_id
            fracciones[indice] = float(fila["fraccion_dentro_loja"])

        filas_columnas = [
            fila_columna("malla", "completo", c, tipos[c], estadisticas[c])
            for c in columnas_atributos
        ]
        estadistica_geometria = EstadisticaColumna(
            filas=filas,
            nulos=nulos_geometria,
            enteros_validos=False,
            numeros_validos=False,
        )
        filas_columnas.append(
            fila_columna(
                "malla",
                "completo",
                columna_geometria,
                geometria["geometry_type_name"],
                estadistica_geometria,
            )
        )

        conteos_espaciales = dict(
            conexion.execute(
                f"""
                SELECT
                    SUM(CASE WHEN es_celda_completa = 1 THEN 1 ELSE 0 END) AS completas,
                    SUM(CASE WHEN es_celda_completa = 0 THEN 1 ELSE 0 END) AS parciales,
                    SUM(CASE WHEN fraccion_dentro_loja < 0.50 THEN 1 ELSE 0 END) AS fraccion_lt_050,
                    SUM(CASE WHEN fraccion_dentro_loja < 0.10 THEN 1 ELSE 0 END) AS fraccion_lt_010,
                    MIN(fraccion_dentro_loja) AS fraccion_minima,
                    MAX(fraccion_dentro_loja) AS fraccion_maxima
                FROM "{tabla}"
                """
            ).fetchone()
        )

        return {
            "columnas": columnas,
            "filas_columnas": filas_columnas,
            "filas": filas,
            "mapeo": mapeo,
            "fracciones": fracciones,
            "duplicados_indice": duplicados_indice,
            "duplicados_id": duplicados_id,
            "nulos_indice": estadisticas["cell_index"].nulos,
            "nulos_id": estadisticas["cell_id"].nulos,
            "srs_id": geometria["srs_id"],
            "tipo_geometria": geometria["geometry_type_name"],
            "nulos_geometria": nulos_geometria,
            "conteos_espaciales": conteos_espaciales,
        }
    finally:
        conexion.close()


def resultado_control(incumplimientos: int) -> str:
    return "CUMPLE" if incumplimientos == 0 else "REVISAR"


def main() -> int:
    configuracion = cargar_json(RUTA_CONFIGURACION)
    manifiesto = cargar_json(RUTA_MANIFIESTO)
    anio_estudio = int(configuracion["anio_estudio"])
    tolerancia = float(configuracion["tolerancia_fracciones"])
    tabla_malla = configuracion["tabla_malla"]
    fuentes_config = configuracion["fuentes"]
    DIRECTORIO_EVIDENCIAS.mkdir(parents=True, exist_ok=True)

    manifiesto_por_destino = {
        entrada["destino_relativo_a_02_datos_raw"].replace("\\", "/"): entrada
        for entrada in manifiesto["archivos"]
    }

    rutas: dict[str, Path] = {}
    inventario_base: dict[str, dict[str, Any]] = {}
    for fuente, datos in fuentes_config.items():
        ruta = RAIZ_INTEGRADOR / datos["ruta"]
        if not ruta.is_file():
            raise FileNotFoundError(f"No existe la fuente {fuente}: {ruta}")
        rutas[fuente] = ruta
        relativo_raw = ruta.relative_to(RAIZ_INTEGRADOR / "02_datos" / "raw")
        clave_manifiesto = relativo_raw.as_posix()
        entrada_manifiesto = manifiesto_por_destino.get(clave_manifiesto)
        if entrada_manifiesto is None:
            raise ValueError(f"La fuente no consta en el manifiesto: {clave_manifiesto}")
        hash_calculado = sha256(ruta)
        inventario_base[fuente] = {
            "fuente": fuente,
            "archivo": ruta.name,
            "formato": datos["formato"],
            "ruta_relativa": datos["ruta"].replace("\\", "/"),
            "procedencia": entrada_manifiesto["origen_relativo_a_FIRELAB_Loja"],
            "periodo": entrada_manifiesto.get(
                "periodo", "no aplica" if fuente == "malla" else "2019-2025"
            ),
            "grano": datos["grano"],
            "clave_esperada": datos["clave"],
            "tamano_bytes": ruta.stat().st_size,
            "sha256_manifiesto": entrada_manifiesto["sha256"],
            "sha256_calculado": hash_calculado,
            "hash_coincide": hash_calculado == entrada_manifiesto["sha256"],
        }
        if not inventario_base[fuente]["hash_coincide"]:
            raise ValueError(f"El hash no coincide para {fuente}: {ruta}")

    print("Perfilando malla...")
    malla = perfilar_malla(rutas["malla"], tabla_malla)
    print("Perfilando VIIRS...")
    viirs = perfilar_csv("viirs", rutas["viirs"], anio_estudio, tolerancia)
    print("Perfilando CHIRPS...")
    chirps = perfilar_csv("chirps", rutas["chirps"], anio_estudio, tolerancia)

    inventario = []
    for fuente, resultado in (("malla", malla), ("viirs", viirs), ("chirps", chirps)):
        fila = dict(inventario_base[fuente])
        fila["filas"] = resultado.get("filas", resultado.get("filas_completas"))
        fila["columnas"] = len(resultado["columnas"])
        inventario.append(fila)

    perfilado_columnas = sorted(
        malla["filas_columnas"] + viirs["filas_columnas"] + chirps["filas_columnas"],
        key=lambda fila: (fila["fuente"], fila["ambito"], fila["variable"]),
    )

    claves_solo_viirs = viirs["claves_periodo"] - chirps["claves_periodo"]
    claves_solo_chirps = chirps["claves_periodo"] - viirs["claves_periodo"]
    celdas_viirs_fuera_malla = viirs["celdas_periodo"] - set(malla["mapeo"])
    celdas_chirps_fuera_malla = chirps["celdas_periodo"] - set(malla["mapeo"])
    cell_id_chirps_inconsistente = sum(
        1
        for indice, cell_id in chirps["pares_chirps"].items()
        if malla["mapeo"].get(indice) != cell_id
    )

    controles_claves = [
        {
            "control": "unicidad_cell_index_malla",
            "fuente": "malla",
            "ambito": "completo",
            "clave": "cell_index",
            "filas_evaluadas": malla["filas"],
            "valores_unicos": len(malla["mapeo"]),
            "nulos_clave": malla["nulos_indice"],
            "duplicados": malla["duplicados_indice"],
            "incumplimientos": malla["nulos_indice"] + malla["duplicados_indice"],
            "resultado": resultado_control(malla["nulos_indice"] + malla["duplicados_indice"]),
            "detalle": "Cada cell_index debe identificar una sola celda.",
        },
        {
            "control": "unicidad_cell_id_malla",
            "fuente": "malla",
            "ambito": "completo",
            "clave": "cell_id",
            "filas_evaluadas": malla["filas"],
            "valores_unicos": len(set(malla["mapeo"].values())),
            "nulos_clave": malla["nulos_id"],
            "duplicados": malla["duplicados_id"],
            "incumplimientos": malla["nulos_id"] + malla["duplicados_id"],
            "resultado": resultado_control(malla["nulos_id"] + malla["duplicados_id"]),
            "detalle": "Cada cell_id debe identificar una sola celda.",
        },
    ]

    for fuente, resultado in (("viirs", viirs), ("chirps", chirps)):
        ambitos = (
            (
                resultado["ambito_completo"],
                resultado["filas_completas"],
                resultado["claves_unicas_completo"],
                resultado["nulos_clave_completo"],
                resultado["duplicados_completo"],
                "completo",
            ),
            (
                f"periodo_{anio_estudio}",
                resultado["filas_periodo"],
                resultado["claves_unicas_periodo"],
                resultado["nulos_clave_periodo"],
                resultado["duplicados_periodo"],
                "periodo",
            ),
        )
        for ambito, filas, unicos, nulos, duplicados, sufijo in ambitos:
            incumplimientos = nulos + duplicados
            controles_claves.append(
                {
                    "control": f"unicidad_clave_{fuente}_{sufijo}",
                    "fuente": fuente,
                    "ambito": ambito,
                    "clave": "cell_index + anio + mes",
                    "filas_evaluadas": filas,
                    "valores_unicos": unicos,
                    "nulos_clave": nulos,
                    "duplicados": duplicados,
                    "incumplimientos": incumplimientos,
                    "resultado": resultado_control(incumplimientos),
                    "detalle": "La clave esperada debe ser única y completa.",
                }
            )

    controles_relaciones = [
        {
            "control": "claves_viirs_sin_chirps",
            "fuente": "viirs_chirps",
            "ambito": f"periodo_{anio_estudio}",
            "clave": "cell_index + anio + mes",
            "filas_evaluadas": len(viirs["claves_periodo"]),
            "valores_unicos": len(viirs["claves_periodo"]),
            "nulos_clave": 0,
            "duplicados": 0,
            "incumplimientos": len(claves_solo_viirs),
            "resultado": resultado_control(len(claves_solo_viirs)),
            "detalle": "Claves presentes en VIIRS que no aparecen en CHIRPS.",
        },
        {
            "control": "claves_chirps_sin_viirs",
            "fuente": "viirs_chirps",
            "ambito": f"periodo_{anio_estudio}",
            "clave": "cell_index + anio + mes",
            "filas_evaluadas": len(chirps["claves_periodo"]),
            "valores_unicos": len(chirps["claves_periodo"]),
            "nulos_clave": 0,
            "duplicados": 0,
            "incumplimientos": len(claves_solo_chirps),
            "resultado": resultado_control(len(claves_solo_chirps)),
            "detalle": "Claves presentes en CHIRPS que no aparecen en VIIRS.",
        },
        {
            "control": "celdas_viirs_fuera_malla",
            "fuente": "viirs_malla",
            "ambito": f"periodo_{anio_estudio}",
            "clave": "cell_index",
            "filas_evaluadas": len(viirs["celdas_periodo"]),
            "valores_unicos": len(viirs["celdas_periodo"]),
            "nulos_clave": 0,
            "duplicados": 0,
            "incumplimientos": len(celdas_viirs_fuera_malla),
            "resultado": resultado_control(len(celdas_viirs_fuera_malla)),
            "detalle": "cell_index de VIIRS que no existen en la malla.",
        },
        {
            "control": "celdas_chirps_fuera_malla",
            "fuente": "chirps_malla",
            "ambito": f"periodo_{anio_estudio}",
            "clave": "cell_index",
            "filas_evaluadas": len(chirps["celdas_periodo"]),
            "valores_unicos": len(chirps["celdas_periodo"]),
            "nulos_clave": 0,
            "duplicados": 0,
            "incumplimientos": len(celdas_chirps_fuera_malla),
            "resultado": resultado_control(len(celdas_chirps_fuera_malla)),
            "detalle": "cell_index de CHIRPS que no existen en la malla.",
        },
        {
            "control": "cell_id_chirps_consistente_con_malla",
            "fuente": "chirps_malla",
            "ambito": f"periodo_{anio_estudio}",
            "clave": "cell_index -> cell_id",
            "filas_evaluadas": len(chirps["pares_chirps"]),
            "valores_unicos": len(chirps["pares_chirps"]),
            "nulos_clave": 0,
            "duplicados": 0,
            "incumplimientos": cell_id_chirps_inconsistente,
            "resultado": resultado_control(cell_id_chirps_inconsistente),
            "detalle": "El cell_id de CHIRPS debe coincidir con la malla para cada cell_index.",
        },
    ]
    controles = controles_claves + controles_relaciones

    fracciones_sin_viirs = [
        malla["fracciones"][indice]
        for indice in viirs["celdas_viirs_sin_observacion"]
        if indice in malla["fracciones"]
    ]
    hallazgos = [
        {
            "hallazgo": "faltantes_viirs_2023",
            "dimension_calidad": "completitud",
            "cantidad_registros": viirs["especiales"]["filas_sin_observacion"],
            "porcentaje_registros": f"{viirs['especiales']['filas_sin_observacion'] * 100 / viirs['filas_periodo']:.6f}",
            "evidencia": f"Afectan {len(viirs['celdas_viirs_sin_observacion'])} celdas durante 12 meses.",
            "decision_actual": "Pendiente. Conservar como nulo y no convertir automáticamente en cero.",
        },
        {
            "hallazgo": "celdas_parciales_malla",
            "dimension_calidad": "validez_espacial",
            "cantidad_registros": malla["conteos_espaciales"]["parciales"],
            "porcentaje_registros": f"{malla['conteos_espaciales']['parciales'] * 100 / malla['filas']:.6f}",
            "evidencia": f"{malla['conteos_espaciales']['fraccion_lt_050']} celdas tienen menos del 50 % de su área dentro de Loja.",
            "decision_actual": "Pendiente. Mantener durante el perfilado y definir luego la regla de aptitud analítica.",
        },
        {
            "hallazgo": "faltantes_viirs_asociados_a_borde",
            "dimension_calidad": "consistencia",
            "cantidad_registros": len(fracciones_sin_viirs),
            "porcentaje_registros": f"{len(fracciones_sin_viirs) * 100 / malla['filas']:.6f}",
            "evidencia": (
                "Fracción dentro de Loja entre "
                f"{min(fracciones_sin_viirs):.12f} y {max(fracciones_sin_viirs):.12f}."
                if fracciones_sin_viirs
                else "No se encontraron celdas afectadas."
            ),
            "decision_actual": "Pendiente. Evaluar cobertura observacional antes de excluir celdas.",
        },
        {
            "hallazgo": "precision_decimal_chirps_valid_coverage",
            "dimension_calidad": "validez",
            "cantidad_registros": chirps["especiales"]["cobertura_menor_que_uno"],
            "porcentaje_registros": f"{chirps['especiales']['cobertura_menor_que_uno'] * 100 / chirps['filas_periodo']:.6f}",
            "evidencia": (
                f"Con tolerancia {tolerancia:g}, "
                f"{chirps['especiales']['cobertura_fuera_tolerancia']} filas quedan fuera del valor esperado 1."
            ),
            "decision_actual": "Usar tolerancia numérica; no comparar decimales mediante igualdad exacta.",
        },
        {
            "hallazgo": "evidencia_fuego_2023",
            "dimension_calidad": "perfil_descriptivo",
            "cantidad_registros": viirs["especiales"]["evidencia_fuego"],
            "porcentaje_registros": f"{viirs['especiales']['evidencia_fuego'] * 100 / viirs['filas_periodo']:.6f}",
            "evidencia": f"{viirs['especiales']['evidencia_fuego_nominal_alta']} celda-meses tienen evidencia nominal/alta.",
            "decision_actual": "Dato descriptivo. No implica todavía una regla de exclusión.",
        },
    ]

    escribir_csv(
        DIRECTORIO_EVIDENCIAS / "inventario_fuentes.csv",
        [
            "fuente",
            "archivo",
            "formato",
            "ruta_relativa",
            "procedencia",
            "periodo",
            "grano",
            "clave_esperada",
            "tamano_bytes",
            "sha256_manifiesto",
            "sha256_calculado",
            "hash_coincide",
            "filas",
            "columnas",
        ],
        inventario,
    )
    escribir_csv(
        DIRECTORIO_EVIDENCIAS / "perfilado_columnas.csv",
        [
            "fuente",
            "ambito",
            "variable",
            "tipo_fuente",
            "tipo_inferido",
            "filas",
            "no_nulos",
            "nulos",
            "porcentaje_nulos",
            "valores_distintos",
            "minimo",
            "maximo",
            "valores_frecuentes",
        ],
        perfilado_columnas,
    )
    escribir_csv(
        DIRECTORIO_EVIDENCIAS / "perfilado_claves_relaciones.csv",
        [
            "control",
            "fuente",
            "ambito",
            "clave",
            "filas_evaluadas",
            "valores_unicos",
            "nulos_clave",
            "duplicados",
            "incumplimientos",
            "resultado",
            "detalle",
        ],
        controles,
    )
    escribir_csv(
        DIRECTORIO_EVIDENCIAS / "hallazgos_perfilado.csv",
        [
            "hallazgo",
            "dimension_calidad",
            "cantidad_registros",
            "porcentaje_registros",
            "evidencia",
            "decision_actual",
        ],
        hallazgos,
    )

    controles_cumplen = sum(fila["resultado"] == "CUMPLE" for fila in controles)
    resumen = f"""# Resumen del perfilado inicial

## Alcance ejecutado

- Periodo analítico perfilado: {anio_estudio}.
- Fuentes: malla, VIIRS mensual y CHIRPS mensual.
- Operación: lectura, inventario y diagnóstico. No se limpiaron, transformaron ni cargaron datos.
- Integridad de archivos: los tres hashes coinciden con el manifiesto de ingesta.

## Conteos principales

| Fuente | Filas completas | Filas de {anio_estudio} | Columnas |
|---|---:|---:|---:|
| Malla | {malla['filas']} | No aplica | {len(malla['columnas'])} |
| VIIRS | {viirs['filas_completas']} | {viirs['filas_periodo']} | {len(viirs['columnas'])} |
| CHIRPS | {chirps['filas_completas']} | {chirps['filas_periodo']} | {len(chirps['columnas'])} |

## Claves y relaciones

- VIIRS y CHIRPS tienen {len(viirs['claves_periodo'])} claves únicas en {anio_estudio}.
- Claves VIIRS sin CHIRPS: {len(claves_solo_viirs)}.
- Claves CHIRPS sin VIIRS: {len(claves_solo_chirps)}.
- Celdas VIIRS fuera de la malla: {len(celdas_viirs_fuera_malla)}.
- Celdas CHIRPS fuera de la malla: {len(celdas_chirps_fuera_malla)}.
- Correspondencias CHIRPS `cell_index -> cell_id` inconsistentes: {cell_id_chirps_inconsistente}.
- Controles de claves y relaciones cumplidos: {controles_cumplen} de {len(controles)}.

## Hallazgos que requieren decisión

- VIIRS tiene {viirs['especiales']['filas_sin_observacion']} filas sin observación en {anio_estudio}, correspondientes a {len(viirs['celdas_viirs_sin_observacion'])} celdas.
- La malla contiene {malla['conteos_espaciales']['parciales']} celdas parciales; {malla['conteos_espaciales']['fraccion_lt_050']} tienen menos del 50 % de su área dentro de Loja.
- Las celdas sin observación VIIRS tienen fracciones dentro de Loja entre {min(fracciones_sin_viirs):.12f} y {max(fracciones_sin_viirs):.12f}.
- `chirps_valid_coverage` presenta diferencias de punto flotante alrededor de 1. Con tolerancia {tolerancia:g}, existen {chirps['especiales']['cobertura_fuera_tolerancia']} incumplimientos.
- Se registran {viirs['especiales']['evidencia_fuego']} celda-meses con evidencia de fuego y {viirs['especiales']['evidencia_fuego_nominal_alta']} con evidencia nominal/alta.

## Siguiente paso

Construir la matriz de calidad y acordar las reglas de tratamiento. En particular, se debe decidir cómo representar las 75 celdas sin observación VIIRS antes de implementar la capa Clean.
"""
    escribir_texto(DIRECTORIO_EVIDENCIAS / "resumen_perfilado.md", resumen)

    print("Perfilado completado.")
    print(f"Evidencias: {DIRECTORIO_EVIDENCIAS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
