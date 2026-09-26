# Guía de Sustentación — FireForest
### Tu bloque: diapositivas 6 a 18 + demo en vivo del Dashboard

Esta guía es para que **estudies y presentes** la segunda mitad de la sustentación (diapositivas 6-18 de `presentacion_final.pdf`) y hagas la demo en vivo del dashboard: **https://fireforest-loja.streamlit.app/**

No repite el informe palabra por palabra — te da el **guión de lo que decir**, el **por qué técnico** de cada decisión (que es lo que más preguntan en un jurado), los **números que debes tener frescos** y las **preguntas más probables con respuesta lista**.

---

## 0. Antes de empezar — Contexto de lo que ya expusieron tus compañeros (diapositivas 1-5)

No lo vas a presentar tú, pero debes poder enlazarlo si te preguntan algo de ahí:

| # | Título | Una frase |
|---|---|---|
| 1 | Portada | — |
| 2 | Estructura de la Sustentación | Mapa de las 4 partes de la charla |
| 3 | Problema y Pregunta de Investigación | El cantón Loja tiene incendios estacionales (may-nov); el reto es integrar datos dispersos (INEC, VIIRS, CHIRPS) a grano celda-mes |
| 4 | Objetivos | Pipeline end-to-end con PostgreSQL/PostGIS + MongoDB + Spark + ML sobre 7.997 celdas × 12 meses |
| 5 | Diccionario de Variables | Las variables clave del dataset final (`fact_celda_mes`) |

**El hilo conductor de toda la charla:** pasar de un prototipo de 2 celdas (Avance 1) a una arquitectura híbrida completa sobre las 7.997 celdas reales del cantón, con datos, calidad, procesamiento distribuido, bases de datos, ML y un dashboard — todo trazable y reproducible.

---

## 1. Tu guión, diapositiva por diapositiva

### Diapositiva 6 — Restricciones y Limitaciones de los Datos

**Qué decir:** "Antes de mostrar resultados, es importante ser honestos sobre las limitaciones de las fuentes que usamos."

- **Restricciones de origen** (columna izquierda):
  - VIIRS tiene resolución nativa de 375 m pero la agregamos a una malla de 500 m → en celdas de borde puede haber sub- o sobre-representación.
  - Los sensores ópticos (VIIRS) pierden detecciones bajo nubosidad, más frecuente en la época lluviosa (mar-abr) — **no es que no haya fuego, es que el satélite no lo vio ese día**.
  - CHIRPS es un producto **interpolado** (combina satélite + estaciones terrestres), no son pluviómetros puros — en terreno andino abrupto puede haber sesgo.
- **Restricciones temporales y de clase** (columna derecha):
  - Grano celda-mes: si llovió fuerte 25 días y hubo un día seco crítico, el promedio mensual lo diluye.
  - Solo un año (2023): no capturamos variabilidad interanual (El Niño/La Niña).
  - **Desbalance de clases: solo 747 de 95.964 observaciones (0,8%) tienen fuego confirmado.** Este dato es clave — lo vas a necesitar para explicar por qué el modelo de ML tiene métricas particulares (diapositiva 14).

**Por qué esta diapositiva importa:** un jurado de ciencia de datos valora mucho que reconozcas las limitaciones *antes* de que te las señalen. Es una señal de rigor, no de debilidad.

---

### Diapositiva 7 — Calidad de Datos y Reglas de Limpieza (ETL)

**Qué decir:** "Detectamos 4 problemas de calidad reales y cada uno se resolvió con una regla explícita, documentada y auditable — nunca de forma silenciosa."

- **Problemas detectados** (izquierda): geometrías parciales fuera del cantón, registros VIIRS duplicados por múltiples pasadas satelitales, nulos en precipitación por vacíos CHIRPS, inconsistencias de proyección (EPSG:32717 vs WGS84).
- **Reglas aplicadas** (derecha):
  - Deduplicación por `(cell_id, anio, mes)`.
  - **`coalesce()` para distinguir "ausencia verificada de fuego" de "dato faltante"** — memoriza esta frase, es el concepto técnico más importante de toda tu parte de la charla (ver la sección de preguntas difíciles más abajo, porque justamente en Spark casi se nos escapó no aplicar esto bien).
  - Reproyección uniforme a `EPSG:32717` antes de cualquier unión espacial.
  - Trazabilidad con hash SHA-256 por archivo fuente.
- **Transformación principal:** malla ⋈ clima (inner join) ⋈ VIIRS (left join) sobre `cell_id`, **conservando las 7.997 celdas aunque no tengan evidencia de incendio** — ningún dato se descarta silenciosamente.

**Por qué Left Join y no Inner Join con VIIRS:** si usáramos inner join, las celdas sin fuego desaparecerían del dataset y no podríamos entrenar un clasificador (necesitas ejemplos negativos). Con left join, esas celdas quedan con nulos que después se tratan explícitamente.

---

### Diapositiva 8 — Salto de Escala: De 2 Celdas a la Malla Cantonal Completa

**Qué decir:** "Esto resume el salto real de este proyecto frente al Avance 1."

| | Avance 1 | Entrega Final |
|---|---|---|
| Celdas | 2 (`LJ_TEST_001/002`, El Cisne) | **7.997** (todo el cantón) |
| Periodo | Sin estacionalidad | **12 meses** completos 2023 |
| Filas | 2 | **95.964** celda-mes |
| Fuego | — | **747** eventos históricos |

El mapa de la derecha muestra la cobertura real: el degradado azul es precipitación acumulada, los puntos rojos son focos VIIRS de septiembre (el mes más crítico), y la línea punteada cian es el límite oficial INEC del cantón.

**Dato para lucirte:** el cantón Loja tiene geografía muy irregular (valle interandino + páramo), por eso la malla no es un rectángulo — se generó por disolución de sectores censales oficiales del INEC (código DPA 1101), no dibujando un cuadrado a mano.

---

### Diapositiva 9 — Arquitectura de Datos Híbrida Multimodelo

**Esta es la diapositiva más importante para justificar "qué se usó y por qué".** Sigue el diagrama de arriba abajo:

1. **Fuentes inmutables:** Malla INEC (GeoPackage), NASA VIIRS (CSV), CHIRPS (Parquet) — nunca se modifican.
2. **Raw Data Lake:** verificación SHA-256 + ingesta controlada, antes de tocar nada.
3. **Apache Spark 4.2 (PySpark):** el motor central que hace las uniones espaciales masivas y las *window functions* (lags 1m, 2m, media móvil, días secos).
4. Desde Spark, el dato se reparte a **tres destinos según su uso**, no porque "sí":

| Motor | Por qué ESE motor y no otro |
|---|---|
| **Parquet (Data Lakehouse)** | Formato columnar, compresión Snappy (>90% menos espacio que CSV), lectura OLAP ultrarrápida — es el que alimenta el modelo de ML y el explorador del dashboard. |
| **PostgreSQL/PostGIS** | Necesitamos **integridad referencial** (claves primarias/foráneas entre celda, fecha y hecho) y **topología espacial real** (`ST_Area`, `ST_Intersects`) con índices GiST — esto un documento NoSQL no lo garantiza. |
| **MongoDB** | La telemetría satelital VIIRS trae metadatos anidados y variables (bandas espectrales, banderas de calidad) que cambian de un sensor a otro — un esquema relacional rígido obligaría a migraciones de DDL constantes. MongoDB lo absorbe sin fricción. |

5. Todo converge en la **capa de analítica**: el modelo Random Forest y el dashboard Streamlit.

**La pregunta que casi seguro te hacen aquí:** *"¿Por qué no usar solo PostgreSQL para todo, o solo MongoDB para todo?"* → Respuesta: un sistema mono-modelo relacional es rígido ante esquemas satelitales cambiantes; uno mono-modelo documental es ineficiente para consultas espaciales topológicas con garantías de integridad. La arquitectura híbrida usa cada motor donde es objetivamente superior — está justificado en la Tabla 1 del informe (Sección 3.2).

---

### Diapositiva 10 — Procesamiento Distribuido en Apache Spark (PySpark)

**Qué decir:** "Aquí está el corazón técnico del pipeline: las funciones de ventana."

- `lag(col("precip"), 1)` y `lag(col("precip"), 2)`: cuánto llovió 1 y 2 meses atrás, **por cada celda de forma independiente** (`Window.partitionBy("cell_id")`).
- `avg(...).rowsBetween(-2, 0)`: media móvil de 3 meses.
- `sum(...).rowsBetween(-2, 0)`: días secos acumulados en el trimestre.

**Hallazgo central (memorízalo, es la conclusión científica del proyecto):** *"El fuego tiene memoria hídrica."* La lluvia cae en mayo (29 mm), pero los incendios no estallan de inmediato — se concentran en agosto-octubre (>15.700 MW acumulados), **después de acumularse cerca de 86 días secos continuos**. Esto se ve clarísimo en el gráfico de doble eje: las barras azules (lluvia) bajan mucho antes de que la línea roja (FRP) suba.

**Por qué esto NO se podía hacer fácil en SQL puro:** calcular "el mes anterior" y "la media de los últimos 3 meses" por cada una de 7.997 series de tiempo independientes en SQL clásico requiere subconsultas correlacionadas o CTEs recursivas — lento y difícil de mantener. Spark lo resuelve nativamente con funciones de ventana particionadas, en segundos.

---

### Diapositiva 11 — Resultados Tabulares: Balance Cantonal en Apache Spark

**Qué decir:** recorre la tabla señalando el patrón, no leas cada celda.

- Enero-mayo: lluvia alta (hasta 325 mm en abril), cero fuego.
- Junio-julio: la lluvia cae a ~17 mm, empiezan los primeros focos (16 y 26 celdas).
- **Agosto-octubre: pico crítico** — 143, 306 y 201 celdas con fuego respectivamente; septiembre solo, 306 celdas y 6.295 MW de FRP.
- Noviembre-diciembre: la lluvia vuelve (~68-77 mm) y el fuego cae a 42 y 6 celdas.
- **Total 2023: 747 celdas-mes con fuego, 16.724,33 MW de FRP liberados en el cantón.**

**Dato técnico que puedes mencionar de pasada:** la columna "Lag 1m" de enero dice `n/d` — es honesto, no un error: enero es el primer mes de la serie, no existe diciembre 2022 en el dataset, así que no se inventa un valor.

---

### Diapositiva 12 — Resultados en PostgreSQL / PostGIS (Modelo Estrella)

**Qué decir:** "Aquí bajamos del análisis agregado a la celda individual, usando el modelo dimensional en PostgreSQL."

- Esquema: `dim_celda` (7.997 polígonos con `ST_MakeEnvelope`, SRID 32717, índice GiST), `dim_fecha` (calendario 2023), `fact_celda_mes` (95.964 filas con PK/FK).
- La consulta de auditoría (`WHERE incendio_observado = true`) confirma los **747 eventos** — el mismo número que en Spark y en MongoDB, lo cual es intencional: es una prueba de **consistencia cruzada entre motores**.
- Top 5 celdas con mayor FRP: todas caen en **octubre** (excepto dos en septiembre) en la zona de `R031/R032/R033` — es decir, geográficamente **contiguas**, no dispersas al azar. Esto conecta directamente con un hallazgo del modelo de ML (diapositiva 14: la variable `fila` resultó muy importante).

**Por qué PostGIS y no coordenadas sueltas en una tabla normal:** GiST permite responder "¿qué celdas intersectan este polígono?" en milisegundos sobre miles de geometrías; sin índice espacial sería un recorrido secuencial completo cada vez.

---

### Diapositiva 13 — Resultados NoSQL en MongoDB 8 (Telemetría BSON)

**Qué decir:** "MongoDB guarda el detalle crudo de la telemetría satelital, con su propio pipeline de agregación nativo."

- Colección `evidencia_viirs_celda_mes`: documentos BSON con coordenadas GeoJSON (`"Point"`), índice `2dsphere`.
- El pipeline de agregación (`$group` + `$cond` + `$sum`) reproduce el mismo cálculo mensual que Spark y PostgreSQL — **verás los mismos números** (septiembre: 306 fuegos, 6.295,15 MW) en las tres tecnologías. Puedes decir explícitamente: *"Verificamos que los tres motores, cargados de forma independiente, muestran resultados consistentes — eso es parte de nuestra trazabilidad."*

**Por qué BSON y no forzar esto en una tabla SQL:** cada documento trae metadatos anidados variables (banda espectral, calidad de píxel) que no todos los registros tienen de la misma forma — en SQL relacional eso implicaría muchas columnas nulas o tablas adicionales; en documentos BSON es natural.

---

### Diapositiva 14 — Modelo Predictivo de Machine Learning (Random Forest)

**Esta es la diapositiva donde más te pueden presionar. Prepárate bien.**

**Qué decir primero (contexto honesto):** "Entrenamos sobre las 95.064 celdas-mes con observación satelital confirmada (excluimos 900 filas sin cobertura VIIRS, que no son 'sin fuego', son 'sin dato' — coherente con lo que explicamos en la diapositiva 7). Partición 80/20: 76.051 para entrenar, 19.013 para evaluar, estratificado por la variable objetivo."

**Los 4 números que debes decir de memoria:**
| Métrica | Valor | Qué significa en una frase |
|---|---|---|
| ROC-AUC | **0,9912** | Separa casi perfectamente celdas con y sin riesgo |
| Recall | **95,97%** (143/149) | De cada 149 incendios reales, detecta 143 — solo se le escapan 6 |
| Precisión | **15,61%** | De cada 100 alertas que da, ~16 son incendios reales |
| F1-Score | **0,2685** | Balance entre precisión y recall, penalizado por la precisión baja |

**⚠️ Anticipa esta pregunta tú mismo, antes de que te la hagan:** *"¿Por qué la precisión es tan baja si el ROC-AUC es casi perfecto?"*

Respuesta lista (dilo con seguridad, es una fortaleza del proyecto, no una falla):
> "Es matemáticamente esperable: solo el 0,79% de los casos son incendios reales — un desbalance extremo. Priorizamos el **Recall** a propósito, porque en gestión de emergencias **el costo de un falso negativo (no avisar de un incendio real) es mucho mayor que el de un falso positivo** (revisar una celda que resultó sin fuego). Balanceamos los pesos de clase (`class_weight='balanced'`) explícitamente para lograr ese Recall alto, sabiendo que eso baja la precisión. Es una decisión de diseño, no una limitación no controlada."

**Variables más importantes (Figura 5b) — y por qué la #4 es interesante:**
1. `dias_secos_acumulados_3m` (20,16%) — el déficit hídrico trimestral, coherente con el hallazgo de la diapositiva 10.
2. `precip_lag_2m` (18,04%) y `precip_media_movil_3m` (13,10%) — memoria hídrica antecedente.
3. **`fila` (11,50%)** — variable de índice espacial de la malla. Su alta importancia revela que **los incendios no se distribuyen uniformemente en el territorio, sino que se agrupan en franjas cantonales concretas** (coherente con el Top-5 de PostGIS, diapositiva 12, todo en la zona R030-R033). Es un hallazgo genuino, no ruido — abre trabajo futuro con variables topográficas (pendiente, orientación).

---

### Diapositiva 15 — Dashboard Interactivo en Streamlit / Plotly

**Esta diapositiva es tu puente hacia la demo en vivo — no te detengas mucho aquí, resume y pasa al navegador.** Ver la Sección 3 de esta guía para el guión completo de la demo.

Menciona solo la pieza más "de ingeniería" de esta diapositiva:

> **Innovación: Motor Dual de Consultas.** El dashboard intenta conectarse en vivo a PostgreSQL y MongoDB; si no puede (por ejemplo, en Streamlit Cloud, donde no hay esas bases de datos instaladas), conmuta automáticamente a un motor embebido SQLite con funciones PostGIS emuladas y un agregador JSON en memoria — **para que nunca se caiga la demo frente al jurado**, sin importar dónde se ejecute.

Luego: "Se los muestro en vivo" → cambia a la pestaña del navegador.

---

### Diapositiva 16 — Gobernanza, Trazabilidad y Estructura para GitHub

**Qué decir:** "Cerramos con cómo garantizamos que este proyecto sea auditable y reproducible por cualquiera, incluyendo ustedes."

- **Trazabilidad criptográfica:** cada archivo fuente tiene un hash SHA-256 verificado en `manifiesto_firelab_loja.json`.
- **Protección de fuentes de terceros:** parte de la malla y telemetría histórica (2019-2025) se tomó como **copia de solo lectura** de un proyecto científico independiente (`FIRELAB_Loja`), autorizada por decisión formal del equipo, sin modificar ni un archivo de ese repositorio.
- **Cero dependencias absolutas:** rutas relativas (`Path(__file__)`) — el docente puede clonar el repo y ejecutarlo tal cual, sin configurar rutas a mano.
- **Estructura limpia:** `datos/`, `bases_datos/`, `pipeline/`, `machine_learning/`, `dashboard/`, `entrega_final/` — cada capa con su responsabilidad.

---

### Diapositiva 17 — Conclusiones y Trabajo Futuro

Lee las 5 conclusiones con seguridad — ya las dominas porque son el resumen de todo lo anterior. Cierra con el trabajo futuro:
- Escalar a 10 años de serie histórica (2015-2025).
- Incorporar NDVI (Sentinel-2) y modelos digitales de elevación (pendiente/orientación) — **conecta esto con el hallazgo de la variable `fila`** de la diapositiva 14, así demuestras que el trabajo futuro nace de un hallazgo real, no es genérico.
- Orquestación automática con Apache Airflow.

### Diapositiva 18 — Cierre

Agradece y abre a preguntas.

---

## 2. La historia que debes tener lista aunque no esté en ninguna diapositiva

El **informe** (Sección 7.2) documenta algo que la presentación no cuenta en detalle por espacio, pero que es la evidencia más fuerte de rigor técnico del proyecto. Si alguien pregunta *"¿tuvieron algún problema durante el desarrollo?"* o *"¿por qué la precisión del modelo es tan distinta a lo que se podría esperar?"*, esta es tu mejor respuesta:

> "Durante el desarrollo detectamos que el motor Spark, al construir la variable objetivo `incendio_observado`, convertía las celdas **sin observación satelital VIIRS** (900 de 95.964, un 0,94%) en 'sin fuego' usando `coalesce`, en lugar de dejarlas como dato faltante — igual que explicamos en la diapositiva 7 que *no* debía pasar. La capa Curated en pandas sí lo hacía bien (con la bandera `apto_analisis`), pero Spark se implementó como una reintegración independiente y no heredó esa bandera. Lo corregimos: recalculamos `apto_analisis` directamente en Spark y reentrenamos el modelo excluyendo esas 900 filas. El Recall casi no cambió (95,97% vs 96,64% antes de corregir), lo que confirma que el modelo sí detecta fuegos reales — pero la Precisión bajó de 55,27% a 15,61%, porque esas 900 filas actuaban como negativos artificialmente "limpios" que inflaban la precisión sin evidencia real. El número más bajo es, paradójicamente, el más honesto."

Esto demuestra: detectas errores propios, entiendes su causa raíz, los corriges con evidencia, y comunicas el impacto con números — exactamente lo que un jurado de ciencia de datos quiere ver.

---

## 3. Guión de la demo en vivo del Dashboard

**URL:** https://fireforest-loja.streamlit.app/

**Antes de la sustentación:** abre el link tú mismo unos minutos antes. Si Streamlit Cloud lo puso a "dormir" por inactividad, tarda ~30-60 segundos en despertar la primera vez — mejor que eso pase antes, no en vivo frente al jurado.

El dashboard tiene 6 secciones en el menú lateral izquierdo. Sigue este orden (coincide con el orden lógico del proyecto):

### 🏛️ 1. Arquitectura y Motores
- Muestra los 4 KPIs de arriba: 7.997 celdas, 95.964 filas, 747 eventos de fuego, **27/27 controles de calidad cumplidos** (16 Clean + 11 Curated).
- Baja al diagrama de flujo en texto y a la tabla de justificación tecnológica — es la misma justificación de la diapositiva 9, pero interactiva. Di: *"Esta es la misma arquitectura que expliqué, ahora consumida en vivo por el dashboard."*

### 🗺️ 2. Explorador Geoespacial (7.997 celdas)
- Mueve el slider de mes a **septiembre (9)** — el mes crítico.
- Cambia la capa a **"Focos de Calor VIIRS"** y el mapa base a **"Satelital HD"**.
- Señala: el contorno cian es el límite oficial INEC, los puntos rojos son los focos reales de septiembre. Puedes mover el slider a otro mes (ej. marzo) para mostrar que el mapa cambia y no hay fuegos — refuerza el mensaje de estacionalidad.
- Menciona las capas alternativas sin necesariamente abrirlas todas: precipitación CHIRPS y grilla completa de 7.997 celdas.

### 📊 3. Consultas y Tablas (SQL / NoSQL / Spark)
- Tiene pestañas internas para SQL, NoSQL, Spark y el explorador Curated.
- Abre la pestaña de **Spark** y muestra la tabla de balance mensual — son los mismos números de tu diapositiva 11, generados en vivo.
- Abre el **explorador Curated** y usa el buscador de celda con `LJ500_R031_C075` (la celda #1 del Top-5 de PostGIS, diapositiva 12) — verán su fila completa con `apto_analisis` incluido.
- Si el jurado pregunta por SQL o MongoDB en vivo, esas pestañas también están ahí — no necesitas memorizar consultas, el dashboard ya las tiene predefinidas.

### 📉 4. Análisis Clima vs Incendios
- El gráfico de doble eje (barras de lluvia + línea de FRP) es la versión interactiva de tu diapositiva 10 — puedes pasar el mouse sobre cada mes para mostrar el valor exacto.
- El gráfico de dispersión de la derecha (días secos vs FRP) es un plus que no está en las diapositivas: muestra visualmente que los meses con más días secos (derecha del gráfico) concentran el FRP más alto — otra forma de decir "memoria hídrica".

### 🤖 5. Predictor de Riesgo (ML) — la parte más interactiva
- Aquí puedes literalmente **hacer una predicción en vivo**. Sugerencia de valores para un caso "de alto riesgo" (similar a septiembre-octubre real):
  - Mes: 9 o 10
  - Precipitación del mes actual: ~15-20 mm
  - Días secos en el mes: ~28
  - Precipitación mes anterior (lag 1m): ~20 mm
  - Precipitación hace 2 meses (lag 2m): ~18 mm
  - Días secos acumulados (3 meses): ~80
  - Fila/Columna: usa `31` y `75` (la celda con más FRP real)
- El medidor (gauge) mostrará una probabilidad alta y la clasificación en rojo ("ALTO RIESGO"). Luego cambia precipitación a un valor alto (ej. 250 mm) y días secos a 0 — el riesgo debe caer a verde. **Esto demuestra en vivo que el modelo responde de forma físicamente coherente**, no es una caja negra arbitraria.
- Arriba de los sliders verás las mismas 4 métricas de tu diapositiva 14 (ROC-AUC, Recall, F1-Score) leídas en vivo desde el modelo entrenado.

### 🛡️ 6. Auditoría y Trazabilidad
- Pestaña "Procedencia y Hashes": muestra los hashes SHA-256 reales del manifiesto de FIRELAB_Loja — **son los hashes reales, leídos en vivo del archivo JSON**, no texto de ejemplo.
- Pestaña "Controles de Calidad": resume los 16+11 controles Clean/Curated.
- Cierra la demo aquí, conecta con la diapositiva 16 (Gobernanza) que ya expusiste, y da paso a conclusiones.

**Si algo falla en vivo (conexión lenta, un gráfico no carga):** no te pongas nervioso — di *"esto es exactamente lo que resuelve el Motor Dual que mencioné: si el motor en vivo falla, conmuta automáticamente al embebido"* y recarga la página. Convierte el imprevisto en una demostración de la robustez del diseño.

---

## 4. Preguntas difíciles adicionales — banco rápido

| Pregunta probable | Respuesta corta |
|---|---|
| ¿Por qué Spark si el dataset cabe en memoria (2 MB)? | Es una decisión arquitectónica pensando en escalar (Sección 5.5 del informe): el patrón de ventanas por celda se paraleliza sin cambios de código si crece a 10 años o a más cantones — no es volumen actual, es la base reutilizable para el trabajo futuro. |
| ¿Por qué no usar solo pandas para todo? | Pandas fue de hecho el prototipo inicial (capa Curated). Spark demuestra el patrón distribuido exigido por la asignatura y es la base que sí escalaría si el proyecto creciera. |
| ¿Cómo garantizan que los datos de FIRELAB_Loja no se corrompieron al copiarlos? | Verificación de hash SHA-256 de cada archivo en el momento de la copia, documentado en el manifiesto de procedencia — es el mismo principio de integridad que usamos para todo el Raw Lake. |
| ¿Qué pasa si faltan más celdas VIIRS en el futuro? | El pipeline ya tiene la bandera `apto_analisis` diseñada exactamente para eso: se conservan como nulas y se excluyen del entrenamiento, nunca se interpretan como "sin fuego". |
| ¿Por qué el Recall es más importante que la Precisión aquí? | Contexto de gestión de emergencias: un falso negativo (incendio no detectado) tiene costo humano/ambiental; un falso positivo solo cuesta una revisión de campo. |
| ¿El modelo generaliza a otros años o cantones? | No — está validado únicamente para el cantón Loja, año 2023 (Sección 7.1 del informe lo declara explícitamente). Es una prueba de concepto reproducible, no un modelo generalizado todavía. |

---

## 5. Chuleta de números (imprime o ten a mano en el celular)

```
Malla:              7.997 celdas de 500m x 500m
Dataset:             95.964 filas celda-mes (12 meses, 2023)
Filas aptas para ML: 95.064 (excluidas 900 sin cobertura VIIRS = 0,94%)
Eventos de fuego:    747 (0,79% del dataset apto)
Split ML:            76.051 train / 19.013 test (80/20)

ROC-AUC:    0,9912
Recall:     95,97%  (143/149)
Precisión:  15,61%
F1-Score:   0,2685

Mes crítico:  Septiembre (306 celdas, 6.295,15 MW)
Trimestre crítico: Agosto-Octubre (>15.700 MW acumulados, 94% del FRP anual)
Latencia hídrica: ~86 días secos antes del pico de incendios

Controles de calidad: 27/27 (16 Clean + 11 Curated)
Motores: PostgreSQL 18/PostGIS · MongoDB 8 · Apache Spark 4.2 · Parquet/Snappy
Dashboard: Streamlit + Plotly, Motor Dual (vivo -> embebido SQLite/JSON)
```

---

## 6. Checklist de último momento

- [ ] Abrir el dashboard 10-15 min antes para que "despierte" del modo suspendido de Streamlit Cloud.
- [ ] Probar el slider del Predictor de Riesgo con los valores sugeridos de la Sección 3, una vez, antes de la sustentación.
- [ ] Tener a mano la URL del repo por si preguntan: `https://github.com/cguillermo79/FireForest`
- [ ] Repasar en voz alta al menos una vez el bloque de "diapositiva 14" y la "historia VIIRS/Spark" (Sección 2) — son las dos partes donde más te pueden presionar.
- [ ] Tener claro el orden: diapositivas 6-14 → transición en diapositiva 15 → demo en vivo (Sección 3 de esta guía) → volver a diapositivas 16-18 para cerrar.
