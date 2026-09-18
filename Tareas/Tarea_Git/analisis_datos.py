"""
Análisis descriptivo de detecciones de incendios (datos de ejemplo).

Resume las detecciones por mes y por nivel de confianza, muestra el
resultado en consola y lo guarda en resultados/resumen.csv
(carpeta excluida del repositorio mediante .gitignore).
"""

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

# Índices de cada campo en las tuplas de datos
FECHA, LAT, LON, FRP, CONFIANZA = range(5)

# Datos sintéticos con estructura similar a detecciones VIIRS
# (fecha, latitud, longitud, FRP en MW, confianza)
DETECCIONES = [
    ("2024-08-03", -1.652, -78.641, 4.8, "nominal"),
    ("2024-08-11", -1.701, -78.598, 7.2, "high"),
    ("2024-08-19", -1.588, -78.702, 2.1, "low"),
    ("2024-08-27", -1.623, -78.655, 9.6, "high"),
    ("2024-09-02", -1.745, -78.612, 3.4, "nominal"),
    ("2024-09-09", -1.690, -78.570, 12.3, "high"),
    ("2024-09-15", -1.612, -78.689, 1.9, "low"),
    ("2024-09-24", -1.672, -78.634, 5.5, "nominal"),
    ("2024-10-05", -1.598, -78.661, 6.7, "nominal"),
    ("2024-10-18", -1.733, -78.590, 8.9, "high"),
]

CARPETA_SALIDA = Path(__file__).parent / "resultados"


def agrupar_frp(detecciones, clave):
    """Agrupa los valores de FRP según la función clave indicada."""
    grupos = defaultdict(list)
    for d in detecciones:
        grupos[clave(d)].append(d[FRP])
    return grupos


def construir_filas(tipo, grupos):
    """Calcula conteo, FRP promedio y FRP máximo de cada grupo."""
    filas = []
    for grupo, valores in sorted(grupos.items()):
        filas.append({
            "tipo": tipo,
            "grupo": grupo,
            "detecciones": len(valores),
            "frp_promedio": round(mean(valores), 2),
            "frp_maximo": max(valores),
        })
    return filas


def main():
    por_mes = agrupar_frp(DETECCIONES, lambda d: d[FECHA][:7])
    por_confianza = agrupar_frp(DETECCIONES, lambda d: d[CONFIANZA])
    filas = construir_filas("mes", por_mes) + construir_filas("confianza", por_confianza)

    print(f"Total de detecciones: {len(DETECCIONES)}")
    print(f"FRP promedio general: {mean(d[FRP] for d in DETECCIONES):.2f} MW\n")
    print(f"{'Tipo':<10} {'Grupo':<10} {'N':>3} {'FRP prom':>9} {'FRP máx':>8}")
    for fila in filas:
        print(f"{fila['tipo']:<10} {fila['grupo']:<10} {fila['detecciones']:>3} "
              f"{fila['frp_promedio']:>9.2f} {fila['frp_maximo']:>8.2f}")

    CARPETA_SALIDA.mkdir(exist_ok=True)
    archivo = CARPETA_SALIDA / "resumen.csv"
    with archivo.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=filas[0].keys())
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"\nResumen guardado en: {archivo}")


if __name__ == "__main__":
    main()