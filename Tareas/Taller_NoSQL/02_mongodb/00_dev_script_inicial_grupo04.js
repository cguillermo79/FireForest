// NOTA: version inicial de desarrollo (solo consultas 1-10, sin carga,
// sin indices y sin actualizaciones). Escrita originalmente contra la
// base 'fireforest' de uso interno del Proyecto Integrador. SUPERADA
// por el entregable definitivo 07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.js,
// que es autosuficiente y usa exclusivamente 'taller_nosql_fireforest'.
// Se conserva unicamente como evidencia del proceso de desarrollo
// (ver 01_documentacion/07_auditoria_guia.md); NO ejecutar tal cual.
// Laboratorio NoSQL MongoDB - Grupo 04
// Base: fireforest | Coleccion: evidencia_viirs_celda_mes

const coleccion = db.evidencia_viirs_celda_mes;

function titulo(numero, pregunta) {
  print("\n==================================================");
  print(`CONSULTA ${numero}`);
  print(pregunta);
  print("==================================================");
}

// 1. Filtro: FRP maxima superior a 20 MW.
titulo(1, "Registros con FRP maxima superior a 20 MW");
coleccion.find(
  { "metricas.frp.maxima_media_mw": { $gt: 20 } },
  { _id: 1, "celda.cell_index": 1, "periodo.anio_mes": 1,
    "metricas.frp.maxima_media_mw": 1 }
).sort({ "metricas.frp.maxima_media_mw": -1, _id: 1 }).forEach(printjson);

// 2. Filtro combinado: anios, umbral FRP y evidencia nominal/alta.
titulo(2, "Registros de 2023 y 2024 con evidencia nominal/alta y FRP >= 10 MW");
coleccion.find(
  {
    "periodo.anio": { $in: [2023, 2024] },
    "metricas.frp.maxima_media_mw": { $gte: 10 },
    evidencias: { $elemMatch: { categoria: "nominal_alta", evidencia_fuego: true } }
  },
  { _id: 1, "periodo.anio_mes": 1, "celda.cell_index": 1,
    "metricas.frp.maxima_media_mw": 1 }
).sort({ "periodo.fecha_inicio": 1, _id: 1 }).forEach(printjson);

// 3. Proyeccion: campos esenciales de diez registros con fuego.
titulo(3, "Informacion esencial de diez registros con evidencia de fuego");
coleccion.find(
  { "metricas.frp.suma_observada_media_mw": { $gt: 0 } },
  { _id: 1, "celda.cell_index": 1, "periodo.anio_mes": 1,
    "metricas.detecciones.media_todas": 1,
    "metricas.frp.suma_observada_media_mw": 1,
    "fuente_satelital.fuente_primaria": 1 }
).sort({ "periodo.fecha_inicio": 1, _id: 1 }).limit(10).forEach(printjson);

// 4. Orden y limite: cinco registros con mayor FRP.
titulo(4, "Cinco registros celda-mes con mayor FRP maxima");
coleccion.find(
  {},
  { _id: 1, "celda.cell_index": 1, "periodo.anio_mes": 1,
    "metricas.frp.maxima_media_mw": 1 }
).sort({ "metricas.frp.maxima_media_mw": -1, _id: 1 }).limit(5).forEach(printjson);

// 5. Campos anidados: disponibilidad y detecciones.
titulo(5, "Registros con 100 % de disponibilidad y al menos una deteccion media");
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

// 6. Arreglos: evidencia nominal/alta mediante elemMatch.
titulo(6, "Registros con evidencia de fuego nominal/alta");
coleccion.find(
  { evidencias: { $elemMatch: {
      categoria: "nominal_alta", evidencia_fuego: true, detecciones_media: { $gt: 0 }
  } } },
  { _id: 1, "celda.cell_index": 1, "periodo.anio_mes": 1,
    evidencias: { $elemMatch: { categoria: "nominal_alta" } } }
).sort({ "periodo.fecha_inicio": 1, _id: 1 }).limit(10).forEach(printjson);

// 7. Agregacion mensual: match, group, project y sort.
titulo(7, "Meses calendario con mayor intensidad termica en la muestra");
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

// 8. Agregacion anual: match, group, project y sort.
titulo(8, "Variacion anual de las metricas de fuego en la muestra");
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

// 9. Transformacion del arreglo evidencias mediante unwind.
titulo(9, "Comparacion entre evidencia total y nominal/alta");
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

// 10. Consulta integradora: dataset plano para analisis estadistico o ML.
titulo(10, "Dataset plano celda-mes para analisis estadistico o ML");
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
