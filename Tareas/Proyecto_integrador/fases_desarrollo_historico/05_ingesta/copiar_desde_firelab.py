"""Copia de SOLO LECTURA de los productos estrictamente necesarios desde
FIRELAB_Loja hacia Tareas/Proyecto_integrador/02_datos/raw/.

Reglas que cumple este script (ver CLAUDE.md y AGENTS.md):
  - FIRELAB_Loja no se modifica: sus archivos solo se abren en modo 'rb'.
    Antes y despues de copiar se compara tamano, fecha de modificacion y
    hash SHA-256 de cada origen; si algo cambia, el script falla.
  - El destino nunca puede estar dentro de FIRELAB_Loja.
  - La copia es exacta (bytes identicos). No se filtra ni transforma nada:
    la seleccion de periodo y la limpieza pertenecen al ETL, no a 02_datos/raw.
  - Un destino ya existente con hash distinto NO se sobrescribe: el script falla.
  - El manifiesto con la procedencia y los hashes se escribe en
    05_ingesta/metadatos/manifiesto_firelab_loja.json (versionado en git).
    Los datos copiados quedan fuera de git (02_datos/raw/** esta ignorado).

Uso, desde cualquier directorio:
    .venv/Scripts/python.exe Tareas/Proyecto_integrador/05_ingesta/copiar_desde_firelab.py

Para agregar otro producto en el futuro, anadirlo a PRODUCTOS solo si es
estrictamente necesario para el proyecto integrador.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ_INTEGRADOR = Path(__file__).resolve().parents[1]
RAIZ_FIREFORREST = RAIZ_INTEGRADOR.parents[1]
ORIGEN_RAIZ = (RAIZ_FIREFORREST.parent / "FIRELAB_Loja").resolve()
DESTINO_RAIZ = RAIZ_INTEGRADOR / "02_datos" / "raw"
MANIFIESTO = RAIZ_INTEGRADOR / "05_ingesta" / "metadatos" / "manifiesto_firelab_loja.json"

# (fuente, ruta relativa dentro de FIRELAB_Loja, ruta relativa dentro de 02_datos/raw, uso)
PRODUCTOS = [
    (
        "malla",
        "08_malla_500m/productos/malla_500m_loja_maestra.gpkg",
        "malla/malla_500m_loja_maestra.gpkg",
        "Malla espacial de 500 m del canton Loja (EPSG:32717) para dim_celda.",
    ),
    (
        "viirs",
        "09_integracion_variables/productos/viirs_500m/"
        "viirs_evidencia_500m_celda_mes_2019_2025_v1_0_3.csv",
        "viirs/viirs_evidencia_500m_celda_mes_2019_2025_v1_0_3.csv",
        "Evidencia VIIRS por celda-mes 2019-2025, version v1.0.3 (la citada por el Taller NoSQL).",
    ),
    (
        "chirps",
        "09_integracion_variables/productos/chirps_500m/chirps_500m_celda_mes_2019_2025.csv",
        "chirps/chirps_500m_celda_mes_2019_2025.csv",
        "Precipitacion CHIRPS por celda-mes 2019-2025.",
    ),
]

BLOQUE = 8 * 1024 * 1024


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        while bloque := f.read(BLOQUE):
            h.update(bloque)
    return h.hexdigest()


def instantanea(ruta: Path) -> tuple:
    st = ruta.stat()
    return (st.st_size, st.st_mtime_ns)


def copiar_exacto(origen: Path, destino: Path) -> None:
    """Copia por bloques a un .part y lo renombra al terminar."""
    temporal = destino.with_suffix(destino.suffix + ".part")
    with origen.open("rb") as fin, temporal.open("wb") as fout:
        while bloque := fin.read(BLOQUE):
            fout.write(bloque)
    os.replace(temporal, destino)


def main() -> int:
    if not ORIGEN_RAIZ.is_dir():
        print(f"ERROR: no existe {ORIGEN_RAIZ}")
        return 1

    plan = []
    for fuente, rel_origen, rel_destino, uso in PRODUCTOS:
        origen = (ORIGEN_RAIZ / rel_origen).resolve()
        destino = (DESTINO_RAIZ / rel_destino).resolve()
        if ORIGEN_RAIZ not in origen.parents:
            print(f"ERROR: el origen sale de FIRELAB_Loja: {origen}")
            return 1
        if ORIGEN_RAIZ in destino.parents or destino == ORIGEN_RAIZ:
            print(f"ERROR: el destino esta dentro de FIRELAB_Loja: {destino}")
            return 1
        if not origen.is_file():
            print(f"ERROR: no existe el origen {origen}")
            return 1
        plan.append((fuente, rel_origen, rel_destino, uso, origen, destino))

    antes = {p[4]: instantanea(p[4]) for p in plan}
    hash_origen_antes = {p[4]: sha256(p[4]) for p in plan}

    entradas = []
    for fuente, rel_origen, rel_destino, uso, origen, destino in plan:
        destino.parent.mkdir(parents=True, exist_ok=True)
        if destino.exists():
            if sha256(destino) != hash_origen_antes[origen]:
                print(f"ERROR: {destino} existe con contenido distinto; no se sobrescribe.")
                return 1
            estado = "ya presente (hash identico)"
        else:
            copiar_exacto(origen, destino)
            estado = "copiado"
        hash_destino = sha256(destino)
        if hash_destino != hash_origen_antes[origen]:
            print(f"ERROR: el hash del destino no coincide con el origen: {destino}")
            return 1
        print(f"[{fuente}] {estado}: {rel_destino} ({destino.stat().st_size} bytes)")
        entradas.append(
            {
                "fuente": fuente,
                "uso": uso,
                "origen_relativo_a_FIRELAB_Loja": rel_origen,
                "destino_relativo_a_02_datos_raw": rel_destino,
                "tamano_bytes": destino.stat().st_size,
                "sha256": hash_destino,
                "modificado_origen_utc": datetime.fromtimestamp(
                    antes[origen][1] / 1e9, tz=timezone.utc
                ).isoformat(),
            }
        )

    # Comprobacion final: FIRELAB_Loja no cambio.
    for _, _, _, _, origen, _ in plan:
        if instantanea(origen) != antes[origen] or sha256(origen) != hash_origen_antes[origen]:
            print(f"ALERTA: el origen cambio durante la copia: {origen}")
            return 1
    print("Origen verificado: tamano, fecha de modificacion y SHA-256 sin cambios.")

    MANIFIESTO.parent.mkdir(parents=True, exist_ok=True)
    MANIFIESTO.write_text(
        json.dumps(
            {
                "descripcion": "Procedencia de las copias de solo lectura tomadas de FIRELAB_Loja.",
                "verificado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "archivos": entradas,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Manifiesto: {MANIFIESTO.relative_to(RAIZ_INTEGRADOR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
