# Guion de exposición — Avance 1, Proyecto Integrador FireForest (v8, 21 diapositivas)

**Duración total programada: 30,0 minutos**, dentro del rango de
aproximadamente 30 minutos solicitado. La diapositiva 21 (referencias)
no tiene tiempo de exposición asignado.

| Expositor | Bloque | Diapositivas | Tiempo |
|---|---|---|---|
| Marco Vinicio Malan Mullo | I. Introducción (incluye ámbito territorial) + arquitectura e implementación | 1–8 | 8,9 min |
| Viviana Isabel Pujos Culque | II. Metodología | 9–15 | 11,0 min |
| Carlos Guillermo Chuncho Morocho | III. Resultados + IV. Discusión + V. Conclusiones | 16–20 | 10,1 min |
| (sin exponer) | Referencias | 21 | — |

**Cambios de esta versión (v8, 2026-09-15):** se incorporó la
diapositiva 6, "Ámbito territorial y localización de las celdas del
prototipo" (0,75 min), entre la pregunta/objetivo/alcance (5) y el
inicio de la Metodología (antes diapositiva 6, ahora 7). Todas las
diapositivas 6–20 anteriores se renumeraron a 7–21. Para mantener el
total en 30,0 minutos sin alargar la exposición, se recortaron 0,75 min
repartidos entre cuatro diapositivas que tenían margen: la 5 (2,5→2,25
min), la 8 (0,75→0,65 min), la 17 (2,0→1,85 min) y la 18 (2,5→2,25
min). El resto de duraciones no cambia.

La nueva diapositiva documenta que una verificación territorial
posterior determinó que las celdas controladas originales del
prototipo (`LJ_04521`, `LJ_04522`) estaban **fuera** del cantón Loja
(dentro del cantón Catamayo, parroquia El Tambo). Se sustituyeron, en
todo el contenido vigente de la presentación y de este guion, por
`LJ_TEST_001` y `LJ_TEST_002` (identificadores de prueba, verificados
dentro del cantón Loja, parroquia El Cisne). El hallazgo sobre las
celdas anteriores **no se borra**: permanece documentado como
evidencia de control de calidad en
`03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`;
no debe mencionarse en la exposición oral salvo que el jurado pregunte
explícitamente por el proceso de verificación (ver preguntas
probables).

Historial anterior (v7, 2026-09-14): la diapositiva 3 incorporó la
captura real del artículo de Fire Ecology; la diapositiva 6 (ahora 7)
ganó numeración discreta de sus seis etapas; la diapositiva 13 (ahora
14) se reorganizó en cuadrantes; el pie de página mostró la sección
activa en negrita. (v6 y anteriores: ver versiones previas de este
documento en el historial de control de versiones.)

---

## 1 — Portada
**Expositor:** Marco Vinicio Malan Mullo · **Duración:** 0,5 min

**Mensaje central:** presentar al equipo y el proyecto sin adelantar resultados.

**Explicación oral:** Buenos días/tardes. Somos el Grupo 4 de la Maestría en Estadística con mención en Ciencia de Datos e Inteligencia Artificial de la ESPOCH: Marco Malan, Viviana Pujos y Carlos Chuncho. Presentamos el Avance 1 de nuestro Proyecto Integrador, "Diseño de una arquitectura híbrida SQL-NoSQL para la integración y consulta de datos de incendios forestales en el cantón Loja". Es un avance de diseño e implementación inicial, no un sistema terminado ni un análisis definitivo de los incendios de Loja.

**Transición:** Veamos la ruta que seguirá la exposición.

**Advertencias:** Ninguna afirmación de resultados en esta diapositiva.

---

## 2 — Ruta de la exposición
**Expositor:** Marco Vinicio Malan Mullo · **Duración:** 0,5 min

**Mensaje central:** la exposición sigue cinco bloques, con el problema integrado dentro de la introducción.

**Explicación oral:** La presentación tiene cinco bloques: Introducción, que incluye el contexto ambiental, el problema y la brecha de datos, la pregunta, el objetivo, el alcance, el ámbito territorial y la arquitectura del sistema; Metodología, el bloque más extenso, donde explicamos el diseño completo; Resultados preliminares, con evidencia real del prototipo; Discusión preliminar; y Conclusiones y próximos pasos.

**Transición:** Empecemos por el bloque de introducción.

---

## 3 — Introducción: contexto territorial y ambiental
**Expositor:** Marco Vinicio Malan Mullo · **Duración:** 1,5 min

**Mensaje central:** la variabilidad altitudinal de Loja reorganiza las condiciones ambientales que controlan el fuego, y ese contexto proviene de un artículo publicado y verificable, no de una afirmación sin respaldo.

**Explicación oral:** El cantón Loja está en los Andes tropicales del sur de Ecuador, con un relieve montañoso que genera transiciones ambientales marcadas en distancias cortas: temperatura, precipitación, humedad, vegetación y combustibles cambian con la altitud. Esto se apoya en el estudio de Balaguer-Beser y colegas, publicado en 2026 en la revista Fire Ecology, que examinó el comportamiento del fuego en tres zonas contrastantes de Loja —Malacatos, Punzara y San Lucas— a lo largo de un gradiente altitudinal de aproximadamente 1549 a 2757 metros sobre el nivel del mar. El esquema que ven a la derecha es una elaboración propia para ilustrar esas tres zonas; no es la figura original del artículo. Abajo les muestro la captura real de la publicación en Springer Nature Link: el artículo "Altitudinal variation in fire behavior in Andean ecosystems in southern Ecuador", en la revista Fire Ecology, volumen 22, artículo 46, publicado el 23 de marzo de 2026 en acceso abierto, firmado por Balaguer-Beser y colegas. El DOI que ven es un enlace real: 10.1186/s42408-026-00470-y. Esta captura respalda visualmente que el contexto territorial que acabo de describir proviene de una fuente verificable, no de una afirmación sin sustento. Una precisión importante: este artículo aporta el contexto ambiental y altitudinal del cantón; no determina ni describe la ubicación de las dos celdas controladas de nuestro prototipo, que verán más adelante, en la diapositiva de ámbito territorial.

**Transición:** Esta heterogeneidad ambiental es exactamente el punto de partida de nuestro problema.

**Advertencias sobre interpretaciones incorrectas:** Estos hallazgos corresponden a tres zonas de estudio específicas, no deben generalizarse a todo el territorio del cantón Loja; la propia diapositiva lo aclara en su pie de fuente. No sugerir, en ningún momento, que las dos celdas controladas del prototipo corresponden a Malacatos, Punzara o San Lucas: el artículo aporta contexto, no ubicación.

**Pronunciación:** "s. n. m." se lee "sobre el nivel del mar". El DOI se lee dígito por dígito o simplemente "DOI uno uno ocho seis, S cuatro dos cuatro cero ocho, cero dos seis, cero cero cuatro siete cero, guion Y".

---

## 4 — Introducción: problema y brecha
**Expositor:** Marco Vinicio Malan Mullo · **Duración:** 1,75 min

**Mensaje central:** el problema ambiental y el problema de Ingeniería de Datos son distintos, y esta diapositiva los conecta en una sola secuencia argumental.

**Explicación oral:** Léanlo conmigo: la heterogeneidad territorial y ambiental de Loja condiciona el análisis del comportamiento del fuego. Para estudiarla deben integrarse observaciones espaciales, climáticas y satelitales que difieren en formato, resolución y granularidad. La carencia de un flujo integrado, trazable y reproducible constituye la brecha de Ingeniería de Datos que aborda FireForest. El diagrama de abajo resume esa cadena: heterogeneidad ambiental lleva a datos heterogéneos, que generan dificultad de integración, que se traduce en una brecha reproducible. El contexto ambiental está respaldado por Balaguer-Beser et al.; la formulación de la brecha de datos es elaboración propia de este equipo.

**Transición:** Frente a esta brecha, formulamos una pregunta, un objetivo y un alcance concretos para este primer avance.

**Advertencias:** No atribuir al artículo de Fire Ecology el diseño SQL-NoSQL de FireForest; ese diseño es elaboración propia del equipo. El inventario interno de datos del proyecto no se presenta como fuente científica del problema; el pie de la diapositiva solo cita a Balaguer-Beser et al. (2026) y la elaboración propia del equipo.

---

## 5 — Pregunta, objetivo y alcance
**Expositor:** Marco Vinicio Malan Mullo · **Duración:** 2,25 min

**Mensaje central:** hay una pregunta de arquitectura (la de este avance) y una pregunta analítica futura; el objetivo y el alcance delimitan honestamente qué se hizo y qué no.

**Explicación oral:** Formulamos dos preguntas de naturaleza distinta. La principal, que sí respondemos en este Avance 1, es de arquitectura: ¿cómo diseñar una arquitectura híbrida SQL-NoSQL que permita integrar, almacenar y consultar de forma reproducible datos heterogéneos de incendios forestales en Loja? Nuestro objetivo general es diseñar esa arquitectura híbrida para integrar VIIRS, CHIRPS y una malla espacial de Loja, construyendo un dataset analítico reproducible por celda y mes. La pregunta derivada, que solo podremos responder con datos reales en etapas posteriores, es: ¿existe relación entre la precipitación mensual y la ocurrencia de detecciones de incendio por celda? Decimos "detecciones", no "incendios": VIIRS identifica detecciones de calor, no un conteo directo de incendios independientes. El alcance: este avance sí incluye la arquitectura híbrida, los modelos SQL y NoSQL, datos controlados y validaciones preliminares; todavía no incluye un sistema operativo, alerta temprana, datos reales completos, modelo predictivo ni relación causal. Y quiero subrayar una delimitación que van a ver ampliada con un mapa en la siguiente diapositiva: el dominio previsto de este proyecto es el cantón Loja completo, pero la cobertura actual del prototipo son únicamente dos celdas controladas, verificadas dentro del cantón, usadas solo para validar el flujo de datos; no representan el territorio cantonal.

**Transición:** Antes de entrar al detalle metodológico, veamos exactamente dónde se ubican esas dos celdas dentro del cantón.

**Advertencias:** Ninguna; esta diapositiva es la que previene sobre-interpretaciones en el resto de la charla.

**Pronunciación:** "VIIRS" se pronuncia /virs/, como en la comunidad científica.

---

## 6 — Ámbito territorial y localización de las celdas del prototipo
**Expositor:** Marco Vinicio Malan Mullo · **Duración:** 0,75 min

**Mensaje central:** el dominio del proyecto es el cantón Loja; las dos celdas de prueba están verificadas espacialmente dentro de su límite oficial, en la parroquia El Cisne, y no representan la diversidad del cantón.

**Qué aparece en la diapositiva:** un mapa reproducible (no una captura de terceros ni una imagen decorativa) con el límite del cantón Loja, los límites de sus 14 parroquias, el cantón Catamayo como contexto, la ubicación de `LJ_TEST_001` y `LJ_TEST_002`, un recuadro ampliado con los dos polígonos de 500×500 m, norte, escala, leyenda, EPSG y la fuente institucional; a la derecha, la Tabla 1 con longitud, latitud, parroquia y distancia al límite de cada celda.

**Explicación oral:** El dominio territorial previsto para FireForest es el cantón Loja completo. Para validar el prototipo usamos dos celdas controladas de 500 por 500 metros, y antes de mostrarles cualquier resultado quisimos verificar dónde caen exactamente. Este mapa se generó de forma reproducible a partir de la capa oficial del INEC, el Marco Geoestadístico Nacional, y de las mismas geometrías que usa nuestra base de datos: no es una captura de Google Maps ni una imagen decorativa. El polígono verde es el límite del cantón Loja, reconstruido a partir de esa capa oficial; las líneas finas son sus catorce parroquias; el contorno punteado a la izquierda es el cantón vecino, Catamayo, que dejamos como referencia de contexto. Las dos celdas, `LJ_TEST_001` y `LJ_TEST_002`, están marcadas cerca del borde noroccidental del cantón; el recuadro de la derecha las amplía para que se distingan sus dos polígonos de 500 por 500 metros. Ambas celdas caen dentro de la parroquia El Cisne, con un margen de más de un kilómetro respecto al límite cantonal —eso es lo que muestra la Tabla 1—. No las elegimos a simple vista: se seleccionaron de una malla sistemática de 500 metros, ancladas a coordenadas exactas, ordenando las celdas candidatas por su coordenada este y luego por la norte, y tomando las dos primeras que cumplían estar completamente dentro del cantón con ese margen de seguridad. Por eso puedo afirmar que no son "cualquier celda": tienen coordenadas y geometría determinadas y verificadas. Dicho esto, siguen siendo solo dos ubicaciones dentro de una sola parroquia: no fueron elegidas para representar la diversidad ambiental, altitudinal o climática del cantón, y sus resultados —que verá Carlos más adelante— validan el funcionamiento técnico del prototipo, no el comportamiento ambiental de Loja.

**Cómo explicar los elementos visuales:** señalar primero el contorno verde completo del cantón, después las líneas parroquiales, después el contorno punteado de Catamayo como contexto; señalar la ubicación aproximada de las celdas en el mapa general y de inmediato dirigir la atención al recuadro ampliado, donde sí se distinguen los dos polígonos; cerrar señalando la fila de la Tabla 1 con la distancia al límite.

**Transición:** Con el ámbito territorial verificado, entremos ya al detalle metodológico: primero, la arquitectura general del sistema.

**Advertencias:** No mencionar en esta diapositiva que existieron celdas anteriores fuera del cantón; esa es información de control de calidad interno, no material de exposición, y solo se menciona si el jurado pregunta directamente (ver preguntas probables). No describir el cantón Catamayo con detalle: se muestra únicamente como referencia visual de contexto. No afirmar que estas dos celdas permiten conclusiones ambientales sobre el cantón.

**Pronunciación:** "INEC" se pronuncia como una palabra, "íˈnek", tal como se dice habitualmente en Ecuador.

---

## 7 — Arquitectura general del sistema
**Expositor:** Marco Vinicio Malan Mullo · **Duración:** 1,0 min

**Inicio del bloque II. Metodología.** Esta diapositiva abre explícitamente el segundo bloque de la exposición; el pie de página cambia de "Presentación"/"I. Introducción" a "II. Metodología" a partir de aquí.

**Mensaje central:** un único flujo, de arriba hacia abajo y numerado en seis etapas, conecta las fuentes originales con el producto analítico final, mostrando dónde se separan y dónde vuelven a unirse MongoDB y PostgreSQL/PostGIS.

**Qué entra:** las fuentes originales — NASA FIRMS (VIIRS), el Climate Hazards Center (CHIRPS) y el límite institucional del INEC, ya usado para verificar las celdas de prueba, aunque la malla completa de producción para todo el cantón todavía está pendiente.

**Qué transformación ocurre:** las fuentes pasan por adquisición e ingesta (API o descarga directa, lectura de archivos, validación inicial) y luego por validación y transformación (estructura, fechas, coordenadas, calidad, duplicados). En ese punto el flujo se separa en dos ramas paralelas: una hacia MongoDB, que conserva las detecciones individuales y sus metadatos, y otra hacia PostgreSQL/PostGIS, que organiza celdas, calendario, clima y agregados diarios. Ambas ramas vuelven a unirse en la integración, que cruza la información por `celda_id` y fecha.

**Qué sale:** el dataset analítico celda-mes, el producto final de la arquitectura.

**Por qué es necesaria esta separación:** MongoDB y PostgreSQL cumplen funciones distintas —una conserva el detalle documental, la otra impone integridad relacional y capacidad espacial— y solo se integran en un paso explícito y controlado, no de forma automática ni ambigua.

**Explicación oral:** Con esta diapositiva iniciamos el bloque de Metodología. El diagrama resume la arquitectura completa, de arriba hacia abajo, en seis etapas numeradas junto a cada bloque. Uno, partimos de las fuentes originales: NASA FIRMS para VIIRS, el Climate Hazards Center para CHIRPS, y el límite institucional del INEC que acaban de ver en el mapa anterior, usado hasta ahora para verificación, con la malla completa de producción para todo el cantón todavía pendiente. Dos, la adquisición e ingesta. Tres, la validación y transformación. Ahí el flujo se separa visiblemente en dos flechas diagonales, sin ninguna línea horizontal entre ellas: una hacia MongoDB, que guarda detecciones individuales y metadatos; otra hacia PostgreSQL con PostGIS, que organiza celdas, calendario, clima y agregados diarios —esa es la etapa cuatro, almacenamiento—. Ambas ramas convergen, también mediante dos flechas diagonales independientes que llegan a puntos distintos del bloque, en la etapa cinco, la integración por `celda_id` y fecha. Y la etapa seis es el producto: el dataset analítico celda-mes. Debajo del diagrama aclaramos el método previsto de adquisición: API o descarga directa de NASA FIRMS y del repositorio CHIRPS. Quiero ser preciso: no decimos que esa adquisición ya se ejecutó, porque no existe esa evidencia en FireForest; el prototipo actual utiliza datos controlados cargados desde archivos locales. Y no mencionamos Google Earth Engine porque su uso pertenece a otro proyecto y no está documentado en este repositorio.

**Transición:** Con esta arquitectura general clara, les muestro brevemente cómo luce implementada en nuestro entorno de desarrollo.

**Advertencias:** No afirmar que la adquisición por API ya fue ejecutada; es el método previsto, todavía no realizado. No mencionar Google Earth Engine. No afirmar que la malla completa del cantón ya está generada: el INEC se usó para verificar dos celdas, no para producir la malla operativa completa.

---

## 8 — Implementación local y colaboración mediante GitHub
**Expositor:** Marco Vinicio Malan Mullo · **Duración:** 0,65 min

**Mensaje central:** el prototipo no es solo un diagrama: existe código real, desarrollado localmente y versionado en un repositorio remoto.

**Explicación oral:** FireForest se desarrolla localmente en VS Code mediante una estructura modular que separa las diferentes etapas del proyecto. A la izquierda ven el árbol completo del repositorio `Proyecto_integrador` junto con un fragmento legible de `cargar_postgres.py`. A la derecha, el repositorio remoto FireForest en GitHub, con la misma ruta `Tareas/Proyecto_integrador`. El repositorio remoto centraliza el código y la documentación, facilita el intercambio de avances entre los integrantes y mantiene el historial de versiones. Ambas capturas son evidencia de implementación y organización del proyecto; no sustituyen al diagrama de arquitectura que acaban de ver.

**Transición:** Con la arquitectura, su implementación y su control de versiones mostrados, le cedo la palabra a Viviana, quien detallará cada componente de la metodología, empezando por las fuentes y variables.

**Advertencias:** No presentar estas capturas como si fueran la arquitectura; son evidencia complementaria de código, organización del repositorio y control de versiones. No decir que GitHub ejecuta el proyecto.

---

## 9 — Fuentes y variables
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 1,5 min

**Mensaje central:** cada fuente aporta una variable con una unidad, resolución y transformación específicas hacia una variable final concreta del esquema.

**Explicación oral:** Gracias, Marco. Antes de la tabla, una precisión sobre el origen de los datos: VIIRS lo distribuye NASA FIRMS, accesible mediante su API o descarga directa por área y periodo; CHIRPS se descarga directamente del repositorio del Climate Hazards Center. Ninguna de las dos pasa por Google Earth Engine en esta arquitectura. Ahora sí, la Tabla 2, "Fuentes, variables y transformaciones del proyecto", muestra exactamente qué medimos, con qué unidad, con qué resolución y cómo se transforma cada variable, usando los nombres reales de nuestro esquema. VIIRS aporta `frp_mw` por detección, que agregamos diaria y mensualmente hacia `frp_suma_mw` y `frp_maxima_mw`; sus coordenadas se asignan espacialmente a un `celda_id`. CHIRPS aporta precipitación diaria en píxeles de unos 5 kilómetros, que agregamos mensualmente. La malla parte de longitud y latitud en grados y se transforma, mediante `ST_SetSRID`, `ST_Transform` y `ST_MakeEnvelope`, en la geometría `geom` en metros. El calendario deriva año y mes de cada fecha. Tres aclaraciones adicionales: la malla actual son dos celdas controladas, ya verificadas con la capa del INEC como vimos en la diapositiva anterior, aunque la malla completa de producción sigue pendiente; el producto VIIRS exacto también está pendiente; y CHIRPS, al asignarse a la malla de 500 metros, no mejora su resolución real.

**Transición:** Con las fuentes claras, veamos por qué la unidad de análisis final —celda-mes— no es lo mismo que una detección individual.

**Pronunciación:** "FRP" se lee letra por letra: efe-erre-pe.

---

## 10 — Unidad de análisis y granularidad
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 1,5 min

**Mensaje central:** existen tres niveles de granularidad y no son equivalentes entre sí.

**Explicación oral:** El primer nivel es la detección individual, que MongoDB conserva con celda y fecha exactas, incluida la hora. El segundo es la celda-día: `fact_incendio` y `fact_clima`, en PostgreSQL, agregan esas detecciones a un registro diario por celda, con la restricción `UNIQUE(celda_id, fecha_id)`. El tercero es la celda-mes, el dataset analítico, obtenido agregando esos registros diarios con `GROUP BY` año y mes. No son equivalentes: al agregar por día se pierde el detalle de cuántas detecciones hubo y a qué hora exacta; nunca existe en las tablas base una fila pre-agregada por mes; y el agregado mensual puede ocultar variación diaria real.

**Transición:** Con esta distinción clara, veamos cómo se organiza el lado relacional del sistema.

---

## 11 — Modelo relacional
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 1,5 min

**Mensaje central:** cuatro tablas relacionales, cada una con una función y una clave bien definidas.

**Explicación oral:** La Tabla 3, "Estructura del modelo relacional", resume las cuatro tablas. `dim_celda` es el catálogo espacial: cada fila es una celda controlada de 500 por 500 metros, con `celda_id` como clave primaria. `dim_fecha` es el calendario: cada fila es un día. `fact_incendio` almacena las detecciones diarias agregadas: cada fila es una celda en un día, con clave única `celda_id` más `fecha_id`, y claves foráneas hacia ambas dimensiones. `fact_clima` tiene la misma estructura para la precipitación diaria. Un punto importante: `fact_incendio` y `fact_clima` no tienen clave foránea entre sí; se cruzan mediante `JOIN` cuando se necesita comparar detecciones y clima.

**Transición:** Ese es el lado relacional. Veamos ahora cómo se estructura el lado documental, en MongoDB.

---

## 12 — Modelo documental
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 1,5 min

**Mensaje central:** MongoDB conserva la detección VIIRS con su estructura anidada original, vinculada lógicamente —no físicamente— a la malla.

**Explicación oral:** Este es un documento real de nuestra colección `detecciones_viirs`, ya actualizado con las celdas verificadas: tiene un identificador de detección, la celda `LJ_TEST_001`, la fecha, la potencia radiativa `frp_mw`, el campo `fire_mask`, y dos objetos anidados: `coordenadas`, con longitud y latitud, y `calidad`, con el indicador `valida`. Estos objetos anidados pueden ganar o perder campos entre versiones del producto VIIRS sin romper el esquema, que es justamente la ventaja de un modelo documental. El vínculo con `celda_id` es lógico, no una clave foránea física: MongoDB no referencia tablas de PostgreSQL. Sobre el campo de calidad, quiero ser preciso: el prototipo filtra los documentos mediante `calidad.valida=true`, tal como lo hace `consultas_mongodb.js`; el campo `fire_mask` se conserva en el documento como atributo de la detección, pero la consulta actual no filtra directamente por él. El producto VIIRS definitivo y el criterio definitivo de calidad deberán confirmarse antes de utilizar datos reales.

**Transición:** Con ambos modelos definidos, veamos cómo estandarizamos el espacio para que convivan.

---

## 13 — Estandarización espacial
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 2,0 min

**Mensaje central:** tres fuentes con formatos y resoluciones distintas —VIIRS, la malla y CHIRPS— convergen en una sola referencia espacial común: la celda.

**Explicación oral:** Para construir cada celda partimos de longitud y latitud en grados, en el sistema EPSG 4326, y las transformamos al sistema EPSG 32717, en metros, apropiado para Ecuador continental. Sobre ese punto ya en metros construimos un cuadrado de 500 por 500 metros centrado en él, cuya área es exactamente 250 mil metros cuadrados. En código, esto son tres funciones encadenadas: `ST_SetSRID` fija el sistema de referencia original, `ST_Transform` reproyecta, y `ST_MakeEnvelope` construye el rectángulo final. Este es exactamente el mismo procedimiento que usamos para verificar y construir las dos celdas de prueba que vieron en el mapa territorial. Debajo, tres líneas paralelas muestran el mismo proceso por fuente: VIIRS pasa de un punto en EPSG 4326 a una reproyección, una asignación espacial y finalmente un `celda_id`; la malla pasa de su centro o límite a EPSG 32717, a la construcción del polígono de 500 por 500 metros, y a `dim_celda.geom`; CHIRPS pasa de un píxel de unos 0,05 grados a una superposición espacial, una asignación a celdas, y a la precipitación por celda. La idea central: la estandarización espacial lleva detecciones, celdas y precipitación a una referencia común basada en `celda_id`. Una aclaración importante: la asignación de CHIRPS a celdas de 500 metros no aumenta su resolución espacial real; varias celdas vecinas terminan compartiendo el mismo valor de precipitación.

**Transición:** Resuelto el espacio, veamos cómo estandarizamos el tiempo.

**Pronunciación:** "EPSG" se lee letra por letra: e-pe-ese-je.

---

## 14 — Estandarización temporal
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 1,5 min

**Mensaje central:** VIIRS y CHIRPS siguen dos flujos horizontales paralelos hasta una granularidad diaria común, y de ahí convergen —sin cruzarse— en un único bloque de resultado a la derecha.

**Definición oral de las ecuaciones:** N de i,m es la suma, para todos los días d del mes m, del número de detecciones N de i,d en la celda i. FRP suma de i,m es la suma de la potencia radiativa FRP de i,d de cada día. FRP máxima de i,m es el máximo de los máximos diarios FRP máximo de i,d. Y P de i,m es la suma de la precipitación diaria P de i,d.

**Explicación oral:** Arriba a la izquierda están las cuatro fórmulas que acabo de definir; arriba a la derecha, la definición de cada símbolo. Abajo, dos filas horizontales paralelas muestran el mismo proceso por fuente, sin que ninguna flecha cruce a la otra fila. La fila VIIRS pasa de la detección individual, con fecha y hora, a una agrupación por celda y día, a `fact_incendio` celda-día, a una agregación mensual, y finalmente a "Detecciones y FRP". La fila CHIRPS pasa de la precipitación píxel-día, a una asignación por celda, a `fact_clima` celda-día, a una suma mensual, y finalmente a "Precipitación acumulada". A la derecha, un único bloque naranja, "Dataset analítico celda-mes", recibe dos flechas independientes, sin cruzarse. En una frase: VIIRS y CHIRPS se transforman a una granularidad común celda-día y posteriormente se agregan por celda y mes. La advertencia final, breve: un valor cero representa ausencia de detecciones únicamente cuando se verificó la cobertura VIIRS; NULL identifica información faltante o no procesada. El detalle de por qué el LEFT JOIN por sí solo no demuestra esa cobertura lo retomo en la diapositiva del resultado de integración SQL.

**Transición:** Con el espacio y el tiempo estandarizados, veamos el proceso completo de integración y control de calidad.

**Pronunciación:** "LEFT JOIN" se pronuncia en inglés, "left yoin".

---

## 15 — ETL y control de calidad
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 1,5 min

**Mensaje central:** el flujo completo va de los archivos de entrada al dataset celda-mes, pasando por una carga en dos motores, un control de calidad único y compartido, y una integración final.

**Explicación oral:** Primero ingresan los archivos: el JSON de detecciones VIIRS y el SQL de esquema y datos controlados. Después, los scripts cargan los datos: `cargar_mongodb.py` hacia MongoDB, `cargar_postgres.py` hacia PostgreSQL con PostGIS. A continuación se aplican los controles de calidad, una sola franja compartida por ambos motores: estructura JSON, identificadores, duplicados, fechas, CRS, geometrías, valores faltantes y calidad de las detecciones. Finalmente, las consultas —`consultas_mongodb.js` del lado documental y la consulta uno del lado relacional, con sus CTE de incendio y clima, LEFT JOIN y COALESCE condicionado— agregan e integran la información para producir `fact_incendio` y `fact_clima` por celda-día, y de ahí el dataset celda-mes. Abajo, en franja aparte con borde discontinuo, señalamos Airflow: la orquestación de estas cuatro etapas está prevista, pero permanece en fase de validación; no la presentamos como una etapa ya ejecutada.

**Transición:** Con la metodología completa, le cedo la palabra a Carlos, quien presentará los resultados reales que obtuvimos.

---

## 16 — Resultado PostGIS
**Expositor:** Carlos Guillermo Chuncho Morocho · **Duración:** 2,0 min

**Mensaje central:** las dos celdas controladas pasaron una validación espacial real, incluida su pertenencia al cantón Loja.

**Explicación oral:** Gracias, Viviana. Antes de la tabla, un flujo breve: partimos de la consulta PostGIS, pasamos por la validación de SRID, geometría y área, llegamos a la tabla de resultados, y de ahí a la interpretación. La Tabla 4, "Validación espacial de las celdas controladas", no es una proyección teórica: es la salida real de la consulta que ven arriba, ejecutada sobre la base `fireforest`, seleccionando el sistema de referencia, la validez y el área de la geometría de cada celda. Ambas celdas, `LJ_TEST_001` y `LJ_TEST_002`, tienen sistema de referencia EPSG 32717, geometría válida, y un área exacta de 250 mil metros cuadrados, coherente con 500 por 500 metros. Estos son los mismos identificadores que vieron en el mapa territorial de la diapositiva 6: están verificadas dentro del cantón Loja, en la parroquia El Cisne, no son códigos administrativos oficiales sino identificadores internos de prueba. Como ya explicamos, estos son datos controlados del prototipo, sin representatividad cantonal.

**Transición:** Del lado relacional, pasemos al lado documental: los resultados de MongoDB.

---

## 17 — Resultado MongoDB
**Expositor:** Carlos Guillermo Chuncho Morocho · **Duración:** 1,85 min

**Mensaje central:** las cifras de FRP provienen de solo dos detecciones controladas.

**Explicación oral:** La Tabla 5, "Detecciones controladas almacenadas en MongoDB", resume esta consulta real, ajustada a la estructura exacta de nuestra colección, que filtra por `calidad.valida` verdadero y proyecta identificador, celda y FRP. La detección en la celda `LJ_TEST_001` tiene 18,4 megavatios, la de `LJ_TEST_002` tiene 9,7. Con las mismas agregaciones de `consultas_mongodb.js` obtuvimos una FRP máxima de 18,4 megavatios y una FRP media de 14,05, calculada por MongoDB mismo, no a mano. Insisto: 14,05 megavatios es la media de dos detecciones controladas, no la FRP media de los incendios del cantón, ni un resultado ambiental generalizable. De nuevo, datos controlados del prototipo, sin representatividad cantonal.

**Transición:** Con ambos lados verificados por separado, veamos el resultado de integrarlos mediante la consulta SQL corregida.

**Pronunciación:** "MW" se lee "megavatios".

---

## 18 — Resultado de integración SQL
**Expositor:** Carlos Guillermo Chuncho Morocho · **Duración:** 2,25 min

**Mensaje central:** ejecutamos la consulta corregida, y además probamos —y confirmamos— el caso que motivó la corrección, en un escenario controlado y acotado.

**Explicación oral:** Este es el fragmento central: se parte del clima como base y se une la detección mediante LEFT JOIN por celda, año y mes. La Tabla 6, "Resultado de la integración mensual en PostgreSQL", muestra las dos celda-mes disponibles, ambas de agosto de 2023, con una detección, la FRP correspondiente y la precipitación acumulada de cada celda; la fila resaltada con fondo tenue es la fila temporal de la prueba, no un resultado persistente. Ahora bien, estas dos filas por sí solas no demuestran el comportamiento que motivó la corrección, porque en ambas coincide que hay detección y clima el mismo mes. Por eso hicimos algo más: dentro de una transacción con ROLLBACK, insertamos una fila sintética de clima para septiembre de 2023 sobre la celda `LJ_TEST_001`, sin ninguna detección asociada, y volvimos a ejecutar la misma lógica. El resultado fue: detecciones en cero, FRP total y máxima en cero, y la precipitación real de 15,2 milímetros conservada. Quiero ser muy preciso con lo que esto demuestra y lo que no: en esta prueba sintética, LEFT JOIN conservó la fila climática y COALESCE representó con cero la ausencia de una fila coincidente de incendio. En datos reales, ese cero solo podrá interpretarse como ausencia de detecciones cuando la cobertura e ingesta VIIRS hayan sido verificadas independientemente. NULL representa información faltante, no procesada o no evaluada. Inmediatamente revertimos la transacción; verificamos que no quedó ninguna fila persistida en la base. Y, como en las diapositivas anteriores: datos controlados del prototipo, sin representatividad cantonal.

**Transición:** Con esta evidencia técnica completa, pasemos a una discusión honesta de lo que esto significa y de sus límites.

**Advertencias sobre interpretaciones incorrectas:** No presentar la fila de septiembre como si fuera un dato real del prototipo; es una prueba deliberadamente insertada y revertida dentro de una transacción, documentada así en la diapositiva. No generalizar el resultado "cero" de la prueba como si demostrara, por sí solo, que hay ausencia real de detecciones en cualquier escenario: mantener exactamente la formulación del párrafo anterior sobre LEFT JOIN, COALESCE y NULL.

**Pronunciación:** "ROLLBACK" se pronuncia en inglés, "rol-bak". "COALESCE" se pronuncia "co-a-les".

---

## 19 — Discusión preliminar y limitaciones
**Expositor:** Carlos Guillermo Chuncho Morocho · **Duración:** 2,0 min

**Mensaje central:** interpretamos los resultados, no solo los listamos; el prototipo demuestra coherencia funcional básica, no viabilidad operativa plena.

**Explicación oral:** De los resultados que acaban de ver se desprenden cuatro hallazgos interpretados. Primero, MongoDB conserva el detalle de cada detección mientras PostgreSQL almacena agregados diarios con restricciones relacionales; cada motor cumple el rol para el que fue elegido. Segundo, la reproyección que aplicamos permitió construir geometrías métricas coherentes en el prototipo, la misma reproyección que usamos para verificar territorialmente las celdas. Tercero, el LEFT JOIN conservó los registros climáticos aun cuando no había una fila coincidente de detecciones, que es exactamente el comportamiento que buscábamos verificar. Cuarto, las pruebas muestran coherencia lógica del diseño, pero todavía no demuestran escalabilidad, rendimiento ni representatividad territorial con solo dos celdas y dos detecciones, ambas en una sola parroquia. Una consideración metodológica adicional: la resolución nativa de CHIRPS limita la variabilidad climática que realmente puede distinguirse entre celdas vecinas de 500 metros; esto es una limitación del dato de origen, no de nuestra implementación. Sobre el alcance de estos resultados quiero ser preciso, con una frase deliberadamente prudente: el prototipo demuestra coherencia funcional básica entre almacenamiento documental, modelo relacional e integración SQL; su viabilidad operativa deberá evaluarse con datos reales, mayor volumen y automatización. No decimos "arquitectura viable" en sentido operacional con solo dos documentos. En cuanto a limitaciones: dos celdas y dos detecciones controladas, sin datos reales completos, malla completa de producción para todo el cantón todavía pendiente —aunque la fuente de verificación, el INEC, ya está identificada—, producto VIIRS y campo de calidad pendientes, cobertura temporal de VIIRS aún no implementada, la orquestación completa mediante Airflow permanece en fase de validación, la carga PostgreSQL requiere mejorar su idempotencia para admitir ejecuciones repetidas, y ningún análisis inferencial ni predictivo todavía.

**Transición:** A partir de este diagnóstico honesto, cerremos con las conclusiones y los próximos pasos hacia el Avance 2.

---

## 20 — Conclusiones preliminares y próximos pasos
**Expositor:** Carlos Guillermo Chuncho Morocho · **Duración:** 2,0 min

**Mensaje central:** el diseño arquitectónico es coherente en un escenario controlado y territorialmente verificado, y sabemos exactamente qué falta para el Avance 2.

**Explicación oral:** Cinco conclusiones. Primero, el diseño integra de forma coherente, en un escenario controlado, datos documentales, relacionales y espaciales. Segundo, PostgreSQL con PostGIS y MongoDB cumplen funciones complementarias, no redundantes. Tercero, la integración diaria permite construir la unidad celda-mes. Cuarto, su aplicación al cantón Loja completo todavía requiere extender la verificación que ya hicimos con el INEC a una malla completa, adquirir los datos reales, comprobar la cobertura y evaluar el flujo con mayor volumen. Quinto, la cobertura de VIIRS debe verificarse explícitamente para diferenciar ausencia real de dato faltante. Los próximos pasos hacia el Avance 2 son: extender la verificación territorial del INEC a la malla completa del cantón, generar esa malla territorial completa, confirmar el producto VIIRS y su campo de calidad, incorporar datos reales de VIIRS y CHIRPS, construir la variable `viirs_disponible`, construir el panel completo celda por mes, automatizar el flujo con Airflow, y finalmente realizar el análisis estadístico. Muchas gracias.

**Transición:** Dejamos proyectadas las referencias consultadas y quedamos abiertos a sus preguntas.

**Advertencias sobre interpretaciones incorrectas:** No cerrar sugiriendo hallazgos ambientales sobre el cantón Loja; el cierre es sobre la arquitectura y el plan de trabajo, no sobre el fenómeno de los incendios. La conclusión 1 ya delimita el alcance del prototipo a un escenario controlado.

**Pronunciación:** "viirs_disponible" se lee como una sola palabra técnica: "viirs guion bajo disponible".

---

## 21 — Referencias
**Expositor:** ninguno (sin tiempo de exposición asignado)

Se deja proyectada durante la ronda de preguntas. Contiene únicamente
las seis fuentes efectivamente citadas: Balaguer-Beser et al. (2026),
NASA EOSDIS FIRMS, Climate Hazards Center (CHIRPS v2.0), y la
documentación oficial de PostgreSQL, PostGIS y MongoDB. Cualquiera de
los tres integrantes puede remitirse directamente a esta diapositiva
si el jurado pregunta por una fuente.

---

## Nota interna: si el jurado pregunta por el proceso de verificación territorial

Esta nota no forma parte del guion oral de ninguna diapositiva; es
información de respaldo. Si un miembro del jurado pregunta
explícitamente cómo se verificaron las celdas, o si hubo algún
problema con datos anteriores, la respuesta honesta es: antes de
construir el mapa de la diapositiva 6, verificamos espacialmente las
coordenadas que se habían usado como celdas de prueba y comprobamos
que no caían dentro del cantón Loja; las sustituimos por
`LJ_TEST_001` y `LJ_TEST_002`, verificadas con la misma capa oficial
del INEC, y conservamos el hallazgo documentado como evidencia de
control de calidad en el repositorio. No es necesario mencionar esto
de forma proactiva durante la exposición.
