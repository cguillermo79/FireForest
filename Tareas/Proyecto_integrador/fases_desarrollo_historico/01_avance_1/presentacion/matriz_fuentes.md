# Matriz de trazabilidad de fuentes — Presentación Avance 1 (v8)

Registra, para cada afirmación o dato citado en `main.tex` /
`Grupo04_Presentacion_AvanceProyectoIntegrador.pdf` (21 diapositivas),
su fuente exacta y si fue verificada directamente por el equipo.

**Cambios de esta versión (v8, 2026-09-15):** se incorporó una nueva
diapositiva 6, "Ámbito territorial y localización de las celdas del
prototipo", entre la diapositiva de pregunta/objetivo/alcance (5) y el
inicio de la Metodología (antes diapositiva 6, ahora 7). Esto desplazó
en +1 la numeración de todas las diapositivas 6–20 anteriores (pasan a
7–21) y de las cinco tablas numeradas anteriores (Tabla 1→2, 2→3,
3→4, 4→5, 5→6); la nueva diapositiva introduce la Tabla 1. El
número total de diapositivas pasa de 20 a 21 (la 21, Referencias,
sigue sin tiempo de exposición formal).

La nueva diapositiva documenta el hallazgo de una verificación
territorial posterior: las celdas controladas originales del prototipo
(`LJ_04521`, `LJ_04522`) resultaron estar **fuera** del cantón Loja
(dentro del cantón Catamayo, parroquia El Tambo) al verificarlas contra
la capa oficial del INEC. Se sustituyeron, en todo el contenido vigente
de la presentación, por `LJ_TEST_001` y `LJ_TEST_002` (identificadores
de prueba, verificados dentro del cantón Loja, parroquia El Cisne). El
hallazgo sobre las celdas anteriores **no se borra**: queda conservado
como evidencia de control de calidad territorial en
`03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`
y en los scripts de migración; no vuelve a aparecer en el contenido
vigente de la presentación ni del guion.

Historial anterior (v7, 2026-09-14): la diapositiva 3 incorporó la
captura real del artículo de Fire Ecology (Springer Nature Link,
`captura3.png`); la diapositiva 6 (ahora 7) ganó numeración discreta de
sus seis etapas; la diapositiva 13 (ahora 14) se reorganizó en
cuadrantes; y el pie de página mostró la sección activa en negrita.
(v6): las diapositivas 6, 12 y 13 (ahora 7, 13, 14) se rediseñaron como
flujos; la diapositiva 14 (ahora 15) pasó de tabla a flujo completo con
Airflow como franja discontinua "en fase de validación"; las tablas
metodológicas quedaron reemplazadas por flujos; las cinco tablas
restantes se numeraron consecutivamente.

## Índice de tablas numeradas

| Tabla | Título | Diapositiva | Procedencia de los valores | Tipo de evidencia |
|---|---|---|---|---|
| 1 | Celdas controladas utilizadas en la validación del prototipo | 6 | INEC, Marco Geoestadístico Nacional (`11_LOJA.zip`, capa `zon_a`); `verificacion_territorial_y_malla.py` | Fuente institucional (INEC) + resultado propio ejecutado (PostGIS) |
| 2 | Fuentes, variables y transformaciones del proyecto | 9 | `schema.sql`; `consulta_01_incendios_clima_mensual.sql`; `detecciones_viirs.json` | Código propio del proyecto |
| 3 | Estructura del modelo relacional | 11 | `03_postgresql_postgis/cargas/schema.sql` | Código propio del proyecto |
| 4 | Validación espacial de las celdas controladas | 16 | Consulta `SELECT celda_id, ST_SRID(geom), ST_IsValid(geom), ST_Area(geom) FROM dim_celda` | Consulta ejecutada sobre `fireforest` (PostgreSQL/PostGIS) |
| 5 | Detecciones controladas almacenadas en MongoDB | 17 | `consultas_mongodb.js` (`$match`/`$group`/`$max`/`$avg`) | Consulta ejecutada sobre `fireforest` (MongoDB) |
| 6 | Resultado de la integración mensual en PostgreSQL | 18 | `consulta_01_incendios_clima_mensual.sql`; prueba en transacción con `ROLLBACK` | Consulta ejecutada sobre `fireforest` (PostgreSQL) |

Numeración consecutiva sin saltos: ninguna tabla metodológica de las
diapositivas 13, 14 o 15 conserva numeración propia (reemplazadas por
flujos), por lo que la Tabla 3 (diapositiva 11) pasa directamente a la
Tabla 4 (diapositiva 16).

**Evidencia ejecutada en sesiones de desarrollo (no recalculada a
mano):** PostgreSQL (`fireforest`, vía `psql`) y MongoDB (`fireforest`,
vía `mongosh`) estaban ambos accesibles localmente. Se ejecutaron
realmente: la validación espacial (`ST_SRID`, `ST_IsValid`, `ST_Area`
sobre `dim_celda`), la consulta completa
`consulta_01_incendios_clima_mensual.sql`, una prueba del caso crítico
(celda-mes con clima y sin detecciones) dentro de una transacción con
`ROLLBACK`, y las tres consultas de `consultas_mongodb.js`. La
verificación territorial de las celdas (dentro/fuera del cantón Loja,
distancia al límite, parroquia) también se ejecutó realmente en
PostgreSQL/PostGIS, dentro de una transacción con `ROLLBACK`, mediante
`03_postgresql_postgis/validacion/validar_celdas_postgis.py`; el
resultado se conserva en `03_postgresql_postgis/evidencias/`. Ningún
valor numérico de las diapositivas 6, 16, 17 o 18 fue inventado o
recalculado manualmente. **Precisión sobre persistencia:** esa
sustitución de celdas fue ejecutada y validada dentro de una
transacción de prueba finalizada con `ROLLBACK`. Se comprobó que la
migración es funcional, pero todavía no se ha persistido en la base
PostgreSQL local; los valores de las diapositivas 16 y 18 reproducen
resultados validados en esa transacción, no el estado permanente
actual de `fireforest` (ver
`03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`,
§5). La colección `detecciones_viirs` de MongoDB (diapositiva 17) sí
está actualizada de forma permanente.

| Diapositiva | Afirmación o dato | Fuente | Tipo de fuente | Referencia completa | Verificada |
|---|---|---|---|---|---|
| 3 | Cantón Loja en los Andes tropicales del sur de Ecuador; relieve genera transiciones ambientales pronunciadas | Balaguer-Beser et al. (2026), *Background* y *Study area* | Primaria (artículo científico) | Balaguer-Beser, A., González, F., Chuncho, C. G., Carrión-Paladines, V., & Juela-Sivisaca, O. (2026). Altitudinal variation in fire behavior in Andean ecosystems in southern Ecuador. *Fire Ecology*, 22, Article 46. https://doi.org/10.1186/s42408-026-00470-y | Sí — PDF leído directamente |
| 3 | Gradiente altitudinal ~1549–2757 m s. n. m.; 3 zonas: Malacatos, Punzara, San Lucas | Balaguer-Beser et al. (2026), *Abstract* y *Study area* | Primaria | Ídem | Sí — cifras y rangos citados textualmente por zona en el artículo |
| 3 | Esquema conceptual de las 3 zonas alrededor del cantón Loja | Elaboración propia (diagrama TikZ, no reproduce la Fig. 1 del artículo) | Propia, basada en fuente primaria | — | Sí — diagrama propio |
| 3 | Captura de la publicación en Springer Nature Link (Fire Ecology, título, fecha de publicación, volumen y número de artículo, autores, indicación de acceso abierto) | Captura original proporcionada por el usuario; recorte/composición propia | Captura propia de fuente primaria (artículo científico) | Balaguer-Beser et al. (2026); `presentacion/captura3.png`; `presentacion/figuras/articulo_fire_ecology_recortado.png` | Sí — recorte verificado visualmente; el DOI coincide con la diapositiva 21 (referencia 1) |
| 3 | Distinción explícita: el artículo aporta el contexto territorial y ambiental de Malacatos, Punzara y San Lucas; no determina la ubicación de las dos celdas controladas del prototipo | Elaboración propia; verificación de ausencia de correspondencia | Verificación propia (ausencia de una afirmación) | — | Sí — ni la diapositiva 3 ni la 5, 6, 16, 17 o 18 asignan las celdas `LJ_TEST_001`/`LJ_TEST_002` a Malacatos, Punzara o San Lucas |
| 4 | Argumento heterogeneidad ambiental → datos heterogéneos → brecha de integración | Contexto ambiental: Balaguer-Beser et al. (2026). Formulación de la brecha de datos: elaboración propia del equipo | Mixta (primaria + propia, claramente distinguidas) | Balaguer-Beser et al. (2026) (ver fila anterior) | Sí — el pie de la diapositiva cita únicamente "Balaguer-Beser et al. (2026) y elaboración propia" |
| 5 | Pregunta principal, pregunta derivada, objetivo general, alcance del Avance 1 | `avance1_corregido.tex`, secciones 1.5 y 6 | Documento propio del proyecto | `01_avance_1/fuente/avance1_corregido.tex` | Sí |
| 5 | Delimitación territorial: dominio previsto = cantón Loja; cobertura actual = 2 celdas controladas, verificadas dentro del cantón (detalle visual en la diapositiva 6) | Elaboración propia, a partir de `datos_ejemplo.sql` y de la verificación territorial (diapositiva 6) | Propia + resultado propio ejecutado | — | Sí |
| 6 | Mapa "Ámbito territorial y localización de las celdas del prototipo": límite del cantón Loja, límites de sus 14 parroquias, cantón Catamayo como contexto, ubicación de `LJ_TEST_001`/`LJ_TEST_002`, recuadro ampliado con los polígonos de 500×500 m, norte, escala, leyenda, EPSG | Generado reproduciblemente con `01_avance_1/presentacion/scripts/generar_mapa_ambito_territorial.py` a partir de la capa oficial del INEC y de las geometrías de celda calculadas con el mismo pipeline que `dim_celda` | Fuente institucional (INEC) + resultado propio ejecutado | INEC, Marco Geoestadístico Nacional, `11_LOJA.zip`, capa `zon_a`, descargado 2026-09-14, EPSG:31992→32717; límite reconstruido por disolución de código DPA. Metadatos completos en `02_datos/metadatos/README_fuente_inec.md` | Sí — no es una captura de terceros ni una imagen decorativa; mapa vectorial generado por script versionado |
| 6 | Tabla 1 "Celdas controladas utilizadas en la validación del prototipo": longitud, latitud, parroquia (El Cisne) y distancia al límite cantonal de `LJ_TEST_001` y `LJ_TEST_002` | `03_postgresql_postgis/validacion/validar_celdas_postgis.py` (ejecutado localmente en PostgreSQL/PostGIS, transacción con `ROLLBACK`); resultados también reproducidos con Shapely/PyProj en `verificacion_territorial_y_malla.py` | Resultado propio ejecutado (PostGIS) | `03_postgresql_postgis/evidencias/tabla_validacion_celdas_nuevas.csv`; `03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md` | Sí — `ST_Within` del centroide y del polígono completo, y `ST_Distance` al límite, ambos confirmados en PostgreSQL/PostGIS real |
| 6 | Criterio de selección: malla sistemática de 500 m anclada a múltiplos de 500 en EPSG:32717, celdas ordenadas por X y luego por Y, margen ≥ 1 km al límite; no orientado a capturar diversidad ambiental | `verificacion_territorial_y_malla.py`, función `construir_malla_y_seleccionar` | Resultado propio ejecutado | Ídem | Sí — selección determinista, sin intervención visual ni conocimiento previo no documentado |
| 6 | Nota de no representatividad ("estas celdas no constituyen una muestra representativa del territorio cantonal") | Elaboración propia, consistente con la delimitación territorial de la diapositiva 5 | Propia | — | Sí |
| 7 | Diagrama de arquitectura general en seis etapas numeradas discretamente | Elaboración propia, a partir del flujo real implementado en `03_postgresql_postgis/` y `04_mongodb/` | Propia | — | Sí |
| 7 | Método previsto de adquisición: API o descarga directa de NASA FIRMS y repositorio CHIRPS; sin uso de Google Earth Engine en este prototipo; límite institucional INEC usado para verificación (malla completa de producción pendiente) | Búsqueda en el repositorio (sin resultados para GEE); `verificacion_territorial_celdas.md` para el estado de la fuente INEC | Verificación propia | — | Sí |
| 8 | Captura de VS Code y de GitHub — evidencia propia de la implementación local y del repositorio remoto | Capturas originales proporcionadas por el usuario; recortes propios | Captura propia | `presentacion/figuras/captura_vscode_recortada.png`; `presentacion/figuras/captura_github_recortada.png` | Sí |
| 9 | Tabla 2, fuente→variable original→transformación→variable final (VIIRS, CHIRPS, malla, calendario) | `03_postgresql_postgis/cargas/schema.sql`; `consultas/consulta_01_incendios_clima_mensual.sql`; `04_mongodb/cargas/detecciones_viirs.json` | Código propio del proyecto | Ídem | Sí — nombres de campo verificados contra el código real |
| 9 | VIIRS: NASA FIRMS; CHIRPS v2.0, Climate Hazards Center (UCSB) | NASA EOSDIS FIRMS; Climate Hazards Center (UCSB) | Primaria (institucional) | NASA EOSDIS FIRMS; Climate Hazards Center, UC Santa Barbara. *CHIRPS v2.0* | Sí |
| 10 | Tres niveles de granularidad (detección, celda-día, celda-mes) y por qué no son equivalentes | `00_documentacion_inicial/diseno_sql_nosql.md`, sección "Unidad de análisis" | Documento propio del proyecto | Ídem | Sí |
| 11 | Tabla 3, tablas `dim_celda`, `dim_fecha`, `fact_incendio`, `fact_clima`: función, grano, clave | `03_postgresql_postgis/cargas/schema.sql` | Código propio del proyecto | Ídem | Sí |
| 12 | Estructura del documento `detecciones_viirs` (campos anidados `coordenadas`, `calidad`), ahora con `celda_id: LJ_TEST_001` y coordenadas verificadas dentro del cantón Loja | `04_mongodb/cargas/detecciones_viirs.json` (documento real, actualizado tras la sustitución de celdas) | Código/dato propio del proyecto | Ídem | Sí — documento reproducido tal cual, sin alterar campos salvo el `celda_id`/coordenadas ya sustituidos |
| 12 | El prototipo filtra mediante `calidad.valida=true`; producto VIIRS y criterio definitivo de calidad pendientes | `04_mongodb/consultas/consultas_mongodb.js` | Código propio del proyecto | Ídem | Sí |
| 13 | Flujo espacial en tres líneas paralelas; fórmulas de reproyección y área; `ST_SetSRID`→`ST_Transform`→`ST_MakeEnvelope` | `03_postgresql_postgis/cargas/datos_ejemplo.sql`; documentación oficial de PostGIS | Código propio + primaria (institucional) | PostGIS Project Steering Committee. *PostGIS Documentation* | Sí |
| 14 | Ecuaciones y definiciones de estandarización temporal; dos flujos horizontales (VIIRS, CHIRPS) convergentes | `consulta_01_incendios_clima_mensual.sql`; `decisiones_metodologicas.md` §2 | Código y documento propios | Ídem | Sí |
| 15 | Flujo ETL completo; Airflow como franja discontinua "en fase de validación" | Código real del repositorio | Código propio del proyecto | Ídem | Sí |
| 15 | Sintaxis `LEFT JOIN` / `COALESCE` | Documentación oficial de PostgreSQL | Primaria (institucional) | PostgreSQL Global Development Group. *PostgreSQL Documentation* | Sí |
| 16 | Flujo previo a la tabla; Tabla 4 "Validación espacial de las celdas controladas": SRID 32717, geometría válida, área 250 000 m² para `LJ_TEST_001` y `LJ_TEST_002`, verificadas dentro del cantón Loja, parroquia El Cisne | Consulta `SELECT celda_id, ST_SRID(geom), ST_IsValid(geom), ST_Area(geom) FROM dim_celda`; coordenadas en `03_postgresql_postgis/cargas/datos_ejemplo.sql` (versión vigente) | Resultado propio (datos controlados) | Ejecutada sobre `fireforest` (PostgreSQL/PostGIS) | Sí — pertenencia cantonal y parroquial confirmadas contra la capa oficial del INEC (diapositiva 6), no una etiqueta sin sustento |
| 17 | Tabla 5 "Detecciones controladas almacenadas en MongoDB": FRP máxima 18,4 MW; FRP media 14,05 MW; 2 documentos, celdas `LJ_TEST_001`/`LJ_TEST_002` | `consultas_mongodb.js`, secciones 1 y 2 (`$match`, `$group`, `$max`, `$avg`), re-ejecutada tras la sustitución de celdas | Resultado propio (datos controlados) | Ejecutada sobre `mongodb://localhost:27017/fireforest`; log en `04_mongodb/evidencias/salida_consultas_mongodb_LJ_TEST.txt` | Sí — salida real de `mongosh` tras recargar `detecciones_viirs.json`, no recalculada a mano |
| 18 | Tabla 6 "Resultado de la integración mensual en PostgreSQL": 2 celda-mes reales (`LJ_TEST_001`, `LJ_TEST_002`) y prueba del caso crítico (celda-mes sintética de septiembre sobre `LJ_TEST_001`, revertida) | Consulta ejecutada en vivo; prueba en transacción con `ROLLBACK`, dentro de `validar_celdas_postgis.py` | Resultado propio (datos controlados) | Ejecutada sobre `fireforest` (PostgreSQL); verificado que no quedó fila persistida tras el `ROLLBACK` | Sí |
| 18 | Aclaración sobre 0 vs. `NULL`: "En la prueba sintética, LEFT JOIN conservó la fila climática y COALESCE representó con cero la ausencia de una fila coincidente de incendio. En datos reales, ese cero solo podrá interpretarse como ausencia de detecciones cuando la cobertura e ingesta VIIRS hayan sido verificadas independientemente. NULL representa información faltante, no procesada o no evaluada." | Elaboración propia, formulación fijada explícitamente para evitar sobregeneralizar el resultado de la prueba sintética | Propia | — | Sí — no se afirma que la prueba demuestre "ausencia de detecciones" en general, solo el comportamiento de `LEFT JOIN`/`COALESCE` en el escenario controlado |
| 6, 16–18 | Etiqueta uniforme "Datos controlados del prototipo; sin representatividad cantonal" | Elaboración propia, siguiendo la delimitación territorial ya declarada en la diapositiva 5 | Propia | — | Sí |
| 19 | Cuatro hallazgos interpretados; frase prudente "coherencia funcional básica" | Elaboración propia, interpretando los resultados de las diapositivas 16–18 | Propia | — | Sí |
| 19 | Limitaciones (2 celdas/2 detecciones, malla completa de producción pendiente —fuente de verificación ya identificada: INEC—, producto VIIRS pendiente, Airflow en validación, idempotencia PostgreSQL pendiente) | `tareas_pendientes.md`, `decisiones_metodologicas.md` §6 | Documentos propios | Ídem | Sí |
| 20 | Conclusiones y próximos pasos (incluye extender la verificación INEC a la malla completa, `viirs_disponible`, Airflow, análisis estadístico) | `avance1_corregido.tex` (secciones 7–8); `tareas_pendientes.md`; `decisiones_metodologicas.md` §6 | Documentos propios | Ídem | Sí |
| 21 | Las 6 referencias completas | Ver filas anteriores | — | — | Sí — cada una fue citada previamente en al menos una diapositiva |

## Notas de cumplimiento de las reglas de citación

- No se generalizan los hallazgos de las 3 zonas del estudio (Malacatos,
  Punzara, San Lucas) a todo el cantón Loja; la diapositiva 3 lo declara
  explícitamente en su pie de fuente.
- No se atribuye al artículo de Fire Ecology el diseño SQL–NoSQL del
  proyecto (diapositiva 4).
- No se afirma uso de Google Earth Engine (diapositivas 7 y 9).
- No se afirma que la adquisición mediante API ya fue ejecutada
  (diapositiva 7): la redacción usa "método previsto de adquisición".
- Las capturas de VS Code y GitHub (diapositiva 8) son evidencia de
  implementación local y de control de versiones remoto, no una
  representación de la arquitectura.
- El campo de calidad del modelo documental (diapositiva 12) filtra por
  `calidad.valida=true`; `fire_mask` se conserva como atributo, no como
  campo de filtro activo.
- "Ausencia de incendio" se reemplazó por "ausencia de detecciones"
  (diapositiva 14).
- **Verificación territorial y sustitución de celdas (diapositiva 6,
  nueva en esta versión):** las celdas controladas originales
  (`LJ_04521`, `LJ_04522`) se verificaron contra la capa oficial del
  INEC y resultaron estar fuera del cantón Loja (cantón Catamayo,
  parroquia El Tambo). Esa evidencia **no se eliminó**: se conserva
  íntegra en `03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`
  como registro de control de calidad, con una nota de trazabilidad que
  explica por qué una medición exploratoria inicial (distancia del
  centroide) y la medición final (distancia del polígono completo)
  dieron cifras distintas para la misma celda. El contenido **vigente**
  de la presentación y del guion usa únicamente `LJ_TEST_001` y
  `LJ_TEST_002` (identificadores de prueba, no códigos administrativos
  oficiales), verificados dentro del cantón Loja, parroquia El Cisne,
  con margen ≥ 1 km al límite cantonal, seleccionados de forma
  determinista (malla anclada a múltiplos de 500 m, ordenada por X y
  luego Y). Se realizó una búsqueda global de `LJ_04521`, `LJ_04522` y
  de sus coordenadas originales en `main.tex`, `guion_exposicion.md`,
  `guion_exposicion.tex` y esta matriz: no aparecen fuera de las
  menciones explícitas al hallazgo histórico en la documentación de
  evidencia (fuera del alcance de este archivo, que solo traza el
  contenido vigente de la presentación).
- **Fuente del mapa territorial:** INEC, Marco Geoestadístico Nacional
  (`11_LOJA.zip`, capa `zon_a`, EPSG:31992, reproyectada a EPSG:32717),
  descargado el 2026-09-14. El paquete del INEC no incluye una capa
  cantonal ya disuelta; el límite del cantón Loja y de sus 14
  parroquias se reconstruyó por disolución de zonas censales agrupadas
  por código DPA — procedimiento documentado íntegramente en
  `02_datos/metadatos/README_fuente_inec.md` y en
  `verificacion_territorial_celdas.md`. Como comprobación adicional
  (no como segunda fuente institucional independiente, porque sus
  datos también proceden del INEC) se consultó en vivo el servicio
  REST de la capa "Parroquias del Ecuador" en ArcGIS Online; se
  describe explícitamente como **comprobación complementaria**, nunca
  como una fuente distinta.
- No se describe a las celdas `LJ_TEST_001`/`LJ_TEST_002` como
  "elaboradas para FireForest": se usa la expresión neutral "celdas
  controladas incorporadas al prototipo FireForest" (diapositiva 6),
  porque provienen de una malla sistemática generada sobre la capa
  oficial, no de un diseño ad hoc.
- La delimitación territorial (dominio previsto: cantón Loja; cobertura
  real: dos celdas controladas verificadas, sin representatividad
  territorial) se explica en detalle en las diapositivas 5 y 6, y se
  repite como etiqueta breve y uniforme en las diapositivas 16, 17 y
  18.
- No se afirma "arquitectura viable" en sentido operacional; se usa la
  redacción prudente "coherencia funcional básica...; su viabilidad
  operativa deberá evaluarse con datos reales, mayor volumen y
  automatización" (diapositivas 19 y 20).
- `viirs_disponible` aparece únicamente como actividad futura pendiente
  (diapositiva 20, "Próximos pasos").
- Las seis tablas numeradas (Tabla 1 a Tabla 6) llevan título en el
  mismo formato ("Tabla N. Título descriptivo"), alineado a la
  izquierda; cada una lleva su línea de fuente debajo. Numeración
  consecutiva sin saltos.
- El pie de página de las 21 diapositivas identifica la sección activa
  en negrita: diapositivas 1–2 "Presentación"; 3–6 "I. Introducción"
  (incluye la nueva diapositiva territorial); 7–15 "II. Metodología";
  16–18 "III. Resultados preliminares"; 19 "IV. Discusión preliminar";
  20 "V. Conclusiones"; 21 "Referencias".
- La captura del artículo de Fire Ecology (diapositiva 3) no se
  interpreta como fuente de la ubicación del prototipo; esa distinción
  se refuerza ahora con la diapositiva 6, que ubica las celdas
  mediante verificación PostGIS independiente contra la capa del INEC,
  no mediante el artículo bibliográfico.
- No se menciona ningún otro proyecto ajeno a FireForest en ningún
  punto de esta matriz ni de la presentación.
