// Operaciones de actualizacion (Parte D de la guia) sobre
// taller_nosql_fireforest.evidencia_viirs_celda_mes.
//
// Las tres actualizaciones agregan o modifican UNICAMENTE metadatos
// operativos del laboratorio; ningun valor satelital real (FRP,
// detecciones, presencia, calidad de observacion) se modifica.
//
// Este script es el mismo PASO 6 incluido en
// 07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.js; se conserva aqui
// como archivo auxiliar independiente para poder ejecutar solo las
// actualizaciones sobre una coleccion ya cargada.
//
// Ejecucion (desde la raiz de FireForest):
//   mongosh "mongodb://localhost:27017" Tareas/Taller_NoSQL/02_mongodb/07_actualizaciones.js

const baseDatos = db.getSiblingDB("taller_nosql_fireforest");
const coleccion = baseDatos.getCollection("evidencia_viirs_celda_mes");

function titulo(texto) {
  print("\n==================================================");
  print(texto);
  print("==================================================");
}

titulo("ACTUALIZACION 1: campo simple con updateOne() (revisado_manualmente)");
const documentoFrpMaxima = coleccion.find(
  {}, { _id: 1, "metricas.frp.maxima_media_mw": 1 }
).sort({ "metricas.frp.maxima_media_mw": -1, _id: 1 }).limit(1).toArray()[0];
print("Documento seleccionado (mayor FRP maxima de la muestra): " + documentoFrpMaxima._id);
print("ANTES:");
printjson(coleccion.findOne({ _id: documentoFrpMaxima._id }, { _id: 1, revisado_manualmente: 1 }));
const resultadoActualizacion1 = coleccion.updateOne(
  { _id: documentoFrpMaxima._id },
  { $set: { revisado_manualmente: true } }
);
print("Resultado updateOne -> matched: " + resultadoActualizacion1.matchedCount +
      ", modified: " + resultadoActualizacion1.modifiedCount);
print("DESPUES:");
printjson(coleccion.findOne({ _id: documentoFrpMaxima._id }, { _id: 1, revisado_manualmente: 1 }));

titulo("ACTUALIZACION 2: campo anidado con updateMany() (metadatos.estado_revision)");
print("ANTES (3 documentos con evidencia de fuego, ordenados por _id):");
coleccion.find(
  { evidencias: { $elemMatch: { categoria: "todas", evidencia_fuego: true } } },
  { _id: 1, "metadatos.estado_revision": 1 }
).sort({ _id: 1 }).limit(3).forEach(printjson);
const resultadoActualizacion2 = coleccion.updateMany(
  { evidencias: { $elemMatch: { categoria: "todas", evidencia_fuego: true } } },
  { $set: { "metadatos.estado_revision": "revisado_taller_nosql" } }
);
print("Resultado updateMany -> matched: " + resultadoActualizacion2.matchedCount +
      ", modified: " + resultadoActualizacion2.modifiedCount);
print("DESPUES (mismos 3 documentos):");
coleccion.find(
  { evidencias: { $elemMatch: { categoria: "todas", evidencia_fuego: true } } },
  { _id: 1, "metadatos.estado_revision": 1 }
).sort({ _id: 1 }).limit(3).forEach(printjson);

titulo("ACTUALIZACION 3: incorporacion de informacion nueva con $push (bitacora_laboratorio)");
print("ANTES (documento de referencia VCM_0001):");
printjson(coleccion.findOne({ _id: "VCM_0001" }, { _id: 1, bitacora_laboratorio: 1 }));
const resultadoActualizacion3 = coleccion.updateMany(
  {},
  { $push: { bitacora_laboratorio: {
      accion: "carga_taller_nosql_fireforest",
      responsable: "Grupo04",
      fecha_procesamiento: new Date()
  } } }
);
print("Resultado updateMany -> matched: " + resultadoActualizacion3.matchedCount +
      ", modified: " + resultadoActualizacion3.modifiedCount);
print("DESPUES (documento de referencia VCM_0001):");
printjson(coleccion.findOne({ _id: "VCM_0001" }, { _id: 1, bitacora_laboratorio: 1 }));
