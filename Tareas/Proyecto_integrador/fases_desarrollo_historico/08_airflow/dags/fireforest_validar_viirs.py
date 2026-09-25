import json
from datetime import datetime
from pathlib import Path

from airflow.sdk import dag, task


RUTA_VIIRS = Path(
    "/opt/airflow/fireforest/nosql/detecciones_viirs.json"
)

CAMPOS_OBLIGATORIOS = {
    "deteccion_id",
    "celda_id",
    "fecha",
    "fuente",
    "sensor",
    "frp_mw",
    "fire_mask",
    "coordenadas",
    "calidad",
}


@dag(
    dag_id="fireforest_validar_viirs",
    description="Valida la calidad de las detecciones VIIRS de FireForest",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["FireForest", "VIIRS", "calidad"],
)
def validar_detecciones_viirs():

    @task
    def comprobar_archivo() -> str:
        if not RUTA_VIIRS.exists():
            raise FileNotFoundError(
                f"No se encontro el archivo: {RUTA_VIIRS}"
            )

        if RUTA_VIIRS.stat().st_size == 0:
            raise ValueError("El archivo VIIRS esta vacio")

        print(f"Archivo encontrado: {RUTA_VIIRS}")
        print(f"Tamano: {RUTA_VIIRS.stat().st_size} bytes")

        return str(RUTA_VIIRS)

    @task
    def validar_calidad(ruta: str) -> dict:
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)

        if not isinstance(datos, list):
            raise TypeError("La raiz del JSON debe ser una lista")

        if not datos:
            raise ValueError("No existen detecciones VIIRS")

        registros_incompletos = []
        identificadores = []
        frp = []
        celdas = set()
        coordenadas_invalidas = 0
        fechas_invalidas = 0
        registros_no_validos = 0

        for numero, registro in enumerate(datos, start=1):
            faltantes = CAMPOS_OBLIGATORIOS - registro.keys()

            if faltantes:
                registros_incompletos.append(
                    {
                        "registro": numero,
                        "campos": sorted(faltantes),
                    }
                )
                continue

            identificadores.append(registro["deteccion_id"])
            celdas.add(registro["celda_id"])

            valor_frp = registro["frp_mw"]
            if not isinstance(valor_frp, (int, float)) or isinstance(
                valor_frp, bool
            ):
                raise TypeError(
                    f"FRP invalido en {registro['deteccion_id']}"
                )
            frp.append(float(valor_frp))

            try:
                datetime.strptime(registro["fecha"], "%Y-%m-%d")
            except (TypeError, ValueError):
                fechas_invalidas += 1

            coordenadas = registro["coordenadas"]
            longitud = coordenadas.get("longitud")
            latitud = coordenadas.get("latitud")

            if not (
                isinstance(longitud, (int, float))
                and isinstance(latitud, (int, float))
                and -180 <= longitud <= 180
                and -90 <= latitud <= 90
            ):
                coordenadas_invalidas += 1

            if registro["calidad"].get("valida") is not True:
                registros_no_validos += 1

        duplicados = len(identificadores) - len(set(identificadores))

        resumen = {
            "total_detecciones": len(datos),
            "registros_incompletos": len(registros_incompletos),
            "identificadores_duplicados": duplicados,
            "fechas_invalidas": fechas_invalidas,
            "coordenadas_invalidas": coordenadas_invalidas,
            "registros_no_validos": registros_no_validos,
            "numero_celdas": len(celdas),
            "frp_promedio_mw": round(sum(frp) / len(frp), 2),
            "frp_maximo_mw": max(frp),
        }

        problemas_criticos = (
            resumen["registros_incompletos"]
            + resumen["identificadores_duplicados"]
            + resumen["fechas_invalidas"]
            + resumen["coordenadas_invalidas"]
        )

        if problemas_criticos > 0:
            raise ValueError(
                f"La validacion encontro problemas: {resumen}"
            )

        return resumen

    @task
    def registrar_resultado(resumen: dict) -> None:
        print("RESUMEN DE CALIDAD VIIRS")
        print(json.dumps(resumen, indent=2, ensure_ascii=False))
        print("Validacion finalizada correctamente")

    ruta = comprobar_archivo()
    resumen = validar_calidad(ruta)
    registrar_resultado(resumen)


validar_detecciones_viirs()