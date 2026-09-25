"""
Carga Masiva de Producción en PostgreSQL / PostGIS (7.997 Celdas)
Proyecto Integrador FireForest - Grupo 04

Puebla:
1. dim_celda con las 7.997 celdas del cantón Loja y su geometría poligonal PostGIS (SRID 32717).
2. dim_fecha con los periodos mensuales y calendario de 2023.
3. fact_celda_mes con las 95.964 observaciones anuales consolidadas.
4. Índices B-Tree y GiST para aceleración de consultas analíticas y espaciales.
"""

import os
import sys
import time
from pathlib import Path
import pandas as pd
from pyproj import Transformer
import psycopg
from dotenv import load_dotenv

# Cargar variables de entorno
base_dir = Path(__file__).resolve().parents[2]
env_path = base_dir / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(env_path)


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "fireforest"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "jack2jun8945")
    )


def main():
    start_time = time.time()
    print("=" * 80)
    print("CARGA DE PRODUCCIÓN EN POSTGRESQL / POSTGIS (MALLA COMPLETA 7.997 CELDAS)")
    print("=" * 80)

    clean_dir = base_dir / "tarea_ETL" / "clean"
    curated_dir = base_dir / "tarea_ETL" / "curated"

    malla_file = clean_dir / "malla_500m.parquet"
    curated_file = curated_dir / "fireforest_celda_mes_2023.parquet"

    if not malla_file.exists() or not curated_file.exists():
        print("[ERROR] No se encontraron los archivos Parquet en clean/curated.")
        sys.exit(1)

    print("1. Leyendo datos limpios de la malla y dataset curado...")
    df_malla = pd.read_parquet(malla_file)
    df_curated = pd.read_parquet(curated_file)
    print(f"   - Malla leída: {len(df_malla):,} celdas")
    print(f"   - Curated leído: {len(df_curated):,} observaciones celda-mes")

    # Transformar coordenadas UTM 17S (EPSG:32717) a WGS84 (EPSG:4326) para lat/lon
    transformer = Transformer.from_crs("EPSG:32717", "EPSG:4326", always_xy=True)
    lons, lats = transformer.transform(df_malla["centro_x_m"].values, df_malla["centro_y_m"].values)
    df_malla["longitud"] = lons
    df_malla["latitud"] = lats

    conn = get_db_connection()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            print("\n2. Preparando extensiones y tablas en PostgreSQL...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

            # Crear tabla fact_celda_mes para el data mart analítico
            cur.execute("""
                CREATE TABLE IF NOT EXISTS fact_celda_mes (
                    id_celda_mes VARCHAR(40) PRIMARY KEY,
                    cell_id VARCHAR(30) NOT NULL REFERENCES dim_celda(celda_id),
                    anio SMALLINT NOT NULL,
                    mes SMALLINT NOT NULL,
                    precipitacion_acumulada_mm NUMERIC(10,2),
                    precipitacion_media_diaria_mm NUMERIC(10,2),
                    precipitacion_maxima_diaria_mm NUMERIC(10,2),
                    dias_humedos_ge1mm SMALLINT,
                    dias_secos_lt1mm SMALLINT,
                    detecciones_incendio NUMERIC(10,2) DEFAULT 0,
                    frp_total_mw NUMERIC(12,2) DEFAULT 0,
                    incendio_observado BOOLEAN NOT NULL DEFAULT FALSE,
                    apto_analisis BOOLEAN NOT NULL DEFAULT TRUE,
                    motivo_no_apto VARCHAR(100)
                );
            """)

            # 2.1 Carga de dim_celda
            print("3. Poblando dim_celda (7.997 celdas con poligonos PostGIS)...")
            celdas_data = []
            for _, r in df_malla.iterrows():
                # Geometria poligonal ST_MakeEnvelope(xmin, ymin, xmax, ymax, 32717)
                celdas_data.append((
                    r["cell_id"],
                    float(r["longitud"]),
                    float(r["latitud"]),
                    float(r["area_nominal_ha"] / 100.0), # km2
                    32717,
                    float(r["xmin_m"]),
                    float(r["ymin_m"]),
                    float(r["xmax_m"]),
                    float(r["ymax_m"])
                ))

            # Upsert celdas
            cur.executemany("""
                INSERT INTO dim_celda (celda_id, longitud, latitud, area_km2, epsg, geom)
                VALUES (%s, %s, %s, %s, %s, ST_MakeEnvelope(%s, %s, %s, %s, 32717))
                ON CONFLICT (celda_id) DO UPDATE SET
                    longitud = EXCLUDED.longitud,
                    latitud = EXCLUDED.latitud,
                    area_km2 = EXCLUDED.area_km2,
                    geom = EXCLUDED.geom;
            """, celdas_data)
            print(f"   [OK] {len(celdas_data):,} celdas cargadas exitosamente.")

            # 2.2 Carga de dim_fecha (meses de 2023)
            print("4. Poblando dim_fecha con el calendario del año 2023...")
            fechas_data = []
            for m in range(1, 13):
                # Representar cada mes como primer día
                fechas_data.append((
                    202300 + m, # fecha_id
                    f"2023-{m:02d}-01",
                    2023,
                    m
                ))
            cur.executemany("""
                INSERT INTO dim_fecha (fecha_id, fecha, anio, mes)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (fecha_id) DO UPDATE SET
                    fecha = EXCLUDED.fecha,
                    anio = EXCLUDED.anio,
                    mes = EXCLUDED.mes;
            """, fechas_data)
            print(f"   [OK] {len(fechas_data)} periodos registrados en dim_fecha.")

            # 2.3 Carga masiva de fact_celda_mes
            print("5. Poblando fact_celda_mes (95.964 observaciones)...")
            fact_data = []
            for _, r in df_curated.iterrows():
                fact_data.append((
                    r["id_celda_mes"],
                    r["cell_id"],
                    int(r["anio"]),
                    int(r["mes"]),
                    float(r["precipitacion_acumulada_mm"]) if pd.notnull(r["precipitacion_acumulada_mm"]) else None,
                    float(r["precipitacion_media_diaria_mm"]) if pd.notnull(r["precipitacion_media_diaria_mm"]) else None,
                    float(r["precipitacion_maxima_diaria_mm"]) if pd.notnull(r["precipitacion_maxima_diaria_mm"]) else None,
                    int(r["dias_humedos_ge1mm"]) if pd.notnull(r["dias_humedos_ge1mm"]) else None,
                    int(r["dias_secos_lt1mm"]) if pd.notnull(r["dias_secos_lt1mm"]) else None,
                    float(r["detecciones_todas_media"]) if pd.notnull(r["detecciones_todas_media"]) else 0.0,
                    float(r["frp_suma_observada_media_mw"]) if pd.notnull(r["frp_suma_observada_media_mw"]) else 0.0,
                    bool(r["evidencia_fuego"]) if pd.notnull(r["evidencia_fuego"]) else False,
                    bool(r["apto_analisis"]) if pd.notnull(r["apto_analisis"]) else True,
                    str(r["motivo_no_apto_analisis"]) if pd.notnull(r["motivo_no_apto_analisis"]) else None
                ))

            cur.executemany("""
                INSERT INTO fact_celda_mes (
                    id_celda_mes, cell_id, anio, mes,
                    precipitacion_acumulada_mm, precipitacion_media_diaria_mm, precipitacion_maxima_diaria_mm,
                    dias_humedos_ge1mm, dias_secos_lt1mm,
                    detecciones_incendio, frp_total_mw, incendio_observado,
                    apto_analisis, motivo_no_apto
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_celda_mes) DO UPDATE SET
                    precipitacion_acumulada_mm = EXCLUDED.precipitacion_acumulada_mm,
                    detecciones_incendio = EXCLUDED.detecciones_incendio,
                    frp_total_mw = EXCLUDED.frp_total_mw,
                    incendio_observado = EXCLUDED.incendio_observado,
                    apto_analisis = EXCLUDED.apto_analisis;
            """, fact_data)
            print(f"   [OK] {len(fact_data):,} filas cargadas en fact_celda_mes.")

            # Crear indices
            print("6. Optimizando índices espaciales y analíticos...")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_dim_celda_geom ON dim_celda USING GIST (geom);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_mes_celda ON fact_celda_mes (cell_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_mes_periodo ON fact_celda_mes (anio, mes);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_mes_incendio ON fact_celda_mes (incendio_observado);")

            conn.commit()
            print("   [COMMIT] Transacción completada con éxito.")

            # -----------------------------------------------------------------
            # CONSULTAS DE VALIDACIÓN Y TABLAS EN PANTALLA
            # -----------------------------------------------------------------
            print("\n" + "=" * 80)
            print("RESULTADOS TABULARES EN POSTGRESQL / POSTGIS")
            print("=" * 80)

            print("\n[TABLA SQL 1] CONTEO Y VERIFICACIÓN DE TABLAS DE PRODUCCIÓN")
            cur.execute("""
                SELECT 'dim_celda' as tabla, count(*) as filas FROM dim_celda
                UNION ALL
                SELECT 'dim_fecha', count(*) FROM dim_fecha
                UNION ALL
                SELECT 'fact_celda_mes', count(*) FROM fact_celda_mes;
            """)
            print(f"{'Tabla':<20} | {'Total Filas':<15}")
            print("-" * 38)
            for r in cur.fetchall():
                print(f"{r[0]:<20} | {r[1]:<15,}")

            print("\n[TABLA SQL 2] TOP 5 CELDAS CON MAYOR FRP Y COORDENADAS ESPACIALES POSTGIS")
            cur.execute("""
                SELECT 
                    f.cell_id,
                    c.longitud,
                    c.latitud,
                    f.mes,
                    f.precipitacion_acumulada_mm,
                    f.frp_total_mw,
                    ST_GeometryType(c.geom) as tipo_geom,
                    ROUND(ST_Area(c.geom)::numeric, 0) as area_m2
                FROM fact_celda_mes f
                JOIN dim_celda c ON f.cell_id = c.celda_id
                WHERE f.incendio_observado = true
                ORDER BY f.frp_total_mw DESC
                LIMIT 5;
            """)
            print(f"{'Celda ID':<16} | {'Longitud':<10} | {'Latitud':<10} | {'Mes':<4} | {'Precip mm':<10} | {'FRP MW':<8} | {'Tipo PostGIS':<12} | {'Área m²':<10}")
            print("-" * 92)
            for r in cur.fetchall():
                print(f"{r[0]:<16} | {r[1]:<10.5f} | {r[2]:<10.5f} | {r[3]:<4} | {r[4]:<10.2f} | {r[5]:<8.2f} | {r[6]:<12} | {r[7]:<10,}")

            print("\n[TABLA SQL 3] RESUMEN ESTACIONAL DE INCENDIOS Y PRECIPITACIÓN EN SQL")
            cur.execute("""
                SELECT 
                    CASE 
                        WHEN mes IN (12, 1, 2) THEN 'Verano/Lluvias Temp'
                        WHEN mes IN (3, 4, 5) THEN 'Otoño/Lluvioso'
                        WHEN mes IN (6, 7, 8) THEN 'Invierno/Seco'
                        ELSE 'Primavera/Fin de Sequia'
                    END as temporada,
                    count(*) as observaciones,
                    ROUND(AVG(precipitacion_acumulada_mm), 2) as precip_media_mm,
                    SUM(CASE WHEN incendio_observado THEN 1 ELSE 0 END) as celdas_con_fuego,
                    ROUND(SUM(frp_total_mw), 2) as frp_total_mw
                FROM fact_celda_mes
                GROUP BY 1
                ORDER BY celdas_con_fuego DESC;
            """)
            print(f"{'Temporada':<25} | {'Observaciones':<14} | {'Precip Media mm':<16} | {'Celdas Fuego':<14} | {'FRP Total MW':<12}")
            print("-" * 88)
            for r in cur.fetchall():
                print(f"{r[0]:<25} | {r[1]:<14,} | {r[2]:<16} | {r[3]:<14,} | {r[4]:<12,}")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error durante la carga en PostgreSQL: {e}")
        raise e
    finally:
        conn.close()

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 80)
    print(f"[EXITO] Carga de Producción en PostgreSQL/PostGIS completada en {elapsed} segundos.")
    print("=" * 80)


if __name__ == "__main__":
    main()
