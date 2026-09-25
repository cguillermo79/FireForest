# Capa Curated

Esta carpeta contiene el producto final integrado por
`cell_id + anio + mes`.

## Archivos que se entregan

- `fireforest_celda_mes_2023.csv`: dataset maestro en formato abierto.
- `fireforest_celda_mes_2023.parquet`: el mismo dataset con tipos preservados.
- `diccionario_datos.csv`: definición de las 45 variables, unidades, tipos,
  origen, derivación y nulabilidad.

El dataset tiene 95.964 filas. Las 900 filas sin observación VIIRS se conservan
con `apto_analisis=false`; el subconjunto para análisis conjunto se obtiene
filtrando `apto_analisis=true` y contiene 95.064 filas. No se publica una copia
adicional filtrada para evitar duplicar productos.
