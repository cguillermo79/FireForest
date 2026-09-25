use("fireforest");

print("\n1. DETECCIONES VALIDAS");

db.detecciones_viirs.find(
  { "calidad.valida": true },
  {
    _id: 0,
    deteccion_id: 1,
    celda_id: 1,
    fecha: 1,
    frp_mw: 1
  }
).forEach(printjson);

print("\n2. RESUMEN DE FRP");

db.detecciones_viirs.aggregate([
  {
    $group: {
      _id: null,
      frp_maxima: { $max: "$frp_mw" },
      frp_promedio: { $avg: "$frp_mw" },
      numero_detecciones: { $sum: 1 }
    }
  }
]).forEach(printjson);

print("\n3. DETECCIONES POR CELDA");

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
]).forEach(printjson);