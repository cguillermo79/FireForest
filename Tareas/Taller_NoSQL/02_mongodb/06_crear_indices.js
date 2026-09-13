// Creacion de indices sobre taller_nosql_fireforest.evidencia_viirs_celda_mes.
// Operacion idempotente: createIndex no duplica un indice ya existente
// con el mismo nombre y definicion.
//
// Ejecucion (desde la raiz de FireForest):
//   mongosh "mongodb://localhost:27017" Tareas/Taller_NoSQL/02_mongodb/06_crear_indices.js

const baseDatos = db.getSiblingDB("taller_nosql_fireforest");
const coleccion = baseDatos.getCollection("evidencia_viirs_celda_mes");

coleccion.createIndex(
  { "celda.cell_index": 1, "periodo.anio": 1, "periodo.mes": 1 },
  { unique: true, name: "ux_celda_anio_mes" }
);

coleccion.createIndex({ "periodo.fecha_inicio": 1 }, { name: "ix_fecha_inicio" });

coleccion.createIndex({ "metricas.frp.maxima_media_mw": -1 }, { name: "ix_frp_maxima" });

coleccion.createIndex(
  { "evidencias.categoria": 1, "evidencias.evidencia_fuego": 1 },
  { name: "ix_evidencias_categoria_fuego" }
);

print("Indices actuales de taller_nosql_fireforest.evidencia_viirs_celda_mes:");
coleccion.getIndexes().forEach(function (indice) {
  print(" - " + indice.name + " -> " + JSON.stringify(indice.key) + (indice.unique ? " (unique)" : ""));
});
