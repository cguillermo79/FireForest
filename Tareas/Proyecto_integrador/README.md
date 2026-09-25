# FireForest: Pipeline de Ingeniería de Datos y Arquitectura Híbrida

> **Escuela Superior Politécnica de Chimborazo (ESPOCH)**  
> **Maestría en Estadística con mención en Ciencia de Datos e Inteligencia Artificial**  
> **Proyecto Integrador — Grupo 04**  
> **Autores:** Marco Vinicio Malan Mullo, Viviana Isabel Pujos Culque, Carlos Guillermo Chuncho Morocho  
> **Ámbito Territorial:** Cantón Loja, Ecuador (Malla Espacial 500 m × 500 m | 7.997 Celdas | 95.964 Observaciones)  
> **Periodo Analizado:** Año 2023 completo a grano celda-mes

---

## 1. Propósito y Resumen Ejecutivo

El proyecto **FireForest** entrega y sustenta un **pipeline completo de ingeniería de datos orientado a analítica geoespacial y aprendizaje automático**. Superando la fase preliminar de 2 celdas del Avance 1, la solución final opera de forma integral sobre **toda la malla espacial cantonal de Loja (7.997 celdas)**, procesando un total de **95.964 observaciones celda-mes**.

La arquitectura articula armónicamente:
1. **Ingesta Inmutable y Trazabilidad (SHA-256):** Fuentes protegidas (malla INEC, telemetría NASA FIRMS VIIRS 375 m y climatología UCSB CHIRPS v2.0).
2. **Procesamiento Distribuido con Apache Spark (PySpark 4.2):** Window Functions distribuidas para calcular retardos climáticos (`lag` de 1 y 2 meses), medias móviles trimestrales (`avg(3m)`) y acumulación de días secos.
3. **Almacenamiento Híbrido Multimodelo:**
   - **PostgreSQL 18 / PostGIS:** Esquema dimensional en estrella (`dim_celda`, `dim_fecha`, `fact_celda_mes`) con polígonos espaciales (SRID 32717) e indexación GiST.
   - **MongoDB 8 (NoSQL):** Repositorio documental semiestructurado para telemetría satelital BSON (`evidencia_viirs_celda_mes`) con índices 2dsphere y pipelines de agregación nativos.
   - **Data Lakehouse (Apache Parquet):** Formato columnar inmutable particionado por año y mes con compresión Snappy.
4. **Machine Learning Supervisado:** Clasificador *Random Forest* entrenado sobre 76.771 filas y evaluado sobre 19.193 filas de prueba, alcanzando un **ROC-AUC de 0,9927** y un **Recall del 96,64%** en la detección de celdas con incendio.
5. **Dashboard Interactivo (Streamlit / Plotly):** Interfaz analítica con imágenes satelitales fotográficas de alta resolución (estilo Google Earth), vectorización del perímetro oficial del cantón Loja (INEC) y un **Motor Dual de Consultas** (ejecución en vivo contra PostgreSQL/MongoDB o mediante base SQLite/JSON embebida para despliegue sin dependencias externas).

---

## 2. Estructura Limpia del Repositorio (GitHub)

Para facilitar la revisión autónoma por parte del docente o evaluador, el repositorio organiza sus artefactos en componentes funcionales estandarizados:

```text
Proyecto_integrador/
│
├── README.md                      <-- Guía maestra y documentación de ejecución autónoma
├── requirements.txt               <-- Dependencias oficiales de Python
├── .env.example                   <-- Variables de entorno de referencia (Postgres, Mongo)
│
├── bases_datos/                   <-- Módulo de Almacenamiento Híbrido (SQL + NoSQL)
│   ├── sql_postgis/               <-- DDL, índices GiST y scripts de carga en PostgreSQL/PostGIS
│   ├── nosql_mongodb/             <-- Documentos BSON, scripts y pipelines de agregación en MongoDB
│   └── fireforest_standalone.db   <-- Base SQLite embebida (95.964 filas) para evaluación autónoma
│
├── datos/                         <-- Repositorio de datos del proyecto
│   ├── raw/                       <-- Perímetro cantonal oficial INEC (limite_canton_loja_wgs84.geojson)
│   └── curated/                   <-- Datasets analíticos Parquet (fireforest_celda_mes_2023.parquet, malla_500m.parquet)
│
├── pipeline/                      <-- Pipeline de Ingeniería de Datos y Cómputo Distribuido
│   ├── ejecutar_pipeline.py       <-- Orquestador para verificar todo el pipeline en 1 solo comando
│   ├── spark_etl_pipeline.py      <-- Pipeline en PySpark (Window Functions, lags climáticos, Data Lake)
│   └── curated_spark_parquet/     <-- Data Lakehouse Parquet particionado generado por Spark (anio/mes)
│
├── machine_learning/              <-- Modelado Predictivo y Evaluación Estadística
│   ├── entrenar_modelo_riesgo.py  <-- Script de entrenamiento estratificado y validación
│   ├── modelo_random_forest_fireforest.joblib <-- Modelo serializado de Random Forest
│   └── metricas_ml.json           <-- Métricas cuantitativas (ROC-AUC: 0.9927, Recall: 96.64%)
│
├── dashboard/                     <-- Aplicación de visualización y consulta interactiva
│   ├── app.py                     <-- Dashboard Streamlit con mapa satelital HD, tablas interactivas y descarga Excel/CSV
│   ├── requirements.txt           <-- Dependencias de despliegue cloud
│   └── logos/                     <-- Logos oficiales ESPOCH y Maestría
│
├── entrega_final/                 <-- Sustentación formal, código LaTeX y documentos compilados
│   ├── informe/                   <-- Código fuente LaTeX (informe_final.tex), figuras y logos
│   ├── presentacion/              <-- Presentación Beamer LaTeX (presentacion_final.tex)
│   └── pdf_finales/               <-- PDFs oficiales listos para descarga y sustentación:
│       ├── Grupo04_InformeFinal_ProyectoIntegrador.pdf
│       └── Grupo04_PresentacionFinal_ProyectoIntegrador.pdf
│
└── fases_desarrollo_historico/    <-- Archivo cronológico del desarrollo del semestre (00_ a 14_ y tarea_ETL)
```

---

## 3. Guía de Ejecución Autónoma (Quickstart para el Docente)

El proyecto está diseñado para ser **100% autónomo**: no requiere rutas absolutas locales ni credenciales preconfiguradas.

### Opción A: Ejecutar el Dashboard Interactivo (Recomendado)
Para explorar de inmediato los mapas satelitales, simular riesgo con Machine Learning y generar tablas SQL/NoSQL:

```bash
# 1. Instalar dependencias básicas (si no están instaladas)
pip install -r requirements.txt

# 2. Lanzar la aplicación interactiva
streamlit run dashboard/app.py
```
> **Nota de Alta Disponibilidad:** Si su computadora no tiene instalados o activos los servicios de PostgreSQL o MongoDB, el dashboard lo detecta de inmediato y conmuta automáticamente a su **motor local embebido** (`bases_datos/fireforest_standalone.db`), permitiendo ejecutar todas las consultas SQL y agregaciones NoSQL en milisegundos sin configuraciones complejas.

### Opción B: Ejecutar el Pipeline Distribuido de Apache Spark
Para procesar las 95.964 observaciones, calcular las ventanas temporales (lags) y regenerar el Data Lakehouse Parquet:

```bash
python pipeline/spark_etl_pipeline.py
```

### Opción C: Re-entrenar el Modelo de Machine Learning
Para entrenar el clasificador Random Forest, evaluar la matriz de confusión y regenerar las curvas ROC:

```bash
python machine_learning/entrenar_modelo_riesgo.py
```

---

## 4. Diccionario de Variables Analíticas y Unidades

El dataset curado combina variables geoespaciales, climáticas antecedente y de telemetría de fuego:

| Variable | Tipo de Dato | Fuente Origen | Descripción y Método de Transformación | Unidad de Medida |
|---|---|---|---|---|
| `cell_id` | String | Malla INEC | Identificador matricial de celda de 500 m × 500 m (`LJ500_Rxxx_Cyyy`) | Código / Texto |
| `longitud` | Float | Malla INEC | Coordenada horizontal del centroide de celda en WGS84 | Grados decimales ($^\circ$) |
| `latitud` | Float | Malla INEC | Coordenada vertical del centroide de celda en WGS84 | Grados decimales ($^\circ$) |
| `area_dentro_loja_ha` | Float | Malla INEC | Superficie de celda dentro del cantón Loja (intersección espacial) | Hectáreas (ha) |
| `anio` | Int | Calendario | Año calendario de observación (2023) | Año |
| `mes` | Int | Calendario | Mes calendario de observación (1 a 12) | Mes (1--12) |
| `precipitacion_acumulada_mm` | Float | CHIRPS v2.0 | Suma mensual de lluvia asignada espacialmente a la celda | Milímetros (mm) |
| `dias_secos_lt1mm` | Int | CHIRPS v2.0 | Conteo mensual de días con lluvia menor a 1 mm | Días (d) |
| `precip_lag_1m` | Float | Spark Window | Lluvia acumulada del mes inmediato anterior (`lag(1)`) | Milímetros (mm) |
| `precip_lag_2m` | Float | Spark Window | Lluvia acumulada 2 meses atrás (`lag(2)`) | Milímetros (mm) |
| `precip_media_movil_3m` | Float | Spark Window | Media móvil de precipitación en la ventana deslizante trimestral | Milímetros (mm) |
| `dias_secos_acumulados_3m` | Int | Spark Window | Días secos acumulados en la ventana trimestral móvil | Días (d) |
| `detecciones_incendio` | Float | NASA FIRMS | Conteo mensual de anomalías térmicas satelitales VIIRS 375 m | Conteo (N) |
| `frp_total_mw` | Float | NASA FIRMS | Potencia Radiativa del Fuego (*Fire Radiative Power*) acumulada | Megavatios (MW) |
| `frp_maxima_mw` | Float | NASA FIRMS | Pico máximo de radiación térmica registrado en la celda-mes | Megavatios (MW) |
| `incendio_observado` | Boolean | Derivada | Presencia real de fuego confirmada (`frp_total_mw > 0`) | Clase binaria $\{0, 1\}$ |
| `probabilidad_riesgo_ml` | Float | Random Forest | Estimación probabilística de riesgo generada por el modelo ML | Probabilidad $[0, 1]$ |

---

## 5. Resultados Tabulares y Analíticos Destacados

### Balance Cantonal Mensual (Procesado por Apache Spark)
Muestra la dinámica climática frente a la severidad de incendios a lo largo de 2023 en las 7.997 celdas:

| Mes | Total Celdas | Precip. Media (mm) | Lag 1m (mm) | Media Móvil 3m (mm) | Días Secos 3m | Celdas con Fuego | FRP Acumulado (MW) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 7.997 | 64,80 | 64,80 | 64,80 | 21,0 d | 7 | 17,71 |
| 2 | 7.997 | 92,35 | 64,80 | 78,57 | 42,8 d | 0 | 0,00 |
| 3 | 7.997 | 312,28 | 92,35 | 156,48 | 61,8 d | 0 | 0,00 |
| 4 | 7.997 | 325,82 | 312,28 | 243,48 | 58,5 d | 0 | 0,00 |
| 5 | 7.997 | 29,03 | 325,82 | 222,38 | 65,5 d | 0 | 0,00 |
| 6 | 7.997 | 16,73 | 29,03 | 123,86 | 73,7 d | 16 | 424,52 |
| 7 | 7.997 | 16,73 | 16,73 | 20,83 | 85,8 d | 26 | 191,17 |
| **8** | **7.997** | **9,73** | **16,73** | **14,40** | **86,2 d** | **109** | **2.512,60** |
| **9** | **7.997** | **19,84** | **9,73** | **15,43** | **86,1 d** | **353** | **8.683,16** |
| **10** | **7.997** | **50,60** | **19,84** | **26,72** | **84,3 d** | **148** | **3.411,46** |
| 11 | 7.997 | 84,95 | 50,60 | 51,80 | 78,4 d | 88 | 1.458,94 |
| 12 | 7.997 | 123,89 | 84,95 | 86,48 | 69,9 d | 0 | 0,00 |

> **Hallazgo Clave:** Los incendios en Loja no ocurren inmediatamente al comenzar el descenso pluviométrico de mayo; requieren un tiempo de **latencia de 2 a 3 meses de sequía continuada** (acumulación de más de 86 días secos en el trimestre), detonando la máxima severidad térmica entre agosto y octubre con **14.607 MW acumulados** (87% del total anual).

### Métricas del Modelo de Machine Learning (Test Set: 19.193 celdas-mes)
- **ROC-AUC:** **0,9927** (Capacidad discriminante casi perfecta).
- **Recall / Sensibilidad:** **96,64%** (144 de 149 incendios reales detectados en el conjunto ciego).
- **F1-Score:** **0,7029**.
- **Top Predictores (Gini Importance):**
  1. `dias_secos_acumulados_3m` ($20,68\%$): Memoria de estiaje trimestral.
  2. `precipitacion_acumulada_mm` ($18,45\%$): Lluvia del mes en curso.
  3. `precip_lag_1m` ($15,92\%$): Retardo pluviométrico del mes previo.

---

## 6. Documentos Académicos Entregables

En la carpeta `entrega_final/pdf_finales/` se encuentran disponibles los documentos finales en formato PDF de alta calidad, compilados a partir de sus fuentes LaTeX:

- 📄 **Informe Final:** [`Grupo04_InformeFinal_ProyectoIntegrador.pdf`](entrega_final/pdf_finales/Grupo04_InformeFinal_ProyectoIntegrador.pdf)  
  *Documento académico completo de 12 páginas con definición del problema, pregunta de investigación, objetivos, metodología, arquitectura multimodelo, diccionario exhaustivo de variables con unidades de medida, tablas de resultados (Spark, PostGIS, MongoDB, ML) y conclusiones.*
- 📊 **Presentación Final:** [`Grupo04_PresentacionFinal_ProyectoIntegrador.pdf`](entrega_final/pdf_finales/Grupo04_PresentacionFinal_ProyectoIntegrador.pdf)  
  *Presentación formal en formato Beamer 16:9 con la paleta de colores institucional de la ESPOCH, diagramas arquitectónicos y visualización de resultados para defensa académica.*

---

## 7. Trazabilidad y Principios de Integridad

- **Protección de Datos Científicos:** El proyecto no modifica repositorios externos de investigación (`FIRELAB_Loja`); utiliza copias independientes verificadas criptográficamente.
- **Auditoría de Ingesta:** Todos los hashes de entrada y metadatos de transformación se encuentran documentados y verificados.
- **Reproducibilidad:** Cada cálculo y visualización es determinístico y reproducible mediante código abierto.
