// Ejecucion: mongosh "mongodb://localhost:27017" Tareas/Taller_NoSQL/02_mongodb/05_validar_coleccion.js
// Valida EXCLUSIVAMENTE la base independiente 'taller_nosql_fireforest'
// (no toca 'fireforest.evidencia_viirs_celda_mes' ni 'fireforest.detecciones_viirs').
const baseDatos = db.getSiblingDB("taller_nosql_fireforest");
const coleccion = baseDatos.getCollection("evidencia_viirs_celda_mes");

print("=== VALIDACIÓN DE LA COLECCIÓN taller_nosql_fireforest.evidencia_viirs_celda_mes ===");

print(
  "DOCUMENTOS:",
  coleccion.countDocuments()
);

print(
  "ID ÚNICOS:",
  coleccion.distinct("_id").length
);

print(
  "FECHAS BSON:",
  coleccion.countDocuments({
    "periodo.fecha_inicio": {
      $type: "date"
    }
  })
);

print(
  "ARREGLOS BSON:",
  coleccion.countDocuments({
    evidencias: {
      $type: "array"
    }
  })
);

print(
  "OBJETOS ANIDADOS:",
  coleccion.countDocuments({
    metricas: {
      $type: "object"
    }
  })
);

print(
  "BOOLEANOS BSON:",
  coleccion.countDocuments({
    "metadatos.datos_simulados": {
      $type: "bool"
    }
  })
);

print(
  "CON FUEGO:",
  coleccion.countDocuments({
    evidencias: {
      $elemMatch: {
        categoria: "todas",
        evidencia_fuego: true
      }
    }
  })
);

print(
  "SIN FUEGO:",
  coleccion.countDocuments({
    evidencias: {
      $elemMatch: {
        categoria: "todas",
        evidencia_fuego: false
      }
    }
  })
);

print("\n=== DOCUMENTO DE EJEMPLO ===");

print(
  EJSON.stringify(
    coleccion.findOne({
      _id: "VCM_0001"
    }),
    null,
    2
  )
);