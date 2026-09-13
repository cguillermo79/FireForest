# Resumen analítico — Taller NoSQL MongoDB (Grupo 04)

Fuente: resultados reales obtenidos al ejecutar
`07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.js` contra
`taller_nosql_fireforest.evidencia_viirs_celda_mes` (105 documentos).
Detalle completo en `02_resultado_consultas_1_10.txt` y
`04_pipelines_agregacion.txt`.

## Carga e integridad

- Documentos cargados: **105** (verificado con `countDocuments()`).
- `_id` únicos: **105**.
- Combinaciones celda–año–mes únicas: **105** (respaldadas por el índice
  único `ux_celda_anio_mes`).
- Fechas BSON (`periodo.fecha_inicio`): **105**.
- Objetos anidados (`metricas`): **105**.
- Arreglos (`evidencias`): **105**.
- Booleanos (`metadatos.datos_simulados`): **105**.
- Con evidencia de fuego (categoría `todas`): **70**.
- Sin evidencia de fuego (categoría `todas`): **35**.
- Con evidencia nominal/alta: **68**.
- FRP máxima de la muestra: **122,32 MW** (documento `VCM_0073`, celda
  1146, periodo 2023-10).

## Patrones estacionales (consulta 7 — agregación por mes calendario)

- **Septiembre** concentra la mayor FRP acumulada de la muestra:
  **350,83 MW** en 22 registros con fuego.
- **Octubre** presenta la mayor FRP promedio por registro: **30,58 MW**,
  y el valor máximo absoluto de la muestra: **122,32 MW**.
- Los meses de julio a diciembre concentran la gran mayoría de los
  registros con fuego (56 de 70), consistente con una estación seca
  más prolongada en el segundo semestre dentro de esta muestra.

## Patrones interanuales (consulta 8 — agregación por año)

- **2023** presenta simultáneamente la mayor FRP acumulada
  (**349,58 MW**) y la mayor FRP promedio (**34,96 MW**) entre los años
  representados en la muestra.
- 2022 muestra los valores más bajos de FRP acumulada (58,74 MW) y
  promedio (5,87 MW) entre los con evidencia de fuego.

## Evidencia total vs. nominal/alta (consulta 9 — `$unwind`)

- Sobre 105 documentos evaluados, 70 tienen evidencia de fuego bajo el
  criterio amplio (`todas`) y 68 bajo el criterio más estricto
  (`nominal_alta`).
- Las detecciones y presencia promedio son ligeramente menores bajo el
  criterio nominal/alta (0,408 y 0,384) que bajo el criterio total
  (0,424 y 0,400), como es esperable al exigir mayor confianza de
  detección.

## Dataset analítico (consulta 10 — integradora)

- El pipeline integrador produce un dataset plano por celda-mes con
  variables derivadas (`frp_por_deteccion_mw`, `proporcion_nominal_alta`)
  listo para análisis estadístico o modelos de aprendizaje automático,
  filtrando por disponibilidad de observación ≥ 95 % y presencia de
  fuego.
- El registro con mayor FRP total (`VCM_0073`, 188,27 MW, 2023-10) fue
  también identificado como el de mayor FRP máxima en la consulta 1 y
  en la consulta 8 (año 2023), lo que da consistencia cruzada entre
  consultas independientes.

## Limitación obligatoria

La muestra es **estratificada** (10 casos con fuego y 5 sin fuego por
año, semilla 2026) y **no debe interpretarse como una estimación de la
prevalencia real de incendios en el cantón Loja**. Los porcentajes
70/35 (66,7 % con fuego) son un artefacto del diseño muestral, no una
proporción poblacional. Ver `03_datos/README.md` y
`01_documentacion/01_planteamiento_caso.md` para el detalle del
método de muestreo y sus límites.
