# Capturas pendientes

Esta carpeta no contiene capturas de pantalla porque el taller se ejecutó
en un entorno de agente sin interfaz gráfica (terminal + mongosh). Todos
los resultados mostrados abajo **sí son reales**, ejecutados contra
`taller_nosql_fireforest` en MongoDB local, y están documentados
textualmente en `../05_resultados/`. Este archivo indica exactamente qué
capturar manualmente, con qué comando y qué debe verse en pantalla, para
completar la evidencia visual del informe.

No se inventaron capturas ni resultados: donde no hay imagen, hay texto
real de la ejecución.

## 1. Colección con 105 documentos (prioridad alta)

- **Herramienta sugerida:** MongoDB Compass o `mongosh`.
- **Comando:**
  ```
  mongosh "mongodb://localhost:27017/taller_nosql_fireforest" --eval "db.evidencia_viirs_celda_mes.countDocuments()"
  ```
- **Qué debe verse:** el valor `105` en la salida, y si se usa Compass,
  el contador de documentos de la colección `evidencia_viirs_celda_mes`
  dentro de la base `taller_nosql_fireforest` mostrando 105.
- **Referencia textual ya generada:** `../05_resultados/01_validacion_carga.txt` (línea "Conteo total de documentos: 105").

## 2. Documento JSON/BSON completo (prioridad alta)

- **Comando:**
  ```
  mongosh "mongodb://localhost:27017/taller_nosql_fireforest" --eval "printjson(db.evidencia_viirs_celda_mes.findOne({_id:'VCM_0001'}))"
  ```
- **Qué debe verse:** el documento completo con todos sus objetos
  anidados (`celda`, `periodo`, `fuente_satelital`, `metricas`,
  `calidad_observacion`, `evidencias`, `muestreo`, `metadatos`) y, tras
  ejecutar el script definitivo, también `bitacora_laboratorio`.
- **Referencia textual ya generada:** `../05_resultados/01_validacion_carga.txt` (sección "Documento de ejemplo completo").

## 3. Consultas representativas (prioridad media)

- **Comando (ejemplo, consulta 1):**
  ```
  mongosh "mongodb://localhost:27017/taller_nosql_fireforest" Tareas/Taller_NoSQL/07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.js
  ```
- **Qué debe verse:** el bloque `CONSULTA 1` con los documentos que
  cumplen `metricas.frp.maxima_media_mw > 20`, encabezados por `VCM_0073`
  con `122.31617512422449`.
- **Referencia textual ya generada:** `../04_consultas/01_consultas_1_a_10.md` y `../05_resultados/02_resultado_consultas_1_10.txt`.

## 4. Pipeline analítico (prioridad media)

- **Qué capturar:** el bloque `CONSULTA 7` (agregación por mes) y
  `CONSULTA 8` (agregación por año) de la misma ejecución anterior.
- **Qué debe verse:** septiembre con `frp_total_muestra_mw: 350.83` y
  octubre con `frp_promedio_mw: 30.58` y `frp_maxima_mw: 122.32`; el año
  2023 con `frp_total_muestra_mw: 349.58` y `frp_promedio_mw: 34.96`.
- **Referencia textual ya generada:** `../05_resultados/04_pipelines_agregacion.txt`.

## 5. Actualizaciones antes/después (prioridad media)

- **Comando:**
  ```
  mongosh "mongodb://localhost:27017/taller_nosql_fireforest" Tareas/Taller_NoSQL/02_mongodb/07_actualizaciones.js
  ```
- **Qué debe verse:** los tres bloques `ACTUALIZACION 1/2/3`, mostrando
  el documento antes (sin el campo) y después (con el campo agregado),
  junto con `matched`/`modified` de cada operación.
- **Referencia textual ya generada:** `../04_consultas/02_actualizaciones.md` y `../05_resultados/03_actualizaciones_antes_despues.txt`.

## Notas para quien tome las capturas

- Ejecutar siempre desde la raíz de `FireForest` para que las rutas
  relativas del script funcionen sin ajustes.
- Usar una fuente monoespaciada de tamaño legible (mínimo 11 pt) y
  recortar la ventana de la terminal para evitar líneas cortadas.
- Guardar las imágenes en esta misma carpeta con nombres descriptivos,
  por ejemplo `01_conteo_105_documentos.png`, `02_documento_completo.png`,
  etc., y luego incorporarlas al informe PDF (`07_entrega/`) en los
  lugares correspondientes de las secciones 7-11.
