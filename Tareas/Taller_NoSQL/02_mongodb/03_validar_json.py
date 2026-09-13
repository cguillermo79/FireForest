"""Validacion del archivo JSON documental antes de cargarlo en MongoDB.

Ejecutar desde la raiz de FireForest:
    .venv\\Scripts\\python.exe Tareas\\Taller_NoSQL\\02_mongodb\\03_validar_json.py
"""

from pathlib import Path
import json

RUTA_SCRIPT = Path(__file__).resolve()
RAIZ_TALLER = RUTA_SCRIPT.parent.parent
ARCHIVO_JSON = RAIZ_TALLER / "03_datos" / "evidencia_viirs_celda_mes.json"

CAMPOS_OBLIGATORIOS_NIVEL_1 = [
    "_id", "celda", "periodo", "fuente_satelital", "metricas",
    "calidad_observacion", "evidencias", "muestreo", "metadatos",
]

if not ARCHIVO_JSON.exists():
    raise FileNotFoundError(f"No se encontro el archivo JSON:\n{ARCHIVO_JSON}")

with ARCHIVO_JSON.open(encoding="utf-8") as archivo:
    documentos = json.load(archivo)

errores = []

if len(documentos) != 105:
    errores.append(f"Se esperaban 105 documentos y se encontraron {len(documentos)}.")

ids = [documento.get("_id") for documento in documentos]
if len(ids) != len(set(ids)):
    errores.append("Existen valores de _id duplicados.")

claves_celda_mes = [
    (documento["celda"]["cell_index"], documento["periodo"]["anio"], documento["periodo"]["mes"])
    for documento in documentos
]
if len(claves_celda_mes) != len(set(claves_celda_mes)):
    errores.append("Existen combinaciones celda-anio-mes duplicadas.")

for indice, documento in enumerate(documentos):
    faltantes = [campo for campo in CAMPOS_OBLIGATORIOS_NIVEL_1 if campo not in documento]
    if faltantes:
        errores.append(f"Documento {indice} ({documento.get('_id')}) sin campos: {faltantes}")
    if not isinstance(documento.get("evidencias"), list) or len(documento["evidencias"]) != 2:
        errores.append(f"Documento {indice} ({documento.get('_id')}) no tiene arreglo 'evidencias' de 2 elementos.")

con_fuego = sum(
    1 for documento in documentos
    if any(evidencia["categoria"] == "todas" and evidencia["evidencia_fuego"] for evidencia in documento["evidencias"])
)
sin_fuego = len(documentos) - con_fuego
nominal_alta = sum(
    1 for documento in documentos
    if any(evidencia["categoria"] == "nominal_alta" and evidencia["evidencia_fuego"] for evidencia in documento["evidencias"])
)
frp_maxima = max(documento["metricas"]["frp"]["maxima_media_mw"] for documento in documentos)

print("=== VALIDACION DEL JSON DOCUMENTAL ===")
print(f"Archivo: {ARCHIVO_JSON}")
print(f"Documentos totales: {len(documentos)}")
print(f"_id unicos: {len(set(ids))}")
print(f"Combinaciones celda-anio-mes unicas: {len(set(claves_celda_mes))}")
print(f"Documentos con evidencia de fuego (categoria 'todas'): {con_fuego}")
print(f"Documentos sin evidencia de fuego (categoria 'todas'): {sin_fuego}")
print(f"Documentos con evidencia nominal/alta: {nominal_alta}")
print(f"FRP maxima de la muestra (MW): {frp_maxima}")

if errores:
    print("\nERRORES ENCONTRADOS:")
    for error in errores:
        print(f" - {error}")
    raise SystemExit(1)

print("\nResultado: el JSON es valido y esta listo para cargarse en MongoDB.")
