# Matriz de trazabilidad de fuentes — Presentación Avance 1 (v7)

Registra, para cada afirmación o dato citado en `main.tex` /
`Grupo04_Presentacion_AvanceProyectoIntegrador.pdf` (20 diapositivas),
su fuente exacta y si fue verificada directamente por el equipo. Esta
versión (v7) actualiza la matriz de la v6 tras la revisión del
2026-09-14: la diapositiva 3 incorpora la captura real del artículo de
Fire Ecology (Springer Nature Link, `captura3.png`) junto al contenido
territorial existente, con cita completa y DOI enlazado; la
diapositiva 6 ganó numeración discreta de sus seis etapas; la
diapositiva 13 se reorganizó en cuadrantes (ecuaciones, definiciones,
dos flujos horizontales, resultado común al extremo derecho con dos
flechas independientes sin cruce); y el pie de página de las 20
diapositivas ahora muestra la sección activa en negrita
(Presentación / I. Introducción / II. Metodología / III. Resultados
preliminares / IV. Discusión preliminar / V. Conclusiones /
Referencias) en lugar de "Proyecto Integrador". Versiones anteriores
(v6, 2026-09-14): las diapositivas 6, 12 y 13 se rediseñaron como
flujos con flechas de punta Latex y dirección inequívoca; la
diapositiva 14 pasó de tabla a flujo completo (entradas, carga, bases
de datos, controles de calidad, transformación e integración,
salidas), con Airflow como franja discontinua explícitamente marcada
"en fase de validación"; las tablas metodológicas de las diapositivas
12, 13 y 14 quedaron reemplazadas por esos flujos y se retiraron; y
las cinco tablas restantes se numeraron consecutivamente (Tabla 1 a
Tabla 5, sin saltos), cada una con título propio sobre la tabla y una
línea de fuente debajo. El número de diapositivas se mantiene en 20.

## Índice de tablas numeradas

| Tabla | Título | Diapositiva | Procedencia de los valores | Tipo de evidencia |
|---|---|---|---|---|
| 1 | Fuentes, variables y transformaciones del proyecto | 8 | `schema.sql`; `consulta_01_incendios_clima_mensual.sql`; `detecciones_viirs.json` | Código propio del proyecto |
| 2 | Estructura del modelo relacional | 10 | `03_postgresql_postgis/cargas/schema.sql` | Código propio del proyecto |
| 3 | Validación espacial de las celdas controladas | 15 | Consulta `SELECT celda_id, ST_SRID(geom), ST_IsValid(geom), ST_Area(geom) FROM dim_celda` | Consulta ejecutada sobre `fireforest` (PostgreSQL/PostGIS) |
| 4 | Detecciones controladas almacenadas en MongoDB | 16 | `consultas_mongodb.js` (`$match`/`$group`/`$max`/`$avg`) | Consulta ejecutada sobre `fireforest` (MongoDB) |
| 5 | Resultado de la integración mensual en PostgreSQL | 17 | `consulta_01_incendios_clima_mensual.sql`; prueba en transacción con `ROLLBACK` | Consulta ejecutada sobre `fireforest` (PostgreSQL) |

Ninguna tabla metodológica previa (estandarización espacial,
estandarización temporal, componentes del ETL) conserva numeración
propia: quedó reemplazada por un flujo en las diapositivas 12, 13 y
14, por lo que la numeración consecutiva de tablas pasa directamente
de la Tabla 2 (diapositiva 10) a la Tabla 3 (diapositiva 15), sin
saltos ni huecos.

**Evidencia ejecutada en sesiones de desarrollo (no recalculada a
mano):** PostgreSQL (`fireforest`, vía `psql`) y MongoDB (`fireforest`,
vía `mongosh`) estaban ambos accesibles localmente. Se ejecutaron
realmente: la validación espacial (`ST_SRID`, `ST_IsValid`, `ST_Area`
sobre `dim_celda`), la consulta completa
`consulta_01_incendios_clima_mensual.sql`, una prueba del caso crítico
(celda-mes con clima y sin detecciones) dentro de una transacción con
`ROLLBACK`, y las tres consultas de `consultas_mongodb.js`. Ningún
valor numérico de las diapositivas 15, 16 o 17 fue inventado o
recalculado manualmente; todos provienen de estas ejecuciones reales.

| Diapositiva | Afirmación o dato | Fuente | Tipo de fuente | Referencia completa | Verificada |
|---|---|---|---|---|---|
| 3 | Cantón Loja en los Andes tropicales del sur de Ecuador; relieve genera transiciones ambientales pronunciadas | Balaguer-Beser et al. (2026), *Background* y *Study area* | Primaria (artículo científico) | Balaguer-Beser, A., González, F., Chuncho, C. G., Carrión-Paladines, V., & Juela-Sivisaca, O. (2026). Altitudinal variation in fire behavior in Andean ecosystems in southern Ecuador. *Fire Ecology*, 22, Article 46. https://doi.org/10.1186/s42408-026-00470-y | Sí — PDF leído directamente |
| 3 | Gradiente altitudinal ~1549–2757 m s. n. m.; 3 zonas: Malacatos, Punzara, San Lucas | Balaguer-Beser et al. (2026), *Abstract* y *Study area* | Primaria | Ídem | Sí — cifras y rangos citados textualmente por zona en el artículo |
| 3 | Esquema conceptual de las 3 zonas alrededor del cantón Loja | Elaboración propia (diagrama TikZ, no reproduce la Fig. 1 del artículo) | Propia, basada en fuente primaria | — | Sí — diagrama propio |
| 3 | Captura de la publicación en Springer Nature Link (Fire Ecology, título, fecha de publicación, volumen y número de artículo, autores, indicación de acceso abierto) — función: contextualización territorial y ambiental del cantón Loja | Captura original proporcionada por el usuario; recorte/composición propia que conserva breadcrumb "Fire Ecology", título, línea "Research \| Open access \| Published", volumen/número de artículo, banner de acceso abierto y autores; elimina menú superior de Springer Nature Link, botones "Download PDF"/"Save article" y la fila de métricas (Accesses/Altmetric) | Captura propia de fuente primaria (artículo científico) | Balaguer-Beser, A., González, F., Chuncho, C. G., Carrión-Paladines, V., & Juela-Sivisaca, O. (2026). Altitudinal variation in fire behavior in Andean ecosystems in southern Ecuador. *Fire Ecology*, 22, Article 46. DOI: https://doi.org/10.1186/s42408-026-00470-y; `presentacion/captura3.png` (original, sin modificar); `presentacion/figuras/articulo_fire_ecology_recortado.png` (recorte usado en la diapositiva) | Sí — recorte verificado visualmente a alta resolución: título, fecha, volumen, autores y acceso abierto legibles; el DOI enlazado en la diapositiva coincide exactamente con el de la diapositiva 20 (referencia 1) |
| 3 | Distinción explícita: el artículo aporta el contexto territorial y ambiental de Malacatos, Punzara y San Lucas; no determina la ubicación de las dos celdas controladas del prototipo | Elaboración propia; verificación de que ninguna diapositiva ni el guion afirman correspondencia entre las celdas controladas y esas tres localidades | Verificación propia (ausencia de una afirmación) | — | Sí — ni la diapositiva 3 ni la 5, 15, 16 o 17 asignan las celdas LJ\_04521/LJ\_04522 a Malacatos, Punzara o San Lucas |
| 4 | Argumento heterogeneidad ambiental → datos heterogéneos → brecha de integración | Contexto ambiental: Balaguer-Beser et al. (2026). Formulación de la brecha de datos: elaboración propia del equipo | Mixta (primaria + propia, claramente distinguidas) | Balaguer-Beser et al. (2026) (ver fila anterior); brecha de datos sin referencia externa, es elaboración propia | Sí — el pie de la diapositiva cita únicamente "Balaguer-Beser et al. (2026) y elaboración propia"; `inventario_fuentes.md` es documentación interna de diseño y ya no se presenta como respaldo científico externo en el texto visible de la diapositiva |
| 5 | Pregunta principal, pregunta derivada, objetivo general, alcance del Avance 1 | `avance1_corregido.tex`, secciones 1.5 y 6 | Documento propio del proyecto | `01_avance_1/fuente/avance1_corregido.tex` | Sí |
| 5 | Delimitación territorial: dominio previsto = cantón Loja; cobertura actual = 2 celdas controladas | Elaboración propia, a partir de `datos_ejemplo.sql` (única malla cargada en el prototipo) | Propia | — | Sí — no existe malla cantonal completa ni límite institucional cargado en el repositorio |
| 6 | Diagrama de arquitectura general en seis etapas numeradas discretamente (1. fuentes originales → 2. adquisición e ingesta → 3. validación y transformación → 4. MongoDB / PostgreSQL-PostGIS, mediante dos flechas diagonales → 5. integración por `celda_id` y fecha, mediante dos flechas diagonales convergentes → 6. dataset celda-mes) | Elaboración propia, a partir del flujo real implementado en `03_postgresql_postgis/` y `04_mongodb/` | Propia | — | Sí — la divergencia y convergencia entre MongoDB y PostgreSQL/PostGIS se representa con flechas diagonales directas de punta Latex (línea 1,1 pt), sin línea horizontal ambigua; la numeración discreta y la separación entre cajas se verificaron visualmente a resolución de proyección |
| 6 | Método previsto de adquisición: API o descarga directa de NASA FIRMS y repositorio CHIRPS; sin uso de Google Earth Engine en este prototipo | Búsqueda en el repositorio ("earthengine", "ee.", "GEE": sin resultados) y en `avance1_corregido.tex`/`inventario_fuentes.md`, que describen API/descarga de FIRMS y descarga directa del repositorio CHIRPS, sin mencionar GEE | Verificación propia (ausencia de evidencia) | — | Sí — se usa "previsto", no "ejecutado": no hay evidencia de una descarga por API ya realizada; GEE no se menciona porque pertenece a otro proyecto y no está documentado en este repositorio |
| 7 | Captura de VS Code (árbol completo de `Proyecto_integrador` y fragmento de `cargar_postgres.py`) — evidencia propia de la implementación local | Captura original proporcionada por el usuario; recorte/composición propia que preserva el árbol completo de carpetas y el código, y elimina terminal vacía, ruta personal completa, menú superior, barra de estado y controles de interfaz irrelevantes | Captura propia del entorno de desarrollo local | `presentacion/captura.png` (original, sin modificar); `presentacion/figuras/captura_vscode_recortada.png` (composición usada en la diapositiva, columna izquierda) | Sí — recorte verificado visualmente a alta resolución: árbol y código legibles, sin ruta personal ni terminal |
| 7 | Captura de GitHub (repositorio remoto `cguillermo79/FireForest`, rama `main`, ruta `Tareas/Proyecto_integrador`, listado de módulos) — evidencia propia del repositorio remoto | Captura original proporcionada por el usuario; recorte propio que conserva el nombre del repositorio, la ruta, el listado de carpetas y el logotipo de GitHub | Captura propia del repositorio remoto (control de versiones) | `presentacion/captura2.png` (original, sin modificar); `presentacion/figuras/captura_github_recortada.png` (recorte usado en la diapositiva, columna derecha) | Sí — recorte verificado visualmente a alta resolución: nombre del repositorio, ruta y listado de carpetas legibles |
| 7 | Función de ambas capturas: documentar la organización del proyecto (entorno local) y el mecanismo de control de versiones (repositorio remoto); no se afirma que los tres integrantes estén enlazados o hayan contribuido | Captura de GitHub: un único commit visible ("Elimina capturas del Taller SQL Relacional", autor `cguillermo79`, 19 horas antes de la captura); no se verificó en Git el historial completo de autores/colaboradores para los tres integrantes | Verificación propia (evidencia parcial) | — | Sí — la captura demuestra la existencia del repositorio remoto y su commit más reciente, no la participación de los tres integrantes; el texto de la diapositiva no hace esa afirmación |
| 8 | Tabla fuente→variable original→transformación→variable final (VIIRS, CHIRPS, malla, calendario) | `03_postgresql_postgis/cargas/schema.sql`; `consultas/consulta_01_incendios_clima_mensual.sql`; `04_mongodb/cargas/detecciones_viirs.json` | Código propio del proyecto | Ídem | Sí — nombres de campo verificados contra el código real, no inventados |
| 8 | VIIRS: NASA FIRMS como distribuidor y método de acceso (API/descarga); CHIRPS v2.0, Climate Hazards Center (UCSB), descarga directa del repositorio, resolución nativa ~0.05° | NASA EOSDIS FIRMS; Climate Hazards Center (UCSB) | Primaria (institucional) | NASA EOSDIS FIRMS. *VIIRS 375 m Active Fire and Thermal Anomalies (VNP14IMG/VJ114IMG)*. https://firms.modaps.eosdis.nasa.gov ; Climate Hazards Center, UC Santa Barbara. *CHIRPS v2.0*. https://www.chc.ucsb.edu/data/chirps | Sí |
| 9 | Tres niveles de granularidad (detección, celda-día, celda-mes) y por qué no son equivalentes | `00_documentacion_inicial/diseno_sql_nosql.md`, sección "Unidad de análisis" | Documento propio del proyecto | Ídem | Sí |
| 10 | Tablas `dim_celda`, `dim_fecha`, `fact_incendio`, `fact_clima`: función, grano, clave | `03_postgresql_postgis/cargas/schema.sql` | Código propio del proyecto | Ídem | Sí — `fact_incendio` se describe como "detecciones diarias agregadas", no como "incendio", para no confundir la unidad VIIRS con incendios reales |
| 10 | Restricciones e integridad relacional (PK, FK, `UNIQUE`) | Documentación oficial de PostgreSQL | Primaria (institucional) | PostgreSQL Global Development Group. *PostgreSQL Documentation*. https://www.postgresql.org/docs/ | Sí |
| 11 | Estructura del documento `detecciones_viirs` (campos anidados `coordenadas`, `calidad`) | `04_mongodb/cargas/detecciones_viirs.json` (documento real, no ejemplo inventado) | Código/dato propio del proyecto | Ídem | Sí — documento reproducido tal cual, sin alterar campos |
| 11 | Vínculo lógico vía `celda_id`, sin FK física entre MongoDB y PostgreSQL; ventaja del modelo documental (esquema flexible) | `diseno_sql_nosql.md`, sección "Relaciones"; documentación oficial de MongoDB (modelo de documentos flexible) | Documento propio + primaria (institucional) | MongoDB, Inc. *MongoDB Manual*. https://www.mongodb.com/docs/ | Sí |
| 11 | El prototipo filtra mediante `calidad.valida=true` y conserva `fire_mask` como atributo (no como campo de filtro activo); producto VIIRS y criterio definitivo de calidad pendientes | `04_mongodb/consultas/consultas_mongodb.js` (filtro real: `{"calidad.valida": true}`, sin referencia a `fire_mask`); `04_mongodb/cargas/detecciones_viirs.json` (conserva `fire_mask` como campo del documento) | Código propio del proyecto | Ídem | Sí — contrastado línea por línea contra `consultas_mongodb.js` y `detecciones_viirs.json`; la redacción anterior ("el campo de calidad usado hoy es `fire_mask`") no coincidía con la consulta real y fue corregida |
| 12 | Flujo espacial en tres líneas paralelas (VIIRS, malla, CHIRPS), cada una con cuatro etapas hasta `celda_id`/`dim_celda.geom`; fórmulas de reproyección y área; procedimiento `ST_SetSRID` → `ST_Transform` → `ST_MakeEnvelope` | `03_postgresql_postgis/cargas/datos_ejemplo.sql` (comentarios y `UPDATE dim_celda`); documentación oficial de PostGIS | Código propio + primaria (institucional) | PostGIS Project Steering Committee. *PostGIS Documentation*. https://postgis.net/documentation/ | Sí — la tabla elemento→estado original→operación→resultado de la v5 se reemplazó por este flujo, sin tabla numerada en esta diapositiva |
| 13 | Diapositiva reorganizada en cuadrantes: ecuaciones (`N_{i,m}`, `FRP^{suma}_{i,m}`, `FRP^{max}_{i,m}`, `P_{i,m}`) arriba a la izquierda; definiciones de `i`, `d`, `m`, `N_{i,d}`, `FRP_{i,d}`, `FRP^{max}_{i,d}`, `P_{i,d}` arriba a la derecha; dos flujos horizontales paralelos (VIIRS, CHIRPS) abajo; resultado común "Dataset analítico celda-mes" al extremo derecho, con dos flechas independientes sin cruce; advertencia final reducida | `consulta_01_incendios_clima_mensual.sql` (lógica `SUM`/`MAX`/`GROUP BY`); `decisiones_metodologicas.md` §2 | Código y documento propios | Ídem | Sí — la convergencia se verificó visualmente sin cruces ni puntas ocultas; "ausencia de incendio" se mantiene reemplazada por "ausencia de detecciones"; la explicación detallada del LEFT JOIN se trasladó a la diapositiva 17 y al guion |
| 14 | Flujo ETL completo (entradas → carga en MongoDB/PostgreSQL → controles de calidad compartidos → transformación e integración → salidas); rol de cada script; carga PostgreSQL pendiente de mejorar idempotencia; orquestación Airflow en fase de validación, mostrada como franja discontinua separada del flujo ejecutado | Código real del repositorio (`08_airflow/dags/fireforest_prueba.py`, `fireforest_validar_viirs.py` confirmados en el repositorio; `schema.sql` confirmado sin `CREATE TABLE IF NOT EXISTS`) | Código propio del proyecto | Ídem | Sí — la tabla de componentes de la v5 se reemplazó por este flujo, sin tabla numerada en esta diapositiva; Airflow no se presenta como etapa ejecutada |
| 14 | Sintaxis `LEFT JOIN` / `COALESCE` usada en la consulta integrada | Documentación oficial de PostgreSQL | Primaria (institucional) | PostgreSQL Global Development Group. *PostgreSQL Documentation*. https://www.postgresql.org/docs/ | Sí |
| 15 | Flujo previo a la tabla (consulta PostGIS → validación de SRID, geometría y área → tabla de resultados → interpretación); Tabla 3 "Validación espacial de las celdas controladas": SRID 32717, geometría válida, área 250 000 m² para LJ_04521 y LJ_04522 | Consulta `SELECT celda_id, ST_SRID(geom), ST_IsValid(geom), ST_Area(geom) FROM dim_celda`; coordenadas de origen en `03_postgresql_postgis/cargas/datos_ejemplo.sql` (LJ_04521: -79.241, -4.082; LJ_04522: -79.236, -4.079) | Resultado propio (datos controlados) | Ejecutada sobre `fireforest` (PostgreSQL/PostGIS) | Sí — sin cartografía oficial de parroquias/cantón en el repositorio para validar la pertenencia territorial exacta de estas coordenadas; de ahí la etiqueta "sin representatividad cantonal" en vez de asignar un nombre territorial |
| 16 | Tabla 4 "Detecciones controladas almacenadas en MongoDB": FRP máxima 18,4 MW; FRP media 14,05 MW; 2 documentos, celdas LJ_04521/LJ_04522 | `consultas_mongodb.js`, secciones 1 y 2 (`$match`, `$group`, `$max`, `$avg`) | Resultado propio (datos controlados) | Ejecutada sobre `mongodb://localhost:27017/fireforest` | Sí — salida real de `mongosh`, no recalculada a mano |
| 17 | Tabla 5 "Resultado de la integración mensual en PostgreSQL": salida de `consulta_01_incendios_clima_mensual.sql` (2 celda-mes reales) y prueba del caso crítico (celda-mes sintética de septiembre, revertida), resaltada con fondo tenue (`Fuego!10`) y nota diferenciadora | Consulta ejecutada en vivo; prueba en transacción con `ROLLBACK` | Resultado propio (datos controlados) | Ejecutada sobre `fireforest` (PostgreSQL); verificado que no quedó fila persistida tras el `ROLLBACK` | Sí — la fila temporal no se presenta como resultado persistente de la base |
| 15–17 | Etiqueta uniforme "Datos controlados del prototipo; sin representatividad cantonal" | Elaboración propia, siguiendo la delimitación territorial ya declarada en la diapositiva 5 | Propia | — | Sí — sustituye los párrafos territoriales extensos que se repetían en cada diapositiva de resultados en la v3; el detalle completo permanece en la diapositiva 5 |
| 18 | Cuatro hallazgos interpretados (roles de MongoDB/PostgreSQL, reproyección, LEFT JOIN, alcance de las pruebas); consideración metodológica sobre resolución de CHIRPS; frase prudente sobre "coherencia funcional básica" (no "arquitectura viable") | Elaboración propia, interpretando los resultados de las diapositivas 15–17 y las propiedades documentadas de CHIRPS (~0.05°, sección de fuentes) | Propia | — | Sí — frase de coherencia funcional preservada tal como fue solicitada |
| 18 | Limitaciones (2 celdas/2 detecciones, fuente institucional pendiente, producto VIIRS pendiente, cobertura temporal VIIRS no implementada, orquestación Airflow en fase de validación, PostgreSQL pendiente de idempotencia) | `tareas_pendientes.md`, `decisiones_metodologicas.md` | Documentos propios | Ídem | Sí — sin expresiones de observación interna de sesión ("auditoría previa", "Docker inactivo", "en esta sesión", "tras la reorganización"); Airflow e idempotencia usan la redacción exacta solicitada |
| 19 | Conclusiones (diseño coherente en escenario controlado; aplicación al cantón Loja pendiente de malla, datos reales, cobertura y volumen) y próximos pasos (incluye `viirs_disponible`, malla completa, Airflow, análisis estadístico) | `avance1_corregido.tex` (secciones 7–8); `tareas_pendientes.md` | Documentos propios | Ídem | Sí — se eliminó la frase de cierre "No se presentan conclusiones ambientales sobre Loja..." por ser redundante con la conclusión 1, que ya delimita el alcance al escenario controlado |
| 20 | Las 6 referencias completas | Ver filas anteriores | — | — | Sí — cada una fue citada previamente en al menos una diapositiva |

## Notas de cumplimiento de las reglas de citación

- No se generalizan los hallazgos de las 3 zonas del estudio (Malacatos,
  Punzara, San Lucas) a todo el cantón Loja; la diapositiva 3 lo declara
  explícitamente en su pie de fuente.
- No se atribuye al artículo de Fire Ecology el diseño SQL–NoSQL del
  proyecto (diapositiva 4): el pie de la diapositiva cita únicamente
  "Balaguer-Beser et al. (2026) y elaboración propia". `inventario_fuentes.md`
  ya no se presenta como respaldo científico externo del problema en el
  texto visible de la diapositiva; se conserva solo como evidencia
  interna de diseño en la documentación del proyecto.
- No se afirma uso de Google Earth Engine (diapositivas 6 y 8): se
  buscó evidencia en todo el repositorio (código, informe,
  `inventario_fuentes.md`) y no se encontró ninguna mención ni script
  relacionado con GEE; el informe describe API/descarga directa de
  NASA FIRMS y descarga directa del repositorio del Climate Hazards
  Center. GEE pertenece a otro proyecto y no está documentado aquí.
- No se afirma que la adquisición mediante API ya fue ejecutada
  (diapositiva 6): la redacción usa "método previsto de adquisición" y
  aclara explícitamente que el prototipo actual utiliza datos
  controlados cargados desde archivos locales.
- Las capturas de VS Code y GitHub (diapositiva 7, independiente de la
  arquitectura en la diapositiva 6) son evidencia de implementación
  local y de control de versiones remoto, no una representación de la
  arquitectura. El recorte de VS Code excluye la terminal vacía, la
  ruta personal completa, el menú superior, la barra de estado y los
  controles de interfaz irrelevantes; conserva el árbol completo de
  `Proyecto_integrador` y el fragmento legible de `cargar_postgres.py`.
  El recorte de GitHub conserva el nombre del repositorio, la ruta
  `Tareas/Proyecto_integrador`, el listado de carpetas y el logotipo
  de GitHub. Ambas imágenes se muestran en columnas de tamaño
  equivalente, sin superponerse.
- La captura de GitHub demuestra la existencia del repositorio remoto
  FireForest y su commit más reciente (autor `cguillermo79`); no se
  afirma que los tres integrantes estén enlazados como colaboradores o
  hayan contribuido con commits propios, porque esa evidencia
  específica no fue verificada en el historial de Git durante esta
  revisión. El texto de la diapositiva y del guion describe el
  repositorio como mecanismo de centralización y control de versiones
  del trabajo del grupo, sin afirmar la participación individual de
  cada integrante.
- El campo de calidad del modelo documental (diapositiva 11) se
  corrigió: la consulta real filtra por `calidad.valida=true`;
  `fire_mask` se conserva como atributo de la detección, pero no es el
  campo que filtra la consulta actual. Verificado contra
  `consultas_mongodb.js` y `detecciones_viirs.json`.
- "Ausencia de incendio" se reemplazó por "ausencia de detecciones"
  (diapositiva 13) para no confundir la observación VIIRS (una
  detección) con el fenómeno real (un incendio).
- La delimitación territorial (dominio previsto: cantón Loja;
  cobertura real: dos celdas controladas, sin representatividad
  territorial) se explica en detalle en la diapositiva 5 y se repite
  como una etiqueta breve y uniforme en las diapositivas 15, 16 y 17,
  sin repetir párrafos extensos. No se asignó a las celdas ninguna
  pertenencia parroquial (Malacatos, Punzara, San Lucas) ni urbana: no
  existe en el repositorio una capa de límite institucional o
  parroquial validada contra la cual intersectar sus coordenadas.
- Se retiraron de las diapositivas las expresiones de observación
  interna de sesión ("Docker inactivo en la auditoría previa", "en
  esta sesión", "tras la reorganización", detalle de nombres y estado
  de cada DAG de Airflow, mención textual de que `schema.sql` "no usa
  CREATE TABLE IF NOT EXISTS"); el hallazgo de fondo (idempotencia
  pendiente, orquestación en validación) se conserva en lenguaje apto
  para exposición, con la redacción exacta solicitada, en las
  diapositivas 14 y 18. El detalle técnico completo permanece en
  `tareas_pendientes.md`.
- Se eliminó la frase de cierre "No se presentan conclusiones
  ambientales sobre Loja: todavía no existen resultados reales
  suficientes" (diapositiva 19, antes 18) por ser redundante: la
  conclusión 1 ya delimita el alcance del prototipo a un escenario
  controlado.
- El esquema de la diapositiva 3 es una elaboración propia (no una
  reproducción de la Figura 1 del artículo), citada como "elaboración
  propia con base en Balaguer-Beser et al. (2026)".
- "Elaboración propia" se usa únicamente para diagramas, cálculos y
  resultados propios; nunca para respaldar una afirmación tomada de la
  literatura (diapositivas 3 y 4 citan a Balaguer-Beser et al.
  directamente para ese fin).
- Ninguna cita, autor o DOI fue inventado: los 6 registros de la
  diapositiva 20 corresponden exactamente a los ya verificados.
- Todas las cifras del prototipo (18,4 MW, 14,05 MW, 250 000 m²,
  EPSG:32717, la fila sintética de septiembre) están marcadas como
  "datos controlados del prototipo" y provienen de ejecuciones reales
  contra las bases `fireforest` (PostgreSQL y MongoDB), no de cálculos
  manuales.
- No se afirma "arquitectura viable" en sentido operacional; se usa la
  redacción prudente solicitada ("coherencia funcional básica...; su
  viabilidad operativa deberá evaluarse con datos reales, mayor volumen
  y automatización") en las diapositivas 18 y 19.
- `viirs_disponible` aparece únicamente como actividad futura pendiente
  (diapositiva 19, "Próximos pasos"), nunca como campo ya implementado.
- Todos los diagramas de flujo de la presentación comparten un único
  estilo de flecha (`flowarr`: punta Latex, ~1 pt de grosor, mismo
  color VerdeOscuro), definido una sola vez en el preámbulo de
  `main.tex` y reutilizado en las diapositivas 3, 4, 6, 9, 12, 13, 14 y
  15; no existen flechas decorativas sin una transformación o
  transferencia de datos asociada.
- Las cinco tablas numeradas (Tabla 1 a Tabla 5) llevan título en el
  mismo formato ("Tabla N. Título descriptivo"), alineado a la
  izquierda y en tamaño `\small` (mayor que las notas de fuente en
  `\tiny`); cada una lleva su línea de fuente debajo. La numeración es
  consecutiva y sin saltos: al eliminarse las tablas metodológicas de
  las diapositivas 12, 13 y 14 (reemplazadas por flujos), la Tabla 3
  pasó a ser la de la diapositiva 15, no la de la 12.
- El pie de página de las 20 diapositivas identifica la sección activa
  en negrita, sustituyendo "Proyecto Integrador" por el nombre de la
  sección: diapositivas 1–2 "Presentación"; 3–5 "I. Introducción"; 6–14
  "II. Metodología"; 15–17 "III. Resultados preliminares"; 18 "IV.
  Discusión preliminar"; 19 "V. Conclusiones"; 20 "Referencias". El
  cambio se implementa con un macro (`\seccionactual`) redefinido antes
  de cada bloque, sin alterar la altura del pie ni añadir diapositivas
  separadoras; verificado que "II. Metodología" aparece exactamente
  desde la diapositiva 6.
- La captura del artículo de Fire Ecology (diapositiva 3) conserva
  únicamente el nombre de la revista, el título, la fecha de
  publicación, el volumen y número de artículo, los autores y la
  indicación de acceso abierto; excluye el menú superior de Springer
  Nature Link, los botones "Download PDF"/"Save article" y la fila de
  métricas (Accesses/Altmetric). No se afirma ni se sugiere en ningún
  texto de la diapositiva o del guion que las dos celdas controladas
  del prototipo correspondan a Malacatos, Punzara o San Lucas: el
  artículo se presenta explícitamente como contexto bibliográfico, no
  como fuente de la ubicación del prototipo.
