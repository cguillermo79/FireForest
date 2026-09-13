# 4. Decisión clave: embebido vs. referencia

La guía advierte explícitamente que "no se calificará como correcto
simplemente poner todo en un JSON". Este documento justifica, campo por
campo, por qué se embebió cada estructura y por qué **no** se usaron
colecciones adicionales ni `$lookup`.

## Criterios aplicados

1. **Cardinalidad:** ¿el dato tiene una relación 1–1 o 1–pocos fija con
   el documento, o puede crecer de forma independiente y potencialmente
   grande?
2. **Frecuencia de actualización:** ¿el dato se escribe una sola vez en
   la carga, o se modifica con frecuencia distinta al resto del
   documento?
3. **Patrón de consulta:** ¿el dato se lee siempre junto con el resto del
   documento, o se necesita consultar de forma independiente y masiva
   (por ejemplo, para paginar miles de eventos)?

## Decisiones de embebido

| Estructura | Cardinalidad | Decisión | Justificación |
|---|---|---|---|
| `celda`, `periodo`, `fuente_satelital` | 1–1 | Embebido (objeto) | Se leen siempre junto con el documento; no cambian tras la carga; no tiene sentido referenciarlos porque no se comparten entre documentos de forma que amerite deduplicación en este taller. |
| `metricas`, `calidad_observacion` | 1–1 | Embebido (objeto) | Son el resultado de una sola agregación mensual por celda; se consultan siempre junto con la identidad celda-mes (por ejemplo, en las consultas 1, 4 y 7). |
| `evidencias` | 1–2 (fijo) | Embebido (arreglo pequeño y acotado) | Cardinalidad fija y pequeña (siempre 2: `todas` y `nominal_alta`); se consulta junto con el documento (`$elemMatch`) o se aplana puntualmente (`$unwind`) solo para un pipeline analítico, no como patrón de acceso principal. |
| `muestreo` | 1–1 | Embebido (objeto) | Metadato de procedencia fijado en la carga; no se actualiza ni se consulta de forma independiente del documento. |
| `metadatos.*`, `revisado_manualmente`, `bitacora_laboratorio` | 1–1 / 1–pocos | Embebido (objeto/arreglo) | Aunque estos campos se **actualizan después de la carga** (Parte D), su cardinalidad sigue siendo pequeña y ligada al documento; no justifican una colección de auditoría aparte para un taller de este tamaño. |

## Por qué NO se usaron referencias ni colecciones adicionales

- **No existe una entidad de cardinalidad alta e independiente.** A
  diferencia de un caso como "estudiante–interacciones" (donde las
  interacciones pueden crecer sin límite y consultarse por separado, por
  ejemplo, paginadas), aquí cada celda-mes tiene como máximo 2 evidencias
  y una bitácora que crece muy lentamente (una entrada por
  reprocesamiento del taller). Separar esto en una colección aparte
  añadiría un `$lookup` sin beneficio de escritura ni de consulta.
- **No hay una entidad compartida entre documentos que amerite
  deduplicación.** La fuente satelital (`fuente_satelital`) y el método
  de muestreo (`muestreo`) son metadatos cortos y de solo lectura;
  normalizarlos en una colección de "catálogo" no reduciría
  significativamente el tamaño del documento ni simplificaría ninguna
  consulta exigida por la guía.
- **El patrón de acceso dominante es "leer/filtrar la celda-mes
  completa".** Las 10 consultas de la Parte C operan siempre sobre la
  colección `evidencia_viirs_celda_mes` como unidad; ninguna requiere
  combinar datos de una segunda colección poblada de forma independiente.

## Cuándo SÍ correspondería una referencia (para trabajo futuro)

Si el proyecto evolucionara para registrar, por ejemplo, revisiones
manuales detalladas de un equipo de varios analistas (con comentarios
extensos, adjuntos o historial largo por analista), esa bitácora
extendida sí debería moverse a una colección `revisiones_laboratorio`
referenciada por `celda_mes_id`, porque en ese escenario cambia la
cardinalidad (potencialmente muchas revisiones por documento) y el
patrón de consulta (listar revisiones de un analista sin cargar todos los
documentos celda-mes). Bajo el alcance actual del taller, esa
complejidad adicional no está justificada.
