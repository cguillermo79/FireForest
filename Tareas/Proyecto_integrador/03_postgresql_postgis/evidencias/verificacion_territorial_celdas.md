# Verificación territorial de las celdas controladas — evidencia de control de calidad

Proyecto: FireForest (independiente; no relacionado con ningún otro proyecto).

Este documento es un **registro de control de calidad territorial**. Conserva,
sin ocultar ni reinterpretar, el hallazgo de que las celdas controladas
originales del prototipo (`LJ_04521`, `LJ_04522`) **no pertenecen al cantón
Loja**, y documenta el proceso reproducible con el que se sustituyeron por
dos celdas nuevas (`LJ_TEST_001`, `LJ_TEST_002`) verificadas dentro del
cantón Loja.

## 1. Resumen del hallazgo

| | |
|---|---|
| Fecha de detección | 2026-09-14 |
| Método de detección | Validación espacial posterior (verificación contra capa oficial del INEC), solicitada explícitamente para auditar la delimitación territorial antes de incorporar un mapa a la presentación |
| Celdas afectadas | `LJ_04521` (lon −79.241, lat −4.082), `LJ_04522` (lon −79.236, lat −4.079) |
| Resultado | **Ambas celdas están fuera del cantón Loja.** Pertenecen al **cantón Catamayo**, **parroquia El Tambo**, en la misma provincia (Loja) pero en un cantón distinto del cantón Loja |
| Distancia al límite del cantón Loja | `LJ_04521`: 1109,45 m fuera del límite. `LJ_04522`: 762,31 m fuera del límite (distancia del polígono de 500×500 m completo al límite reconstruido del cantón Loja) |
| Disposición | **No se reinterpretaron ni se reutilizaron.** Se sustituyeron por `LJ_TEST_001` y `LJ_TEST_002` (sección 4), con migración permanente ya aplicada en PostgreSQL (`COMMIT` real, 2026-09-14) y MongoDB (ver sección 5). Este documento y sus evidencias asociadas se conservan como registro permanente del hallazgo |

Declaraciones explícitas requeridas:

- `LJ_04521` y `LJ_04522` **están en el cantón Catamayo**, no en el cantón Loja.
- Ambas **pertenecen a la parroquia El Tambo** (código DPA `110351`).
- **No pueden utilizarse como celdas de prueba del cantón Loja**: el dominio
  declarado del proyecto FireForest es el cantón Loja, y estas coordenadas
  quedan fuera de su límite oficial.
- Fueron **detectadas mediante una validación espacial posterior** a su uso
  en el Avance 1 (la ubicación de estas celdas nunca había sido verificada
  contra una capa territorial oficial antes de esta auditoría).
- **Fueron sustituidas y no reinterpretadas**: no se ajustó el discurso
  para hacerlas parecer válidas (por ejemplo, no se redefinió el dominio
  del proyecto como "cantón Loja y alrededores" ni se eliminó la mención
  al cantón Catamayo).

## 1.bis Nota de trazabilidad: discrepancia entre la primera y la segunda medición de distancia

Durante esta auditoría se reportaron dos cifras de distancia distintas para
las mismas celdas, en dos momentos distintos del trabajo:

| | Primera auditoría (exploratoria) | Segunda auditoría (script final) |
|---|---|---|
| `LJ_04521` | 1417,9 m fuera | 1109,45 m fuera |
| `LJ_04522` | 1037,8 m fuera | 762,31 m fuera |

**Ninguna de las dos cifras se elimina ni se corrige por error de cálculo.**
Ambas son correctas; miden cosas distintas. Esta nota deja registradas las
cuatro combinaciones posibles (centroide/polígono × frontera/geometría) en
los dos CRS involucrados, para que no quede ambigüedad.

### Cálculo completo (`Point.distance` / `Polygon.distance` de Shapely,
equivalente a `ST_Distance` de PostGIS; geometrías ya proyectadas, por lo
que la distancia se calcula en el plano, en **metros**)

| Celda | Geometría | CRS | Objetivo | Distancia (m) |
|---|---|---|---|---|
| `LJ_04521` | Centroide (punto) | EPSG:31992 (nativo INEC) | `ST_Boundary(canton_loja.geom)` | 1417,87 |
| `LJ_04521` | Centroide (punto) | EPSG:31992 (nativo INEC) | `canton_loja.geom` (geometría completa) | 1417,87 |
| `LJ_04521` | Polígono 500×500 m | EPSG:31992 (nativo INEC) | `ST_Boundary(canton_loja.geom)` | 1109,45 |
| `LJ_04521` | Polígono 500×500 m | EPSG:31992 (nativo INEC) | `canton_loja.geom` (geometría completa) | 1109,45 |
| `LJ_04521` | Centroide (punto) | EPSG:32717 (trabajo del proyecto) | `ST_Boundary(canton_loja.geom)` | 1417,87 |
| `LJ_04521` | Centroide (punto) | EPSG:32717 (trabajo del proyecto) | `canton_loja.geom` (geometría completa) | 1417,87 |
| `LJ_04521` | Polígono 500×500 m | EPSG:32717 (trabajo del proyecto) | `ST_Boundary(canton_loja.geom)` | 1109,45 |
| `LJ_04521` | Polígono 500×500 m | EPSG:32717 (trabajo del proyecto) | `canton_loja.geom` (geometría completa) | 1109,45 |
| `LJ_04522` | Centroide (punto) | EPSG:31992 / EPSG:32717 (igual en ambos) | frontera / geometría (igual en ambos) | 1037,79 |
| `LJ_04522` | Polígono 500×500 m | EPSG:31992 / EPSG:32717 (igual en ambos) | frontera / geometría (igual en ambos) | 762,31 |

### Explicación exacta de la diferencia

1. **CRS (EPSG:31992 vs EPSG:32717): diferencia de 0,0000 m.** Se
   verificó calculando la misma distancia (centroide → frontera) en ambos
   CRS para las mismas celdas: el resultado es idéntico a 4 decimales. SIRGAS
   1995 y WGS84 son, para fines prácticos, coincidentes en el Ecuador
   continental (diferencia de re-proyección de un punto: 1–5 cm, verificado
   por separado con `pyproj`). **La elección de CRS no explica ninguna
   parte de la discrepancia observada.**

   **Nota de corrección conceptual:** la transformación ejecutada en el
   entorno PROJ produjo una diferencia numérica de 0,0000 m para las
   geometrías evaluadas. Esto **no implica identidad conceptual entre
   SIRGAS 1995 y WGS84**: son datums distintos, con definiciones propias;
   la coincidencia numérica observada aplica a esta región y a la
   precisión de trabajo de este proyecto (metros), no es una equivalencia
   general entre ambos sistemas de referencia.

2. **Frontera vs geometría completa (`ST_Boundary` vs geometría): diferencia
   de 0,0000 m en este caso.** Como ambas celdas están **fuera** del
   cantón Loja (no lo intersectan), la distancia de un objeto exterior a la
   geometría rellena es, por definición, igual a la distancia a su
   frontera. Esta distinción solo produce una diferencia distinta de cero
   cuando el objeto está **dentro** del polígono (ahí la distancia a la
   geometría rellena es 0, mientras que la distancia a la frontera puede
   ser mayor que 0). **Tampoco explica la discrepancia observada.**

3. **Centroide (punto) vs polígono completo de 500×500 m: esta es la única
   causa real de la discrepancia.**
   - `LJ_04521`: 1417,87 m (centroide) − 1109,45 m (polígono) = **308,42 m**
     de diferencia.
   - `LJ_04522`: 1037,79 m (centroide) − 762,31 m (polígono) = **275,48 m**
     de diferencia.
   - Motivo: el polígono de 500×500 m se extiende 250 m en cada dirección
     desde su centroide. El borde del polígono más cercano al cantón Loja
     queda, por lo tanto, más cerca del límite cantonal que el propio
     centroide — la reducción observada (275–308 m) es coherente con un
     desplazamiento de hasta 250 m en la dirección del límite más un
     componente diagonal, según el ángulo exacto de aproximación de cada
     celda.
   - La **primera auditoría** (exploratoria, antes de tener el script
     final) midió `canton_geom.boundary.distance(punto_centroide)` —
     **distancia del centroide**.
   - La **segunda auditoría** (script
     `verificacion_territorial_y_malla.py`, función `verificar_celda`) mide
     `cell.distance(boundary_loja)` con `cell` = el polígono de 500×500 m
     completo — **distancia del polígono**, que es la magnitud
     efectivamente pedida por el criterio de selección
     (`ST_Distance(celda.geom, ST_Boundary(canton_loja.geom)) >= 1000`, es
     decir, sobre `celda.geom`, no sobre su centroide).

### Cuál cifra es la vigente

La cifra vigente para cualquier decisión (incluida la selección de
`LJ_TEST_001`/`LJ_TEST_002` en la sección 4) es siempre la del
**polígono completo** (`ST_Distance(celda.geom, ...)`), porque es la que
pide literalmente el criterio de margen de seguridad. Las cifras de la
primera auditoría (centroide) permanecen en este documento sin alterar,
como registro histórico de esa primera exploración; esta nota es la
corrección de contexto, no un reemplazo de esos números.

## 2. Fuente oficial utilizada

| Campo | Valor |
|---|---|
| Institución | INEC — Instituto Nacional de Estadística y Censos (Ecuador) |
| Dataset | Marco Geoestadístico Nacional, paquete provincial |
| Archivo | `11_LOJA.zip` → `11_loja.gpkg` (GeoPackage) |
| Capa | `zon_a` (zonas censales); campo `zon` = código DPA de 9 dígitos (provincia+cantón+parroquia+zona) |
| Fecha de descarga | 2026-09-14 |
| URL | `https://www.ecuadorencifras.gob.ec/documentos/web-inec/Geografia_Estadistica/Documentos/11_LOJA.zip` |
| EPSG nativo de la capa | EPSG:31992 (SIRGAS 1995 / UTM zone 17S) |
| EPSG de trabajo del proyecto | EPSG:32717 (WGS84 / UTM zone 17S), igual que `dim_celda.geom` |
| Campos DPA usados | `zon` (código de 9 dígitos: prefijo de 4 = cantón, prefijo de 6 = parroquia) |
| Procedimiento de disolución | Unión geométrica (`unary_union`) de todas las zonas censales cuyo código `zon` comparte el mismo prefijo de cantón (4 dígitos) para el límite cantonal, o el mismo prefijo de parroquia (6 dígitos) para los límites parroquiales |
| Capa administrativa cantonal directa | **No existe** en el paquete del INEC. Se revisaron las 9 capas del GeoPackage (`loc_p`, `edif_p`, `ingresos_l`, `ejes_l`, `zon_a`, `sec_a`, `man_a`, `ca04_a`, `aream_a`); ninguna es un polígono cantonal o parroquial ya disuelto. Por eso se usó la reconstrucción por disolución de `zon_a`, documentada aquí explícitamente |
| Control de calidad de la reconstrucción | Área del cantón Loja reconstruido: **1891,19 km²**, consistente con el área comúnmente publicada para este cantón |
| Limitaciones | Ver `Tareas/Proyecto_integrador/02_datos/metadatos/README_fuente_inec.md`, sección 5 (no es la fuente jurídica de límites de CONALI; es una reconstrucción por disolución censal, no un polígono cantonal publicado como tal; no se versionó el paquete provincial completo, solo extractos por cantón) |

Metadatos completos, licencia y archivos descargados: ver
`Tareas/Proyecto_integrador/02_datos/metadatos/README_fuente_inec.md`.

## 3. Segunda comprobación (no es una fuente independiente)

Se realizó una comprobación adicional consultando en vivo el servicio REST
de la capa "Parroquias del Ecuador" (ArcGIS Online, cuenta `sigcfe`),
cuyos propios metadatos declaran que sus datos "fueron descargados
directamente del sitio oficial del INEC". **No se presenta como una fuente
oficial independiente**, porque su origen declarado es el mismo INEC; se usó
únicamente como una comprobación cruzada con un motor de consulta espacial
distinto, sobre otra publicación del mismo origen institucional.

- Servicio: `https://services7.arcgis.com/iFGeGXTAJXnjq0YN/ArcGIS/rest/services/Parroquias_del_Ecuador/FeatureServer/0`
- Fecha de consulta: 2026-09-14
- Campos: `DPA_DESPRO`, `DPA_DESCAN`, `DPA_DESPAR`, `DPA_CANTON`, `DPA_PARROQ`
- Resultado para `LJ_04521` (`geometry=-79.241,-4.082`, `inSR=4326`,
  `spatialRel=esriSpatialRelIntersects`):
  `{"DPA_DESPRO": "LOJA", "DPA_DESCAN": "CATAMAYO", "DPA_DESPAR": "EL TAMBO", "DPA_CANTON": "1103", "DPA_PARROQ": "110351"}`
- Resultado para `LJ_04522` (`geometry=-79.236,-4.079`): mismo resultado
  (`CATAMAYO` / `EL TAMBO` / `1103` / `110351`)

Coincide exactamente con la reconstrucción propia descrita en la sección 2,
usando un motor y una copia de datos distintos.

## 4. Celdas de reemplazo verificadas dentro del cantón Loja

### 4.1 Criterio de selección (reproducible, sin intervención visual)

1. Se construyó una **malla sistemática de celdas de 500×500 m**, anclada a
   múltiplos de 500 en EPSG:32717 (`x = k·500`, `y = j·500`, `k,j` enteros),
   sobre el rectángulo envolvente del cantón Loja reconstruido.
2. Se conservaron únicamente las celdas cuyo **polígono completo** está
   contenido en el cantón Loja — equivalente a
   `ST_Within(celda.geom, canton_loja.geom)`.
3. Se aplicó un **margen de seguridad ≥ 1000 m** respecto del límite
   cantonal — equivalente a
   `ST_Distance(celda.geom, ST_Boundary(canton_loja.geom)) >= 1000`.
4. De las celdas que cumplen ambos criterios (**5949** sobre un total de
   18 700 celdas de la malla completa del rectángulo envolvente; 7152 de
   ellas ya cumplían el criterio 2 antes de aplicar el margen), se
   **ordenaron por coordenada X ascendente y luego Y ascendente**, y se
   tomaron las **dos primeras** de esa lista ordenada.
5. No se aplicó ningún criterio de conveniencia visual, cercanía a una
   localidad conocida, ni conocimiento previo no documentado. El
   procedimiento completo es determinista y reproducible ejecutando
   `Tareas/Proyecto_integrador/01_avance_1/presentacion/scripts/verificacion_territorial_y_malla.py`.

### 4.2 Identificadores

- `LJ_TEST_001` y `LJ_TEST_002` son **identificadores de prueba**
  (`TEST` es literal en el nombre, para dejar explícito que son datos
  controlados de validación técnica, no observaciones reales).
- **No reutilizan** `LJ_04521` ni `LJ_04522` con coordenadas distintas: son
  identificadores nuevos, para no crear ambigüedad con el hallazgo
  documentado en este archivo.
- Algoritmo de asignación: `LJ_TEST_{idx:03d}`, con `idx` = posición
  (1, 2, …) de la celda dentro de la lista ordenada por (X, Y) descrita en
  §4.1. Es decir, el sufijo numérico refleja el orden determinista de
  selección, no un conteo arbitrario.

### 4.3 Tabla de validación

Tabla completa reproducible en
`Tareas/Proyecto_integrador/03_postgresql_postgis/evidencias/tabla_validacion_celdas_nuevas.csv`.
Resumen:

| Celda | Longitud | Latitud | Centroide UTM (X, Y) | EPSG | Área (`ST_Area` equiv.) | Cantón | Parroquia | Distancia al límite | `ST_Within` centroide | `ST_Within` polígono completo |
|---|---|---|---|---|---|---|---|---|---|---|
| `LJ_TEST_001` | −79.520851 | −3.805328 | (664250.0, 9579250.0) | 32717 | 250 000 m² | Loja | El Cisne | 1085,01 m | `true` | `true` |
| `LJ_TEST_002` | −79.516342 | −3.809842 | (664750.0, 9578750.0) | 32717 | 250 000 m² | Loja | El Cisne | 1066,05 m | `true` | `true` |

Ambas celdas caen en la parroquia **El Cisne** (código DPA `110153`),
determinada con la misma capa oficial disuelta por parroquia (no por
inspección visual). Las dos celdas quedan adyacentes en diagonal (separadas
500 m en X y 500 m en Y — no se tocan por un lado completo), consecutivas en
el orden de selección descrito en §4.1, no necesariamente contiguas en el
sentido de compartir un borde.

### 4.4 Advertencia de alcance (igual que las celdas anteriores)

Estas dos celdas, igual que las originales, son **datos controlados usados
únicamente para validación técnica** del prototipo (almacenamiento,
reproyección, agregación temporal, consultas de integración). Dos
ubicaciones dentro de una sola parroquia **no** constituyen una muestra
representativa de la variabilidad ambiental, altitudinal o climática del
cantón Loja, y no deben presentarse como tales.

## 5. Ejecución en PostgreSQL/PostGIS — tres etapas diferenciadas

Las verificaciones territoriales de este documento se calcularon
originalmente con **Shapely + PyProj** (Python), reproduciendo la misma
semántica y aritmética planar que `ST_Within`, `ST_Distance`, `ST_Area`
y `ST_Transform` de PostGIS. Después se ejecutaron realmente en
PostgreSQL/PostGIS, en tres etapas separadas y con evidencia propia
cada una:

**(a) Prueba transaccional inicial (`ROLLBACK`, no persiste nada).**
El usuario ejecutó localmente, con sus propias credenciales (nunca
compartidas ni almacenadas por el asistente),
`Tareas/Proyecto_integrador/03_postgresql_postgis/validacion/validar_celdas_postgis.py`
contra la base `fireforest` real, dentro de una transacción que
**termina siempre en `ROLLBACK`**. Resultado en
`Tareas/Proyecto_integrador/03_postgresql_postgis/evidencias/salida_validacion_postgis_celdas.txt`:
confirmó, **dentro de esa transacción**, que la migración era
funcional (sin huérfanos ni duplicados, SRID 32717, geometría válida,
área 250 000 m², dentro del cantón Loja y de El Cisne, distancias
1085,00 m/1066,01 m, integración celda-mes correcta, caso sintético
"clima sin detección" con `detecciones_totales = 0`), pero **no
persistió ningún cambio**: tras el `ROLLBACK`, `LJ_04521`/`LJ_04522`
seguían existiendo en la base y `LJ_TEST_001`/`LJ_TEST_002` todavía no.

**(b) Migración permanente (`COMMIT` real).** El usuario ejecutó
localmente el **2026-09-14**
`Tareas/Proyecto_integrador/03_postgresql_postgis/validacion/aplicar_celdas_postgis.py`
— un ejecutor independiente y nuevo, que no modifica ni reutiliza la
lógica de `validar_celdas_postgis.py` (ese script se conserva intacto,
terminando siempre en `ROLLBACK`). Antes de escribir nada, guardó un
respaldo recuperable de las filas de `LJ_04521`/`LJ_04522` (`dim_celda`,
`fact_incendio`, `fact_clima`, geometría como `ST_AsEWKT`+SRID+área, sin
credenciales) en
`Tareas/Proyecto_integrador/03_postgresql_postgis/evidencias/respaldo_celdas_anteriores.json`.
Ejecutó la migración (`Tareas/Proyecto_integrador/03_postgresql_postgis/cargas/aplicar_actualizacion_celdas_prueba.sql`,
parseada respetando sus bloques `DO $$...$$` de precondición y
postcondición) dentro de una única transacción y confirmó con
**`COMMIT` real**. Log completo en
`Tareas/Proyecto_integrador/03_postgresql_postgis/evidencias/salida_aplicacion_postgis_celdas.txt`:
10 sentencias de la migración ejecutadas (ver nota de trazabilidad al
final de esta sección sobre por qué 10 y no las 12 que detecta el
parser), con 2 filas afectadas en cada `DELETE`/`INSERT`/`UPDATE` sobre
`dim_celda`, `fact_incendio` y `fact_clima`.

**(c) Verificación del estado ya persistido (conexión nueva, solo
lectura).** El mismo ejecutor cerró la conexión de migración, abrió una
conexión **nueva** exclusivamente de lectura, y confirmó contra el
estado real y ya persistido de la base (mismo log que (b)): `LJ_04521`
y `LJ_04522` ausentes; `LJ_TEST_001` y `LJ_TEST_002` presentes; sin
huérfanos ni duplicados; SRID 32717; geometría válida; área
250 000 m²; dentro del cantón Loja y de la parroquia El Cisne (centroide
y polígono completo); distancia al límite 1085,00 m y 1066,01 m; y la
consulta de integración celda-mes con 2 filas y los valores esperados
de FRP y precipitación. Una reejecución adicional de cierre, también de
solo lectura y también contra el estado ya persistido, se guardó por
separado en
`Tareas/Proyecto_integrador/03_postgresql_postgis/evidencias/salida_reejecucion_cierre_postgis_mongodb.txt`,
sin sobrescribir ninguno de los registros anteriores.

**Estado final:** PostgreSQL y MongoDB usan ahora, de forma
**permanente**, `LJ_TEST_001` y `LJ_TEST_002`. `LJ_04521`/`LJ_04522` no
existen en el estado persistido de ninguna de las dos bases; se
conservan únicamente como hallazgo histórico en este documento y en el
respaldo JSON.

**Nota de trazabilidad — 10 sentencias ejecutadas frente a 12
detectadas por el parser.** El parser de
`aplicar_celdas_postgis.py` (compartido en su lógica con
`validar_celdas_postgis.py`) detecta **12** sentencias en
`aplicar_actualizacion_celdas_prueba.sql`: 1 `BEGIN`, 1 bloque `DO`
de precondición, 7 sentencias `DELETE`/`INSERT`/`UPDATE`, 2 bloques
`DO` de postcondición, y 1 `COMMIT`. El ejecutor filtra explícitamente
`BEGIN` y `COMMIT` antes de ejecutar y contar (esas dos sentencias las
gestiona la propia conexión de Python: `psycopg.connect(...)` abre la
transacción real, y `conn.commit()`/`conn.rollback()` la cierran; dejar
que el archivo `.sql` emitiera su propio `BEGIN`/`COMMIT` literal
entraría en conflicto con el control transaccional del script). Por
eso el log de ejecución reporta **10** sentencias: 12 detectadas − 2
filtradas (`BEGIN`, `COMMIT`) = 10 ejecutadas. Verificado línea por
línea contra el log real: aparecen exactamente 10 líneas de resultado
(3 `DO`, 3 `DELETE`, 1 `INSERT dim_celda`, 1 `UPDATE`, 1 `INSERT
fact_clima`, 1 `INSERT fact_incendio`).

## 6. Archivos de evidencia relacionados

| Archivo | Contenido |
|---|---|
| `02_datos/metadatos/README_fuente_inec.md` | Metadatos completos de la fuente INEC |
| `02_datos/raw/malla/inec_zonas_censales_canton_1101_loja.geojson` | Capa oficial (zonas censales), cantón Loja, SRID nativo 31992 |
| `02_datos/raw/malla/inec_zonas_censales_canton_1103_catamayo.geojson` | Capa oficial (zonas censales), cantón Catamayo — evidencia del hallazgo |
| `01_avance_1/presentacion/scripts/verificacion_territorial_y_malla.py` | Script reproducible: reconstrucción de límites, re-verificación de celdas originales, generación de malla y selección determinista de celdas nuevas, tabla de validación |
| `01_avance_1/presentacion/scripts/generar_mapa_ambito_territorial.py` | Script reproducible del mapa de la presentación |
| `01_avance_1/presentacion/figuras/mapa_ambito_territorial_celdas.png` / `.pdf` | Mapa generado |
| `03_postgresql_postgis/evidencias/tabla_validacion_celdas_nuevas.csv` | Tabla de validación completa (salida del script) |
| `03_postgresql_postgis/evidencias/salida_verificacion_territorial_y_malla.txt` | Registro de ejecución completo del script de verificación (Shapely/PyProj) |
| `03_postgresql_postgis/validacion/validar_celdas_postgis.py` | (a) Script de prueba transaccional, `ROLLBACK` siempre |
| `03_postgresql_postgis/evidencias/salida_validacion_postgis_celdas.txt` | (a) Log de la prueba transaccional |
| `03_postgresql_postgis/cargas/aplicar_actualizacion_celdas_prueba.sql` | (b) Migración permanente ejecutable (`BEGIN`…`COMMIT`), con precondiciones y postcondiciones |
| `03_postgresql_postgis/validacion/aplicar_celdas_postgis.py` | (b)+(c) Ejecutor de la migración permanente y de la verificación posterior en conexión nueva |
| `03_postgresql_postgis/evidencias/respaldo_celdas_anteriores.json` | (b) Respaldo de `LJ_04521`/`LJ_04522` previo al `COMMIT` |
| `03_postgresql_postgis/evidencias/salida_aplicacion_postgis_celdas.txt` | (b)+(c) Log de la migración permanente y su verificación posterior |
| `03_postgresql_postgis/evidencias/salida_reejecucion_cierre_postgis_mongodb.txt` | Reejecución de cierre (solo lectura) de PostgreSQL y MongoDB tras el `COMMIT` |
| `03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md` | Este documento |
