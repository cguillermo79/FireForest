use("fireforest");

// 1. Consultar detecciones válidas
db.detecciones_viirs.find(
  { "calidad.valida": true },
  { _id: 0, deteccion_id: 1, celda_id: 1, fecha: 1, frp_mw: 1 }
);

// 2. Obtener la FRP máxima
db.detecciones_viirs.aggregate([
  {
    $group: {
      _id: null,
      frp_maxima: { $max: "$frp_mw" },
      frp_promedio: { $avg: "$frp_mw" },
      numero_detecciones: { $sum: 1 }
    }
  }
]);

// 3. Agrupar detecciones por celda
db.detecciones_viirs.aggregate([
  {
    $group: {
      _id: "$celda_id",
      numero_detecciones: { $sum: 1 },
      frp_promedio: { $avg: "$frp_mw" },
      frp_maxima: { $max: "$frp_mw" }
    }
  },
  {
    $sort: { numero_detecciones: -1 }
  }
]);