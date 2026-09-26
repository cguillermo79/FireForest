"""
Entrenamiento y Evaluación del Modelo de Machine Learning
Proyecto Integrador FireForest - Grupo 04

Objetivo:
Predecir el riesgo de ocurrencia de incendio forestal por celda-mes (500m)
utilizando variables climáticas antecedentes (lags y déficit hídrico de 1 a 3 meses).
"""

import os
import sys
import time
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    precision_score, recall_score, f1_score
)
import joblib

base_dir = Path(__file__).resolve().parents[1] if Path(__file__).resolve().parent.name == "machine_learning" else Path(__file__).resolve().parents[2]
curated_spark = base_dir / "pipeline" / "curated_spark_parquet"
if not curated_spark.exists():
    curated_spark = base_dir / "09_spark_pyspark" / "resultados" / "curated_spark_parquet"
analisis_dir = base_dir / "machine_learning" if (base_dir / "machine_learning").exists() else base_dir / "10_analisis"
tablas_dir = analisis_dir
tablas_dir.mkdir(parents=True, exist_ok=True)


def main():
    start_time = time.time()
    print("=" * 80)
    print("ENTRENAMIENTO DEL MODELO PREDICTIVO DE RIESGO DE INCENDIO FORESTAL (ML)")
    print("=" * 80)

    # 1. Cargar el dataset enriquecido por Spark
    print("1. Cargando dataset procesado desde el Data Lake Parquet de Spark...")
    if not curated_spark.exists():
        print(f"[ERROR] No existe el directorio Parquet en {curated_spark}")
        sys.exit(1)

    import pyarrow.dataset as ds
    dataset = ds.dataset(str(curated_spark), format="parquet", partitioning=["anio", "mes"])
    df = dataset.to_table().to_pandas()
    print(f"   [OK] {len(df):,} observaciones celda-mes leídas.")

    # 2. Filtrado de observaciones válidas
    # Se excluyen las celdas-mes sin cobertura satelital VIIRS (apto_analisis = False): esas filas
    # no tienen evidencia observada de incendio y no deben interpretarse como ausencia confirmada.
    if "apto_analisis" in df.columns:
        df_clean = df[df["apto_analisis"] == True].copy()
    elif "cobertura_chirps_valida" in df.columns:
        df_clean = df[df["cobertura_chirps_valida"] == True].copy()
    else:
        df_clean = df.copy()
    print(f"   [OK] {len(df_clean):,} registros aptos para modelado.")

    # 3. Preparación de variables predictoras (Features)
    feature_cols = [
        "precipitacion_acumulada_mm",
        "precip_lag_1m",
        "precip_lag_2m",
        "precip_media_movil_3m",
        "dias_secos_lt1mm",
        "dias_secos_acumulados_3m",
        "mes",
        "fila",
        "columna"
    ]

    # Imputar los primeros dos meses sin lag (enero y febrero) con la media
    for col in ["precip_lag_1m", "precip_lag_2m", "precip_media_movil_3m", "dias_secos_acumulados_3m"]:
        df_clean[col] = df_clean[col].fillna(df_clean[col].median())

    X = df_clean[feature_cols]
    y = df_clean["incendio_observado"].astype(int)

    total_fuegos = y.sum()
    total_no_fuegos = len(y) - total_fuegos
    print(f"   - Casos con incendio (clase 1) : {total_fuegos:,} ({total_fuegos/len(y)*100:.2f}%)")
    print(f"   - Casos sin incendio (clase 0) : {total_no_fuegos:,} ({total_no_fuegos/len(y)*100:.2f}%)")

    # 4. División Train / Test estratificada (80% / 20%)
    print("\n2. División de datos Train (80%) y Test (20%) con balanceo estratificado...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=2026, stratify=y
    )
    print(f"   - Muestra Entrenamiento : {len(X_train):,} celdas-mes")
    print(f"   - Muestra Evaluación    : {len(X_test):,} celdas-mes")

    # 5. Entrenamiento Random Forest Classifier con ponderación de clases
    print("\n3. Entrenando Random Forest Classifier (n_estimators=100)...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        class_weight="balanced",
        random_state=2026,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)
    print("   [OK] Modelo entrenado exitosamente.")

    # 6. Predicciones y Métricas
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    roc_auc = roc_auc_score(y_test, y_prob)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    # -------------------------------------------------------------------------
    # TABLAS DE RESULTADOS DEL MODELO EN PANTALLA
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("RESULTADOS TABULARES DEL MODELO DE MACHINE LEARNING")
    print("=" * 80)

    print("\n[TABLA ML 1] MÉTRICAS GLOBALES DE DESEMPEÑO DEL MODELO")
    print(f"{'Métrica':<25} | {'Valor':<10}")
    print("-" * 38)
    print(f"{'ROC-AUC Score':<25} | {roc_auc:<10.4f}")
    print(f"{'Recall (Sensibilidad)':<25} | {rec:<10.4f}")
    print(f"{'Precision':<25} | {prec:<10.4f}")
    print(f"{'F1-Score':<25} | {f1:<10.4f}")

    print(f"\n[TABLA ML 2] MATRIZ DE CONFUSIÓN (CONJUNTO DE PRUEBA: {len(X_test):,} CELDAS-MES)")
    print(f"{'Real / Predicho':<20} | {'Pred: Sin Fuego (0)':<20} | {'Pred: Con Fuego (1)':<20}")
    print("-" * 66)
    print(f"{'Real: Sin Fuego (0)':<20} | {cm[0,0]:<20,} | {cm[0,1]:<20,}")
    print(f"{'Real: Con Fuego (1)':<20} | {cm[1,0]:<20,} | {cm[1,1]:<20,}")

    print("\n[TABLA ML 3] IMPORTANCIA DE VARIABLES PREDICTORAS (FEATURE IMPORTANCE)")
    importances = pd.DataFrame({
        "Variable": feature_cols,
        "Importancia_Pct": np.round(clf.feature_importances_ * 100, 2)
    }).sort_values("Importancia_Pct", ascending=False).reset_index(drop=True)

    print(f"{'Rango':<6} | {'Variable Predictora':<32} | {'Importancia %':<15}")
    print("-" * 60)
    for i, r in importances.iterrows():
        print(f"#{i+1:<5} | {r['Variable']:<32} | {r['Importancia_Pct']:<15.2f}%")

    # 7. Guardar modelo y artefactos
    model_path = tablas_dir / "modelo_random_forest_fireforest.joblib"
    joblib.dump(clf, model_path)
    
    metrics_path = tablas_dir / "metricas_ml.json"
    metrics_dict = {
        "algoritmo": "RandomForestClassifier",
        "n_estimators": 100,
        "max_depth": 12,
        "class_weight": "balanced",
        "roc_auc": round(float(roc_auc), 4),
        "recall": round(float(rec), 4),
        "precision": round(float(prec), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": cm.tolist(),
        "importancia_variables": importances.to_dict(orient="records"),
        "tiempo_entrenamiento_segundos": round(time.time() - start_time, 2)
    }
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_dict, f, indent=2, ensure_ascii=False)

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 80)
    print(f"[EXITO] Modelo de ML entrenado y guardado en: {model_path}")
    print(f"Métricas y tablas guardadas en: {metrics_path} ({elapsed} segundos)")
    print("=" * 80)


if __name__ == "__main__":
    main()
