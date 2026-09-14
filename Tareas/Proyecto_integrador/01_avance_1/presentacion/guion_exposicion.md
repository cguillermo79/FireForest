# Guion de exposición — Avance 1, Proyecto Integrador FireForest (v7, 20 diapositivas)

**Duración total programada: 30,0 minutos**, dentro del rango de
aproximadamente 30 minutos solicitado. La diapositiva 20 (referencias)
no tiene tiempo de exposición asignado.

| Expositor | Bloque | Diapositivas | Tiempo |
|---|---|---|---|
| Marco Vinicio Malan Mullo | I. Introducción + arquitectura e implementación | 1–7 | 8,5 min |
| Viviana Isabel Pujos Culque | II. Metodología | 8–14 | 11,0 min |
| Carlos Guillermo Chuncho Morocho | III. Resultados + IV. Discusión + V. Conclusiones | 15–19 | 10,5 min |
| (sin exponer) | Referencias | 20 | — |

Esta versión (v7) corrige la v6 de 20 diapositivas: la diapositiva 3
incorpora la captura real del artículo de Fire Ecology (Springer
Nature Link) junto al contenido territorial existente, con cita y DOI
enlazado (duración 1,25→1,5 min; diapositiva 4 se ajustó de 2,0 a
1,75 min para compensar); la diapositiva 6 ganó numeración
discreta de sus seis etapas y más separación entre cajas y
flechas; la diapositiva 13 se reorganizó en cuadrantes (ecuaciones
arriba-izquierda, definiciones arriba-derecha, dos flujos horizontales
abajo, resultado común al extremo derecho mediante dos flechas
independientes sin cruce) y la advertencia final se redujo; el pie de
página ahora muestra la sección activa (Presentación / I.
Introducción / II. Metodología / III. Resultados preliminares /
IV. Discusión preliminar / V. Conclusiones / Referencias) en negrita
en vez de "Proyecto Integrador"; y el estilo de flecha global se
revisó a línea de 1,1 pt con punta Latex. La duración total se
mantiene en 30,0 minutos. Versiones anteriores: v6 rediseñó los
flujos de las diapositivas 6, 12 y 13 con flechas más visibles y
convirtió la diapositiva 14 (ETL) de tabla a flujo completo,
eliminando las tablas metodológicas de las diapositivas 12, 13 y 14 y
numerando consecutivamente las cinco tablas restantes (Tabla 1 a Tabla
5); v5 dividió la diapositiva 7 en dos columnas (VS Code y GitHub); v4
dividió la antigua diapositiva 6 (arquitectura + captura de VS Code)
en dos diapositivas independientes, llevando la presentación de 19 a
20 diapositivas; corrigió el pie de la diapositiva 4, la explicación
del campo de calidad del modelo documental, y "ausencia de incendio"
por "ausencia de detecciones" (revisión del 2026-09-14).

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

**Explicación oral:** La presentación tiene cinco bloques: Introducción, que incluye el contexto ambiental, el problema y la brecha de datos, la pregunta, el objetivo, el alcance y la arquitectura del sistema; Metodología, el bloque más extenso, donde explicamos el diseño completo; Resultados preliminares, con evidencia real del prototipo; Discusión preliminar; y Conclusiones y próximos pasos.

**Transición:** Empecemos por el bloque de introducción.

---

## 3 — Introducción: contexto territorial y ambiental
**Expositor:** Marco Vinicio Malan Mullo · **Duración:** 1,5 min

**Mensaje central:** la variabilidad altitudinal de Loja reorganiza las condiciones ambientales que controlan el fuego, y ese contexto proviene de un artículo publicado y verificable, no de una afirmación sin respaldo.

**Explicación oral:** El cantón Loja está en los Andes tropicales del sur de Ecuador, con un relieve montañoso que genera transiciones ambientales marcadas en distancias cortas: temperatura, precipitación, humedad, vegetación y combustibles cambian con la altitud. Esto se apoya en el estudio de Balaguer-Beser y colegas, publicado en 2026 en la revista Fire Ecology, que examinó el comportamiento del fuego en tres zonas contrastantes de Loja —Malacatos, Punzara y San Lucas— a lo largo de un gradiente altitudinal de aproximadamente 1549 a 2757 metros sobre el nivel del mar. El esquema que ven a la derecha es una elaboración propia para ilustrar esas tres zonas; no es la figura original del artículo. Abajo les muestro la captura real de la publicación en Springer Nature Link: el artículo "Altitudinal variation in fire behavior in Andean ecosystems in southern Ecuador", en la revista Fire Ecology, volumen 22, artículo 46, publicado el 23 de marzo de 2026 en acceso abierto, firmado por Balaguer-Beser y colegas. El DOI que ven es un enlace real: 10.1186/s42408-026-00470-y. Esta captura respalda visualmente que el contexto territorial que acabo de describir proviene de una fuente verificable, no de una afirmación sin sustento. Una precisión importante: este artículo aporta el contexto ambiental y altitudinal del cantón; no determina ni describe la ubicación de las dos celdas controladas de nuestro prototipo, que verán más adelante.

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
**Expositor:** Marco Vinicio Malan Mullo · **Duración:** 2,5 min

**Mensaje central:** hay una pregunta de arquitectura (la de este avance) y una pregunta analítica futura; el objetivo y el alcance delimitan honestamente qué se hizo y qué no.

**Explicación oral:** Formulamos dos preguntas de naturaleza distinta. La principal, que sí respondemos en este Avance 1, es de arquitectura: ¿cómo diseñar una arquitectura híbrida SQL-NoSQL que permita integrar, almacenar y consultar de forma reproducible datos heterogéneos de incendios forestales en Loja? Nuestro objetivo general es diseñar esa arquitectura híbrida para integrar VIIRS, CHIRPS y una malla espacial de Loja, construyendo un dataset analítico reproducible por celda y mes. La pregunta derivada, que solo podremos responder con datos reales en etapas posteriores, es: ¿existe relación entre la precipitación mensual y la ocurrencia de detecciones de incendio por celda? Decimos "detecciones", no "incendios": VIIRS identifica detecciones de calor, no un conteo directo de incendios independientes. El alcance: este avance sí incluye la arquitectura híbrida, los modelos SQL y NoSQL, datos controlados y validaciones preliminares; todavía no incluye un sistema operativo, alerta temprana, datos reales completos, modelo predictivo ni relación causal. Y quiero subrayar una delimitación que van a ver repetida de forma breve en los resultados: el dominio previsto de este proyecto es el cantón Loja completo, pero la cobertura actual del prototipo son únicamente dos celdas controladas, usadas solo para validar el flujo de datos; no representan el territorio cantonal.

**Transición:** Antes de entrar al detalle metodológico, les muestro la arquitectura general que hace posible todo esto.

**Advertencias:** Ninguna; esta diapositiva es la que previene sobre-interpretaciones en el resto de la charla.

**Pronunciación:** "VIIRS" se pronuncia /virs/, como en la comunidad científica.

---

## 6 — Arquitectura general del sistema
**Expositor:** Marco Vinicio Malan Mullo · **Duración:** 1,0 min

**Inicio del bloque II. Metodología.** Esta diapositiva abre explícitamente el segundo bloque de la exposición; el pie de página cambia de "Presentación"/"I. Introducción" a "II. Metodología" a partir de aquí.

**Mensaje central:** un único flujo, de arriba hacia abajo y numerado en seis etapas, conecta las fuentes originales con el producto analítico final, mostrando dónde se separan y dónde vuelven a unirse MongoDB y PostgreSQL/PostGIS.

**Qué entra:** las fuentes originales — NASA FIRMS (VIIRS), el Climate Hazards Center (CHIRPS) y un límite espacial todavía pendiente de fuente institucional.

**Qué transformación ocurre:** las fuentes pasan por adquisición e ingesta (API o descarga directa, lectura de archivos, validación inicial) y luego por validación y transformación (estructura, fechas, coordenadas, calidad, duplicados). En ese punto el flujo se separa en dos ramas paralelas: una hacia MongoDB, que conserva las detecciones individuales y sus metadatos, y otra hacia PostgreSQL/PostGIS, que organiza celdas, calendario, clima y agregados diarios. Ambas ramas vuelven a unirse en la integración, que cruza la información por `celda_id` y fecha.

**Qué sale:** el dataset analítico celda-mes, el producto final de la arquitectura.

**Por qué es necesaria esta separación:** MongoDB y PostgreSQL cumplen funciones distintas —una conserva el detalle documental, la otra impone integridad relacional y capacidad espacial— y solo se integran en un paso explícito y controlado, no de forma automática ni ambigua.

**Explicación oral:** Con esta diapositiva iniciamos el bloque de Metodología. El diagrama resume la arquitectura completa, de arriba hacia abajo, en seis etapas numeradas junto a cada bloque. Uno, partimos de las fuentes originales: NASA FIRMS para VIIRS, el Climate Hazards Center para CHIRPS, y un límite espacial todavía pendiente de fuente institucional. Dos, la adquisición e ingesta. Tres, la validación y transformación. Ahí el flujo se separa visiblemente en dos flechas diagonales, sin ninguna línea horizontal entre ellas: una hacia MongoDB, que guarda detecciones individuales y metadatos; otra hacia PostgreSQL con PostGIS, que organiza celdas, calendario, clima y agregados diarios —esa es la etapa cuatro, almacenamiento—. Ambas ramas convergen, también mediante dos flechas diagonales independientes que llegan a puntos distintos del bloque, en la etapa cinco, la integración por `celda_id` y fecha. Y la etapa seis es el producto: el dataset analítico celda-mes. Debajo del diagrama aclaramos el método previsto de adquisición: API o descarga directa de NASA FIRMS y del repositorio CHIRPS. Quiero ser preciso: no decimos que esa adquisición ya se ejecutó, porque no existe esa evidencia en FireForest; el prototipo actual utiliza datos controlados cargados desde archivos locales. Y no mencionamos Google Earth Engine porque su uso pertenece a otro proyecto y no está documentado en este repositorio.

**Transición:** Con esta arquitectura general clara, les muestro brevemente cómo luce implementada en nuestro entorno de desarrollo.

**Advertencias:** No afirmar que la adquisición por API ya fue ejecutada; es el método previsto, todavía no realizado. No mencionar Google Earth Engine.

---

## 7 — Implementación local y colaboración mediante GitHub
**Expositor:** Marco Vinicio Malan Mullo · **Duración:** 0,75 min

**Mensaje central:** el prototipo no es solo un diagrama: existe código real, desarrollado localmente y versionado en un repositorio remoto.

**Explicación oral:** FireForest se desarrolla localmente en VS Code mediante una estructura modular que separa las diferentes etapas del proyecto. A la izquierda ven el árbol completo del repositorio `Proyecto_integrador` —documentación inicial, datos, PostgreSQL/PostGIS, MongoDB, ingesta, calidad de datos, ETL e integración, Airflow, Spark, análisis, resultados y entrega final— junto con un fragmento legible de `cargar_postgres.py`, el script que conecta con PostgreSQL y ejecuta el esquema y la carga de los datos controlados. A la derecha, el repositorio remoto FireForest en GitHub, con la misma ruta `Tareas/Proyecto_integrador`. El repositorio remoto centraliza el código y la documentación, facilita el intercambio de avances entre los integrantes y mantiene el historial de versiones; GitHub almacena y versiona el código, la ejecución ocurre en el entorno local. Ambas capturas son evidencia de implementación y organización del proyecto; no sustituyen al diagrama de arquitectura que acaban de ver.

**Transición:** Con la arquitectura, su implementación y su control de versiones mostrados, le cedo la palabra a Viviana, quien detallará cada componente de la metodología, empezando por las fuentes y variables.

**Advertencias:** No presentar estas capturas como si fueran la arquitectura; son evidencia complementaria de código, organización del repositorio y control de versiones. La captura de GitHub demuestra la existencia del repositorio remoto y su commit más reciente; no se afirma que los tres integrantes estén enlazados o hayan contribuido, porque esa evidencia específica no fue verificada en esta revisión. No decir que GitHub ejecuta el proyecto.

---

## 8 — Fuentes y variables
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 1,5 min

**Mensaje central:** cada fuente aporta una variable con una unidad, resolución y transformación específicas hacia una variable final concreta del esquema.

**Explicación oral:** Gracias, Marco. Antes de la tabla, una precisión sobre el origen de los datos: VIIRS lo distribuye NASA FIRMS, accesible mediante su API o descarga directa por área y periodo; CHIRPS se descarga directamente del repositorio del Climate Hazards Center. Ninguna de las dos pasa por Google Earth Engine en esta arquitectura. Ahora sí, la Tabla 1, "Fuentes, variables y transformaciones del proyecto", muestra exactamente qué medimos, con qué unidad, con qué resolución y cómo se transforma cada variable, usando los nombres reales de nuestro esquema. VIIRS aporta `frp_mw` por detección, que agregamos diaria y mensualmente hacia `frp_suma_mw` y `frp_maxima_mw`; sus coordenadas se asignan espacialmente a un `celda_id`. CHIRPS aporta precipitación diaria en píxeles de unos 5 kilómetros, que agregamos mensualmente. La malla parte de longitud y latitud en grados y se transforma, mediante `ST_SetSRID`, `ST_Transform` y `ST_MakeEnvelope`, en la geometría `geom` en metros. El calendario deriva año y mes de cada fecha. Tres aclaraciones adicionales: la malla actual son dos celdas controladas, la fuente institucional definitiva está pendiente; el producto VIIRS exacto también está pendiente; y CHIRPS, al asignarse a la malla de 500 metros, no mejora su resolución real.

**Transición:** Con las fuentes claras, veamos por qué la unidad de análisis final —celda-mes— no es lo mismo que una detección individual.

**Pronunciación:** "FRP" se lee letra por letra: efe-erre-pe.

---

## 9 — Unidad de análisis y granularidad
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 1,5 min

**Mensaje central:** existen tres niveles de granularidad y no son equivalentes entre sí.

**Explicación oral:** El primer nivel es la detección individual, que MongoDB conserva con celda y fecha exactas, incluida la hora. El segundo es la celda-día: `fact_incendio` y `fact_clima`, en PostgreSQL, agregan esas detecciones a un registro diario por celda, con la restricción `UNIQUE(celda_id, fecha_id)`. El tercero es la celda-mes, el dataset analítico, obtenido agregando esos registros diarios con `GROUP BY` año y mes. No son equivalentes: al agregar por día se pierde el detalle de cuántas detecciones hubo y a qué hora exacta; nunca existe en las tablas base una fila pre-agregada por mes; y el agregado mensual puede ocultar variación diaria real.

**Transición:** Con esta distinción clara, veamos cómo se organiza el lado relacional del sistema.

---

## 10 — Modelo relacional
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 1,5 min

**Mensaje central:** cuatro tablas relacionales, cada una con una función y una clave bien definidas.

**Explicación oral:** La Tabla 2, "Estructura del modelo relacional", resume las cuatro tablas. `dim_celda` es el catálogo espacial: cada fila es una celda controlada de 500 por 500 metros, con `celda_id` como clave primaria. `dim_fecha` es el calendario: cada fila es un día. `fact_incendio` almacena las detecciones diarias agregadas: cada fila es una celda en un día, con clave única `celda_id` más `fecha_id`, y claves foráneas hacia ambas dimensiones. `fact_clima` tiene la misma estructura para la precipitación diaria. Un punto importante: `fact_incendio` y `fact_clima` no tienen clave foránea entre sí; se cruzan mediante `JOIN` cuando se necesita comparar detecciones y clima.

**Transición:** Ese es el lado relacional. Veamos ahora cómo se estructura el lado documental, en MongoDB.

---

## 11 — Modelo documental
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 1,5 min

**Mensaje central:** MongoDB conserva la detección VIIRS con su estructura anidada original, vinculada lógicamente —no físicamente— a la malla.

**Explicación oral:** Este es un documento real de nuestra colección `detecciones_viirs`: tiene un identificador de detección, la celda, la fecha, la potencia radiativa `frp_mw`, el campo `fire_mask`, y dos objetos anidados: `coordenadas`, con longitud y latitud, y `calidad`, con el indicador `valida`. Estos objetos anidados pueden ganar o perder campos entre versiones del producto VIIRS sin romper el esquema, que es justamente la ventaja de un modelo documental. El vínculo con `celda_id` es lógico, no una clave foránea física: MongoDB no referencia tablas de PostgreSQL. Sobre el campo de calidad, quiero ser preciso: el prototipo filtra los documentos mediante `calidad.valida=true`, tal como lo hace `consultas_mongodb.js`; el campo `fire_mask` se conserva en el documento como atributo de la detección, pero la consulta actual no filtra directamente por él. El producto VIIRS definitivo y el criterio definitivo de calidad deberán confirmarse antes de utilizar datos reales.

**Transición:** Con ambos modelos definidos, veamos cómo estandarizamos el espacio para que convivan.

---

## 12 — Estandarización espacial
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 2,0 min

**Mensaje central:** tres fuentes con formatos y resoluciones distintas —VIIRS, la malla y CHIRPS— convergen en una sola referencia espacial común: la celda.

**Qué entra:** una detección VIIRS como punto en longitud/latitud (EPSG:4326); el centro o límite de la malla; un píxel CHIRPS de aproximadamente 0,05°.

**Qué transformación ocurre:** cada fuente sigue su propio flujo de cuatro pasos, mostrado como una línea paralela e independiente en la diapositiva. La detección VIIRS se reproyecta y se le asigna espacialmente una celda. La malla se reproyecta a EPSG:32717 y se construye como un polígono de 500 por 500 metros. CHIRPS se superpone espacialmente y se asigna a las celdas que cubre. Las ecuaciones de la izquierda formalizan la reproyección y la construcción del polígono; en código son tres funciones encadenadas: `ST_SetSRID`, `ST_Transform` y `ST_MakeEnvelope`.

**Qué sale:** las tres fuentes terminan referenciadas por `celda_id`: la detección VIIRS como `celda_id`, la malla como `dim_celda.geom`, y CHIRPS como precipitación asociada a la celda.

**Por qué es necesaria esta transformación:** sin una referencia espacial común no se pueden cruzar detecciones, malla y precipitación en una sola consulta; por eso el resultado de las tres líneas es siempre el mismo identificador de celda.

**Explicación oral:** Para construir cada celda partimos de longitud y latitud en grados, en el sistema EPSG 4326, y las transformamos al sistema EPSG 32717, en metros, apropiado para Ecuador continental. Sobre ese punto ya en metros construimos un cuadrado de 500 por 500 metros centrado en él, cuya área es exactamente 250 mil metros cuadrados. En código, esto son tres funciones encadenadas: `ST_SetSRID` fija el sistema de referencia original, `ST_Transform` reproyecta, y `ST_MakeEnvelope` construye el rectángulo final. Debajo, tres líneas paralelas muestran el mismo proceso por fuente: VIIRS pasa de un punto en EPSG 4326 a una reproyección, una asignación espacial y finalmente un `celda_id`; la malla pasa de su centro o límite a EPSG 32717, a la construcción del polígono de 500 por 500 metros, y a `dim_celda.geom`; CHIRPS pasa de un píxel de unos 0,05 grados a una superposición espacial, una asignación a celdas, y a la precipitación por celda. La idea central: la estandarización espacial lleva detecciones, celdas y precipitación a una referencia común basada en `celda_id`. Una aclaración importante: la asignación de CHIRPS a celdas de 500 metros no aumenta su resolución espacial real; varias celdas vecinas terminan compartiendo el mismo valor de precipitación.

**Transición:** Resuelto el espacio, veamos cómo estandarizamos el tiempo.

**Pronunciación:** "EPSG" se lee letra por letra: e-pe-ese-je.

---

## 13 — Estandarización temporal
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 1,5 min

**Mensaje central:** VIIRS y CHIRPS siguen dos flujos horizontales paralelos hasta una granularidad diaria común, y de ahí convergen —sin cruzarse— en un único bloque de resultado a la derecha.

**Qué entra:** una detección VIIRS individual, con fecha y hora; una precipitación CHIRPS por píxel-día.

**Qué transformación ocurre:** el flujo VIIRS (fila superior) se agrupa por celda y día en `fact_incendio`, y ese resultado diario se agrega mensualmente. El flujo CHIRPS (fila inferior) se asigna a la celda por día en `fact_clima`, y se suma mensualmente. Las fórmulas de la zona superior izquierda formalizan esa agregación; las definiciones de símbolos, en la zona superior derecha, precisan qué es cada término a nivel diario antes de agregarlo.

**Qué sale:** ambos flujos terminan en "Detecciones y FRP" y "Precipitación acumulada" respectivamente, y convergen mediante dos flechas independientes —una desde cada fila, sin cruzarse— en dos puntos distintos del borde izquierdo de un único bloque a la derecha: el dataset analítico celda-mes.

**Por qué es necesaria esta transformación:** VIIRS y CHIRPS nacen en granularidades distintas (una detección puntual, un píxel diario); sin llevarlas primero a celda-día no podrían agregarse de forma comparable a celda-mes.

**Definición oral de las ecuaciones:** N de i,m es la suma, para todos los días d del mes m, del número de detecciones N de i,d en la celda i. FRP suma de i,m es la suma de la potencia radiativa FRP de i,d de cada día. FRP máxima de i,m es el máximo de los máximos diarios FRP máximo de i,d. Y P de i,m es la suma de la precipitación diaria P de i,d. Aquí i es la celda espacial, d es el día y m es el mes; N de i,d es el número de detecciones en la celda i durante el día d; FRP de i,d es la potencia radiativa acumulada en la celda y día; FRP máximo de i,d es la máxima potencia radiativa diaria; y P de i,d es la precipitación diaria asignada a la celda.

**Explicación oral:** Arriba a la izquierda están las cuatro fórmulas que acabo de definir; arriba a la derecha, la definición de cada símbolo. Abajo, dos filas horizontales paralelas muestran el mismo proceso por fuente, sin que ninguna flecha cruce a la otra fila. La fila VIIRS pasa de la detección individual, con fecha y hora, a una agrupación por celda y día, a `fact_incendio` celda-día, a una agregación mensual, y finalmente a "Detecciones y FRP". La fila CHIRPS pasa de la precipitación píxel-día, a una asignación por celda, a `fact_clima` celda-día, a una suma mensual, y finalmente a "Precipitación acumulada". A la derecha, un único bloque naranja, "Dataset analítico celda-mes", recibe dos flechas independientes: una que sale de "Detecciones y FRP" y llega a la parte superior del borde izquierdo del bloque, y otra que sale de "Precipitación acumulada" y llega a la parte inferior de ese mismo borde; ninguna de las dos se cruza con la otra. En una frase: VIIRS y CHIRPS se transforman a una granularidad común celda-día y posteriormente se agregan por celda y mes. La advertencia final, breve: un valor cero representa ausencia de detecciones únicamente cuando se verificó la cobertura VIIRS; NULL identifica información faltante o no procesada. El detalle de por qué el LEFT JOIN por sí solo no demuestra esa cobertura lo retomo en la diapositiva del resultado de integración SQL.

**Transición:** Con el espacio y el tiempo estandarizados, veamos el proceso completo de integración y control de calidad.

**Pronunciación:** "LEFT JOIN" se pronuncia en inglés, "left yoin".

---

## 14 — ETL y control de calidad
**Expositor:** Viviana Isabel Pujos Culque · **Duración:** 1,5 min

**Mensaje central:** el flujo completo va de los archivos de entrada al dataset celda-mes, pasando por una carga en dos motores, un control de calidad único y compartido, y una integración final.

**Qué entra:** el JSON de detecciones VIIRS y el SQL de esquema y datos controlados.

**Qué transformación ocurre:** cada entrada se carga con su script correspondiente —`cargar_mongodb.py` hacia MongoDB, `cargar_postgres.py` hacia PostgreSQL/PostGIS—, y ambas rutas convergen en una única franja de controles de calidad compartida: estructura JSON, identificadores, duplicados, fechas, CRS, geometrías, valores faltantes y calidad de las detecciones. De ahí el flujo se separa de nuevo hacia las consultas de transformación e integración: `consultas_mongodb.js` del lado documental, `consulta_01_incendios_clima_mensual.sql` del lado relacional.

**Qué sale:** ambas consultas convergen en `fact_incendio` y `fact_clima` por celda-día, que finalmente se integran en el dataset celda-mes.

**Por qué es necesaria esta secuencia:** ningún dato entra directamente a las consultas de integración sin pasar primero por el control de calidad compartido; eso es lo que permite confiar en el resultado final aunque provenga de dos motores distintos.

**Explicación oral:** Primero ingresan los archivos: el JSON de detecciones VIIRS y el SQL de esquema y datos controlados. Después, los scripts cargan los datos: `cargar_mongodb.py` hacia MongoDB, `cargar_postgres.py` hacia PostgreSQL con PostGIS. A continuación se aplican los controles de calidad, una sola franja compartida por ambos motores: estructura JSON, identificadores, duplicados, fechas, CRS, geometrías, valores faltantes y calidad de las detecciones. Finalmente, las consultas —`consultas_mongodb.js` del lado documental y la consulta uno del lado relacional, con sus CTE de incendio y clima, LEFT JOIN y COALESCE condicionado— agregan e integran la información para producir `fact_incendio` y `fact_clima` por celda-día, y de ahí el dataset celda-mes. Abajo, en franja aparte con borde discontinuo, señalamos Airflow: la orquestación de estas cuatro etapas está prevista, pero permanece en fase de validación; no la presentamos como una etapa ya ejecutada.

**Transición:** Con la metodología completa, le cedo la palabra a Carlos, quien presentará los resultados reales que obtuvimos.

---

## 15 — Resultado PostGIS
**Expositor:** Carlos Guillermo Chuncho Morocho · **Duración:** 2,0 min

**Mensaje central:** las dos celdas controladas pasaron una validación espacial real.

**Explicación oral:** Gracias, Viviana. Antes de la tabla, un flujo breve: partimos de la consulta PostGIS, pasamos por la validación de SRID, geometría y área, llegamos a la tabla de resultados, y de ahí a la interpretación. La Tabla 3, "Validación espacial de las celdas controladas", no es una proyección teórica: es la salida real de la consulta que ven arriba, ejecutada sobre la base `fireforest`, seleccionando el sistema de referencia, la validez y el área de la geometría de cada celda. Ambas celdas, LJ_04521 y LJ_04522, tienen sistema de referencia EPSG 32717, geometría válida, y un área exacta de 250 mil metros cuadrados, coherente con 500 por 500 metros. Una aclaración: esos identificadores son internos del prototipo, no códigos administrativos ni sectores oficiales de Loja. Como ya explicamos en la diapositiva de alcance, estos son datos controlados del prototipo, sin representatividad cantonal.

**Transición:** Del lado relacional, pasemos al lado documental: los resultados de MongoDB.

---

## 16 — Resultado MongoDB
**Expositor:** Carlos Guillermo Chuncho Morocho · **Duración:** 2,0 min

**Mensaje central:** las cifras de FRP provienen de solo dos detecciones controladas.

**Explicación oral:** La Tabla 4, "Detecciones controladas almacenadas en MongoDB", resume esta consulta real, ajustada a la estructura exacta de nuestra colección, que filtra por `calidad.valida` verdadero y proyecta identificador, celda y FRP. La detección en la celda LJ_04521 tiene 18,4 megavatios, la de LJ_04522 tiene 9,7. Con las mismas agregaciones de `consultas_mongodb.js` obtuvimos una FRP máxima de 18,4 megavatios y una FRP media de 14,05, calculada por MongoDB mismo, no a mano. Insisto: 14,05 megavatios es la media de dos detecciones controladas, no la FRP media de los incendios del cantón, ni un resultado ambiental generalizable. De nuevo, datos controlados del prototipo, sin representatividad cantonal.

**Transición:** Con ambos lados verificados por separado, veamos el resultado de integrarlos mediante la consulta SQL corregida.

**Pronunciación:** "MW" se lee "megavatios".

---

## 17 — Resultado de integración SQL
**Expositor:** Carlos Guillermo Chuncho Morocho · **Duración:** 2,5 min

**Mensaje central:** ejecutamos la consulta corregida, y además probamos —y confirmamos— el caso que motivó la corrección.

**Explicación oral:** Este es el fragmento central: se parte del clima como base y se une la detección mediante LEFT JOIN por celda, año y mes. La Tabla 5, "Resultado de la integración mensual en PostgreSQL", muestra las dos celda-mes disponibles, ambas de agosto de 2023, con una detección, la FRP correspondiente y la precipitación acumulada de cada celda; la fila resaltada con fondo tenue es la fila temporal de la prueba, no un resultado persistente. Ahora bien, estas dos filas por sí solas no demuestran el comportamiento que motivó la corrección, porque en ambas coincide que hay detección y clima el mismo mes. Por eso hicimos algo más: dentro de una transacción con ROLLBACK, insertamos una fila sintética de clima para septiembre de 2023, sin ninguna detección asociada, y volvimos a ejecutar la misma lógica. El resultado fue: detecciones en cero, FRP total y máxima en cero, y la precipitación real de 15,2 milímetros conservada. Esto confirma que el LEFT JOIN preserva el mes climático en vez de descartarlo. Inmediatamente revertimos la transacción; verificamos que no quedó ninguna fila persistida en la base. Ese cero refleja el escenario controlado de esta prueba, no una cobertura VIIRS verificada de forma independiente. Y, como en las diapositivas anteriores: datos controlados del prototipo, sin representatividad cantonal.

**Transición:** Con esta evidencia técnica completa, pasemos a una discusión honesta de lo que esto significa y de sus límites.

**Advertencias sobre interpretaciones incorrectas:** No presentar la fila de septiembre como si fuera un dato real del prototipo; es una prueba deliberadamente insertada y revertida dentro de una transacción, documentada así en la diapositiva.

**Pronunciación:** "ROLLBACK" se pronuncia en inglés, "rol-bak". "COALESCE" se pronuncia "co-a-les".

---

## 18 — Discusión preliminar y limitaciones
**Expositor:** Carlos Guillermo Chuncho Morocho · **Duración:** 2,0 min

**Mensaje central:** interpretamos los resultados, no solo los listamos; el prototipo demuestra coherencia funcional básica, no viabilidad operativa plena.

**Explicación oral:** De los resultados que acaban de ver se desprenden cuatro hallazgos interpretados. Primero, MongoDB conserva el detalle de cada detección mientras PostgreSQL almacena agregados diarios con restricciones relacionales; cada motor cumple el rol para el que fue elegido. Segundo, la reproyección que aplicamos permitió construir geometrías métricas coherentes en el prototipo. Tercero, el LEFT JOIN conservó los registros climáticos aun cuando no había una fila coincidente de detecciones, que es exactamente el comportamiento que buscábamos verificar. Cuarto, las pruebas muestran coherencia lógica del diseño, pero todavía no demuestran escalabilidad, rendimiento ni representatividad territorial con solo dos celdas y dos detecciones. Una consideración metodológica adicional: la resolución nativa de CHIRPS limita la variabilidad climática que realmente puede distinguirse entre celdas vecinas de 500 metros; esto es una limitación del dato de origen, no de nuestra implementación. Sobre el alcance de estos resultados quiero ser preciso, con una frase deliberadamente prudente: el prototipo demuestra coherencia funcional básica entre almacenamiento documental, modelo relacional e integración SQL; su viabilidad operativa deberá evaluarse con datos reales, mayor volumen y automatización. No decimos "arquitectura viable" en sentido operacional con solo dos documentos. En cuanto a limitaciones: dos celdas y dos detecciones controladas, sin datos reales completos, fuente institucional de la malla pendiente, producto VIIRS y campo de calidad pendientes, cobertura temporal de VIIRS aún no implementada, la orquestación completa mediante Airflow permanece en fase de validación, la carga PostgreSQL requiere mejorar su idempotencia para admitir ejecuciones repetidas, y ningún análisis inferencial ni predictivo todavía.

**Transición:** A partir de este diagnóstico honesto, cerremos con las conclusiones y los próximos pasos hacia el Avance 2.

---

## 19 — Conclusiones preliminares y próximos pasos
**Expositor:** Carlos Guillermo Chuncho Morocho · **Duración:** 2,0 min

**Mensaje central:** el diseño arquitectónico es coherente en un escenario controlado, y sabemos exactamente qué falta para el Avance 2.

**Explicación oral:** Cinco conclusiones. Primero, el diseño integra de forma coherente, en un escenario controlado, datos documentales, relacionales y espaciales. Segundo, PostgreSQL con PostGIS y MongoDB cumplen funciones complementarias, no redundantes. Tercero, la integración diaria permite construir la unidad celda-mes. Cuarto, su aplicación al cantón Loja completo todavía requiere completar la malla, adquirir los datos reales, comprobar la cobertura y evaluar el flujo con mayor volumen. Quinto, la cobertura de VIIRS debe verificarse explícitamente para diferenciar ausencia real de dato faltante. Los próximos pasos hacia el Avance 2 son: seleccionar y validar el límite institucional oficial, generar la malla territorial completa, confirmar el producto VIIRS y su campo de calidad, incorporar datos reales de VIIRS y CHIRPS, construir la variable `viirs_disponible`, construir el panel completo celda por mes, automatizar el flujo con Airflow, y finalmente realizar el análisis estadístico. Muchas gracias.

**Transición:** Dejamos proyectadas las referencias consultadas y quedamos abiertos a sus preguntas.

**Advertencias sobre interpretaciones incorrectas:** No cerrar sugiriendo hallazgos ambientales sobre el cantón Loja; el cierre es sobre la arquitectura y el plan de trabajo, no sobre el fenómeno de los incendios. La conclusión 1 ya delimita el alcance del prototipo a un escenario controlado; no es necesario añadir una frase adicional sobre conclusiones ambientales.

**Pronunciación:** "viirs_disponible" se lee como una sola palabra técnica: "viirs guion bajo disponible".

---

## 20 — Referencias
**Expositor:** ninguno (sin tiempo de exposición asignado)

Se deja proyectada durante la ronda de preguntas. Contiene únicamente
las seis fuentes efectivamente citadas: Balaguer-Beser et al. (2026),
NASA EOSDIS FIRMS, Climate Hazards Center (CHIRPS v2.0), y la
documentación oficial de PostgreSQL, PostGIS y MongoDB. Cualquiera de
los tres integrantes puede remitirse directamente a esta diapositiva
si el jurado pregunta por una fuente.
