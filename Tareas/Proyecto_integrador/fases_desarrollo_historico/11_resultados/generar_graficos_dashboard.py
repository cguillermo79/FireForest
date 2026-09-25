"""
Generador de Gráficos y Evidencias Visuales del Dashboard
Proyecto Integrador FireForest - Grupo 04

Genera figuras PNG de alta resolución de:
1. Mapa cantonal de las 7.997 celdas espaciales con focos de calor.
2. Gráfico bivariado de Precipitación vs FRP mensual.
3. Matriz de Confusión del modelo de ML.
4. Gráfico de Importancia de Variables de Sequía.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pyproj import Transformer

# Configuración estética
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10

base_dir = Path(__file__).resolve().parents[1]
curated_file = base_dir / "tarea_ETL" / "curated" / "fireforest_celda_mes_2023.parquet"
malla_file = base_dir / "tarea_ETL" / "clean" / "malla_500m.parquet"
metrics_file = base_dir / "10_analisis" / "tablas" / "metricas_ml.json"
out_dir = base_dir / "11_resultados"

df_curated = pd.read_parquet(curated_file)
df_malla = pd.read_parquet(malla_file)

# Transformar coordenadas a WGS84
transformer = Transformer.from_crs("EPSG:32717", "EPSG:4326", always_xy=True)
lons, lats = transformer.transform(df_malla["centro_x_m"].values, df_malla["centro_y_m"].values)
df_malla["longitud"] = lons
df_malla["latitud"] = lats

df = df_curated.merge(df_malla[["cell_id", "longitud", "latitud"]], on="cell_id", how="left")

# -----------------------------------------------------------------------------
# FIGURA 1: MAPA CANTONAL DE LAS 7.997 CELDAS (CON FOCOS DE INCENDIO EN SEPTIEMBRE)
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 8), dpi=200)
df_sep = df[df["mes"] == 9]
sc = ax.scatter(
    df_sep["longitud"], df_sep["latitud"],
    c=df_sep["precipitacion_acumulada_mm"],
    cmap="YlGnBu", s=6, alpha=0.7, label="Celdas de 500m (7.997 celdas)"
)
cbar = plt.colorbar(sc, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label("Precipitación Acumulada Mensual (mm)")

# Resaltar celdas con incendio
df_fuego_sep = df_sep[df_sep["evidencia_fuego"] == True]
ax.scatter(
    df_fuego_sep["longitud"], df_fuego_sep["latitud"],
    c="red", edgecolors="black", s=35, linewidths=0.5,
    label=f"Focos de Incendio (VIIRS: {len(df_fuego_sep)} celdas)"
)

# Dibujar perímetro oficial del Cantón Loja si existe
boundary_file = base_dir / "02_datos" / "raw" / "malla" / "limite_canton_loja_wgs84.geojson"
if boundary_file.exists():
    with open(boundary_file, "r", encoding="utf-8") as f:
        boundary_gj = json.load(f)
    from shapely.geometry import shape
    poly = shape(boundary_gj["features"][0]["geometry"])
    if poly.geom_type == "Polygon":
        x, y = poly.exterior.xy
        ax.plot(x, y, color="#003366", linewidth=2.0, linestyle="--", label="Límite Cantonal Oficial (INEC)")
    elif poly.geom_type == "MultiPolygon":
        for p in poly.geoms:
            x, y = p.exterior.xy
            ax.plot(x, y, color="#003366", linewidth=2.0, linestyle="--")

ax.set_title("Malla Espacial Cantonal de Loja (7.997 Celdas de 500m × 500m)\nDistribución de Precipitaciones e Incendios - Septiembre 2023", fontsize=12, fontweight="bold")
ax.set_xlabel("Longitud (WGS84)")
ax.set_ylabel("Latitud (WGS84)")
ax.legend(loc="upper right", frameon=True)
plt.tight_layout()
fig.savefig(out_dir / "mapa_7997_celdas_loja.png")
plt.close(fig)

# -----------------------------------------------------------------------------
# FIGURA 2: EVOLUCIÓN MENSUAL CLIMA VS INCENDIOS
# -----------------------------------------------------------------------------
df_mensual = df.groupby("mes").agg({
    "precipitacion_acumulada_mm": "mean",
    "frp_suma_observada_media_mw": "sum",
    "evidencia_fuego": "sum"
}).reset_index()

fig, ax1 = plt.subplots(figsize=(10, 5), dpi=200)

color_lluvia = "#1f77b4"
color_frp = "#d62728"

ax1.bar(df_mensual["mes"], df_mensual["precipitacion_acumulada_mm"], color=color_lluvia, alpha=0.7, width=0.55, label="Precipitación Media (mm)")
ax1.set_xlabel("Mes del Año 2023", fontweight="bold")
ax1.set_ylabel("Precipitación Promedio Cantonal (mm)", color=color_lluvia, fontweight="bold")
ax1.tick_params(axis='y', labelcolor=color_lluvia)
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"])

ax2 = ax1.twinx()
ax2.plot(df_mensual["mes"], df_mensual["frp_suma_observada_media_mw"], color=color_frp, marker='o', linewidth=2.5, markersize=7, label="FRP Acumulado (MW)")
ax2.set_ylabel("Potencia Radiativa de Fuego - FRP (MW)", color=color_frp, fontweight="bold")
ax2.tick_params(axis='y', labelcolor=color_frp)
ax2.grid(False)

plt.title("Dinámica Temporal Cantón Loja: Déficit de Lluvias vs Incendios Forestales (2023)", fontsize=12, fontweight="bold")
plt.tight_layout()
fig.savefig(out_dir / "serie_temporal_clima_vs_incendios.png")
plt.close(fig)

# -----------------------------------------------------------------------------
# FIGURA 3: MATRIZ DE CONFUSIÓN DEL MODELO DE MACHINE LEARNING
# -----------------------------------------------------------------------------
if metrics_file.exists():
    with open(metrics_file, "r") as f:
        mdata = json.load(f)
    cm = np.array(mdata["confusion_matrix"])

    fig, ax = plt.subplots(figsize=(6, 5), dpi=200)
    im = ax.imshow(cm, cmap="Blues")

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Pred: Sin Fuego", "Pred: Con Fuego"], fontweight="bold")
    ax.set_yticklabels(["Real: Sin Fuego", "Real: Con Fuego"], fontweight="bold")

    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center", color=color, fontsize=12, fontweight="bold")

    ax.set_title(f"Matriz de Confusión (Test: 19.193 Celdas-Mes)\nROC-AUC: {mdata['roc_auc']:.4f} | Recall: {mdata['recall']*100:.1f}%", fontsize=11, fontweight="bold")
    plt.tight_layout()
    fig.savefig(out_dir / "matriz_confusion_ml.png")
    plt.close(fig)

    # -----------------------------------------------------------------------------
    # FIGURA 4: IMPORTANCIA DE VARIABLES PREDICTORAS (FEATURE IMPORTANCE)
    # -----------------------------------------------------------------------------
    df_imp = pd.DataFrame(mdata["importancia_variables"]).sort_values("Importancia_Pct", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    bars = ax.barh(df_imp["Variable"], df_imp["Importancia_Pct"], color="#ff7f0e", alpha=0.85)
    ax.set_xlabel("Importancia Relativa en el Modelo (%)", fontweight="bold")
    ax.set_title("Importancia de Variables en la Predicción de Incendios Forestales (Random Forest)", fontsize=11, fontweight="bold")
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.3, bar.get_y() + bar.get_height()/2, f"{w:.2f}%", va="center", fontsize=9)
    ax.set_xlim(0, max(df_imp["Importancia_Pct"]) + 4)
    plt.tight_layout()
    fig.savefig(out_dir / "importancia_variables_ml.png")
    plt.close(fig)

print("[OK] Gráficos del Dashboard exportados exitosamente a 11_resultados/")
