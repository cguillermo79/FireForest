# Fuente oficial de la malla / límites territoriales — INEC

Proyecto: FireForest (independiente). Este documento es la copia
**versionable** de la procedencia de la capa oficial usada para reconstruir
el límite del cantón Loja y verificar espacialmente las celdas controladas
del prototipo. Los datos crudos en sí (`11_LOJA.zip`, el GeoPackage, y los
extractos GeoJSON voluminosos) **no se versionan** — quedan solo en disco
local, bajo `02_datos/raw/malla/`, excluidos por `.gitignore`
(`02_datos/raw/**`, política ya existente del proyecto). Este documento
permite regenerarlos exactamente cuando se necesiten, sin depender de que
esos binarios estén en el repositorio.

## 1. Identificación del dataset

| Campo | Valor |
|---|---|
| Institución | INEC — Instituto Nacional de Estadística y Censos (Ecuador) |
| Dataset | Marco Geoestadístico Nacional, paquete provincial |
| URL exacta de descarga | `https://www.ecuadorencifras.gob.ec/documentos/web-inec/Geografia_Estadistica/Documentos/11_LOJA.zip` |
| Página de referencia | `https://www.ecuadorencifras.gob.ec/documentos/web-inec/Geografia_Estadistica/Micrositio_geoportal/descargas.html` |
| Fecha de descarga | 2026-09-14 |
| Tamaño del ZIP | 106 536 429 bytes (`Content-Length` verificado con `curl -I`) |
| Tamaño del GeoPackage descomprimido | 215 277 568 bytes |
| Última modificación (servidor, cabecera `Last-Modified`) | 2026-07-08 |
| Licencia / condiciones de uso | El sitio del INEC no publica una licencia explícita junto al archivo de descarga; es un dato estadístico oficial de acceso público de una institución del Estado ecuatoriano. No se declara aquí una licencia que el INEC no haya publicado explícitamente. |

### Hashes SHA-256 (verificación de integridad de la descarga)

| Archivo | SHA-256 |
|---|---|
| `11_LOJA.zip` | `54be6b6f56327fb9e3de934d62a89e905afea1983cfca10d995e05f169f593f4` |
| `11_loja.gpkg` (dentro del ZIP) | `2f9cb1f1cd233ea7aaf2103de818e265b3523d070f7851819bb687907c907619` |
| `inec_zonas_censales_canton_1101_loja.geojson` (extracto) | `89805f542d7ffb9cd029dad948aa0b54c9a7660eabfc746c10b0aeb26f1f5c79` |
| `inec_zonas_censales_canton_1103_catamayo.geojson` (extracto) | `e2db774920ca560f26590776235d6c741d9a8d2e005c819694af4dcc67fb84e3` |

Si al regenerar estos archivos con los comandos de la sección 6 los hashes
no coinciden, el INEC actualizó el paquete provincial desde la fecha de
descarga indicada arriba; en ese caso hay que volver a ejecutar la
verificación territorial completa antes de confiar en los resultados
existentes.

## 2. Archivo y capa utilizados

- **Archivo**: `11_loja.gpkg` (GeoPackage), dentro de `11_LOJA.zip`.
- **Capa**: `zon_a` (zonas censales). El GeoPackage contiene 9 capas
  (`loc_p`, `edif_p`, `ingresos_l`, `ejes_l`, `zon_a`, `sec_a`, `man_a`,
  `ca04_a`, `aream_a`); se revisaron las 9 y **ninguna es una capa
  administrativa cantonal o parroquial directa** (un polígono único por
  cantón/parroquia ya disuelto). Por eso el límite se reconstruyó a partir
  de `zon_a` (ver §4).
- **Extractos versionables por cantón** (no el paquete completo):
  - `inec_zonas_censales_canton_1101_loja.geojson` — 93 entidades (cantón
    Loja, código DPA `1101`, 14 parroquias).
  - `inec_zonas_censales_canton_1103_catamayo.geojson` — 18 entidades
    (cantón Catamayo, código DPA `1103`; conservado como evidencia del
    hallazgo de control de calidad territorial, ver
    `03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`).

## 3. Sistema de referencia (CRS)

| | |
|---|---|
| CRS nativo de la capa `zon_a` | **EPSG:31992** — SIRGAS 1995 / UTM zone 17S |
| CRS de procesamiento del proyecto | **EPSG:32717** — WGS84 / UTM zone 17S (mismo CRS que `dim_celda.geom`) |
| Reproyección aplicada | `EPSG:31992 → EPSG:32717` mediante PyProj (`Transformer.from_crs(..., always_xy=True)`), equivalente a `ST_Transform` de PostGIS |
| Efecto práctico de la reproyección | Verificado numéricamente: diferencia de **0,0000 m** entre calcular una distancia en EPSG:31992 nativo o en EPSG:32717 reproyectado, para las mismas geometrías (SIRGAS 1995 y WGS84 son prácticamente coincidentes en el Ecuador continental) — ver detalle en `03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`, sección de trazabilidad de distancias |

## 4. Campos DPA y procedimiento de selección/disolución

Campo `zon` de la capa `zon_a`: código DPA de 9 dígitos
`PP CC PP ZZZ` (provincia 2 dígitos + cantón 2 dígitos + parroquia 2
dígitos + zona 3 dígitos).

Procedimiento **efectivamente aplicado** (reproducible con el script de la
sección 6):

1. **Selección**: filtrar las entidades de `zon_a` cuyo campo `zon`
   empieza con el prefijo de 4 dígitos del cantón deseado
   (`1101` = Loja, `1103` = Catamayo), con `ogr2ogr ... -where "zon LIKE '1101%'"`.
2. **Disolución del límite cantonal**: unión geométrica (`unary_union` de
   Shapely, equivalente a `ST_Union`/`ST_Dissolve` de PostGIS) de todas las
   zonas seleccionadas de un mismo cantón, sin agrupar por parroquia.
3. **Disolución de límites parroquiales**: la misma unión geométrica, pero
   agrupando las zonas por los primeros 6 dígitos de `zon` (código de
   parroquia) antes de unir.
4. **Control de calidad de la disolución**: el área resultante del cantón
   Loja disuelto es **1891,19 km²**, consistente con el área comúnmente
   publicada para ese cantón — se usó como verificación de que la
   disolución no dejó vacíos significativos ni se hizo sobre datos
   incorrectos.

### Número de entidades

| Capa | Entidades |
|---|---|
| `zon_a`, cantón Loja (`1101`) | 93 zonas censales → 14 parroquias tras disolver por código de 6 dígitos |
| `zon_a`, cantón Catamayo (`1103`) | 18 zonas censales |

## 5. Limitaciones (sin cambios respecto de la versión anterior de este documento)

- No es la fuente jurídica de límites internos (esa es CONALI, Comité
  Nacional de Límites Internos, adscrito al Ministerio de Gobierno); el
  Marco Geoestadístico del INEC es la referencia estadística nacional más
  accesible, no una resolución de límites.
- Es una reconstrucción por disolución de unidades censales, no un
  polígono cantonal publicado como tal por el INEC.
- Las zonas censales se diseñan para fines del Censo de Población y
  Vivienda 2020, no específicamente para trazar límites administrativos;
  su borde exterior coincide con el límite cantonal por construcción del
  marco geoestadístico, pero un ajuste posterior de CONALI no se reflejaría
  aquí hasta una nueva descarga.
- No se versiona el paquete completo de la provincia (106,5 MB comprimidos
  / ~215 MB el GeoPackage) ni los extractos GeoJSON voluminosos; ver §6
  para regenerarlos.

## 6. Comandos para reproducir la descarga y el procesamiento

Los comandos siguientes son independientes de rutas personales: usan solo
nombres de archivo relativos al directorio de trabajo actual y asumen que
`curl` (incluido en Windows 10/11) y `ogr2ogr` (incluido con PostgreSQL,
PostGIS o QGIS/OSGeo4W) están disponibles en el `PATH` de la sesión. Si
`ogr2ogr` no está en el `PATH`, abra la terminal desde el "OSGeo4W Shell"
de QGIS, o agregue temporalmente la carpeta `bin` de su instalación de
PostgreSQL/PostGIS al `PATH` de la sesión actual antes de ejecutar estos
comandos.

```powershell
# 1) Descargar el paquete provincial oficial (106,5 MB)
curl.exe -o 11_LOJA.zip "https://www.ecuadorencifras.gob.ec/documentos/web-inec/Geografia_Estadistica/Documentos/11_LOJA.zip"

# 2) Verificar integridad (debe coincidir con el hash de la seccion 1)
Get-FileHash .\11_LOJA.zip -Algorithm SHA256

# 3) Descomprimir
Expand-Archive .\11_LOJA.zip -DestinationPath .

# 4) Verificar integridad del GeoPackage (debe coincidir con el hash de la seccion 1)
Get-FileHash .\11_loja.gpkg -Algorithm SHA256

# 5) Extraer las zonas censales del canton Loja (1101) y Catamayo (1103)
ogr2ogr -f GeoJSON inec_zonas_censales_canton_1101_loja.geojson 11_loja.gpkg zon_a -where "zon LIKE '1101%'"
ogr2ogr -f GeoJSON inec_zonas_censales_canton_1103_catamayo.geojson 11_loja.gpkg zon_a -where "zon LIKE '1103%'"

# 6) Copiar los dos GeoJSON generados a Tareas/Proyecto_integrador/02_datos/raw/malla/
#    (quedan fuera de git por .gitignore; son la entrada del script de verificacion)
```

Con esos dos archivos en `02_datos/raw/malla/`, el script
`Tareas/Proyecto_integrador/01_avance_1/presentacion/scripts/verificacion_territorial_y_malla.py`
reconstruye los límites, vuelve a verificar las celdas y regenera la malla
y la selección de celdas de forma determinista, sin ninguna ruta personal
codificada (usa rutas relativas a partir de la ubicación del propio
script).

## 7. Segunda comprobación (no es una fuente independiente)

Ver el detalle completo en
`03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`,
sección 3. Resumen: se consultó en vivo el servicio REST de la capa
"Parroquias del Ecuador" en ArcGIS Online, cuyos propios metadatos declaran
que sus datos provienen del mismo INEC — se usó solo como comprobación
cruzada de cálculo, no como fuente institucional distinta.
