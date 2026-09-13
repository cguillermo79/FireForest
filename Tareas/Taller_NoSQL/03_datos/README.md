# Datos — Taller NoSQL MongoDB (Grupo 04)

## Origen

- **Naturaleza de los datos:** registros reales de VIIRS procesados
  previamente, extraídos de una fuente externa de solo lectura (no se
  modificó, movió ni sobrescribió ningún archivo de esa fuente; este
  taller trabaja exclusivamente con la copia independiente de esta
  carpeta).
- **Versión del producto de origen:** `v1.0.3`.
- **Periodo cubierto por el producto de origen:** 2019–2025.
- **Fuente primaria satelital:** NASA FIRMS — VIIRS (resolución nativa
  ~375–927 m, agregada a celdas de 500 m).

## Archivos de esta carpeta

| Archivo | Descripción |
|---|---|
| `muestra_viirs_celda_mes_2019_2025.csv` | Muestra estratificada, generada por `02_mongodb/01_extraer_muestra_viirs.py`. |
| `evidencia_viirs_celda_mes.json` | Documentos MongoDB generados por `02_mongodb/02_transformar_viirs_a_json.py` a partir del CSV anterior. |

**No se copió el CSV completo de origen (108,35 MB).** Solo se conserva la
muestra independiente descrita abajo.

## Método de muestreo

- **Método:** muestreo aleatorio estratificado por año y por evidencia de
  fuego (`viirs_evidencia_fuego_any`), implementado con
  `pandas.DataFrame.sample`.
- **Semilla:** `2026` (semilla base; cada año usa `2026 + año` para el
  estrato con fuego y `2026 + año + 100` para el estrato sin fuego, de
  modo que el muestreo es determinístico y reproducible).
- **Tamaño por año:** 10 registros con evidencia de fuego + 5 registros
  sin evidencia de fuego = 15 registros por año.
- **Años incluidos:** 2019, 2020, 2021, 2022, 2023, 2024, 2025 (7 años ×
  15 registros = 105 registros).

## Composición de la muestra (verificada por ejecución real)

- **Registros totales:** 105.
- **Registros con evidencia de fuego (criterio `todas`):** 70.
- **Registros sin evidencia de fuego:** 35.
- **Registros con evidencia nominal/alta:** 68.
- **FRP máxima de la muestra:** 122,3162 MW aprox. (122.31617512422449 MW
  exacto, documento `VCM_0073`, celda 1146, periodo 2023-10).
- **Datos simulados:** `false` para los 105 registros — son registros
  reales de VIIRS procesados previamente, no datos inventados ni
  simulados.

## Advertencia sobre representatividad

La muestra es **estratificada, no aleatoria simple**: se fijó
deliberadamente una proporción de 10 casos con fuego por 5 sin fuego en
cada año, para asegurar variedad suficiente de valores y poder ejecutar
consultas no triviales (tal como exige la guía del laboratorio). Por lo
tanto:

- **La proporción 70/35 (66,7 % con fuego) NO estima la prevalencia real
  de incendios en el cantón Loja.** Es un artefacto del diseño muestral.
- Cualquier estadística descriptiva calculada sobre esta muestra
  (promedios, máximos, totales por mes o año) debe interpretarse
  exclusivamente dentro de la muestra, y no debe generalizarse a la
  población completa de celdas-mes del cantón.
- El propósito de la muestra es exclusivamente pedagógico: demostrar el
  diseño documental, la carga, las consultas y las agregaciones de
  MongoDB con datos reales y variados.

## Reproducción

Desde la raíz de `FireForest`, con el entorno virtual `.venv` activado:

```bash
.venv\Scripts\python.exe Tareas\Taller_NoSQL\02_mongodb\01_extraer_muestra_viirs.py
.venv\Scripts\python.exe Tareas\Taller_NoSQL\02_mongodb\02_transformar_viirs_a_json.py
.venv\Scripts\python.exe Tareas\Taller_NoSQL\02_mongodb\03_validar_json.py
```

Estos tres pasos son deterministas: dado el mismo archivo fuente
(registros de VIIRS procesados previamente), siempre producen los
mismos 105 registros/documentos.
