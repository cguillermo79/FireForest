# Consultas MongoDB 1-10 — Taller NoSQL (Grupo 04)

Base: `taller_nosql_fireforest` · Colección: `evidencia_viirs_celda_mes` (105 documentos reales de VIIRS).

Todas las consultas incluyen un criterio de orden secundario por `_id` (o por la clave de agrupación) para evitar ambigüedad en caso de empates. El resultado completo y sin recortar de cada consulta está disponible en `../05_resultados/02_resultado_consultas_1_10.txt` (consultas 1-10) y `../05_resultados/04_pipelines_agregacion.txt` (consultas 7-10).

## Consulta 1 — Filtro (comparador $gt)

**Pregunta:** ¿Qué registros celda-mes presentan una FRP máxima superior a 20 MW?

**Código:**
```javascript
coleccion.find(
  { "metricas.frp.maxima_media_mw": { $gt: 20 } },
  { _id: 1, "celda.cell_index": 1, "periodo.anio_mes": 1,
    "metricas.frp.maxima_media_mw": 1 }
).sort({ "metricas.frp.maxima_media_mw": -1, _id: 1 }).forEach(printjson);
```

**Resultado real (ejecución en mongosh):**
```text
{
  _id: 'VCM_0073',
  celda: {
    cell_index: 1146
  },
  periodo: {
    anio_mes: '2023-10'
  },
  metricas: {
    frp: {
      maxima_media_mw: 122.31617512422449
    }
  }
}
{
  _id: 'VCM_0009',
  celda: {
    cell_index: 1415
  },
  periodo: {
    anio_mes: '2019-09'
  },
  metricas: {
    frp: {
      maxima_media_mw: 90
    }
  }
}
{
  _id: 'VCM_0066',
  celda: {
    cell_index: 5353
  },
  periodo: {
    anio_mes: '2023-08'
  },
  metricas: {
    frp: {
      maxima_media_mw: 66.5999984741211
    }
  }
}
{
  _id: 'VCM_0101',
  celda: {
    cell_index: 7104
  },
  periodo: {
    anio_mes: '2025-12'
  },
  metricas: {
    frp: {
      maxima_media_mw: 58.20000076293945
    }
  }
}
{
  _id: 'VCM_0020',
  celda: {
    cell_index: 5727
... (resultado completo en 05_resultados/02_resultado_consultas_1_10.txt)
```

**Interpretación:** 13 de los 105 registros superan 20 MW de FRP máxima; el mayor es VCM_0073 (cell_index 1146, 2023-10) con 122,32 MW, seguido por VCM_0009 (2019-09, 90 MW). Estos son los eventos de mayor intensidad térmica puntual de la muestra.

## Consulta 2 — Filtro combinado ($in, $gte, $elemMatch)

**Pregunta:** ¿Qué registros de 2023-2024 combinan FRP máxima ≥ 10 MW con evidencia nominal/alta de fuego?

**Código:**
```javascript
coleccion.find(
  {
    "periodo.anio": { $in: [2023, 2024] },
    "metricas.frp.maxima_media_mw": { $gte: 10 },
    evidencias: { $elemMatch: { categoria: "nominal_alta", evidencia_fuego: true } }
  },
  { _id: 1, "periodo.anio_mes": 1, "celda.cell_index": 1,
    "metricas.frp.maxima_media_mw": 1 }
).sort({ "periodo.fecha_inicio": 1, _id: 1 }).forEach(printjson);
```

**Resultado real (ejecución en mongosh):**
```text
{
  _id: 'VCM_0065',
  celda: {
    cell_index: 5277
  },
  periodo: {
    anio_mes: '2023-08'
  },
  metricas: {
    frp: {
      maxima_media_mw: 23.84117709889131
    }
  }
}
{
  _id: 'VCM_0066',
  celda: {
    cell_index: 5353
  },
  periodo: {
    anio_mes: '2023-08'
  },
  metricas: {
    frp: {
      maxima_media_mw: 66.5999984741211
    }
  }
}
{
  _id: 'VCM_0068',
  celda: {
    cell_index: 1297
  },
  periodo: {
    anio_mes: '2023-09'
  },
  metricas: {
    frp: {
      maxima_media_mw: 33.635443578792525
    }
  }
}
{
  _id: 'VCM_0070',
  celda: {
    cell_index: 4471
  },
  periodo: {
    anio_mes: '2023-09'
  },
  metricas: {
    frp: {
      maxima_media_mw: 10.69342118815372
    }
  }
... (resultado completo en 05_resultados/02_resultado_consultas_1_10.txt)
```

**Interpretación:** 11 registros de 2023-2024 combinan FRP relevante con evidencia de fuego nominal/alta, confirmando que la intensidad térmica alta coincide, en general, con observaciones de mayor confianza de detección.

## Consulta 3 — Proyección

**Pregunta:** ¿Cuál es la información esencial (proyección de campos) de los primeros 10 registros con fuego?

**Código:**
```javascript
coleccion.find(
  { "metricas.frp.suma_observada_media_mw": { $gt: 0 } },
  { _id: 1, "celda.cell_index": 1, "periodo.anio_mes": 1,
    "metricas.detecciones.media_todas": 1,
    "metricas.frp.suma_observada_media_mw": 1,
    "fuente_satelital.fuente_primaria": 1 }
).sort({ "periodo.fecha_inicio": 1, _id: 1 }).limit(10).forEach(printjson);
```

**Resultado real (ejecución en mongosh):**
```text
{
  _id: 'VCM_0001',
  celda: {
    cell_index: 1803
  },
  periodo: {
    anio_mes: '2019-01'
  },
  fuente_satelital: {
    fuente_primaria: 'NASA FIRMS - VIIRS'
  },
  metricas: {
    detecciones: {
      media_todas: 1
    },
    frp: {
      suma_observada_media_mw: 4.699999809265137
    }
  }
}
{
  _id: 'VCM_0002',
  celda: {
    cell_index: 1808
  },
  periodo: {
    anio_mes: '2019-03'
  },
  fuente_satelital: {
    fuente_primaria: 'NASA FIRMS - VIIRS'
  },
  metricas: {
    detecciones: {
      media_todas: 0.8235294117647058
    },
    frp: {
      suma_observada_media_mw: 6.752941019394818
    }
  }
}
{
  _id: 'VCM_0005',
  celda: {
    cell_index: 3433
  },
  periodo: {
    anio_mes: '2019-07'
  },
  fuente_satelital: {
    fuente_primaria: 'NASA FIRMS - VIIRS'
  },
  metricas: {
    detecciones: {
      media_todas: 1
    },
... (resultado completo en 05_resultados/02_resultado_consultas_1_10.txt)
```

**Interpretación:** La proyección limita la salida a los campos indispensables (celda, periodo, detecciones y FRP), útil para reportes resumidos sin exponer toda la estructura anidada.

## Consulta 4 — Orden y límite (sort + limit)

**Pregunta:** ¿Cuáles son los 5 registros celda-mes con mayor FRP máxima de toda la muestra?

**Código:**
```javascript
coleccion.find(
  {},
  { _id: 1, "celda.cell_index": 1, "periodo.anio_mes": 1,
    "metricas.frp.maxima_media_mw": 1 }
).sort({ "metricas.frp.maxima_media_mw": -1, _id: 1 }).limit(5).forEach(printjson);
```

**Resultado real (ejecución en mongosh):**
```text
{
  _id: 'VCM_0073',
  celda: {
    cell_index: 1146
  },
  periodo: {
    anio_mes: '2023-10'
  },
  metricas: {
    frp: {
      maxima_media_mw: 122.31617512422449
    }
  }
}
{
  _id: 'VCM_0009',
  celda: {
    cell_index: 1415
  },
  periodo: {
    anio_mes: '2019-09'
  },
  metricas: {
    frp: {
      maxima_media_mw: 90
    }
  }
}
{
  _id: 'VCM_0066',
... (resultado completo en 05_resultados/02_resultado_consultas_1_10.txt)
```

**Interpretación:** Los cinco registros con mayor FRP máxima absoluta están liderados por VCM_0073 (122,32 MW, 2023-10) y VCM_0009 (90 MW, 2019-09); estos casos son candidatos prioritarios para revisión manual o estudios de caso.

## Consulta 5 — Campos anidados

**Pregunta:** ¿Qué registros combinan 100% de disponibilidad de observación con al menos una detección media?

**Código:**
```javascript
coleccion.find(
  {
    "calidad_observacion.disponibilidad_pct": 100,
    "metricas.detecciones.media_todas": { $gte: 1 }
  },
  { _id: 1, "periodo.anio_mes": 1, "celda.cell_index": 1,
    "calidad_observacion.disponibilidad_pct": 1,
    "calidad_observacion.dias_validos_media": 1,
    "metricas.detecciones.media_todas": 1 }
).sort({ "metricas.detecciones.media_todas": -1, _id: 1 }).limit(10).forEach(printjson);
```

**Resultado real (ejecución en mongosh):**
```text
{
  _id: 'VCM_0009',
  celda: {
    cell_index: 1415
  },
  periodo: {
    anio_mes: '2019-09'
  },
  metricas: {
    detecciones: {
      media_todas: 2
    }
  },
  calidad_observacion: {
    dias_validos_media: 30,
    disponibilidad_pct: 100
  }
}
{
  _id: 'VCM_0073',
  celda: {
    cell_index: 1146
  },
  periodo: {
    anio_mes: '2023-10'
  },
  metricas: {
    detecciones: {
      media_todas: 2
    }
  },
  calidad_observacion: {
    dias_validos_media: 31,
    disponibilidad_pct: 100
  }
}
{
  _id: 'VCM_0001',
  celda: {
    cell_index: 1803
  },
  periodo: {
    anio_mes: '2019-01'
  },
  metricas: {
    detecciones: {
      media_todas: 1
    }
  },
  calidad_observacion: {
    dias_validos_media: 31,
    disponibilidad_pct: 100
  }
}
{
... (resultado completo en 05_resultados/02_resultado_consultas_1_10.txt)
```

**Interpretación:** Diez registros combinan disponibilidad perfecta de observación (100%) con al menos una detección media, es decir, meses en los que el satélite observó la celda de forma completa y consistente y además hubo señal de fuego.

## Consulta 6 — Arreglos ($elemMatch)

**Pregunta:** ¿Qué registros tienen evidencia de fuego nominal/alta según el arreglo `evidencias` ($elemMatch)?

**Código:**
```javascript
coleccion.find(
  { evidencias: { $elemMatch: {
      categoria: "nominal_alta", evidencia_fuego: true, detecciones_media: { $gt: 0 }
  } } },
  { _id: 1, "celda.cell_index": 1, "periodo.anio_mes": 1,
    evidencias: { $elemMatch: { categoria: "nominal_alta" } } }
).sort({ "periodo.fecha_inicio": 1, _id: 1 }).limit(10).forEach(printjson);
```

**Resultado real (ejecución en mongosh):**
```text
{
  _id: 'VCM_0002',
  celda: {
    cell_index: 1808
  },
  periodo: {
    anio_mes: '2019-03'
  },
  evidencias: [
    {
      categoria: 'nominal_alta',
      detecciones_media: 0.8235294117647058,
      presencia_fraccion: 0.8235294117647058,
      evidencia_fuego: true
    }
  ]
}
{
  _id: 'VCM_0005',
  celda: {
    cell_index: 3433
  },
  periodo: {
    anio_mes: '2019-07'
  },
  evidencias: [
    {
      categoria: 'nominal_alta',
      detecciones_media: 1,
      presencia_fraccion: 1,
      evidencia_fuego: true
    }
  ]
}
{
  _id: 'VCM_0006',
  celda: {
    cell_index: 3462
  },
  periodo: {
    anio_mes: '2019-07'
  },
  evidencias: [
    {
      categoria: 'nominal_alta',
      detecciones_media: 0.1764705882352941,
      presencia_fraccion: 0.1764705882352941,
      evidencia_fuego: true
    }
  ]
}
{
  _id: 'VCM_0007',
  celda: {
    cell_index: 1076
... (resultado completo en 05_resultados/02_resultado_consultas_1_10.txt)
```

**Interpretación:** Diez registros muestran evidencia de fuego bajo el criterio más estricto (nominal/alta) con al menos una detección media, útil para análisis que requieren mayor confianza que el criterio 'todas'.

## Consulta 7 — Agregación ($match+$group+$sort, por mes)

**Pregunta:** ¿En qué meses calendario se concentra la mayor intensidad térmica (FRP) de la muestra?

**Código:**
```javascript
coleccion.aggregate([
  { $match: { "metricas.frp.suma_observada_media_mw": { $gt: 0 } } },
  { $group: {
      _id: "$periodo.mes", registros_con_fuego: { $sum: 1 },
      frp_total_muestra_mw: { $sum: "$metricas.frp.suma_observada_media_mw" },
      frp_promedio_mw: { $avg: "$metricas.frp.suma_observada_media_mw" },
      frp_maxima_mw: { $max: "$metricas.frp.maxima_media_mw" }
  } },
  { $project: { _id: 0, mes: "$_id", registros_con_fuego: 1,
      frp_total_muestra_mw: { $round: ["$frp_total_muestra_mw", 2] },
      frp_promedio_mw: { $round: ["$frp_promedio_mw", 2] },
      frp_maxima_mw: { $round: ["$frp_maxima_mw", 2] }
  } },
  { $sort: { frp_total_muestra_mw: -1, mes: 1 } }
]).forEach(printjson);
```

**Resultado real (ejecución en mongosh):**
```text
{
  registros_con_fuego: 22,
  mes: 9,
  frp_total_muestra_mw: 350.83,
  frp_promedio_mw: 15.95,
  frp_maxima_mw: 90
}
{
  registros_con_fuego: 11,
  mes: 10,
  frp_total_muestra_mw: 336.41,
  frp_promedio_mw: 30.58,
  frp_maxima_mw: 122.32
}
{
  registros_con_fuego: 12,
  mes: 11,
  frp_total_muestra_mw: 162.65,
  frp_promedio_mw: 13.55,
  frp_maxima_mw: 36.9
}
{
  registros_con_fuego: 10,
  mes: 12,
  frp_total_muestra_mw: 113.22,
  frp_promedio_mw: 11.32,
  frp_maxima_mw: 58.2
}
{
  registros_con_fuego: 7,
  mes: 8,
  frp_total_muestra_mw: 108.24,
  frp_promedio_mw: 15.46,
  frp_maxima_mw: 66.6
}
{
  registros_con_fuego: 4,
  mes: 7,
  frp_total_muestra_mw: 49.09,
  frp_promedio_mw: 12.27,
  frp_maxima_mw: 35.2
}
{
  registros_con_fuego: 2,
  mes: 1,
  frp_total_muestra_mw: 15.4,
  frp_promedio_mw: 7.7,
  frp_maxima_mw: 10.7
}
{
  registros_con_fuego: 1,
  mes: 3,
  frp_total_muestra_mw: 6.75,
  frp_promedio_mw: 6.75,
  frp_maxima_mw: 6.75
}
{
  registros_con_fuego: 1,
  mes: 2,
  frp_total_muestra_mw: 2.34,
... (resultado completo en 05_resultados/02_resultado_consultas_1_10.txt)
```

**Interpretación:** Septiembre concentra la mayor FRP acumulada de la muestra (350,83 MW en 22 registros), mientras que octubre presenta la mayor FRP promedio por registro (30,58 MW) y el máximo absoluto (122,32 MW), lo que sugiere un pico de intensidad en octubre aunque septiembre acumula más eventos.

## Consulta 8 — Agregación ($match+$group+$sort, por año)

**Pregunta:** ¿Cómo varían las métricas de fuego (FRP, detecciones) entre los años representados en la muestra?

**Código:**
```javascript
coleccion.aggregate([
  { $match: { "metricas.frp.suma_observada_media_mw": { $gt: 0 } } },
  { $group: {
      _id: "$periodo.anio", registros_con_fuego: { $sum: 1 },
      detecciones_promedio: { $avg: "$metricas.detecciones.media_todas" },
      frp_promedio_mw: { $avg: "$metricas.frp.suma_observada_media_mw" },
      frp_total_muestra_mw: { $sum: "$metricas.frp.suma_observada_media_mw" },
      frp_maxima_mw: { $max: "$metricas.frp.maxima_media_mw" }
  } },
  { $project: { _id: 0, anio: "$_id", registros_con_fuego: 1,
      detecciones_promedio: { $round: ["$detecciones_promedio", 3] },
      frp_promedio_mw: { $round: ["$frp_promedio_mw", 2] },
      frp_total_muestra_mw: { $round: ["$frp_total_muestra_mw", 2] },
      frp_maxima_mw: { $round: ["$frp_maxima_mw", 2] }
  } },
  { $sort: { frp_total_muestra_mw: -1, anio: 1 } }
]).forEach(printjson);
```

**Resultado real (ejecución en mongosh):**
```text
{
  registros_con_fuego: 10,
  anio: 2023,
  detecciones_promedio: 0.733,
  frp_promedio_mw: 34.96,
  frp_total_muestra_mw: 349.58,
  frp_maxima_mw: 122.32
}
{
  registros_con_fuego: 10,
  anio: 2020,
  detecciones_promedio: 0.654,
  frp_promedio_mw: 20.12,
  frp_total_muestra_mw: 201.22,
  frp_maxima_mw: 52.6
}
{
  registros_con_fuego: 10,
  anio: 2019,
  detecciones_promedio: 0.834,
  frp_promedio_mw: 18.05,
  frp_total_muestra_mw: 180.51,
  frp_maxima_mw: 90
}
{
  registros_con_fuego: 10,
  anio: 2024,
  detecciones_promedio: 0.661,
  frp_promedio_mw: 14.89,
  frp_total_muestra_mw: 148.86,
  frp_maxima_mw: 36.9
}
{
  registros_con_fuego: 10,
  anio: 2025,
  detecciones_promedio: 0.626,
  frp_promedio_mw: 11.91,
  frp_total_muestra_mw: 119.12,
  frp_maxima_mw: 58.2
}
{
  registros_con_fuego: 10,
  anio: 2021,
  detecciones_promedio: 0.494,
  frp_promedio_mw: 8.69,
  frp_total_muestra_mw: 86.91,
  frp_maxima_mw: 35.2
}
{
  registros_con_fuego: 10,
  anio: 2022,
  detecciones_promedio: 0.448,
  frp_promedio_mw: 5.87,
  frp_total_muestra_mw: 58.74,
  frp_maxima_mw: 16.64
... (resultado completo en 05_resultados/02_resultado_consultas_1_10.txt)
```

**Interpretación:** 2023 combina la mayor FRP acumulada (349,58 MW) y la mayor FRP promedio (34,96 MW) entre los siete años representados, mientras que 2022 presenta los valores más bajos (58,74 MW acumulados, 5,87 MW promedio) dentro de la muestra estratificada.

## Consulta 9 — Transformación ($unwind)

**Pregunta:** ¿Qué diferencias existen entre la evidencia de fuego total y la evidencia nominal/alta?

**Código:**
```javascript
coleccion.aggregate([
  { $unwind: "$evidencias" },
  { $group: {
      _id: "$evidencias.categoria", documentos_evaluados: { $sum: 1 },
      documentos_con_fuego: { $sum: { $cond: ["$evidencias.evidencia_fuego", 1, 0] } },
      detecciones_promedio: { $avg: "$evidencias.detecciones_media" },
      presencia_promedio: { $avg: "$evidencias.presencia_fraccion" }
  } },
  { $project: { _id: 0, categoria: "$_id", documentos_evaluados: 1,
      documentos_con_fuego: 1,
      detecciones_promedio: { $round: ["$detecciones_promedio", 3] },
      presencia_promedio: { $round: ["$presencia_promedio", 3] }
  } },
  { $sort: { categoria: 1 } }
]).forEach(printjson);
```

**Resultado real (ejecución en mongosh):**
```text
{
  documentos_evaluados: 105,
  documentos_con_fuego: 68,
  categoria: 'nominal_alta',
  detecciones_promedio: 0.408,
  presencia_promedio: 0.384
}
{
  documentos_evaluados: 105,
  documentos_con_fuego: 70,
  categoria: 'todas',
  detecciones_promedio: 0.424,
  presencia_promedio: 0.4
}
```

**Interpretación:** Sobre 105 documentos evaluados (tras $unwind), 70 tienen evidencia de fuego bajo el criterio 'todas' y 68 bajo 'nominal_alta'; las detecciones y presencia promedio son levemente menores bajo el criterio más estricto, como es esperable.

## Consulta 10 — Consulta integradora (múltiples etapas)

**Pregunta:** ¿Cómo se obtiene un dataset plano celda-mes, con variables derivadas, para análisis estadístico o ML?

**Código:**
```javascript
coleccion.aggregate([
  { $match: {
      "metricas.frp.suma_observada_media_mw": { $gt: 0 },
      "calidad_observacion.disponibilidad_pct": { $gte: 95 }
  } },
  { $set: {
      frp_por_deteccion_mw: { $cond: [
        { $gt: ["$metricas.detecciones.media_todas", 0] },
        { $divide: ["$metricas.frp.suma_observada_media_mw",
                    "$metricas.detecciones.media_todas"] }, 0
      ] },
      proporcion_nominal_alta: { $cond: [
        { $gt: ["$metricas.detecciones.media_todas", 0] },
        { $divide: ["$metricas.detecciones.media_nominal_alta",
                    "$metricas.detecciones.media_todas"] }, 0
      ] }
  } },
  { $project: {
      _id: 0, registro_id: "$_id", cell_index: "$celda.cell_index",
      anio: "$periodo.anio", mes: "$periodo.mes", anio_mes: "$periodo.anio_mes",
      detecciones_media: { $round: ["$metricas.detecciones.media_todas", 3] },
      frp_total_media_mw: { $round: ["$metricas.frp.suma_observada_media_mw", 2] },
      frp_maxima_mw: { $round: ["$metricas.frp.maxima_media_mw", 2] },
      frp_por_deteccion_mw: { $round: ["$frp_por_deteccion_mw", 2] },
      proporcion_nominal_alta: { $round: ["$proporcion_nominal_alta", 3] },
      disponibilidad_pct: "$calidad_observacion.disponibilidad_pct",
      presencia_fuego: { $literal: 1 }
  } },
  { $sort: { frp_total_media_mw: -1, registro_id: 1 } },
  { $limit: 15 }
]).forEach(printjson);
```

**Resultado real (ejecución en mongosh):**
```text
{
  registro_id: 'VCM_0073',
  cell_index: 1146,
  anio: 2023,
  mes: 10,
  anio_mes: '2023-10',
  detecciones_media: 2,
  frp_total_media_mw: 188.27,
  frp_maxima_mw: 122.32,
  frp_por_deteccion_mw: 94.14,
  proporcion_nominal_alta: 1,
  disponibilidad_pct: 100,
  presencia_fuego: 1
}
{
  registro_id: 'VCM_0009',
  cell_index: 1415,
  anio: 2019,
  mes: 9,
  anio_mes: '2019-09',
  detecciones_media: 2,
  frp_total_media_mw: 104.4,
  frp_maxima_mw: 90,
  frp_por_deteccion_mw: 52.2,
  proporcion_nominal_alta: 1,
  disponibilidad_pct: 100,
  presencia_fuego: 1
}
{
  registro_id: 'VCM_0066',
  cell_index: 5353,
  anio: 2023,
  mes: 8,
  anio_mes: '2023-08',
  detecciones_media: 1,
  frp_total_media_mw: 66.6,
  frp_maxima_mw: 66.6,
  frp_por_deteccion_mw: 66.6,
  proporcion_nominal_alta: 1,
  disponibilidad_pct: 100,
  presencia_fuego: 1
}
{
  registro_id: 'VCM_0101',
  cell_index: 7104,
  anio: 2025,
  mes: 12,
  anio_mes: '2025-12',
  detecciones_media: 1,
  frp_total_media_mw: 58.2,
  frp_maxima_mw: 58.2,
  frp_por_deteccion_mw: 58.2,
  proporcion_nominal_alta: 1,
  disponibilidad_pct: 96.7741928100586,
  presencia_fuego: 1
}
{
  registro_id: 'VCM_0020',
  cell_index: 5727,
  anio: 2020,
  mes: 9,
  anio_mes: '2020-09',
  detecciones_media: 1,
  frp_total_media_mw: 52.6,
  frp_maxima_mw: 52.6,
  frp_por_deteccion_mw: 52.6,
  proporcion_nominal_alta: 1,
  disponibilidad_pct: 100,
  presencia_fuego: 1
}
{
  registro_id: 'VCM_0024',
  cell_index: 1644,
  anio: 2020,
  mes: 10,
  anio_mes: '2020-10',
  detecciones_media: 1,
  frp_total_media_mw: 44.8,
  frp_maxima_mw: 44.8,
  frp_por_deteccion_mw: 44.8,
  proporcion_nominal_alta: 1,
  disponibilidad_pct: 100,
  presencia_fuego: 1
}
{
  registro_id: 'VCM_0034',
  cell_index: 4675,
  anio: 2021,
  mes: 7,
  anio_mes: '2021-07',
... (resultado completo en 05_resultados/02_resultado_consultas_1_10.txt)
```

**Interpretación:** El pipeline integrador combina $match, $set (variables derivadas) y $project para producir un dataset plano de registros con fuego y alta disponibilidad, ordenado por FRP total; el primer registro (VCM_0073, 2023-10) coincide con el de mayor FRP máxima identificado en las consultas 1, 4 y 8, dando consistencia cruzada al análisis.
