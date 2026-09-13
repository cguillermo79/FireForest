# 7. Auditoría final contra la guía original

Guía auditada: `00_guia/Guia_Laboratorio_NoSQL_MongoDB_3_5_puntos.pdf`
(M1721, 3,50 puntos, Grupo 04). Todos los resultados marcados como
"real" provienen de una ejecución efectiva de `mongosh`/`pdflatex`
realizada durante esta auditoría, no de valores supuestos.

## Tabla de auditoría criterio por criterio

| # / Sección guía | Requisito textual resumido | Evidencia / archivo | Comando de verificación | Resultado real | Estado | Corrección aplicada / pendiente |
|---|---|---|---|---|---|---|
| §2 | Justificación del uso de MongoDB para el caso | `01_documentacion/01_planteamiento_caso.md` | Lectura del documento | Justifica anidamiento variable, evidencia de cardinalidad fija y metadatos que evolucionan tras la carga | CUMPLE | Ninguna |
| §3 (Colección principal) | Definir colección principal y su propósito | `01_documentacion/02_diseno_documental.md` | Lectura del documento | `evidencia_viirs_celda_mes` en `taller_nosql_fireforest`, propósito declarado | CUMPLE | Ninguna |
| §3 (Documento) | Unidad documental claramente definida | `01_documentacion/02_diseno_documental.md` | Lectura del documento | Celda de 500 m observada en un mes calendario | CUMPLE | Ninguna |
| §3 (Campos) | Diseño de campos obligatorios/opcionales/variables | `01_documentacion/03_diccionario_datos.md` | Lectura del documento | Tabla completa con tipo BSON, rango y obligatoriedad de cada campo | CUMPLE | Ninguna |
| §3 (Anidamiento) | Objetos embebidos justificados | `01_documentacion/02_diseno_documental.md`, `04_embebido_vs_referencia.md` | Lectura de ambos documentos | 6 objetos anidados justificados por cardinalidad y patrón de acceso | CUMPLE | Ninguna |
| §3 (Arreglos) | Uso justificado de arreglos embebidos | `01_documentacion/02_diseno_documental.md` | `mongosh --eval "db.getSiblingDB('taller_nosql_fireforest').evidencia_viirs_celda_mes.countDocuments({evidencias:{$type:'array'}})"` | 105/105 documentos con `evidencias` tipo array | CUMPLE | Ninguna |
| §3 (Referencias) | Explicar embebido vs. referencia | `01_documentacion/04_embebido_vs_referencia.md` | Lectura del documento | Justifica explícitamente por qué NO se usan referencias/`$lookup` | CUMPLE | Ninguna |
| §4 | Documento de ejemplo completo, adaptado al caso | `01_documentacion/02_diseno_documental.md` (esquema), `05_resultados/01_validacion_carga.txt` (documento real) | `mongosh --eval "printjson(db.getSiblingDB('taller_nosql_fireforest').evidencia_viirs_celda_mes.findOne({_id:'VCM_0001'}))"` | Documento completo con 8 objetos/arreglos anidados | CUMPLE | Ninguna |
| §5.1-2 | ≥30 documentos de prueba, con variedad | `03_datos/`, `07_entrega/*.js` | `countDocuments()` | 105 documentos (≥30), 7 años, 2 estratos, valores de FRP entre 0 y 122,32 MW | CUMPLE | Ninguna |
| §5.4 | Explicar relación si hay varias colecciones | `01_documentacion/04_embebido_vs_referencia.md` | Lectura del documento | Se justifica explícitamente el uso de una única colección | CUMPLE | No aplica (una sola colección) |
| §5.5 | Código reproducible (.js/.txt/.ipynb) | `07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.js` | `mongosh "mongodb://localhost:27017" 07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.js` (× 2) | Ejecutado 2 veces; salida idéntica salvo timestamp operativo (ver auditoría técnica) | CUMPLE | Ninguna |
| §6, Nº1-2 | Dos filtros con comparadores ($gt/$gte/$lt/$in) | `04_consultas/01_consultas_1_a_10.md` consultas 1-2 | Ejecución del script | 13 y 11 registros respectivamente, con `$gt`, `$in`, `$gte`, `$elemMatch` | CUMPLE | Ninguna |
| §6, Nº3 | Proyección | Consulta 3 | Ejecución del script | 10 documentos, 5 campos proyectados | CUMPLE | Ninguna |
| §6, Nº4 | Orden y límite (`sort`+`limit`) | Consulta 4 | Ejecución del script | 5 documentos ordenados desc. por FRP máxima | CUMPLE | Ninguna |
| §6, Nº5 | Campos anidados | Consulta 5 | Ejecución del script | 10 documentos filtrados por `calidad_observacion.disponibilidad_pct` | CUMPLE | Ninguna |
| §6, Nº6 | Arreglos con `$elemMatch` | Consulta 6 | Ejecución del script | 10 documentos con `evidencias: {$elemMatch:{...}}}` | CUMPLE | Ninguna |
| §6, Nº7-8 | Pipeline `$match+$group+$sort` (2) | Consultas 7 y 8 | Ejecución del script | Agregación por mes y por año, con resultados verificados (ver más abajo) | CUMPLE | Ninguna |
| §6, Nº9 | `$project` y/o `$unwind` | Consulta 9 | Ejecución del script | `$unwind` sobre `evidencias` + `$group` + `$project` | CUMPLE | Ninguna |
| §6, Nº10 | Consulta integradora multietapa | Consulta 10 | Ejecución del script | `$match+$set+$project+$sort+$limit`, dataset plano de 15 filas | CUMPLE | Ninguna |
| §7 | Actualización de campo simple | `04_consultas/02_actualizaciones.md`, actualización 1 | Ejecución del script | `updateOne()`, matched:1, modified:1 | CUMPLE | Ninguna |
| §7 | Actualización de campo anidado/arreglo | Actualización 2 | Ejecución del script | `updateMany()` sobre `metadatos.estado_revision`, matched:70, modified:70 | CUMPLE | Ninguna |
| §7 | Incorporación de información nueva (`$set`/`$push`/`$addToSet`) | Actualización 3 | Ejecución del script | `$push` sobre `bitacora_laboratorio`, matched:105, modified:105 | CUMPLE | Ninguna |
| §7 | Explicación del efecto de cada actualización | `04_consultas/02_actualizaciones.md` | Lectura del documento | Efecto explicado para las 3 actualizaciones; se aclara que no se tocan valores satelitales | CUMPLE | Ninguna |
| §8 | Unidad de análisis definida | `01_documentacion/05_conexion_ciencia_datos.md` | Lectura del documento | Celda-mes | CUMPLE | Ninguna |
| §8 | Variable objetivo/resultado | Ídem | Lectura del documento | FRP máxima (continua) o evidencia de fuego (binaria) | CUMPLE | Ninguna |
| §8 | Variables derivadas | Ídem, consulta 10 | Ejecución del script | `frp_por_deteccion_mw`, `proporcion_nominal_alta` calculadas realmente | CUMPLE | Ninguna |
| §8 | Consulta/pipeline de extracción para ML/estadística | Consulta 10 | Ejecución del script | Dataset plano exportable a `pandas.DataFrame` | CUMPLE | Ninguna |
| §9 | Interpretación de resultados | `01_documentacion/06_interpretacion_resultados.md`, `05_resultados/05_resumen_analitico.md` | Lectura de ambos documentos | Interpretación basada en valores reales (septiembre/octubre/2023) | CUMPLE | Ninguna |
| §9 | Conclusiones | `01_documentacion/06_interpretacion_resultados.md`, informe PDF §10 | Lectura | 3 conclusiones explícitas | CUMPLE | Ninguna |
| §13 | Relación con el Proyecto Integrador | `01_documentacion/06_interpretacion_resultados.md`, informe PDF | Lectura | Se referencia `AGENTS.md` y la unidad celda-mes del proyecto | CUMPLE | Ninguna |
| §10 | PDF de 6-9 páginas sin contar portada | `07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.pdf` | `pdflatex` (salida: "Output written on ... (7 pages...)") | 7 páginas totales = 1 portada + 6 de contenido | CUMPLE (límite inferior) | Ninguna; se documenta que 6 es el mínimo del rango solicitado |
| §10 | Nombres de entregables sugeridos | `07_entrega/` | `ls 07_entrega` | `Grupo04_Laboratorio_NoSQL_MongoDB.{pdf,js,tex}` | CUMPLE | Ninguna |
| General | Legibilidad de código/resultados/capturas | Informe PDF, `04_consultas/`, `06_capturas/` | Revisión visual del PDF compilado (7 páginas, sin *overfull hbox*) | Sin desbordamientos ni advertencias en la compilación (`pdflatex`, 0 *warnings* en la última pasada) | CUMPLE | No hay capturas de pantalla reales (ver más abajo) |
| General | Reproducibilidad | `07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.js`, `README.md` | Ejecución 2 veces consecutivas | Resultados idénticos (diff vacío tras enmascarar timestamp) | CUMPLE | Ninguna |
| §6 (capturas) | Evidencia visual de colección, documento, consultas, pipeline, actualizaciones | `06_capturas/` | Inspección de la carpeta | No existen capturas de pantalla (entorno de agente sin interfaz gráfica) | CUMPLE PARCIALMENTE | Se documentó `capturas_pendientes.md` con comando exacto y resultado esperado para cada captura; pendiente que un integrante del grupo tome las capturas reales en su equipo |

## Observaciones adicionales de auditoría

1. **Archivos previos conservados como evidencia de desarrollo, no como
   entregable final:** `02_mongodb/00_dev_script_inicial_grupo04.js`
   (versión inicial, sin carga/índices/actualizaciones, escrita
   originalmente contra `fireforest`) y
   `02_mongodb/00_dev_consultas_pipelines_borrador.js` (borrador de las
   consultas 7-10). Ambos se conservaron por instrucción explícita de no
   eliminar archivos dudosos, se marcaron con una nota "SUPERADO" en su
   encabezado y se corrigió su base de datos objetivo a
   `taller_nosql_fireforest` para que no puedan ejecutarse por error
   contra `fireforest`.
2. **Aislamiento verificado respecto de `fireforest`:** antes de ejecutar
   el script definitivo se confirmó que `fireforest.evidencia_viirs_celda_mes`
   tenía 105 documentos y `fireforest.detecciones_viirs` tenía 2
   documentos; después de ejecutar el script definitivo dos veces, ambas
   colecciones **no cambiaron** (el script solo opera sobre
   `taller_nosql_fireforest`).
3. **Único punto "CUMPLE PARCIALMENTE":** la ausencia de capturas de
   pantalla reales, inevitable en un entorno de ejecución por agente sin
   interfaz gráfica. Se mitigó documentando exactamente qué capturar y
   con qué comando (`06_capturas/capturas_pendientes.md`), de modo que
   cualquier integrante del grupo pueda completarlas en minutos sobre la
   misma carga de datos (el script es idempotente).

## Estimación conservadora de la rúbrica (sobre 3,50)

| Criterio | Máximo | Estimado | Evidencia | Riesgo detectado | Acción correctiva |
|---|---:|---:|---|---|---|
| Planteamiento y justificación | 0,35 | 0,32 | `01_planteamiento_caso.md` | El caso es un subconjunto de VIIRS ya usado en el Proyecto Integrador; originalidad limitada frente a otros dominios sugeridos por la guía | Ninguna necesaria; la guía permite explícitamente reutilizar el dominio del Proyecto Integrador |
| Diseño documental | 0,70 | 0,65 | `02_diseno_documental.md`, `03_diccionario_datos.md`, `04_embebido_vs_referencia.md` | Ninguna colección de referencia real (no hay `$lookup` demostrado en la práctica, solo justificado por qué no se necesita) | Si se exige demostrar `$lookup` en la revisión, agregar una colección secundaria opcional (p. ej. catálogo de fuentes satelitales) |
| Implementación y datos | 0,45 | 0,43 | 105 documentos reales, carga verificada 2 veces, índices creados | Ninguno relevante | Ninguna |
| Consultas MongoDB | 0,80 | 0,75 | 10 consultas con pregunta/código/resultado/interpretación, resultados reales verificados | Las consultas 1-6 son en su mayoría filtros sobre el mismo campo FRP; podría objetarse poca variedad temática (aunque cumplen los operadores exigidos) | Ninguna obligatoria; se podría añadir una consulta adicional sobre `calidad_observacion` como variedad extra en una futura iteración |
| Aggregation Framework | 0,55 | 0,52 | Consultas 7-10, 2 pipelines interpretados + 1 integrador | Ninguno relevante | Ninguna |
| Actualizaciones y evolución | 0,25 | 0,24 | 3 actualizaciones con antes/después reales | Ninguno relevante | Ninguna |
| Conexión analítica e interpretación | 0,25 | 0,23 | `05_conexion_ciencia_datos.md`, `06_interpretacion_resultados.md` | Ninguno relevante | Ninguna |
| Presentación y reproducibilidad | 0,15 | 0,12 | Estructura de carpetas, README, script idempotente, PDF de 7 páginas sin errores de compilación | Faltan capturas de pantalla reales (ver punto 3 arriba) | Completar capturas siguiendo `06_capturas/capturas_pendientes.md` |
| **Total** | **3,50** | **3,26** | | | |

**Nota:** esta estimación es conservadora y no otorga automáticamente el
puntaje máximo; el único riesgo con impacto real en la nota es la
ausencia de capturas de pantalla, que es un elemento de presentación
fácilmente subsanable y no afecta la corrección técnica del taller.
