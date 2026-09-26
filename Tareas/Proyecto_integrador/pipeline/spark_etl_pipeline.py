"""
Pipeline de Procesamiento Distribuido con Apache Spark / PySpark
Proyecto Integrador FireForest - Grupo 04

Este script implementa el procesamiento escalable del dataset cantonal de Loja (7.997 celdas x 12 meses):
1. Ingesta distribuida de Malla Espacial, CHIRPS (Clima) y VIIRS (Incendios).
2. Transformaciones con Window Functions (Lags de precipitación, déficit hídrico acumulado).
3. Consultas analíticas y de auditoría con Spark SQL.
4. Exportación del Data Mart Curated particionado en formato Parquet.
"""

import os
import sys
import time
import json
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def get_spark_session() -> SparkSession:
    """Inicializa la sesión de Spark optimizada para ejecución local."""
    return (
        SparkSession.builder
        .appName("FireForest_Spark_Pipeline")
        .master("local[*]")
        .config("spark.driver.memory", "4g")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .getOrCreate()
    )


def main():
    start_time = time.time()
    print("=" * 80)
    print("INICIANDO PIPELINE DISTRIBUIDO CON APACHE SPARK (PySpark)")
    print("=" * 80)

    base_dir = Path(__file__).resolve().parents[1] if Path(__file__).resolve().parent.name == "pipeline" else Path(__file__).resolve().parents[2]
    clean_dir = base_dir / "datos" / "curated"
    if not (clean_dir / "malla_500m.parquet").exists():
        clean_dir = base_dir / "tarea_ETL" / "clean"
    curated_dir = base_dir / "datos" / "curated"
    if not (curated_dir / "fireforest_celda_mes_2023.parquet").exists():
        curated_dir = base_dir / "tarea_ETL" / "curated"
    output_dir = base_dir / "pipeline"
    parquet_out = output_dir / "curated_spark_parquet"
    parquet_out.mkdir(parents=True, exist_ok=True)

    spark = get_spark_session()
    spark.sparkContext.setLogLevel("ERROR")
    print(f"[OK] Sesion de Apache Spark version {spark.version} iniciada correctamente.\n")

    # -------------------------------------------------------------------------
    # 1. CARGA DISTRIBUIDA DE DATASETS
    # -------------------------------------------------------------------------
    print("1. Ingesta de fuentes de datos hacia DataFrames de Spark...")
    malla_path = clean_dir / "malla_500m.parquet"
    chirps_path = clean_dir / "chirps_2023.parquet"
    viirs_path = clean_dir / "viirs_2023.parquet"

    if not malla_path.exists() or not chirps_path.exists() or not viirs_path.exists():
        print(f"[ERROR] No se encontraron los archivos en {clean_dir}")
        sys.exit(1)

    df_malla = spark.read.parquet(str(malla_path))
    df_chirps = spark.read.parquet(str(chirps_path))
    df_viirs = spark.read.parquet(str(viirs_path))

    malla_count = df_malla.count()
    chirps_count = df_chirps.count()
    viirs_count = df_viirs.count()

    print(f"   - Malla Cantonal 500m : {malla_count:,} celdas espaciales")
    print(f"   - Registros CHIRPS    : {chirps_count:,} observaciones mensuales")
    print(f"   - Registros VIIRS     : {viirs_count:,} observaciones mensuales\n")

    # -------------------------------------------------------------------------
    # 2. INTEGRACION Y TRANSFORMACION CON WINDOW FUNCTIONS
    # -------------------------------------------------------------------------
    print("2. Integracion de malla, clima e incendios y calculo de variables derivadas...")

    # Join entre Malla y Clima (evitando duplicar fila y columna que ya vienen en chirps)
    malla_cols_to_keep = [c for c in df_malla.columns if c not in df_chirps.columns or c == "cell_id"]
    df_clima_malla = df_chirps.join(
        df_malla.select(*malla_cols_to_keep),
        on="cell_id",
        how="inner"
    )

    # Left Join hacia VIIRS (evidencia satelital)
    df_integrado = df_clima_malla.join(
        df_viirs.select(
            "cell_id", "anio", "mes",
            F.col("detecciones_todas_media").alias("viirs_detecciones_media"),
            F.col("presencia_fuego_frac").alias("viirs_presencia_fuego_frac"),
            F.col("frp_suma_observada_media_mw").alias("viirs_frp_suma_mw"),
            F.col("frp_maxima_media_mw").alias("viirs_frp_maxima_mw"),
            F.col("evidencia_fuego").alias("viirs_evidencia_fuego"),
            F.col("dias_validos_media").alias("viirs_dias_validos"),
            F.col("observacion_viirs_disponible")
        ),
        on=["cell_id", "anio", "mes"],
        how="left"
    )

    # Bandera de aptitud para analisis: replica el contrato de calidad de la capa Curated
    # (observacion_viirs_disponible AND observado_mes AND cobertura_chirps_valida). Las celdas-mes
    # sin cobertura VIIRS deben quedar excluidas del entrenamiento, no reinterpretadas como "sin fuego".
    df_integrado = df_integrado.withColumn(
        "apto_analisis",
        F.coalesce(F.col("observacion_viirs_disponible"), F.lit(False))
        & F.coalesce(F.col("observado_mes"), F.lit(False))
        & F.coalesce(F.col("cobertura_chirps_valida"), F.lit(False))
    ).withColumn(
        # Variable objetivo: se conserva nula cuando no hay observacion satelital, en lugar de
        # coalescerse a False (lo que la reinterpretaria como ausencia confirmada de incendio).
        "incendio_observado",
        F.col("viirs_evidencia_fuego")
    ).withColumn(
        "detecciones_incendio",
        F.coalesce(F.col("viirs_detecciones_media"), F.lit(0.0))
    ).withColumn(
        "frp_total_mw",
        F.coalesce(F.col("viirs_frp_suma_mw"), F.lit(0.0))
    )

    # Definir ventana temporal por celda ordenada por mes
    w_celda = Window.partitionBy("cell_id").orderBy("mes")
    w_celda_3m = Window.partitionBy("cell_id").orderBy("mes").rowsBetween(-2, 0)

    # Calculo de caracteristicas avanzadas (Lags y medias moviles)
    df_analitico = df_integrado.withColumn(
        "precip_lag_1m",
        F.lag("precipitacion_acumulada_mm", 1).over(w_celda)
    ).withColumn(
        "precip_lag_2m",
        F.lag("precipitacion_acumulada_mm", 2).over(w_celda)
    ).withColumn(
        "precip_media_movil_3m",
        F.avg("precipitacion_acumulada_mm").over(w_celda_3m)
    ).withColumn(
        "dias_secos_acumulados_3m",
        F.sum("dias_secos_lt1mm").over(w_celda_3m)
    ).withColumn(
        # Indice de severidad de sequia: precipitacion acumulada < 30mm y lag < 30mm
        "condicion_sequia_extrema",
        F.when(
            (F.col("precipitacion_acumulada_mm") < 30.0) &
            (F.coalesce(F.col("precip_lag_1m"), F.lit(999.0)) < 40.0),
            True
        ).otherwise(False)
    ).withColumn(
        # Categoria de riesgo de incendio combinando sequia y calor
        "categoria_riesgo_forestal",
        F.when(
            (F.coalesce(F.col("incendio_observado"), F.lit(False)) == True) | (F.col("frp_total_mw") > 5.0),
            F.lit("ALTO_IMPACTO")
        ).when(
            (F.col("condicion_sequia_extrema") == True) & (F.col("dias_secos_lt1mm") >= 25),
            F.lit("RIESGO_ALTO_SEQUIA")
        ).when(
            F.col("precipitacion_acumulada_mm") < 50.0,
            F.lit("RIESGO_MODERADO")
        ).otherwise(
            F.lit("RIESGO_BAJO")
        )
    )

    df_analitico.createOrReplaceTempView("view_fireforest_celda_mes")

    # -------------------------------------------------------------------------
    # 3. CONSULTAS ANALITICAS CON SPARK SQL (TABLAS DE RESULTADOS)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("RESULTADOS TABULARES OBTENIDOS MEDIANTE SPARK SQL")
    print("=" * 80)

    # TABLA 1: Balance Cantonal Mensual (12 Meses del 2023)
    print("\n[TABLA 1] BALANCE MENSUAL CANTONAL DE CLIMA E INCENDIOS (7.997 CELDAS)")
    tabla_1 = spark.sql("""
        SELECT 
            mes,
            COUNT(DISTINCT cell_id) as total_celdas,
            ROUND(AVG(precipitacion_acumulada_mm), 2) as precip_media_cantonal_mm,
            ROUND(MIN(precipitacion_acumulada_mm), 2) as precip_min_mm,
            ROUND(MAX(precipitacion_acumulada_mm), 2) as precip_max_mm,
            ROUND(AVG(dias_secos_lt1mm), 1) as dias_secos_promedio,
            SUM(CASE WHEN incendio_observado THEN 1 ELSE 0 END) as celdas_con_fuego,
            ROUND(SUM(frp_total_mw), 2) as frp_total_acumulado_mw
        FROM view_fireforest_celda_mes
        GROUP BY mes
        ORDER BY mes
    """)
    tabla_1.show(12, truncate=False)

    # TABLA 2: Top 10 Celdas con Mayor Actividad de Incendio
    print("\n[TABLA 2] TOP 10 CELDAS CON MAYOR RADIACION TERMICA (FRP) EN 2023")
    tabla_2 = spark.sql("""
        SELECT 
            cell_id,
            fila,
            columna,
            mes,
            ROUND(precipitacion_acumulada_mm, 2) as precip_mes_mm,
            ROUND(precip_lag_1m, 2) as precip_mes_anterior_mm,
            dias_secos_lt1mm,
            ROUND(frp_total_mw, 2) as frp_mw,
            categoria_riesgo_forestal
        FROM view_fireforest_celda_mes
        WHERE incendio_observado = true
        ORDER BY frp_total_mw DESC
        LIMIT 10
    """)
    tabla_2.show(10, truncate=False)

    # TABLA 3: Matriz de Contingencia Sequia vs Incendios
    print("\n[TABLA 3] MATRIZ DE CONTINGENCIA: CONDICION DE SEQUIA VS INCENDIO OBSERVADO")
    tabla_3 = spark.sql("""
        SELECT 
            condicion_sequia_extrema,
            categoria_riesgo_forestal,
            COUNT(*) as total_observaciones_celda_mes,
            SUM(CASE WHEN incendio_observado THEN 1 ELSE 0 END) as casos_con_incendio,
            ROUND(100.0 * SUM(CASE WHEN incendio_observado THEN 1 ELSE 0 END) / COUNT(*), 4) as tasa_incidencia_pct
        FROM view_fireforest_celda_mes
        GROUP BY condicion_sequia_extrema, categoria_riesgo_forestal
        ORDER BY condicion_sequia_extrema DESC, casos_con_incendio DESC
    """)
    tabla_3.show(truncate=False)

    # TABLA 4: Auditoria de Cobertura Espacial de la Malla
    print("\n[TABLA 4] AUDITORIA DE COBERTURA ESPACIAL CANTONAL (7.997 CELDAS)")
    tabla_4 = spark.sql("""
        SELECT 
            categoria_cobertura_territorial,
            es_celda_completa,
            COUNT(DISTINCT cell_id) as total_celdas,
            ROUND(100.0 * COUNT(DISTINCT cell_id) / 7997.0, 2) as pct_territorio,
            ROUND(SUM(area_dentro_loja_ha), 2) as area_total_ha
        FROM view_fireforest_celda_mes
        WHERE mes = 1
        GROUP BY categoria_cobertura_territorial, es_celda_completa
        ORDER BY total_celdas DESC
    """)
    tabla_4.show(truncate=False)

    # -------------------------------------------------------------------------
    # 4. EXPORTACION DEL DATA LAKE PARQUET PARTICIONADO
    # -------------------------------------------------------------------------
    print(f"\n4. Exportando Data Lake Curated particionado en: {parquet_out} ...")
    
    # En Windows, para evitar la dependencia de hadoop/winutils.exe, convertimos el DataFrame
    # distribuido a tabla Arrow/Pandas y particionamos de forma nativa e inmutable.
    pdf_analitico = df_analitico.toPandas()
    import pyarrow as pa
    import pyarrow.dataset as ds

    table = pa.Table.from_pandas(pdf_analitico)
    ds.write_dataset(
        table,
        base_dir=str(parquet_out),
        format="parquet",
        partitioning=["anio", "mes"],
        existing_data_behavior="overwrite_or_ignore"
    )

    # Guardar métricas en JSON
    metrics = {
        "spark_version": spark.version,
        "malla_celdas_totales": malla_count,
        "total_registros_procesados": len(pdf_analitico),
        "columnas_totales": len(pdf_analitico.columns),
        "columnas": list(pdf_analitico.columns),
        "meses_evaluados": 12,
        "anio": 2023,
        "tiempo_ejecucion_segundos": round(time.time() - start_time, 2),
        "salida_parquet": str(parquet_out)
    }
    
    with open(output_dir / "metricas_spark.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    # Generar informe Markdown con los resultados de Spark
    with open(output_dir / "resumen_spark.md", "w", encoding="utf-8") as f:
        f.write("# Evidencia de Ejecución de Apache Spark / PySpark\n\n")
        f.write(f"- **Versión Spark:** {spark.version}\n")
        f.write(f"- **Total Celdas Cantonales:** {malla_count:,}\n")
        f.write(f"- **Total Observaciones Celda-Mes:** {len(pdf_analitico):,}\n")
        f.write(f"- **Tiempo de Cómputo Distribuido:** {metrics['tiempo_ejecucion_segundos']} segundos\n")
        f.write(f"- **Ubicación Parquet Particionado:** `{parquet_out}`\n\n")
        f.write("## Variables Generadas por PySpark:\n")
        for col in pdf_analitico.columns:
            f.write(f"- `{col}`\n")

    print("\n" + "=" * 80)
    print(f"[EXITO] Pipeline PySpark completado en {metrics['tiempo_ejecucion_segundos']} segundos.")
    print(f"Total registros analiticos consolidados: {metrics['total_registros_procesados']:,}")
    print(f"Particiones Parquet generadas exitosamente en {parquet_out}")
    print("=" * 80)

    spark.stop()


if __name__ == "__main__":
    main()
