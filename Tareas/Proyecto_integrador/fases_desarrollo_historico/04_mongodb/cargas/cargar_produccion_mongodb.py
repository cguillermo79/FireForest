"""
Carga de Producción en MongoDB (Telemetría Satelital NoSQL)
Proyecto Integrador FireForest - Grupo 04

Puebla la colección `detecciones_viirs` y `evidencia_viirs_celda_mes` con documentos
semiestructurados correspondientes a la telemetría satelital 2023.
Ejecuta pipelines de agregación documental para auditoría y analítica.
"""

import os
import sys
import time
from pathlib import Path
import pandas as pd
import pymongo
from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parents[2]
env_path = base_dir / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(env_path)


def main():
    start_time = time.time()
    print("=" * 80)
    print("CARGA DE TELEMETRÍA SATELITAL EN MONGODB (COLECCIONES DE PRODUCCIÓN)")
    print("=" * 80)

    curated_file = base_dir / "tarea_ETL" / "curated" / "fireforest_celda_mes_2023.parquet"
    malla_file = base_dir / "tarea_ETL" / "clean" / "malla_500m.parquet"

    df_curated = pd.read_parquet(curated_file)
    df_malla = pd.read_parquet(malla_file)

    # Filtrar todos los eventos de incendio (747 casos) + muestra balanceada de control (453 casos)
    df_fuegos = df_curated[df_curated["evidencia_fuego"] == True]
    df_control = df_curated[df_curated["evidencia_fuego"] == False].sample(n=453, random_state=2026)
    df_muestra = pd.concat([df_fuegos, df_control]).reset_index(drop=True)

    # Pegar coordenadas de la malla
    from pyproj import Transformer
    transformer = Transformer.from_crs("EPSG:32717", "EPSG:4326", always_xy=True)
    coords_dict = {}
    for _, r in df_malla.iterrows():
        lon, lat = transformer.transform(r["centro_x_m"], r["centro_y_m"])
        coords_dict[r["cell_id"]] = {"longitud": round(lon, 6), "latitud": round(lat, 6)}

    # Conectar a MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGO_DB", "fireforest")
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]

    col_telemetria = db["evidencia_viirs_celda_mes"]

    # Construir documentos BSON enriquecidos
    documentos = []
    for _, r in df_muestra.iterrows():
        cid = r["cell_id"]
        coords = coords_dict.get(cid, {"longitud": -79.2, "latitud": -4.0})
        doc = {
            "id_celda_mes": r["id_celda_mes"],
            "celda": {
                "cell_id": cid,
                "cell_index": int(r["cell_index"]),
                "fila": int(r["fila"]),
                "columna": int(r["columna"]),
                "coordenadas": {
                    "type": "Point",
                    "coordinates": [coords["longitud"], coords["latitud"]]
                }
            },
            "periodo": {
                "anio": int(r["anio"]),
                "mes": int(r["mes"]),
                "anio_mes": f"{r['anio']}-{int(r['mes']):02d}"
            },
            "sensor": {
                "fuente": "NASA FIRMS - VIIRS",
                "instrumento": "VIIRS_SNPP_375m",
                "asset_gee": str(r["asset_fuente_viirs"]) if pd.notnull(r["asset_fuente_viirs"]) else None
            },
            "telemetria": {
                "detecciones_media": float(r["detecciones_todas_media"]) if pd.notnull(r["detecciones_todas_media"]) else 0.0,
                "presencia_fraccion": float(r["presencia_fuego_frac"]) if pd.notnull(r["presencia_fuego_frac"]) else 0.0,
                "frp_suma_mw": float(r["frp_suma_observada_media_mw"]) if pd.notnull(r["frp_suma_observada_media_mw"]) else 0.0,
                "frp_maxima_mw": float(r["frp_maxima_media_mw"]) if pd.notnull(r["frp_maxima_media_mw"]) else 0.0,
                "evidencia_fuego": bool(r["evidencia_fuego"])
            },
            "clima_asociado": {
                "precipitacion_mm": float(r["precipitacion_acumulada_mm"]) if pd.notnull(r["precipitacion_acumulada_mm"]) else 0.0,
                "dias_secos": int(r["dias_secos_lt1mm"]) if pd.notnull(r["dias_secos_lt1mm"]) else 0
            },
            "calidad": {
                "apto_analisis": bool(r["apto_analisis"]),
                "dias_validos": float(r["dias_validos_media"]) if pd.notnull(r["dias_validos_media"]) else 0.0
            }
        }
        documentos.append(doc)

    print(f"1. Insertando/actualizando {len(documentos):,} documentos en la colección 'evidencia_viirs_celda_mes'...")
    col_telemetria.delete_many({}) # Limpieza para recarga limpia
    col_telemetria.insert_many(documentos)

    # Crear índices NoSQL
    col_telemetria.create_index([("periodo.anio_mes", pymongo.ASCENDING)])
    col_telemetria.create_index([("celda.cell_id", pymongo.ASCENDING)])
    col_telemetria.create_index([("telemetria.frp_suma_mw", pymongo.DESCENDING)])
    col_telemetria.create_index([("celda.coordenadas", pymongo.GEOSPHERE)])

    total_docs = col_telemetria.count_documents({})
    print(f"   [OK] {total_docs:,} documentos BSON indexados con éxito.")

    # -------------------------------------------------------------------------
    # PIPELINES DE AGREGACIÓN DOCUMENTAL (TABLAS EN PANTALLA)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("RESULTADOS TABULARES EN MONGODB (PIPELINES DE AGREGACIÓN)")
    print("=" * 80)

    # TABLA MONGO 1: Resumen de eventos por mes
    print("\n[TABLA NOSQL 1] AGREGACIÓN MENSUAL DE DETECCIONES Y RADIACIÓN TÉRMICA")
    pipeline_mes = [
        {"$group": {
            "_id": "$periodo.anio_mes",
            "total_documentos": {"$sum": 1},
            "fuegos_observados": {"$sum": {"$cond": ["$telemetria.evidencia_fuego", 1, 0]}},
            "frp_acumulado_mw": {"$sum": "$telemetria.frp_suma_mw"},
            "precip_promedio_mm": {"$avg": "$clima_asociado.precipitacion_mm"}
        }},
        {"$sort": {"_id": 1}}
    ]
    res_mes = list(col_telemetria.aggregate(pipeline_mes))
    print(f"{'Periodo':<12} | {'Docs':<8} | {'Fuegos':<8} | {'FRP Total MW':<14} | {'Precip Promedio mm':<18}")
    print("-" * 70)
    for r in res_mes:
        print(f"{r['_id']:<12} | {r['total_documentos']:<8} | {r['fuegos_observados']:<8} | {r['frp_acumulado_mw']:<14.2f} | {r['precip_promedio_mm']:<18.2f}")

    # TABLA MONGO 2: Top 5 eventos de mayor FRP en MongoDB
    print("\n[TABLA NOSQL 2] TOP 5 EVENTOS CON MAYOR FRP Y COORDENADAS GEOJSON EN MONGODB")
    pipeline_top = [
        {"$match": {"telemetria.evidencia_fuego": True}},
        {"$sort": {"telemetria.frp_suma_mw": -1}},
        {"$limit": 5},
        {"$project": {
            "_id": 0,
            "cell_id": "$celda.cell_id",
            "periodo": "$periodo.anio_mes",
            "longitud": {"$arrayElemAt": ["$celda.coordenadas.coordinates", 0]},
            "latitud": {"$arrayElemAt": ["$celda.coordenadas.coordinates", 1]},
            "frp_mw": "$telemetria.frp_suma_mw",
            "precip_mm": "$clima_asociado.precipitacion_mm"
        }}
    ]
    res_top = list(col_telemetria.aggregate(pipeline_top))
    print(f"{'Celda ID':<16} | {'Periodo':<10} | {'Longitud':<10} | {'Latitud':<10} | {'FRP MW':<10} | {'Precip mm':<10}")
    print("-" * 74)
    for r in res_top:
        print(f"{r['cell_id']:<16} | {r['periodo']:<10} | {r['longitud']:<10.5f} | {r['latitud']:<10.5f} | {r['frp_mw']:<10.2f} | {r['precip_mm']:<10.2f}")

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 80)
    print(f"[EXITO] Ingesta y Agregaciones NoSQL en MongoDB completadas en {elapsed} segundos.")
    print("=" * 80)


if __name__ == "__main__":
    main()
