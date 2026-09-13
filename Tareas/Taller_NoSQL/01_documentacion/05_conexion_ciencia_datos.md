# 5. Conexión con Ciencia de Datos (Parte 8 de la guía)

## Unidad de análisis

Una **fila del dataset analítico final** representa una **celda espacial
de 500 m observada durante un mes calendario** (celda-mes), identificada
por `celda.cell_index + periodo.anio + periodo.mes`. Esta es la misma
unidad de análisis declarada para todo el Proyecto Integrador FireForest
(ver `AGENTS.md`), lo que permite que este componente NoSQL se integre
directamente con el componente SQL sin redefinir la granularidad.

## Variable objetivo o resultado

Se proponen dos variables objetivo posibles, ambas ya presentes en la
colección:

1. **Variable continua:** `metricas.frp.maxima_media_mw` — la intensidad
   térmica máxima observada en la celda-mes, útil para modelos de
   regresión o para identificar los eventos más severos (consultas 1 y
   4).
2. **Variable binaria:** `evidencias[categoria="todas"].evidencia_fuego`
   — presencia/ausencia de fuego en la celda-mes, útil para modelos de
   clasificación (por ejemplo, predecir la probabilidad de fuego a partir
   de variables climáticas o de cobertura en el futuro Proyecto
   Integrador).

## Variables derivadas

Ya calculadas en la consulta integradora (consulta 10) mediante `$set`:

- `frp_por_deteccion_mw` = FRP total observado ÷ detecciones medias:
  intensidad térmica normalizada por número de detecciones, para
  comparar celdas con distinto número de pasadas satelitales válidas.
- `proporcion_nominal_alta` = detecciones nominal/alta ÷ detecciones
  totales: fracción de las detecciones que tienen alta confianza,
  utilizable como indicador de calidad/confiabilidad de la señal de
  fuego en esa celda-mes.

Otras variables derivadas posibles para trabajo futuro (no calculadas en
este taller, pero extraíbles con el mismo patrón de pipeline):
frecuencia de meses con fuego por celda en una ventana de varios años, o
razón entre FRP máxima y FRP acumulada (indicador de concentración vs.
dispersión temporal del evento).

## Extracción para análisis estadístico o aprendizaje automático

La **consulta 10** (`04_consultas/01_consultas_1_a_10.md`) es exactamente
el mecanismo de extracción: un pipeline de agregación con `$match`
(filtra observaciones con fuego y disponibilidad ≥ 95 %), `$set`
(variables derivadas) y `$project` (aplanamiento a columnas simples),
que produce un **dataset plano** —una fila por celda-mes con columnas
escalares— directamente exportable a pandas (`list(coleccion.aggregate([...]))`
→ `pandas.DataFrame`) o a CSV/Parquet para entrenar un modelo. Esto
resuelve exactamente la pregunta guía de la Parte 8: "¿qué consulta o
pipeline permitiría obtener un dataset plano o resumido para análisis
estadístico/ML?".

## Limitaciones de la muestra estratificada para este propósito

Como la muestra es estratificada (10 casos con fuego + 5 sin fuego por
año, ver `03_datos/README.md`), **cualquier modelo entrenado
directamente sobre esta muestra estimaría probabilidades de fuego
sesgadas al alza** (66,7 % de positivos en la muestra, proporción que no
representa la incidencia real). Para un uso real en el Proyecto
Integrador, sería necesario: (a) recalibrar las probabilidades con la
tasa base real de la población, o (b) extraer una muestra aleatoria
simple (no estratificada) o la población completa antes de modelar.
