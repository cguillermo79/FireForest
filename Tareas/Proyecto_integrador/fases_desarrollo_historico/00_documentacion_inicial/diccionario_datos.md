# Diccionario de datos

> **Pendiente.** Este documento aún no ha sido redactado como archivo
> independiente. Actualmente el detalle de campos existe de forma
> parcial y dispersa en:
>
> - `../03_postgresql_postgis/cargas/schema.sql` (columnas, tipos y
>   restricciones de `dim_celda`, `dim_fecha`, `fact_incendio`,
>   `fact_clima`).
> - `../04_mongodb/cargas/detecciones_viirs.json` (estructura del
>   documento de ejemplo de la colección `detecciones_viirs`).
> - `inventario_fuentes.md` (variables requeridas y metadatos por
>   fuente, a nivel conceptual).
>
> Falta consolidar aquí un diccionario formal (campo, tipo, unidad,
> rango/valores válidos, obligatoriedad, fuente) que cubra tanto las
> tablas de PostgreSQL como la colección de MongoDB y el futuro dataset
> integrado celda-mes, antes de declarar esta actividad como completada.

## Nota de trazabilidad: `celda_id` de prueba

- Valores vigentes de `celda_id` en los datos controlados del prototipo:
  `LJ_TEST_001`, `LJ_TEST_002`. El sufijo `TEST` es literal: son
  **identificadores internos de prueba** para validación técnica, **no
  códigos administrativos oficiales** ni identificadores catastrales o
  parroquiales de ninguna institución.
- No se reutilizan `LJ_04521` ni `LJ_04522`: esos identificadores
  correspondían a celdas verificadas, mediante la capa oficial del INEC,
  **fuera** del cantón Loja (dentro del cantón Catamayo, parroquia El
  Tambo). Quedan documentados como hallazgo de control de calidad, no como
  datos vigentes. Ver
  `../03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`.
- `dim_celda.geom` se almacena en **EPSG:32717** (WGS84 / UTM 17S),
  reproyectada desde `longitud`/`latitud` en EPSG:4326. La capa oficial
  usada para verificar la pertenencia cantonal (INEC, Marco Geoestadístico
  Nacional) tiene su SRID nativo en **EPSG:31992** (SIRGAS 1995 / UTM
  17S); se reproyecta a EPSG:32717 antes de comparar con `dim_celda.geom`.
  Metadatos completos en `../02_datos/metadatos/README_fuente_inec.md`.
- `LJ_TEST_001` y `LJ_TEST_002` pertenecen, según esa misma capa oficial,
  a la parroquia **El Cisne** (cantón Loja). Dos celdas de 500×500 m en
  una sola parroquia son datos de prueba para validar el flujo técnico
  (almacenamiento, reproyección, agregación, integración); no pretenden
  capturar la diversidad ambiental, altitudinal o climática del cantón ni
  constituir una muestra representativa.
