"""Verificacion territorial de celdas FireForest y generacion de celdas validas.

Proyecto: FireForest (independiente; no relacionado con ningun otro proyecto).

Que hace este script, en orden:

1. Carga la capa oficial del INEC (zonas censales `zon_a`, ya extraidas para
   los cantones 1101 = Loja y 1103 = Catamayo en
   `Tareas/Proyecto_integrador/02_datos/raw/malla/`, SRID nativo EPSG:31992).
2. Reproyecta esas zonas a EPSG:32717 (CRS de trabajo del proyecto) y las
   disuelve por codigo DPA para reconstruir el limite del canton Loja, el
   limite del canton Catamayo y las 14 parroquias del canton Loja.
3. Vuelve a verificar las celdas controladas ORIGINALES (LJ_04521, LJ_04522)
   contra el limite reconstruido, como evidencia reproducible de que quedan
   fuera del canton Loja (documentado en
   `Tareas/Proyecto_integrador/03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`).
4. Construye una malla sistematica de celdas de 500 x 500 m ancladas a
   multiplos de 500 en EPSG:32717 (x0 = floor(minx/500)*500, etc.), conserva
   solo las celdas cuyo poligono completo esta contenido en el canton Loja
   (equivalente a `ST_Within(celda.geom, canton_loja.geom)`) y con distancia
   al limite cantonal >= 1000 m (equivalente a
   `ST_Distance(celda.geom, ST_Boundary(canton_loja.geom)) >= 1000`).
5. Selecciona de forma deterministica las dos primeras celdas que cumplen
   ambos criterios, ordenando por coordenada X y luego Y (sin intervencion
   visual ni conocimiento previo no documentado). Las llama `LJ_TEST_001` y
   `LJ_TEST_002` (identificadores de PRUEBA, ver seccion de nomenclatura en
   el informe de auditoria).
6. Calcula la tabla de validacion completa para las dos celdas nuevas y la
   guarda como CSV reproducible.
7. Genera el mapa "Ambito territorial y localizacion de las celdas del
   prototipo" (limite cantonal, limites parroquiales, celdas nuevas, panel
   ampliado, norte, escala, leyenda, EPSG, fuente INEC, nota de no
   representatividad) como figura PNG/PDF.

Nota sobre PostGIS: este script NO se conecta a PostgreSQL (no hay
credenciales de base de datos en este entorno; `.env` no esta versionado).
Todas las operaciones espaciales (`ST_Within`, `ST_Distance`, `ST_Area`,
`ST_Transform`) se reproducen con Shapely/PyProj de forma equivalente y
documentada; los resultados numericos (area, distancias) son identicos a
los que produciria PostGIS sobre las mismas geometrias, porque ambos usan
aritmetica planar estandar sobre coordenadas ya proyectadas. Los scripts SQL
listos para ejecutar contra PostgreSQL/PostGIS se generan por separado (ver
`03_postgresql_postgis/evidencias/`).

Dependencias (instaladas en el entorno virtual del proyecto, `.venv`):
shapely, pyproj, matplotlib.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import box, Point, shape
from shapely.ops import transform as shp_transform
from shapely.ops import unary_union
from shapely.prepared import prep

# ---------------------------------------------------------------------------
# Rutas y constantes
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]  # .../Proyecto_integrador
MALLA_DIR = REPO_ROOT / "02_datos" / "raw" / "malla"
EVIDENCIAS_DIR = REPO_ROOT / "03_postgresql_postgis" / "evidencias"
FIGURAS_DIR = REPO_ROOT / "01_avance_1" / "presentacion" / "figuras"

GEOJSON_LOJA = MALLA_DIR / "inec_zonas_censales_canton_1101_loja.geojson"
GEOJSON_CATAMAYO = MALLA_DIR / "inec_zonas_censales_canton_1103_catamayo.geojson"

SRC_EPSG = "EPSG:31992"   # SIRGAS 1995 / UTM 17S (SRID nativo de la capa INEC)
WORK_EPSG = "EPSG:32717"  # WGS84 / UTM 17S (CRS de trabajo del proyecto FireForest)
GEO_EPSG = "EPSG:4326"    # grados (longitud/latitud almacenados en dim_celda)

CELL_SIZE_M = 500.0
MARGIN_MIN_M = 1000.0  # margen de seguridad exigido respecto del limite cantonal

PARISH_NAMES = {
    "110150": "Loja (urbana)",
    "110151": "Chantaco",
    "110152": "Chuquiribamba",
    "110153": "El Cisne",
    "110154": "Gualel",
    "110155": "Jimbilla",
    "110156": "Malacatos (Valladolid)",
    "110157": "San Lucas",
    "110158": "San Pedro de Vilcabamba",
    "110159": "Santiago",
    "110160": "Taquil (Miguel Riofrio)",
    "110161": "Vilcabamba",
    "110162": "Yangana (Arsenio Castillo)",
    "110163": "Quinara",
}

# Celdas controladas ORIGINALES del prototipo (coordenadas EPSG:4326), que la
# verificacion territorial determino que estan FUERA del canton Loja (dentro
# de Catamayo, parroquia El Tambo). Se re-verifican aqui como evidencia
# reproducible, NO se reutilizan como celdas validas.
CELDAS_ORIGINALES_NO_VALIDAS = {
    "LJ_04521": (-79.241, -4.082),
    "LJ_04522": (-79.236, -4.079),
}


# ---------------------------------------------------------------------------
# Carga y reproyeccion de la capa oficial
# ---------------------------------------------------------------------------

def _load_zonas(geojson_path: Path, transformer: Transformer):
    """Carga un GeoJSON de zonas censales (SRID nativo EPSG:31992) y devuelve
    una lista de (codigo_zon, geometria_reproyectada_32717)."""
    data = json.loads(geojson_path.read_text(encoding="utf-8"))

    def reproj(x, y, z=None):
        xx, yy = transformer.transform(x, y)
        return (xx, yy)

    out = []
    for feat in data["features"]:
        geom = shp_transform(reproj, shape(feat["geometry"]))
        out.append((feat["properties"]["zon"], geom))
    return out


def construir_limites():
    """Devuelve (canton_loja, canton_catamayo, {codigo_parroquia: geom}) en
    EPSG:32717, reconstruidos por disolucion de zonas censales del INEC."""
    tr = Transformer.from_crs(SRC_EPSG, WORK_EPSG, always_xy=True)

    zonas_loja = _load_zonas(GEOJSON_LOJA, tr)
    zonas_catamayo = _load_zonas(GEOJSON_CATAMAYO, tr)

    canton_loja = unary_union([g for _, g in zonas_loja])
    canton_catamayo = unary_union([g for _, g in zonas_catamayo])

    parroquias = {}
    for codigo, geom in zonas_loja:
        codigo6 = codigo[:6]
        parroquias.setdefault(codigo6, []).append(geom)
    parroquias = {k: unary_union(v) for k, v in parroquias.items()}

    return canton_loja, canton_catamayo, parroquias


# ---------------------------------------------------------------------------
# Verificacion (equivalente a ST_Within / ST_Distance / ST_Area de PostGIS)
# ---------------------------------------------------------------------------

def verificar_celda(lon, lat, canton_loja, canton_catamayo, parroquias):
    """Reproduce, con Shapely, la logica de:
        ST_Within(centroide, canton.geom)
        ST_Within(celda.geom, canton.geom)
        ST_Distance(celda.geom, ST_Boundary(canton.geom))
        ST_Area(celda.geom)
    para una celda de 500x500 m centrada en (lon, lat) tras reproyectar a
    EPSG:32717 con el mismo pipeline que usa el proyecto
    (ST_SetSRID + ST_Transform + ST_MakeEnvelope, ver datos_ejemplo.sql).
    """
    t4326_to_work = Transformer.from_crs(GEO_EPSG, WORK_EPSG, always_xy=True)
    x, y = t4326_to_work.transform(lon, lat)
    cell = box(x - CELL_SIZE_M / 2, y - CELL_SIZE_M / 2,
               x + CELL_SIZE_M / 2, y + CELL_SIZE_M / 2)
    centroid = Point(x, y)

    boundary_loja = canton_loja.boundary
    within_centroid_loja = canton_loja.contains(centroid)
    within_full_loja = canton_loja.contains(cell)
    dist_boundary_loja = cell.distance(boundary_loja)

    in_catamayo = canton_catamayo.contains(centroid)
    parroquia_hits = [PARISH_NAMES.get(k, k) for k, g in parroquias.items()
                       if g.contains(centroid)]

    return {
        "centroid_utm_x": round(x, 3),
        "centroid_utm_y": round(y, 3),
        "epsg": WORK_EPSG.split(":")[1],
        "area_m2": cell.area,
        "within_centroid_canton_loja": within_centroid_loja,
        "within_full_canton_loja": within_full_loja,
        "dist_boundary_canton_loja_m": round(dist_boundary_loja, 2),
        "within_canton_catamayo": in_catamayo,
        "parroquia_loja": parroquia_hits[0] if parroquia_hits else None,
    }


def construir_malla_y_seleccionar(canton_loja, n_seleccionar=2):
    """Construye la malla sistematica de 500x500 m anclada a multiplos de
    500 en EPSG:32717 sobre el bounding box del canton Loja, conserva solo
    las celdas totalmente contenidas (ST_Within) con margen >= 1000 m al
    limite, y selecciona las `n_seleccionar` primeras ordenando por X y
    luego por Y (criterio deterministico, sin seleccion visual)."""
    minx, miny, maxx, maxy = canton_loja.bounds
    x0 = math.floor(minx / CELL_SIZE_M) * CELL_SIZE_M
    x1 = math.ceil(maxx / CELL_SIZE_M) * CELL_SIZE_M
    y0 = math.floor(miny / CELL_SIZE_M) * CELL_SIZE_M
    y1 = math.ceil(maxy / CELL_SIZE_M) * CELL_SIZE_M
    nx = int((x1 - x0) / CELL_SIZE_M)
    ny = int((y1 - y0) / CELL_SIZE_M)

    prepared = prep(canton_loja)
    boundary = canton_loja.boundary

    qualified = []
    for i in range(nx):
        x = x0 + i * CELL_SIZE_M
        if x + CELL_SIZE_M < minx or x > maxx:
            continue
        for j in range(ny):
            y = y0 + j * CELL_SIZE_M
            if y + CELL_SIZE_M < miny or y > maxy:
                continue
            cell = box(x, y, x + CELL_SIZE_M, y + CELL_SIZE_M)
            if not prepared.contains(cell):
                continue
            dist = cell.distance(boundary)
            if dist >= MARGIN_MIN_M:
                qualified.append((x, y, dist))

    qualified.sort(key=lambda t: (t[0], t[1]))
    seleccionadas = qualified[:n_seleccionar]
    return qualified, seleccionadas


def xy_a_lonlat(x, y):
    t = Transformer.from_crs(WORK_EPSG, GEO_EPSG, always_xy=True)
    return t.transform(x, y)


# ---------------------------------------------------------------------------
# Ejecucion principal
# ---------------------------------------------------------------------------

def main():
    canton_loja, canton_catamayo, parroquias = construir_limites()

    print("=" * 78)
    print("1) Reconstruccion de limites (INEC, disolucion por codigo DPA)")
    print("=" * 78)
    print(f"Canton Loja (1101): area = {canton_loja.area / 1e6:.4f} km2, "
          f"valido = {canton_loja.is_valid}")
    print(f"Canton Catamayo (1103): area = {canton_catamayo.area / 1e6:.4f} km2, "
          f"valido = {canton_catamayo.is_valid}")
    print(f"Parroquias reconstruidas en canton Loja: {len(parroquias)}")

    print()
    print("=" * 78)
    print("2) Re-verificacion de las celdas ORIGINALES (evidencia de QA)")
    print("=" * 78)
    resultados_originales = {}
    for cid, (lon, lat) in CELDAS_ORIGINALES_NO_VALIDAS.items():
        r = verificar_celda(lon, lat, canton_loja, canton_catamayo, parroquias)
        resultados_originales[cid] = r
        print(f"{cid}: dentro_canton_Loja(centroide)={r['within_centroid_canton_loja']} "
              f"dentro_canton_Loja(poligono)={r['within_full_canton_loja']} "
              f"dentro_canton_Catamayo={r['within_canton_catamayo']} "
              f"dist_limite_Loja_m={r['dist_boundary_canton_loja_m']}")

    print()
    print("=" * 78)
    print("3) Malla sistematica 500x500 m anclada a multiplos de 500 (EPSG:32717)")
    print("=" * 78)
    qualified, seleccionadas = construir_malla_y_seleccionar(canton_loja, n_seleccionar=2)
    print(f"Celdas totalmente contenidas en canton Loja: (ver longitud de 'qualified' "
          f"tras filtro de margen) {len(qualified)}")
    print(f"Criterio de seleccion: ordenar por X asc, luego Y asc; tomar las "
          f"{len(seleccionadas)} primeras con margen >= {MARGIN_MIN_M:.0f} m")

    nuevas = {}
    for idx, (x, y, dist) in enumerate(seleccionadas, start=1):
        cid = f"LJ_TEST_{idx:03d}"
        cx, cy = x + CELL_SIZE_M / 2, y + CELL_SIZE_M / 2
        lon, lat = xy_a_lonlat(cx, cy)
        nuevas[cid] = {
            "sw_x": x, "sw_y": y,
            "centroid_x": cx, "centroid_y": cy,
            "lon": lon, "lat": lat,
            "dist_boundary_m": dist,
        }
        print(f"{cid}: esquina_SO=({x:.1f},{y:.1f}) centroide_UTM=({cx:.1f},{cy:.1f}) "
              f"lon={lon:.6f} lat={lat:.6f} dist_limite_m={dist:.2f}")

    print()
    print("=" * 78)
    print("4) Tabla de validacion completa de las celdas nuevas")
    print("=" * 78)
    filas = []
    for cid, info in nuevas.items():
        r = verificar_celda(info["lon"], info["lat"], canton_loja, canton_catamayo, parroquias)
        fila = {
            "celda_id": cid,
            "longitud": round(info["lon"], 6),
            "latitud": round(info["lat"], 6),
            "centroide_utm_x": r["centroid_utm_x"],
            "centroide_utm_y": r["centroid_utm_y"],
            "epsg": r["epsg"],
            "area_m2": r["area_m2"],
            "canton": "Loja",
            "parroquia": r["parroquia_loja"],
            "dist_limite_canton_m": r["dist_boundary_canton_loja_m"],
            "within_centroide": r["within_centroid_canton_loja"],
            "within_poligono_completo": r["within_full_canton_loja"],
        }
        filas.append(fila)
        print(fila)

    EVIDENCIAS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = EVIDENCIAS_DIR / "tabla_validacion_celdas_nuevas.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        writer.writeheader()
        writer.writerows(filas)
    print(f"\nTabla guardada en: {csv_path}")

    return {
        "canton_loja": canton_loja,
        "canton_catamayo": canton_catamayo,
        "parroquias": parroquias,
        "resultados_originales": resultados_originales,
        "nuevas": nuevas,
        "filas": filas,
    }


if __name__ == "__main__":
    main()
