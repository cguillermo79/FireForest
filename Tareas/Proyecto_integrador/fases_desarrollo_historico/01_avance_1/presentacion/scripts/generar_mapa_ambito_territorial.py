"""Genera la figura "Ambito territorial y localizacion de las celdas del
prototipo" para la presentacion del Avance 1 de FireForest.

Se apoya en `verificacion_territorial_y_malla.py` (misma carpeta) para
reconstruir el limite del canton Loja, sus 14 parroquias, y las dos celdas
de prueba seleccionadas de forma deterministica (`LJ_TEST_001`,
`LJ_TEST_002`).

El mapa se genera reproduciblemente a partir de la capa oficial del INEC y
de las geometrias de celda calculadas con el mismo pipeline que usa
`dim_celda` (EPSG:4326 -> EPSG:32717, ST_MakeEnvelope de 500x500 m). No se
usa ninguna captura de mapa de terceros ni imagen decorativa.

Salida: `01_avance_1/presentacion/figuras/mapa_ambito_territorial_celdas.png`
y `.pdf` (vectorial, apto para incluir en LaTeX).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.lines import Line2D

from verificacion_territorial_y_malla import (
    FIGURAS_DIR,
    construir_limites,
    construir_malla_y_seleccionar,
    xy_a_lonlat,
    CELL_SIZE_M,
)

FUENTE_TEXTO = (
    "Fuente: INEC, Marco Geoestadistico Nacional, paquete provincial "
    "11_LOJA.zip (descargado 2026-09-14 de ecuadorencifras.gob.ec).\n"
    "Limite cantonal y parroquial reconstruidos por disolucion de zonas "
    "censales (capa zon_a) agrupadas por codigo DPA. CRS de trabajo: "
    "EPSG:32717 (WGS84 / UTM 17S)."
)

NOTA_TEXTO = (
    "El dominio del proyecto es el canton Loja. Para validar el prototipo "
    "se utilizan dos celdas controladas de 500 x 500 m, verificadas "
    "espacialmente dentro de su limite oficial. Estas celdas no "
    "constituyen una muestra representativa del territorio cantonal."
)


def _poly_patch(geom, **kwargs):
    """Devuelve una lista de MplPolygon para un (Multi)Polygon de shapely,
    dibujando primero el exterior y agregando los huecos si los hay."""
    patches = []
    geoms = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    for g in geoms:
        xs, ys = g.exterior.xy
        patches.append(MplPolygon(list(zip(xs, ys)), **kwargs))
    return patches


def _add_scale_bar(ax, length_km, x0_frac=0.05, y0_frac=0.06):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x0 = xlim[0] + x0_frac * (xlim[1] - xlim[0])
    y0 = ylim[0] + y0_frac * (ylim[1] - ylim[0])
    length_m = length_km * 1000
    ax.plot([x0, x0 + length_m], [y0, y0], color="black", linewidth=2.5,
             solid_capstyle="butt")
    for xoff in (x0, x0 + length_m):
        ax.plot([xoff, xoff], [y0 - (ylim[1] - ylim[0]) * 0.006,
                                y0 + (ylim[1] - ylim[0]) * 0.006],
                 color="black", linewidth=1.2)
    ax.text(x0 + length_m / 2, y0 + (ylim[1] - ylim[0]) * 0.015,
            f"{length_km:g} km", ha="center", va="bottom", fontsize=8)


def _add_north_arrow(ax, x_frac=0.93, y_frac=0.90):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x = xlim[0] + x_frac * (xlim[1] - xlim[0])
    y = ylim[0] + y_frac * (ylim[1] - ylim[0])
    arrow_len = (ylim[1] - ylim[0]) * 0.06
    ax.annotate("N", xy=(x, y + arrow_len), xytext=(x, y),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.6),
                ha="center", va="bottom", fontsize=11, fontweight="bold")


def main():
    canton_loja, canton_catamayo, parroquias = construir_limites()
    _, seleccionadas = construir_malla_y_seleccionar(canton_loja, n_seleccionar=2)

    celdas = []
    for idx, (x, y, dist) in enumerate(seleccionadas, start=1):
        cid = f"LJ_TEST_{idx:03d}"
        celdas.append({
            "id": cid,
            "sw": (x, y),
            "centro": (x + CELL_SIZE_M / 2, y + CELL_SIZE_M / 2),
        })

    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_axes([0.06, 0.14, 0.60, 0.80])  # panel general
    ax_inset = fig.add_axes([0.68, 0.46, 0.30, 0.46])  # recuadro ampliado

    # --- panel general -----------------------------------------------
    for patch in _poly_patch(canton_loja, facecolor="#d5eae1", edgecolor="#1b5e37",
                              linewidth=1.8, zorder=2, label="Limite canton Loja"):
        ax.add_patch(patch)

    for codigo, geom in parroquias.items():
        for patch in _poly_patch(geom, facecolor="none", edgecolor="#2e7d50",
                                  linewidth=0.6, zorder=3):
            ax.add_patch(patch)

    for patch in _poly_patch(canton_catamayo, facecolor="#f5f5f5", edgecolor="#7c5937",
                              linewidth=1.0, linestyle="--", zorder=1):
        ax.add_patch(patch)

    minx, miny, maxx, maxy = canton_loja.bounds
    pad = 3000
    ax.set_xlim(minx - pad, maxx + pad)
    ax.set_ylim(miny - pad, maxy + pad)
    ax.set_aspect("equal")
    ax.set_xlabel("Este (m) - EPSG:32717")
    ax.set_ylabel("Norte (m) - EPSG:32717")
    ax.set_title("Ambito territorial y localizacion de las celdas del prototipo",
                 fontsize=13, fontweight="bold", color="#1b5e37")

    cell_colors = ["#c4561a", "#1b5e37"]
    for c, col in zip(celdas, cell_colors):
        cx, cy = c["centro"]
        ax.plot(cx, cy, marker="s", markersize=6, color=col,
                 markeredgecolor="black", markeredgewidth=0.6, zorder=5)
    # una sola etiqueta agrupada (las dos celdas quedan a <1 km, indistinguibles
    # a esta escala); el detalle individual se muestra en el recuadro ampliado
    label_x = sum(c["centro"][0] for c in celdas) / len(celdas)
    label_y = max(c["centro"][1] for c in celdas)
    ax.annotate("LJ_TEST_001 / LJ_TEST_002\n(ver recuadro ampliado)",
                (label_x, label_y), textcoords="offset points", xytext=(10, 14),
                fontsize=7.5, color="#c4561a", fontweight="bold",
                ha="left", va="bottom")

    # recuadro de zoom (rectangulo indicador) sobre el panel general
    zx0 = min(c["sw"][0] for c in celdas) - 400
    zy0 = min(c["sw"][1] for c in celdas) - 400
    zx1 = max(c["sw"][0] for c in celdas) + CELL_SIZE_M + 400
    zy1 = max(c["sw"][1] for c in celdas) + CELL_SIZE_M + 400
    ax.add_patch(MplPolygon([(zx0, zy0), (zx1, zy0), (zx1, zy1), (zx0, zy1)],
                             fill=False, edgecolor="#c4561a", linewidth=1.2, zorder=6))

    _add_scale_bar(ax, length_km=10)
    _add_north_arrow(ax)

    legend_elems = [
        MplPolygon([(0, 0)], facecolor="#d5eae1", edgecolor="#1b5e37", label="Canton Loja"),
        Line2D([0], [0], color="#2e7d50", linewidth=0.8, label="Limites parroquiales (Loja)"),
        MplPolygon([(0, 0)], facecolor="#f5f5f5", edgecolor="#7c5937", linestyle="--",
                    label="Canton vecino (Catamayo, contexto)"),
        Line2D([0], [0], marker="s", color="#c4561a", linestyle="None", markersize=7,
               label="Celda de prueba (LJ_TEST_00x)"),
        MplPolygon([(0, 0)], fill=False, edgecolor="#c4561a", label="Recuadro ampliado"),
    ]
    leg = ax.legend(handles=legend_elems, loc="lower left", fontsize=7.5,
                     framealpha=1.0, facecolor="white", edgecolor="#999999")
    leg.set_zorder(10)

    ax.text(0.01, -0.10, FUENTE_TEXTO, transform=ax.transAxes, fontsize=6.8,
            va="top", ha="left", color="#333333")

    # --- recuadro ampliado ---------------------------------------------
    for patch in _poly_patch(canton_loja, facecolor="#d5eae1", edgecolor="#1b5e37",
                              linewidth=1.0, zorder=1):
        ax_inset.add_patch(patch)
    for codigo, geom in parroquias.items():
        for patch in _poly_patch(geom, facecolor="none", edgecolor="#2e7d50",
                                  linewidth=0.5, zorder=2):
            ax_inset.add_patch(patch)

    colors = ["#c4561a", "#1b5e37"]
    for c, col in zip(celdas, colors):
        sx, sy = c["sw"]
        ax_inset.add_patch(MplPolygon(
            [(sx, sy), (sx + CELL_SIZE_M, sy), (sx + CELL_SIZE_M, sy + CELL_SIZE_M),
             (sx, sy + CELL_SIZE_M)],
            facecolor=col, edgecolor="black", linewidth=1.0, alpha=0.75, zorder=5))
        ax_inset.annotate(c["id"], (sx + CELL_SIZE_M / 2, sy + CELL_SIZE_M),
                           textcoords="offset points", xytext=(0, 4),
                           ha="center", fontsize=7.5, fontweight="bold")

    ax_inset.set_xlim(zx0, zx1)
    ax_inset.set_ylim(zy0, zy1)
    ax_inset.set_aspect("equal")
    ax_inset.set_title("Recuadro ampliado: poligonos de 500 x 500 m", fontsize=9)
    ax_inset.tick_params(labelsize=6.5)
    _add_scale_bar(ax_inset, length_km=0.5, x0_frac=0.06, y0_frac=0.06)

    fig.text(0.68, 0.40, "EPSG:32717 (WGS84 / UTM 17S)\nArea por celda: 250 000 m2 (0,25 km2)",
              fontsize=8, va="top")
    fig.text(0.68, 0.30,
             "\n".join(_wrap(NOTA_TEXTO, 46)),
             fontsize=8.3, va="top", color="#7c2d12", fontweight="bold",
             bbox=dict(boxstyle="round", facecolor="#faf3ea", edgecolor="#c4561a"))

    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    out_png = FIGURAS_DIR / "mapa_ambito_territorial_celdas.png"
    out_pdf = FIGURAS_DIR / "mapa_ambito_territorial_celdas.pdf"
    fig.savefig(out_png, dpi=220)
    fig.savefig(out_pdf)
    print("Mapa guardado en:")
    print(" -", out_png)
    print(" -", out_pdf)


def _wrap(text, width):
    import textwrap
    return textwrap.wrap(text, width)


if __name__ == "__main__":
    main()
