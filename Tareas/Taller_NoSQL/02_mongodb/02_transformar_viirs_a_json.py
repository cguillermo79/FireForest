from pathlib import Path
import json

import pandas as pd


# ============================================================
# RUTAS
# ============================================================

RUTA_SCRIPT = Path(__file__).resolve()
RAIZ_TALLER = RUTA_SCRIPT.parent.parent

ARCHIVO_ENTRADA = (
    RAIZ_TALLER
    / "03_datos"
    / "muestra_viirs_celda_mes_2019_2025.csv"
)

ARCHIVO_SALIDA = (
    RAIZ_TALLER
    / "03_datos"
    / "evidencia_viirs_celda_mes.json"
)


# ============================================================
# VALIDACIÓN DEL ARCHIVO
# ============================================================

if not ARCHIVO_ENTRADA.exists():
    raise FileNotFoundError(
        f"No se encontró la muestra:\n{ARCHIVO_ENTRADA}"
    )

datos = pd.read_csv(ARCHIVO_ENTRADA)

if datos.empty:
    raise ValueError("El archivo CSV no contiene registros.")

if datos.isna().any().any():
    raise ValueError(
        "La muestra contiene valores ausentes. "
        "Debe revisarse antes de generar el JSON."
    )

if datos["registro_id"].duplicated().any():
    raise ValueError("Existen identificadores de registro duplicados.")

if datos.duplicated(["cell_index", "anio", "mes"]).any():
    raise ValueError("Existen combinaciones celda-mes duplicadas.")


# ============================================================
# CONSTRUCCIÓN DE LOS DOCUMENTOS
# ============================================================

documentos = []

for fila in datos.itertuples(index=False):
    documento = {
        "_id": str(fila.registro_id),

        "celda": {
            "cell_index": int(fila.cell_index),
            "unidad_espacial": "celda_500m"
        },

        "periodo": {
            "anio": int(fila.anio),
            "mes": int(fila.mes),
            "anio_mes": str(fila.anio_mes),
            "fecha_inicio": {
                "$date": (
                    f"{int(fila.anio):04d}-"
                    f"{int(fila.mes):02d}-01T00:00:00Z"
                )
            }
        },

        "fuente_satelital": {
            "fuente_primaria": str(fila.fuente_primaria),
            "asset_gee": str(fila.asset_fuente),
            "soporte_nativo_m": float(fila.viirs_soporte_nativo_m),
            "procedencia": str(fila.procedencia),
            "version_origen": str(fila.version_origen)
        },

        "metricas": {
            "detecciones": {
                "media_todas": float(
                    fila.viirs_detecciones_todas_support_mean
                ),
                "media_nominal_alta": float(
                    fila.viirs_detecciones_nominal_alta_support_mean
                )
            },

            "presencia": {
                "fraccion_todas": float(
                    fila.viirs_presencia_fuego_support_frac
                ),
                "fraccion_nominal_alta": float(
                    fila.viirs_presencia_fuego_nominal_alta_support_frac
                )
            },

            "frp": {
                "suma_observada_media_mw": float(
                    fila.viirs_frp_suma_observada_support_mean_mw
                ),
                "maxima_media_mw": float(
                    fila.viirs_frp_maxima_support_mean_mw
                )
            }
        },

        "calidad_observacion": {
            "dias_validos_media": float(
                fila.viirs_dias_validos_support_mean
            ),
            "disponibilidad_pct": float(
                fila.viirs_disponibilidad_support_pct
            ),
            "observado_media": float(
                fila.viirs_observado_support_mean
            ),
            "cobertura_fuente_fraccion": float(
                fila.viirs_source_coverage_frac
            ),
            "soporte_observado_fraccion": float(
                fila.viirs_observed_support_frac
            )
        },

        "evidencias": [
            {
                "categoria": "todas",
                "detecciones_media": float(
                    fila.viirs_detecciones_todas_support_mean
                ),
                "presencia_fraccion": float(
                    fila.viirs_presencia_fuego_support_frac
                ),
                "evidencia_fuego": bool(
                    fila.viirs_evidencia_fuego_any
                )
            },
            {
                "categoria": "nominal_alta",
                "detecciones_media": float(
                    fila.viirs_detecciones_nominal_alta_support_mean
                ),
                "presencia_fraccion": float(
                    fila.viirs_presencia_fuego_nominal_alta_support_frac
                ),
                "evidencia_fuego": bool(
                    fila.viirs_evidencia_fuego_nominal_alta_any
                )
            }
        ],

        "muestreo": {
            "estrato": str(fila.estrato_muestra),
            "metodo": "estratificado_por_anio_y_evidencia",
            "semilla": 2026
        },

        "metadatos": {
            "unidad_analisis": str(fila.unidad_analisis),
            "datos_simulados": bool(fila.datos_simulados),
            "uso": "Laboratorio NoSQL MongoDB - M1721"
        }
    }

    documentos.append(documento)


# ============================================================
# EXPORTACIÓN
# ============================================================

with ARCHIVO_SALIDA.open(
    "w",
    encoding="utf-8"
) as archivo_json:
    json.dump(
        documentos,
        archivo_json,
        ensure_ascii=False,
        indent=2
    )

print("JSON documental generado correctamente.")
print(f"Archivo:\n{ARCHIVO_SALIDA}")
print(f"\nDocumentos generados: {len(documentos)}")
print(f"Documentos con dos evidencias: {sum(len(d['evidencias']) == 2 for d in documentos)}")
print(f"Datos simulados: {sum(d['metadatos']['datos_simulados'] for d in documentos)}")
print(f"Años incluidos: {sorted({d['periodo']['anio'] for d in documentos})}")