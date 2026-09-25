# Tarea ETL — FireForest

## Entrega oficial

El archivo que deben revisar los compañeros y recibir el profesor es:

`FireForest_Tarea_ETL_entrega_completa_2026-09-20.zip`

Al descomprimirlo aparece una sola carpeta llamada `tarea_ETL/`. El ZIP ya
contiene los datos de entrada, los resultados y las evidencias necesarias; no
es necesario buscar, copiar ni descargar bases desde otra carpeta del
repositorio.

## Contenido del ZIP

- `raw/`: datos originales de entrada necesarios para el periodo 2023.
- `clean/`: bases limpias ya generadas y listas para revisar.
- `curated/`: dataset analítico final y su diccionario de datos.
- `evidencias/`: controles de calidad y prueba de reproducibilidad.
- `codigo/`: scripts utilizados para construir los resultados.
- `configuracion/`: parámetros y dependencias del proceso.
- `README.md`: explicación del contenido y reproducción opcional.

`raw/` y `clean/` cumplen funciones diferentes: `raw/` contiene las entradas
sin transformar y `clean/` contiene las bases resultantes después de aplicar
las reglas de limpieza. Ambas capas ya vienen incluidas en el ZIP.

## Revisión y reproducción

Para revisar la entrega no es necesario ejecutar ningún comando: se pueden
abrir directamente los CSV de `clean/`, `curated/` y `evidencias/`.

La ejecución del ETL es opcional y sirve únicamente para demostrar que los
resultados pueden regenerarse. Las instrucciones están dentro del `README.md`
incluido en el propio ZIP.

## Resultado entregado

- 7.997 celdas espaciales.
- 95.964 filas VIIRS Clean.
- 95.964 filas CHIRPS Clean.
- 95.964 filas en Curated.
- 95.064 filas aptas para análisis.
- 900 filas sin observación VIIRS conservadas como nulas.
- Cero duplicados en `cell_id + anio + mes`.
