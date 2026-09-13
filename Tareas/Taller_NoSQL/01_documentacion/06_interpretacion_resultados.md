# 6. Interpretación de resultados

Todos los valores citados aquí provienen de la ejecución real de
`07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.js` contra
`taller_nosql_fireforest.evidencia_viirs_celda_mes`; el detalle línea por
línea está en `05_resultados/`.

## Carga y estructura documental

La carga de los 105 documentos fue completa y consistente: 105 `_id`
únicos, 105 combinaciones celda-año-mes únicas, 105 fechas BSON, 105
objetos `metricas` anidados, 105 arreglos `evidencias` y 105 booleanos
`metadatos.datos_simulados`. Esto confirma que el diseño documental
(objetos anidados + arreglo de evidencias) se mantiene íntegro para el
100 % de la muestra, sin documentos parciales ni con tipos BSON
inconsistentes.

## Distribución con/sin evidencia de fuego

70 documentos (66,7 %) presentan evidencia de fuego bajo el criterio
amplio (`todas`) y 35 (33,3 %) no la presentan; bajo el criterio más
estricto (`nominal_alta`) el número de documentos con fuego baja
ligeramente a 68. Esta distribución **es consecuencia directa del diseño
de muestreo estratificado (10/5 por año)** y no debe leerse como una
estimación de la incidencia real de incendios en el cantón Loja (ver
`03_datos/README.md`).

## Estacionalidad e interanualidad

- **Septiembre** concentra la mayor FRP acumulada de la muestra (350,83
  MW en 22 registros con fuego), lo que sugiere que, dentro de esta
  muestra, septiembre es el mes con más eventos de fuego detectados
  aunque no necesariamente los más intensos individualmente.
- **Octubre** presenta la mayor FRP promedio por registro (30,58 MW) y el
  valor máximo absoluto de la muestra (122,32 MW), lo que indica que,
  aunque haya menos eventos que en septiembre (11 registros), estos
  tienden a ser más intensos.
- **2023** combina la mayor FRP acumulada (349,58 MW) y la mayor FRP
  promedio (34,96 MW) entre los siete años representados, distinguiéndose
  como el año de mayor intensidad térmica dentro de la muestra.

## Evidencia total vs. nominal/alta

Al comparar ambos criterios de confianza (consulta 9), las detecciones y
la presencia promedio son consistentemente menores bajo `nominal_alta`
(0,408 y 0,384) que bajo `todas` (0,424 y 0,400). Esto es coherente con
la definición de ambos criterios: `nominal_alta` es un subconjunto más
exigente de `todas`, por lo que sus promedios no pueden superar a los del
criterio amplio.

## Consistencia cruzada

El documento `VCM_0073` (celda 1146, 2023-10) aparece de forma consistente
como el caso más extremo en tres consultas independientes: es el de mayor
FRP máxima (consultas 1 y 4), pertenece al año con mayor FRP promedio
(consulta 8) y encabeza el dataset plano de la consulta integradora
(consulta 10) con el mayor FRP total (188,27 MW). Esta consistencia entre
consultas construidas de forma independiente es una señal de que el
modelo documental y las consultas están correctamente alineados con los
datos reales.

## Conclusiones

1. El modelo documental (objetos anidados + arreglo `evidencias` de
   cardinalidad fija) fue suficiente para responder las 10 consultas y
   los 2+ pipelines exigidos sin necesidad de colecciones adicionales.
2. Los metadatos operativos del laboratorio (`estado_revision`,
   `revisado_manualmente`, `bitacora_laboratorio`) se incorporaron de
   forma incremental mediante actualizaciones (`$set`, `$push`) sin
   afectar ningún valor satelital, demostrando que el esquema soporta
   evolución posterior a la carga.
3. Los resultados analíticos (estacionalidad en septiembre-octubre,
   2023 como año de mayor intensidad) son observaciones válidas
   **dentro de esta muestra estratificada** y sirven como prueba de
   concepto de las agregaciones que el Proyecto Integrador podría
   ejecutar sobre la población completa de celdas-mes.

## Relación con la arquitectura del Proyecto Integrador

Este taller reutiliza la unidad de análisis celda-mes definida en
`AGENTS.md` del Proyecto Integrador FireForest y demuestra el componente
MongoDB de su arquitectura híbrida SQL–NoSQL (`README.md` raíz): los
mismos pipelines de agregación usados aquí (consulta 10) son el patrón
que, en el proyecto completo, alimentaría el dataset analítico
celda-mes junto con las tablas de hechos de PostgreSQL/PostGIS
(`fact_incendio`, `fact_clima`), sin necesidad de rediseñar la unidad de
análisis ni el esquema documental.
