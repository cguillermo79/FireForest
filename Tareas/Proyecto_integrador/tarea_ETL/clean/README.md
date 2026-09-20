# Capa Clean

Esta carpeta contiene las fuentes de 2023 tipadas y estandarizadas por separado.
Cada dataset se publica en CSV para revisión y en Parquet para conservar tipos.
La ejecución reemplaza de forma atómica las salidas; no acumula registros.

## Productos

- `malla_500m.csv` y `malla_500m.parquet`: atributos de 7.997 celdas, sin
  duplicar la geometría del GeoPackage Raw.
- `viirs_2023.csv` y `viirs_2023.parquet`: 95.964 observaciones celda-mes con
  `cell_id`, periodo, banderas de cobertura y banderas IQR.
- `chirps_2023.csv` y `chirps_2023.parquet`: 95.964 observaciones celda-mes con
  tipos explícitos, periodo, fracción de días húmedos y banderas IQR.
- `observaciones_viirs_sin_cobertura_2023.*`: 900 excepciones no críticas que
  se conservan como nulas y no se interpretan como ausencia de fuego.
- `rechazos_criticos_2023.*`: estructura de rechazos; contiene cero filas en
  la ejecución actual porque todos los controles críticos se cumplieron.

La capa Clean todavía no integra VIIRS con CHIRPS. Esa unión corresponde a
Curated y deberá mantener cardinalidad uno a uno por
`cell_index + anio + mes`.
