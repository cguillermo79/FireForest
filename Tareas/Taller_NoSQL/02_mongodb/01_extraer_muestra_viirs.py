from pathlib import Path

import pandas as pd


# ============================================================
# RUTAS
# ============================================================

RUTA_SCRIPT = Path(__file__).resolve()
RAIZ_FIREFORREST = RUTA_SCRIPT.parents[3]
RAIZ_ANALISIS_CIENCIA = RAIZ_FIREFORREST.parent

ARCHIVO_ORIGEN = (
    RAIZ_ANALISIS_CIENCIA
    / "FIRELAB_Loja"
    / "09_integracion_variables"
    / "productos"
    / "viirs_500m"
    / "viirs_evidencia_500m_celda_mes_2019_2025_v1_0_3.csv"
)

ARCHIVO_SALIDA = (
    RUTA_SCRIPT.parent.parent
    / "03_datos"
    / "muestra_viirs_celda_mes_2019_2025.csv"
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

SEMILLA = 2026
CASOS_FUEGO_POR_ANIO = 10
CASOS_SIN_FUEGO_POR_ANIO = 5

CAMPOS_ESENCIALES = [
    "cell_index",
    "anio",
    "mes",
    "anio_mes",
    "viirs_detecciones_todas_support_mean",
    "viirs_detecciones_nominal_alta_support_mean",
    "viirs_frp_suma_observada_support_mean_mw",
    "viirs_frp_maxima_support_mean_mw",
    "viirs_evidencia_fuego_any",
    "viirs_evidencia_fuego_nominal_alta_any",
]


# ============================================================
# VALIDACIÓN DEL ARCHIVO DE ORIGEN
# ============================================================

if not ARCHIVO_ORIGEN.exists():
    raise FileNotFoundError(
        f"No se encontró el archivo fuente (registros de VIIRS "
        f"procesados previamente):\n{ARCHIVO_ORIGEN}"
    )

print(f"Archivo de origen:\n{ARCHIVO_ORIGEN}")
print("\nLeyendo datos reales de VIIRS...")


# ============================================================
# LECTURA Y DEPURACIÓN
# ============================================================

datos = pd.read_csv(ARCHIVO_ORIGEN)

columnas_faltantes = [
    columna for columna in CAMPOS_ESENCIALES
    if columna not in datos.columns
]

if columnas_faltantes:
    raise ValueError(
        f"Faltan columnas esenciales: {columnas_faltantes}"
    )

datos_validos = datos.dropna(subset=CAMPOS_ESENCIALES).copy()

datos_validos["cell_index"] = datos_validos["cell_index"].astype(int)
datos_validos["anio"] = datos_validos["anio"].astype(int)
datos_validos["mes"] = datos_validos["mes"].astype(int)

datos_validos["viirs_evidencia_fuego_any"] = (
    datos_validos["viirs_evidencia_fuego_any"].astype(int)
)

datos_validos["viirs_evidencia_fuego_nominal_alta_any"] = (
    datos_validos[
        "viirs_evidencia_fuego_nominal_alta_any"
    ].astype(int)
)


# ============================================================
# MUESTREO ESTRATIFICADO Y REPRODUCIBLE
# ============================================================

muestras = []

for anio in sorted(datos_validos["anio"].unique()):
    datos_anio = datos_validos[datos_validos["anio"] == anio]

    con_fuego = datos_anio[
        datos_anio["viirs_evidencia_fuego_any"] == 1
    ].sample(
        n=CASOS_FUEGO_POR_ANIO,
        random_state=SEMILLA + int(anio),
    )

    sin_fuego = datos_anio[
        datos_anio["viirs_evidencia_fuego_any"] == 0
    ].sample(
        n=CASOS_SIN_FUEGO_POR_ANIO,
        random_state=SEMILLA + int(anio) + 100,
    )

    con_fuego = con_fuego.copy()
    sin_fuego = sin_fuego.copy()

    con_fuego["estrato_muestra"] = "con_fuego"
    sin_fuego["estrato_muestra"] = "sin_fuego"

    muestras.extend([con_fuego, sin_fuego])

muestra = pd.concat(muestras, ignore_index=True)

muestra = muestra.sort_values(
    ["anio", "mes", "cell_index"]
).reset_index(drop=True)

muestra.insert(
    0,
    "registro_id",
    [f"VCM_{numero:04d}" for numero in range(1, len(muestra) + 1)],
)

muestra["procedencia"] = "registros_previamente_procesados"
muestra["fuente_primaria"] = "NASA FIRMS - VIIRS"
muestra["unidad_analisis"] = "celda_mes_500m"
muestra["datos_simulados"] = False
muestra["version_origen"] = "v1.0.3"

# El identificador de activo del archivo de origen contiene una ruta
# interna (usuario y nombre de carpeta) que no debe aparecer en los
# documentos finales. Se reemplaza por un identificador generico
# VIIRS_PREP_<anio>_<mes> que preserva la trazabilidad temporal sin
# exponer esa ruta. Los valores cientificos (FRP, detecciones,
# presencia, calidad de observacion, etc.) no se modifican.
muestra["asset_fuente"] = muestra.apply(
    lambda fila: f"VIIRS_PREP_{int(fila['anio']):04d}_{int(fila['mes']):02d}",
    axis=1,
)


# ============================================================
# EXPORTACIÓN EN FIREFORREST
# ============================================================

ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
muestra.to_csv(ARCHIVO_SALIDA, index=False, encoding="utf-8")

print("\nMuestra generada correctamente.")
print(f"Archivo de salida:\n{ARCHIVO_SALIDA}")
print(f"\nNúmero total de registros: {len(muestra)}")

print("\nDistribución por año y estrato:")
print(
    muestra.groupby(
        ["anio", "estrato_muestra"]
    ).size().unstack(fill_value=0)
)

print("\nRegistros con fuego:")
print(int(muestra["viirs_evidencia_fuego_any"].sum()))

print("\nRegistros sin fuego:")
print(int((muestra["viirs_evidencia_fuego_any"] == 0).sum()))

print("\nFRP máxima de la muestra:")
print(muestra["viirs_frp_maxima_support_mean_mw"].max())