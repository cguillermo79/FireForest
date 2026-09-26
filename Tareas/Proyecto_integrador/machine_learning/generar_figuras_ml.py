"""
Regenera las figuras de evaluación del modelo (matriz de confusión e importancia de
variables) a partir de metricas_ml.json, y las publica en entrega_final/informe/figuras/.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

base_dir = Path(__file__).resolve().parents[1]
metrics_file = base_dir / "machine_learning" / "metricas_ml.json"
out_dir = base_dir / "entrega_final" / "informe" / "figuras"
out_dir.mkdir(parents=True, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10

with open(metrics_file, "r", encoding="utf-8") as f:
    mdata = json.load(f)

cm = np.array(mdata["confusion_matrix"])
test_size = int(cm.sum())

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
ax.set_title(
    f"Matriz de Confusión (Test: {test_size:,} Celdas-Mes)\n"
    f"ROC-AUC: {mdata['roc_auc']:.4f} | Recall: {mdata['recall']*100:.2f}%",
    fontsize=11, fontweight="bold"
)
plt.tight_layout()
fig.savefig(out_dir / "matriz_confusion_ml.png")
plt.close(fig)

df_imp = pd.DataFrame(mdata["importancia_variables"]).sort_values("Importancia_Pct", ascending=True)
fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
bars = ax.barh(df_imp["Variable"], df_imp["Importancia_Pct"], color="#ff7f0e", alpha=0.85)
ax.set_xlabel("Importancia Relativa en el Modelo (%)", fontweight="bold")
ax.set_title("Importancia de Variables en la Predicción de Incendios Forestales (Random Forest)", fontsize=11, fontweight="bold")
for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.3, bar.get_y() + bar.get_height() / 2, f"{w:.2f}%", va="center", fontsize=9)
ax.set_xlim(0, max(df_imp["Importancia_Pct"]) + 4)
plt.tight_layout()
fig.savefig(out_dir / "importancia_variables_ml.png")
plt.close(fig)

print(f"[OK] Figuras regeneradas en {out_dir}")
