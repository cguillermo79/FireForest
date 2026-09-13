# 1. Planteamiento del caso

## Problema ambiental

Los incendios forestales en el cantón Loja generan información
heterogénea: detecciones satelitales puntuales, agregados espaciales y
temporales, indicadores de calidad de observación y metadatos de
procedencia que cambian de granularidad según la fuente. Consolidar esta
información en una única estructura documental —celda espacial (500 m) ×
mes— permite responder preguntas operativas (¿dónde y cuándo hay más
intensidad de fuego?) y analíticas (¿qué variables explican la
variabilidad de la intensidad térmica entre celdas y periodos?) sin
forzar un esquema relacional rígido sobre datos que varían en forma
(número de evidencias, disponibilidad de observación, metadatos
operativos que se agregan después de la carga inicial).

Este laboratorio es el componente NoSQL de la arquitectura preliminar del
Proyecto Integrador FireForest (ver `AGENTS.md` y el `README.md` de la
raíz del proyecto), que declara la celda-mes como unidad de análisis
central del proyecto.

## Qué información se necesita almacenar

Para cada celda de 500 m observada en un mes concreto se necesita
almacenar: la identidad espacial y temporal de la observación, la fuente
satelital y su versión, las métricas de detección de fuego (número de
detecciones, presencia fraccional, radiación de fuego —FRP—), la calidad
de la observación (disponibilidad, días válidos), la evidencia de fuego
bajo dos criterios de confianza distintos (todas las detecciones vs.
únicamente nominal/alta confianza), el método de muestreo utilizado para
construir el conjunto de prueba, y metadatos operativos del laboratorio
que evolucionan después de la carga (estado de revisión, bitácora de
procesamiento).

## Por qué esta información es más natural como documento que como tablas

- El número de **evidencias por criterio de confianza** (`evidencias`)
  puede crecer o cambiar de contenido sin alterar el resto del
  documento; representarlo como un arreglo embebido evita una tabla de
  unión adicional para un caso de cardinalidad pequeña y fija por
  documento.
- Los **metadatos operativos** (`metadatos.estado_revision`,
  `bitacora_laboratorio`) se agregan de forma incremental **después** de
  la carga inicial (ver Parte D — actualizaciones), un patrón de
  escritura parcial que encaja mejor con `$set`/`$push` sobre un
  documento que con `ALTER TABLE` o tablas de auditoría adicionales.
- Los objetos anidados (`celda`, `periodo`, `fuente_satelital`,
  `metricas`, `calidad_observacion`, `muestreo`) agrupan atributos que
  **siempre se consultan y se leen juntos** como una sola unidad
  celda-mes, lo que en MongoDB se resuelve con un único `findOne()` en
  lugar de varios `JOIN`.

## Preguntas operativas y analíticas que responde MongoDB en este taller

1. **Operativa:** ¿qué registros celda-mes superan un umbral de FRP
   relevante (por ejemplo, 20 MW) y en qué periodo ocurrieron? (consultas
   1 y 4).
2. **Analítica:** ¿en qué meses calendario y en qué años se concentra la
   mayor intensidad térmica de la muestra, y cómo varía la evidencia de
   fuego entre el criterio amplio y el criterio nominal/alta de
   confianza? (consultas 7, 8 y 9).

Ambas preguntas se responden con el mismo documento base
(`evidencia_viirs_celda_mes`), sin necesidad de colecciones adicionales,
lo que confirma que el modelo documental es adecuado para este caso.
