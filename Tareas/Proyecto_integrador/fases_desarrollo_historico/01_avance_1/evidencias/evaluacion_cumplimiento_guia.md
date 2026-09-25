# Evaluación de cumplimiento — Avance 1 vs. guía

**Documento evaluado:** `../entrega/Grupo04_AvanceProyectoIntegrador.pdf`
**Guía de referencia:** `../guia/Guia_Avance_Proyecto_Integrador.pdf`
**Fecha de la evaluación:** 2026-09-13 (posterior a la entrega; evaluación
interna del equipo, realizada durante la auditoría técnica de la
reorganización del repositorio).

> **Esta evaluación es una estimación interna del equipo, no una
> calificación oficial del docente.** Se elaboró comparando, punto por
> punto, el contenido real del PDF entregado contra cada requisito
> textual de la guía. Ni el PDF entregado ni `../fuente/avance1.tex` se
> modificaron para producir este documento.

> **Nota posterior (2026-09-15):** una validación territorial
> determinó que las celdas controladas usadas en el informe entregado
> (`LJ_04521`, `LJ_04522`) no pertenecen al cantón Loja. El informe
> entregado se conserva intacto, sin modificar; el detalle completo del
> hallazgo y su corrección (aplicada solo en la presentación, el guion
> y la documentación técnica posteriores, no en este informe) está en
> `fe_de_erratas_territorial.md`, en esta misma carpeta. Actualización
> (2026-09-14): la sustitución por `LJ_TEST_001`/`LJ_TEST_002` ya se
> aplicó de forma **permanente** en PostgreSQL (`COMMIT` real,
> verificado en conexión nueva) y en MongoDB; ver
> `03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`
> §5.

## 1. Requisitos formales

| Requisito de la guía | Evidencia en la entrega | Estado |
|---|---|---|
| Modalidad: trabajo grupal | Portada lista 3 integrantes (Malan Mullo, Pujos Culque, Chuncho Morocho), Grupo 4 | CUMPLE |
| Entrega: un archivo PDF por grupo | Un único archivo PDF (`Grupo04_AvanceProyectoIntegrador.pdf`) | CUMPLE |
| Nombre del archivo: `GrupoXX_AvanceProyectoIntegrador.pdf` | Nombre real: `Grupo04_AvanceProyectoIntegrador.pdf` — coincide exactamente con el patrón | CUMPLE |

## 2. Extensión

La guía recomienda **5 a 8 páginas, sin contar portada**. El documento
entregado tiene **9 páginas en total: 1 portada + 8 páginas de
contenido** (secciones 1 a 9, incluyendo referencias). Contando solo
las páginas de contenido (sin portada), son **8 páginas**, que
corresponde exactamente al **límite superior** del rango recomendado.

**Estado: CUMPLE** (en el límite superior del rango; no lo excede).

## 3. Definición del problema (sección 1 de la guía)

La guía exige: contexto, población/institución/proceso, objetivo
general, usuarios/beneficiarios, y una o más preguntas.

| Elemento exigido | Sección en la entrega | Estado |
|---|---|---|
| Contexto y situación que motiva el proyecto | 1.1 | CUMPLE |
| Población, institución, proceso o sistema involucrado | 1.2 (incluye nota explícita de que es un ejercicio académico sin convenio real) | CUMPLE |
| Objetivo general del proyecto | 1.3 | CUMPLE |
| Usuarios o beneficiarios potenciales | 1.4 (3 grupos de beneficiarios) | CUMPLE |
| Una o más preguntas que podrían responderse con los datos | 1.5: 1 pregunta principal de arquitectura + 3 preguntas analíticas derivadas | CUMPLE (excede el mínimo de una pregunta) |

**Estado global: CUMPLE.**

## 4. Inventario de las tres fuentes (sección 3 de la guía)

La guía exige mínimo 3 fuentes, combinando estructurada/semiestructurada/no
estructurada, cada una con: origen, estructura, tipo de captura,
formato, metadatos, almacenamiento y riesgos.

| Fuente | Origen | Tipo | Captura | Formato | Metadatos | Almacenamiento | Riesgos | Estado |
|---|---|---|---|---|---|---|---|---|
| Malla espacial (2.1) | Malla de ejemplo/controlada; fuente institucional definitiva **pendiente** para Avance 2 | Geoespacial estructurado | Manual/una vez (SIG o Python) | GeoJSON/GeoPackage/CSV | Resolución, EPSG, fecha de generación | PostgreSQL/PostGIS (`dim_celda`) | Geometrías inválidas, CRS incorrecto | CUMPLE, con pendiente explícito (fuente institucional) |
| VIIRS (2.2) | NASA FIRMS, VIIRS Active Fire ~375 m | Observacional espacio-temporal | Automática (API/descarga) | CSV/JSON | Sensor, fecha/hora, FRP, `fire_mask` | MongoDB (detalle) + PostgreSQL (diario) | Duplicados, falsos positivos, cambios de API, reprocesamiento | CUMPLE, con pendiente explícito (producto/campo de calidad exactos, ver `../../14_gestion/decisiones_metodologicas.md`) |
| CHIRPS (2.3) | Climate Hazards Center (UCSB), CHIRPS v2.0 | Climático espacio-temporal | Automática | CSV/GeoTIFF/Parquet | Producto/versión, unidad, periodo | PostgreSQL (`fact_clima`) + Parquet | Valores faltantes, cambios en el repositorio | CUMPLE |

Las tres fuentes combinan datos geoespaciales, observacionales y
climáticos, con formatos y almacenamientos distintos (PostgreSQL y
MongoDB), cumpliendo la recomendación de heterogeneidad. Se incluye
además una "Aclaración y riesgos transversales" (no exigida
explícitamente, mérito adicional) que distingue ocurrencia, frecuencia
e intensidad.

**Estado global: CUMPLE.**

## 5. Diseño SQL vs. NoSQL (sección 4 de la guía)

| Elemento de la tabla-guía | Contenido en la entrega | Estado |
|---|---|---|
| Entidades | 3.1: `dim_celda`, `dim_fecha`, `fact_incendio`, `fact_clima` (SQL); `detecciones_viirs` (NoSQL) | CUMPLE |
| Relaciones | 3.2: FKs explícitas, `UNIQUE(celda_id, fecha_id)`, aclara que la integración Mongo→Postgres no es por FK sino por ETL | CUMPLE |
| SQL: datos estables/relacionales | 3.3 (fila SQL) | CUMPLE |
| NoSQL: datos flexibles/anidados | 3.3 (fila NoSQL) | CUMPLE |
| Consulta: qué preguntas resuelve el sistema | 3.5, con ejemplo de SQL y de agregación MongoDB | CUMPLE |
| ¿Por qué SQL / por qué NoSQL? (exigido explícitamente) | 3.4, un párrafo para cada tecnología | CUMPLE |

**Observación de forma:** la guía organiza estos elementos en una única
tabla (incluyendo la fila "ML: unidad de análisis"); la entrega los
distribuye en subsecciones (3.1–3.5) y traslada la unidad de análisis a
la sección 6. El contenido está completo, solo cambia la organización
visual respecto a la tabla sugerida — no es un incumplimiento.

**Estado global: CUMPLE.**

## 6. Modelo preliminar (sección 5 de la guía)

| Requisito | Evidencia | Estado |
|---|---|---|
| Tablas principales | 4.1: `dim_celda`, `dim_fecha`, `fact_incendio`, `fact_clima` | CUMPLE |
| Clave primaria de cada tabla | Columna PK en la tabla 4.1 (`celda_id`, `fecha_id`, `incendio_id`, `clima_id`) | CUMPLE |
| Principales claves foráneas | Columna FK en la misma tabla | CUMPLE |
| Relaciones entre tablas | Enumeradas debajo de la tabla (1–N en ambos sentidos) | CUMPLE |
| Ejemplo de documento JSON (NoSQL) | 4.3, documento completo de `detecciones_viirs` con campos anidados (`coordenadas`, `calidad`) | CUMPLE |

Adicionalmente, la entrega incluye un diccionario de variables (4.2,
no exigido explícitamente) con variables almacenadas y derivadas —
mérito adicional que facilita la trazabilidad hacia la corrección de
la consulta SQL (ver sección 13).

**Estado global: CUMPLE (con mérito adicional).**

## 7. Arquitectura (sección 6 de la guía)

La guía exige un diagrama que muestre el flujo desde el origen hasta el
uso analítico, identificando fuentes, captura, almacenamiento,
procesamiento, integración y producto analítico.

La entrega (sección 5, Figura 1) presenta un diagrama de 9 etapas:
Fuentes → Ingesta → Validación y limpieza → Estandarización temporal y
espacial → Almacenamiento → Agregación celda-mes → Integración →
Dataset analítico → Estadística/ML/Dashboard. Cubre los 6 elementos
exigidos por la guía y añade dos etapas intermedias (validación,
estandarización) no exigidas pero coherentes con el resto del
documento.

**Estado: CUMPLE (con mérito adicional).**

## 8. Pregunta analítica y unidad de análisis (sección 7 de la guía)

| Requisito | Evidencia | Estado |
|---|---|---|
| Al menos una pregunta analítica resoluble con estadística/visualización/ML | Sección 6: "¿Existe relación entre la precipitación acumulada mensual y la ocurrencia de incendios por celda espacial?" (más 2 preguntas adicionales en 1.5) | CUMPLE |
| Unidad de análisis del dataset final | Sección 6: "celda espacial de 500 m × 500 m observada durante un mes (clave `celda_id + anio + mes`)" | CUMPLE |

**Estado: CUMPLE.**

## 9. Dataset esperado

No es una sección obligatoria por nombre en la guía, pero está
implícita en "cuál será mi dataset final" (pregunta guía del avance) y
en el criterio de evaluación "dataset esperado". La entrega lo describe
explícitamente en la sección 6: tabla/archivo Parquet o CSV, una fila
por celda-mes, con identificador de celda, coordenadas, detecciones e
intensidad (FRP), y precipitación acumulada/media/máxima del mes.

**Estado: CUMPLE.**

## 10. Plan preliminar de implementación (sección 8 de la guía)

La guía exige una tabla de 8 etapas con actividad y resultado esperado.
La entrega (sección 7) reproduce las mismas 8 etapas de la guía y añade
una columna "Estado" (Completado / Pendiente), más un mapeo explícito
a Avance 1 / Avance 2 / Informe final. Esto es consistente con
`14_gestion/plan_implementacion.md` (el mismo documento fuente, ya
reubicado como archivo técnico activo del proyecto).

**Estado: CUMPLE (con mérito adicional: columna de estado y mapeo a entregas).**

## 11. Lista de comprobación de la guía (sección 11)

| Ítem de la guía | Verificación | Estado |
|---|---|---|
| ☐ Problema definido con claridad, abordable con datos | Sección 1 completa | ✅ |
| ☐ ≥3 fuentes descritas (origen, tipo, captura, formato, metadatos, almacenamiento, riesgos) | Sección 2, las 3 fuentes con los 7 atributos | ✅ |
| ☐ Justificación de qué va en SQL y qué en NoSQL | Sección 3.4 | ✅ |
| ☐ Esquema relacional preliminar + ejemplo JSON | Secciones 4.1 y 4.3 | ✅ |
| ☐ Arquitectura con flujo completo fuente→producto analítico | Sección 5, Figura 1 | ✅ |
| ☐ Pregunta analítica + unidad de análisis coherente | Sección 6 | ✅ |
| ☐ Plan de implementación con etapas y resultados esperados | Sección 7 | ✅ |
| ☐ Archivo final en PDF con el nombre solicitado | `Grupo04_AvanceProyectoIntegrador.pdf` | ✅ |

**8 de 8 ítems de la lista de comprobación se cumplen.**

## 12. Evaluación según la rúbrica (estimación interna, no oficial)

| Criterio | Máximo | Estimación |
|---|---:|---:|
| Definición y justificación del problema | 0,40 | 0,40 |
| Inventario y caracterización de fuentes | 0,60 | 0,58 |
| Diseño y justificación SQL-NoSQL | 0,60 | 0,60 |
| Modelo y arquitectura preliminar | 0,60 | 0,55 |
| Pregunta, unidad y dataset esperado | 0,40 | 0,40 |
| Plan, coherencia y presentación | 0,40 | 0,37 |
| **Total** | **3,00** | **2,90** |

**Justificación de los descuentos menores:**

- *Inventario de fuentes (0,58/0,60):* la fuente institucional
  definitiva de la malla y el producto/campo de calidad exacto de VIIRS
  quedan pendientes de confirmar (declarado explícitamente en la propia
  entrega, sección 2.1 y 2.2); es una honestidad metodológica correcta,
  pero técnicamente el inventario aún no está 100% cerrado.
- *Modelo y arquitectura (0,55/0,60):* el ejemplo SQL ilustrativo de la
  sección 3.5 usa un `JOIN` directo entre `fact_incendio` y
  `fact_clima` a grano diario que, de aplicarse tal cual sin la agregación
  mensual previa que describe el propio texto, tendría el mismo
  problema que se detectó y corrigió en el archivo técnico completo
  (`consultas/consulta_01_incendios_clima_mensual.sql`, ver sección 13
  más abajo): perder celda-meses con clima pero sin incendio. El texto
  aclara que es "ilustrativo" y remite a la versión completa, lo cual
  mitiga el impacto, pero introduce una pequeña inconsistencia entre el
  fragmento mostrado y el comportamiento correcto ya documentado en la
  sección 4.1 (nota de granularidad).
- *Plan y presentación (0,37/0,40):* presentación sobria y ordenada,
  con tablas y un diagrama (cumple la recomendación de no ser solo
  texto); el pequeño descuento refleja que el plan, al ser preliminar,
  no anticipa todavía el hallazgo metodológico de la sección 13.

**Total estimado: 2,90 / 3,00.** Esta estimación es interna y no
reemplaza la calificación que asigne el docente.

## 13. Corrección técnica encontrada durante esta auditoría

Al revisar el archivo técnico referenciado en la sección 3.5 de la
entrega (`consultas/consulta_01_incendios_clima_mensual.sql`), se
detectó que la consulta completa (no el fragmento ilustrativo del PDF)
usaba `INNER JOIN` entre las agregaciones mensuales de incendio y
clima, lo que descartaba celda-meses con precipitación pero sin
incendio — es decir, trataba "ausencia de incendio" como "dato
faltante". **Se corrigió el archivo técnico** (no el PDF ni el `.tex`)
para usar `LEFT JOIN` desde el clima hacia el incendio, con
`COALESCE(..., 0)`. El detalle completo, incluyendo la validación con
`EXPLAIN` y una prueba en transacción revertida, está en
`../../14_gestion/decisiones_metodologicas.md`.

Este hallazgo **no invalida el Avance 1**: la guía indica explícitamente
que "no se requiere todavía un diseño definitivo" y que las consultas
del avance son ilustrativas. Se registra aquí porque afecta la
precisión de la sección 3.5 de la entrega y debe corregirse de forma
consistente para el Avance 2.

## 14. Fortalezas

1. **Coherencia de punta a punta:** el documento sigue exactamente la
   cadena "problema → fuentes → SQL/NoSQL → modelo → arquitectura →
   pregunta/unidad → plan", tal como pide la "pregunta guía del avance"
   de la sección 1 de la guía.
2. **Honestidad metodológica:** declara explícitamente qué es dato de
   ejemplo/controlado y qué queda pendiente para Avance 2 (fuente de la
   malla, producto VIIRS exacto), en vez de simular que ya está resuelto.
3. **Nota de granularidad temporal (4.1):** explica con precisión los
   tres niveles (detección individual, registro diario, dataset
   celda-mes), evitando una confusión común en este tipo de diseños.
4. **Aclaración conceptual:** distingue explícitamente ocurrencia,
   frecuencia e intensidad de incendio (no exigido por la guía, pero
   evita una interpretación errónea de los datos).
5. **Referencias académicas y técnicas citadas** (NASA FIRMS, CHIRPS,
   PostgreSQL, PostGIS, MongoDB) — no exigidas explícitamente por la
   guía, mérito adicional de rigor.

## 15. Observaciones

1. El fragmento SQL ilustrativo (sección 3.5) no reflejaba, tal como
   está escrito, la agregación mensual previa por CTE que sí se
   implementó en el archivo técnico completo; esto pudo generar una
   impresión ligeramente distinta a la lógica real de la consulta.
2. Los pendientes de la fuente 1 (malla) y fuente 2 (VIIRS) — fuente
   institucional definitiva, producto/versión exactos, campo de calidad
   real (`fire_mask` vs. `confidence`) — están declarados en el texto
   pero no tienen todavía una fecha ni responsable asignado.
3. La organización de la sección 4 (Diseño comparativo) usa subsecciones
   en lugar de la tabla de 6 filas sugerida por la guía; el contenido
   está completo, es solo una diferencia de formato.

## 16. Correcciones requeridas para el Avance 2

1. Corregir y validar la consulta mensual de forma consistente en todo
   el proyecto (✅ ya corregida en el archivo técnico durante esta
   auditoría; pendiente reflejar el mismo patrón en el futuro pipeline
   de integración celda-mes de `07_etl_integracion/`).
2. Confirmar la fuente institucional definitiva del límite del cantón
   Loja, con fecha de descarga, versión y sistema de referencia
   documentados.
3. Confirmar el producto VIIRS exacto y el campo de calidad real
   (`fire_mask`, `confidence` u otro) antes de fijar el criterio de
   filtrado, evitando mezclar campos de productos distintos.
4. Construir el panel completo celda-mes usando `LEFT JOIN` desde una
   base completa (clima o el producto cartesiano celda × mes), no desde
   los incendios, para no perder celda-meses sin fuego.
5. Diferenciar de forma explícita, en el diseño del dataset integrado,
   "ausencia de incendio" (`0`) de "dato realmente faltante" (`NULL`
   documentado).

Ver el detalle operativo de cada uno de estos puntos en
`../../14_gestion/tareas_pendientes.md` y
`../../14_gestion/decisiones_metodologicas.md`.

## 17. Addendum (2026-09-13) — Evaluación de la versión corregida

Se generó una versión corregida del informe
(`../fuente/avance1_corregido.tex` /
`../entrega/Grupo04_AvanceProyectoIntegrador_corregido.pdf`, **pendiente
de aprobación**, sin sustituir la entrega original) que aplica las
correcciones 1–5 descritas en `../../14_gestion/decisiones_metodologicas.md`.
Esta sección **no reemplaza** la evaluación de las secciones 1–16
(que sigue describiendo la entrega original tal como fue presentada);
es una estimación adicional, igualmente interna y no oficial, aplicable
solo a la versión corregida.

| Criterio | Máximo | Original | Corregida |
|---|---:|---:|---:|
| Definición y justificación del problema | 0,40 | 0,40 | 0,40 |
| Inventario y caracterización de fuentes | 0,60 | 0,58 | 0,59 |
| Diseño y justificación SQL-NoSQL | 0,60 | 0,60 | 0,60 |
| Modelo y arquitectura preliminar | 0,60 | 0,55 | 0,60 |
| Pregunta, unidad y dataset esperado | 0,40 | 0,40 | 0,40 |
| Plan, coherencia y presentación | 0,40 | 0,37 | 0,39 |
| **Total** | **3,00** | **2,90** | **2,98** |

**Justificación de las mejoras:**

- *Inventario de fuentes (0,59):* la descripción de los pendientes
  (fuente de la malla, producto/campo VIIRS) es ahora más precisa y
  técnicamente verificada (se documentó incluso la discrepancia real de
  EPSG 4326 vs. 32717 en los datos de ejemplo), pero los pendientes en
  sí siguen sin resolverse, por lo que no llega al máximo.
- *Modelo y arquitectura (0,60):* se corrigió la inconsistencia entre
  el ejemplo SQL ilustrativo y la agregación mensual real (ahora usa
  `LEFT JOIN` + `COALESCE`, validado con `EXPLAIN` y ejecución real), y
  se corrigió la oración del ejemplo JSON que afirmaba una agregación
  directa a celda-mes. Sin inconsistencias detectadas.
- *Plan, coherencia y presentación (0,39):* se añadió la aclaración de
  ausencia de incendio vs. dato faltante y la nota sobre el panel
  `celda × mes` del Avance 2, reforzando la coherencia; se retiene un
  descuento mínimo porque la versión corregida aún no ha sido
  aprobada ni verificada por el docente.

**Nueva estimación total: 2,98 / 3,00** (interna, no oficial;
condicionada a que las correcciones sean aprobadas).
