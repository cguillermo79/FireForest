# Informe de Ingeniería de Datos y Pipeline Analítico
## Proyecto Integrador: FireForest — Arquitectura Híbrida de Datos
**Grupo 04 — Maestría / Programa Académico de Ciencia de Datos**  
**Ámbito Territorial:** Cantón Loja, Ecuador (Malla 500 m × 500 m, 7.997 Celdas)  
**Periodo de Estudio:** 12 Meses (Año 2023 completo a grano celda-mes)

---

## 1. Resumen Ejecutivo e Idea Fuerza

> *"Una solución de datos no termina cuando el código corre: termina cuando los datos son confiables, trazables, útiles y comprensibles para tomar decisiones."*

El presente proyecto entrega y sustenta un **pipeline completo de ingeniería de datos orientado a analítica y aprendizaje automático**. La solución supera la fase preliminar de dos celdas del Avance 1 y opera de forma integral sobre **toda la malla espacial cantonal de Loja (7.997 celdas)**, procesando un total de **95.964 observaciones celda-mes**.

La arquitectura articula armónicamente:
1. **Ingesta y Raw Lake:** Fuentes inmutables protegidas mediante hashes SHA-256 (Malla GeoPackage, telemetría NASA FIRMS VIIRS y precipitación satelital CHIRPS).
2. **Procesamiento Distribuido con Apache Spark (PySpark):** Limpieza, agregaciones pesadas, transformaciones de series temporales (lags climáticos de 1 a 3 meses) y consultas Spark SQL.
3. **Almacenamiento Híbrido Multimodelo:**
   - **PostgreSQL / PostGIS:** Esquema dimensional en estrella con polígonos espaciales (SRID 32717) e indexación GiST.
   - **MongoDB (NoSQL):** Repositorio documental para la telemetría satelital semiestructurada con GeoJSON e índices compuestos.
   - **Data Lake (Parquet):** Almacenamiento columnar inmutable particionado por año y mes con compresión Snappy.
4. **Machine Learning:** Modelo supervisado *Random Forest* para predicción de riesgo de incendios con un **ROC-AUC de 0.9927** y un **Recall del 96.64%**.
5. **Consumo y Visualización:** Dashboard interactivo en *Streamlit / Plotly* para exploración geoespacial, análisis temporal y simulación de riesgo en tiempo real.

---

## 2. Arquitectura de Datos Implementada

```
                                ARQUITECTURA GENERAL FIREFOREST
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │ 1. FUENTES DE ENTRADA HETEROGÉNEAS                                                     │
 │    • Cartografía Vectorial: Malla maestra 500m (INEC / GeoPackage, 7.997 celdas)       │
 │    • Sensor Satelital NASA: VIIRS SNPP 375m (FRP, calidad, detecciones diarias)        │
 │    • Climatología CHIRPS: Precipitación diaria grillada a 500m (mm)                    │
 └───────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │ Ingesta controlada Python + Hash SHA-256
                                             ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │ 2. RAW LAKE & VALIDACIÓN INICIAL                                                       │
 │    • Preservación inmutable sin alterar fuentes externas (FIRELAB_Loja protegido)       │
 │    • Perfilado de tipos, rangos físicos, completitud y unicidad                        │
 └───────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │ Carga en memoria distribuida
                                             ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │ 3. PROCESAMIENTO DISTRIBUIDO CON APACHE SPARK (PySpark 4.2.0)                          │
 │    • Join espacial-temporal entre Malla, Clima e Incendios                             │
 │    • Window Functions: Lags de lluvia (1m, 2m), medias móviles (3m) y días secos       │
 │    • Detección distribuida de banderas de atípicos y condiciones de sequía             │
 └───────────────────┬───────────────────────┼───────────────────────┬────────────────────┘
                     │                       │                       │
                     ▼                       ▼                       ▼
 ┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
 │ 4. DATA LAKE (PARQUET)  │ │ 5. POSTGRESQL / POSTGIS │ │ 6. MONGODB (NoSQL)      │
 │ • Formato columnar OLAP │ │ • Malla vectorial GiST  │ │ • Telemetría GeoJSON    │
 │ • Particionado: anio/mes│ │ • fact_celda_mes analít.│ │ • Agregaciones BSON     │
 │ • 95.964 filas curadas  │ │ • Integridad PK/FK      │ │ • Consultas por doc     │
 └─────────────┬───────────┘ └───────────┬─────────────┘ └───────────┬─────────────┘
               │                         │                           │
               └─────────────────────────┼───────────────────────────┘
                                         ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │ 7. CONSUMO, ANALÍTICA AVANZADA Y APRENDIZAJE AUTOMÁTICO                                │
 │    • Machine Learning: Clasificador Random Forest (Predicción de Riesgo de Incendio)    │
 │    • Dashboard Interactivo: Streamlit + Plotly (Explorador Cartográfico y Simulador)   │
 └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Matriz de Justificación Técnica por Caso de Uso

Cumpliendo la directriz pedagógica de justificar las decisiones tecnológicas:

| Motor / Formato | Tipo de Almacenamiento | Rol en FireForest | Justificación Técnica de Selección |
|---|---|---|---|
| **PostgreSQL / PostGIS** | Relacional Objeto-Espacial (SQL) | Malla cantonal (`dim_celda`), calendario (`dim_fecha`) y hechos mensuales (`fact_celda_mes`). | Integridad referencial estricta (claves foráneas), tipos numéricos fijos, indexación espacial R-Tree/GiST sobre polígonos UTM 17S y soporte nativo para consultas relacionales OLAP con agregaciones `JOIN` y `GROUP BY`. |
| **MongoDB** | Documental NoSQL (BSON) | Colección `evidencia_viirs_celda_mes` y telemetría de eventos de calor. | Modelo de esquema flexible para capturar metadatos satelitales anidados (bandas espectrales, nivel de confianza variable, arrays de coordenadas GeoJSON) y ejecutar pipelines de agregación documental (`$match`, `$group`, `$project`). |
| **Data Lake (Parquet)** | Archivo Columnar Comprimido | Capas Raw, Clean y Curated (`curated_spark_parquet`). | Almacenamiento desacoplado de bajo costo, inmutabilidad de datos históricos, compresión eficiente Snappy (>90% de reducción frente a CSV) y lectura por proyección de columnas de alta velocidad para data science. |
| **Apache Spark (PySpark)** | Motor Distribuido en Memoria | Pipeline ETL masivo, Window Functions y cálculo de matrices analíticas. | Capacidad para procesar en paralelo grandes volúmenes de telemetría geoespacial sin desbordar la memoria de un solo nodo, ejecutando transformaciones temporales avanzadas (lags, medias móviles de 3 meses) y consultas Spark SQL. |

---

## 4. Resultados Tabulares Obtenidos en la Ejecución

### A. Resultados de Apache Spark (Spark SQL)

#### Tabla 1: Balance Cantonal Mensual (Cantón Loja - 7.997 Celdas)
```text
+---+------------+------------------------+-------------+-------------+-------------------+----------------+----------------------+
|mes|total_celdas|precip_media_cantonal_mm|precip_min_mm|precip_max_mm|dias_secos_promedio|celdas_con_fuego|frp_total_acumulado_mw|
+---+------------+------------------------+-------------+-------------+-------------------+----------------+----------------------+
|1  |7997        |64.80                   |2.97         |163.71       |21.0               |7               |17.71                 |
|2  |7997        |92.35                   |51.57        |165.30       |21.8               |0               |0.00                  |
|3  |7997        |312.28                  |93.22        |563.87       |19.0               |0               |0.00                  |
|4  |7997        |325.82                  |195.24       |783.09       |17.7               |0               |0.00                  |
|5  |7997        |29.03                   |6.98         |65.38        |28.8               |0               |0.00                  |
|6  |7997        |16.73                   |0.00         |41.44        |27.2               |16              |424.52                |
|7  |7997        |16.73                   |0.00         |49.71        |29.8               |26              |191.17                |
|8  |7997        |24.05                   |0.00         |67.49        |28.5               |143             |2512.57               |
|9  |7997        |16.61                   |8.59         |31.64        |27.4               |306             |6295.15               |
|10 |7997        |78.31                   |35.20        |128.53       |20.0               |201             |6910.86               |
|11 |7997        |68.18                   |32.69        |110.95       |22.0               |42              |347.58                |
|12 |7997        |76.65                   |28.33        |123.98       |23.8               |6               |24.77                 |
+---+------------+------------------------+-------------+-------------+-------------------+----------------+----------------------+
```
*Interpretación:* La precipitación cae drásticamente a partir de mayo (<30 mm/mes), acumulando 5 meses seguidos de sequía severa que culminan en el pico de incendios forestales en agosto, septiembre y octubre (sumando más de 15.000 MW de FRP acumulado).

#### Tabla 2: Contingencia Sequía vs Incendios en Spark
```text
+------------------------+-------------------------+-----------------------------+------------------+-------------------+
|condicion_sequia_extrema|categoria_riesgo_forestal|total_observaciones_celda_mes|casos_con_incendio|tasa_incidencia_pct|
+------------------------+-------------------------+-----------------------------+------------------+-------------------+
|true                    |ALTO_IMPACTO             |487                          |487               |100.0000 %         |
|true                    |RIESGO_ALTO_SEQUIA       |25016                        |0                 |0.0000 %           |
|false                   |ALTO_IMPACTO             |260                          |260               |100.0000 %         |
|false                   |RIESGO_MODERADO          |19944                        |0                 |0.0000 %           |
|false                   |RIESGO_BAJO              |50250                        |0                 |0.0000 %           |
+------------------------+-------------------------+-----------------------------+------------------+-------------------+
```

---

### B. Resultados en PostgreSQL / PostGIS

```text
Tabla                | Total Filas    
--------------------------------------
dim_celda            | 7,999          (7.997 celdas cantón + 2 celdas históricas prueba)
dim_fecha            | 14             (Calendario consolidado 2023)
fact_celda_mes       | 95,964         (12 meses x 7.997 celdas de Loja)
```

#### Top 5 Celdas con Mayor Radiación Térmica (FRP) y Geometría PostGIS:
```text
Celda ID         | Longitud   | Latitud    | Mes  | Precip mm  | FRP MW   | Tipo PostGIS | Área m²   
--------------------------------------------------------------------------------------------
LJ500_R031_C075  | -79.20900  | -4.36989   | 10   | 97.95      | 327.90   | ST_Polygon   | 250,000   
LJ500_R031_C076  | -79.20450  | -4.36988   | 10   | 97.95      | 246.57   | ST_Polygon   | 250,000   
LJ500_R121_C056  | -79.29546  | -3.96316   | 9    | 13.91      | 242.80   | ST_Polygon   | 250,000   
LJ500_R032_C075  | -79.20901  | -4.36537   | 10   | 97.95      | 224.25   | ST_Polygon   | 250,000   
LJ500_R031_C077  | -79.19999  | -4.36987   | 10   | 99.17      | 205.90   | ST_Polygon   | 250,000   
```

---

### C. Resultados en MongoDB (Pipelines NoSQL)

```text
Periodo      | Docs     | Fuegos   | FRP Total MW   | Precip Promedio mm
----------------------------------------------------------------------
2023-01      | 46       | 7        | 17.71          | 60.89             
2023-02      | 37       | 0        | 0.00           | 92.86             
2023-03      | 35       | 0        | 0.00           | 297.88            
2023-04      | 29       | 0        | 0.00           | 339.47            
2023-05      | 33       | 0        | 0.00           | 29.02             
2023-06      | 53       | 16       | 424.52         | 14.98             
2023-07      | 61       | 26       | 191.17         | 13.80             
2023-08      | 188      | 143      | 2512.57        | 13.98             
2023-09      | 348      | 306      | 6295.15        | 15.44             
2023-10      | 246      | 201      | 6910.86        | 84.41             
2023-11      | 75       | 42       | 347.58         | 66.85             
2023-12      | 49       | 6        | 24.77          | 75.92             
```

---

### D. Resultados del Modelo de Machine Learning

Entrenado sobre 76.771 celdas-mes y evaluado en un conjunto de prueba independiente de 19.193 celdas-mes:

| Métrica de Evaluación | Valor Obtenido | Interpretación Analítica |
|---|---|---|
| **ROC-AUC Score** | **0.9927** | Excelente capacidad de discriminación entre celdas en riesgo vs celdas seguras. |
| **Recall (Sensibilidad)** | **96.64%** | Captura 144 de los 149 focos de incendio reales del conjunto de prueba. |
| **Precision** | **14.37%** | Proporción esperable ante el desbalance extremo de clases (0.78% fuegos). |
| **F1-Score** | **0.2502** | Óptimo balance para sistemas de alerta temprana de protección civil. |

#### Matriz de Confusión:
```text
Real / Predicho      | Pred: Sin Fuego (0)  | Pred: Con Fuego (1) 
------------------------------------------------------------------
Real: Sin Fuego (0)  | 18,186               | 858                 
Real: Con Fuego (1)  | 5 (Falsos Negativos) | 144 (Aciertos)      
```

#### Importancia de Variables Predictoras (Feature Importance):
1. **Días secos acumulados en 3 meses (`dias_secos_acumulados_3m`):** 20.68%
2. **Precipitación con retraso de 2 meses (`precip_lag_2m`):** 17.74%
3. **Media móvil trimestral de lluvia (`precip_media_movil_3m`):** 12.89%
4. **Posición latitudinal / fila grilla (`fila`):** 11.52%
5. **Precipitación con retraso de 1 mes (`precip_lag_1m`):** 8.50%

*Conclusión del Modelo:* El riesgo de incendio no depende exclusivamente de si llovió en el mes en curso, sino del **déficit hídrico acumulado durante los 60 a 90 días previos**, lo cual valida la necesidad de un motor distribuido como Spark para computar estas ventanas históricas.

---

## 5. Instrucciones de Ejecución y Reproducción

Para ejecutar y validar todo el pipeline desde la raíz del proyecto:

```powershell
# 1. Activar entorno virtual
.venv\Scripts\activate

# 2. Ejecutar Pipeline Distribuido de Apache Spark
python Tareas\Proyecto_integrador\09_spark_pyspark\scripts\spark_etl_pipeline.py

# 3. Cargar en PostgreSQL / PostGIS (Malla 7.997 celdas)
python Tareas\Proyecto_integrador\03_postgresql_postgis\cargas\cargar_produccion_postgres.py

# 4. Cargar en MongoDB NoSQL y ejecutar agregaciones
python Tareas\Proyecto_integrador\04_mongodb\cargas\cargar_produccion_mongodb.py

# 5. Entrenar y evaluar el modelo de Machine Learning
python Tareas\Proyecto_integrador\10_analisis\scripts\entrenar_modelo_riesgo.py

# 6. Levantar el Dashboard Interactivo de BI
streamlit run Tareas\Proyecto_integrador\11_resultados\dashboard_fireforest.py
```

---

## 6. Conclusión y Cumplimiento

El proyecto integrador FireForest cumple a cabalidad con los cuatro productos de clase requeridos:
1. **Pipeline integrador documentado:** Totalmente reproducible y trazable de extremo a extremo.
2. **Modelo de almacenamiento híbrido:** Combinación justificada de PostgreSQL/PostGIS, MongoDB, Data Lake Parquet y Apache Spark.
3. **Dataset limpio y transformado:** Malla completa de 7.997 celdas con controles de calidad aprobados al 100%.
4. **Reporte final con interpretación y Dashboard:** Aplicación analítica visual que permite a los tomadores de decisiones anticipar el riesgo forestal en el cantón Loja.
