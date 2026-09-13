// Carga auxiliar de desarrollo: inserta el contenido de
// 03_datos/evidencia_viirs_celda_mes.json en la base independiente
// 'taller_nosql_fireforest'.
//
// El entregable final (07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.js)
// NO depende de este archivo: lleva los 105 documentos embebidos
// directamente. Este script se conserva como alternativa reproducible
// de carga desde el JSON externo, util durante el desarrollo del taller.
//
// Ejecucion (desde la raiz de FireForest):
//   mongosh "mongodb://localhost:27017" Tareas/Taller_NoSQL/02_mongodb/04_cargar_mongodb.js

const NOMBRE_BASE = "taller_nosql_fireforest";
const NOMBRE_COLECCION = "evidencia_viirs_celda_mes";
const RUTA_JSON = "Tareas/Taller_NoSQL/03_datos/evidencia_viirs_celda_mes.json";

const baseDatos = db.getSiblingDB(NOMBRE_BASE);

const documentosTexto = cat(RUTA_JSON);
const documentos = EJSON.parse(documentosTexto);

print(`Documentos leidos de ${RUTA_JSON}: ${documentos.length}`);

if (baseDatos.getCollectionNames().includes(NOMBRE_COLECCION)) {
  baseDatos.getCollection(NOMBRE_COLECCION).drop();
  print(`Coleccion previa eliminada: ${NOMBRE_BASE}.${NOMBRE_COLECCION}`);
}

baseDatos.createCollection(NOMBRE_COLECCION);
const resultado = baseDatos.getCollection(NOMBRE_COLECCION).insertMany(documentos);
print(`Documentos insertados en ${NOMBRE_BASE}.${NOMBRE_COLECCION}: ${Object.keys(resultado.insertedIds).length}`);
