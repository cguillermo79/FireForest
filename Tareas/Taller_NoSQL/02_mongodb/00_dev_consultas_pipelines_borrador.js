// NOTA: borrador de desarrollo de las consultas 7-10 (agregacion).
// Superado por 04_consultas/ y por 07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.js,
// que contienen las 10 consultas completas y definitivas. Se conserva
// como evidencia del proceso de desarrollo (ver 01_documentacion/07_auditoria_guia.md).
// Se fija explicitamente la base independiente para evitar ejecutarlo
// por error contra 'fireforest'.
const baseDatos = db.getSiblingDB("taller_nosql_fireforest");
const coleccion = baseDatos.getCollection("evidencia_viirs_celda_mes");

function titulo(numero, pregunta) {
  print("\n==================================================");
  print(`CONSULTA ${numero}`);
  print(pregunta);
  print("==================================================");
}

titulo(
  7,
  "¿En qué meses calendario se concentra la mayor intensidad térmica de la muestra?"
);

coleccion.aggregate([
  {
    $match: {
      "metricas.frp.suma_observada_media_mw": {
        $gt: 0
      }
    }
  },
  {
    $group: {
      _id: "$periodo.mes",

      registros_con_fuego: {
        $sum: 1
      },

      frp_total_muestra_mw: {
        $sum: "$metricas.frp.suma_observada_media_mw"
      },

      frp_promedio_mw: {
        $avg: "$metricas.frp.suma_observada_media_mw"
      },

      frp_maxima_mw: {
        $max: "$metricas.frp.maxima_media_mw"
      }
    }
  },
  {
    $project: {
      _id: 0,
      mes: "$_id",
      registros_con_fuego: 1,

      frp_total_muestra_mw: {
        $round: ["$frp_total_muestra_mw", 2]
      },

      frp_promedio_mw: {
        $round: ["$frp_promedio_mw", 2]
      },

      frp_maxima_mw: {
        $round: ["$frp_maxima_mw", 2]
      }
    }
  },
  {
    $sort: {
      frp_total_muestra_mw: -1,
      mes: 1
    }
  }
])
.forEach(printjson);


// ============================================================
// CONSULTA 8: AGREGACIÓN POR AÑO
// Etapas: $match, $group y $sort
// Pregunta: ¿Cómo varían las métricas de fuego entre los años
// representados en la muestra?
// ============================================================

titulo(
  8,
  "¿Cómo varían las métricas de fuego entre los años representados en la muestra?"
);

coleccion.aggregate([
  {
    $match: {
      "metricas.frp.suma_observada_media_mw": {
        $gt: 0
      }
    }
  },
  {
    $group: {
      _id: "$periodo.anio",

      registros_con_fuego: {
        $sum: 1
      },

      detecciones_promedio: {
        $avg: "$metricas.detecciones.media_todas"
      },

      frp_promedio_mw: {
        $avg: "$metricas.frp.suma_observada_media_mw"
      },

      frp_total_muestra_mw: {
        $sum: "$metricas.frp.suma_observada_media_mw"
      },

      frp_maxima_mw: {
        $max: "$metricas.frp.maxima_media_mw"
      }
    }
  },
  {
    $project: {
      _id: 0,
      anio: "$_id",
      registros_con_fuego: 1,

      detecciones_promedio: {
        $round: ["$detecciones_promedio", 3]
      },

      frp_promedio_mw: {
        $round: ["$frp_promedio_mw", 2]
      },

      frp_total_muestra_mw: {
        $round: ["$frp_total_muestra_mw", 2]
      },

      frp_maxima_mw: {
        $round: ["$frp_maxima_mw", 2]
      }
    }
  },
  {
    $sort: {
      frp_total_muestra_mw: -1,
      anio: 1
    }
  }
])
.forEach(printjson);


// ============================================================
// CONSULTA 9: TRANSFORMACIÓN DE UN ARREGLO
// Etapas: $unwind, $group, $project y $sort
// Pregunta: ¿Qué diferencias existen entre la evidencia total
// y la evidencia de confianza nominal/alta?
// ============================================================

titulo(
  9,
  "¿Qué diferencias existen entre la evidencia total y la evidencia nominal/alta?"
);

coleccion.aggregate([
  {
    $unwind: "$evidencias"
  },
  {
    $group: {
      _id: "$evidencias.categoria",

      documentos_evaluados: {
        $sum: 1
      },

      documentos_con_fuego: {
        $sum: {
          $cond: [
            "$evidencias.evidencia_fuego",
            1,
            0
          ]
        }
      },

      detecciones_promedio: {
        $avg: "$evidencias.detecciones_media"
      },

      presencia_promedio: {
        $avg: "$evidencias.presencia_fraccion"
      }
    }
  },
  {
    $project: {
      _id: 0,
      categoria: "$_id",
      documentos_evaluados: 1,
      documentos_con_fuego: 1,

      detecciones_promedio: {
        $round: ["$detecciones_promedio", 3]
      },

      presencia_promedio: {
        $round: ["$presencia_promedio", 3]
      }
    }
  },
  {
    $sort: {
      categoria: 1
    }
  }
])
.forEach(printjson);


// ============================================================
// CONSULTA 10: CONSULTA INTEGRADORA
// Etapas: $match, $set, $project, $sort y $limit
// Pregunta: ¿Cómo se obtiene un dataset plano de registros con
// fuego para análisis estadístico o aprendizaje automático?
// ============================================================

titulo(
  10,
  "¿Cómo se obtiene un dataset plano para análisis estadístico o aprendizaje automático?"
);

coleccion.aggregate([
  {
    $match: {
      "metricas.frp.suma_observada_media_mw": {
        $gt: 0
      },

      "calidad_observacion.disponibilidad_pct": {
        $gte: 95
      }
    }
  },
  {
    $set: {
      frp_por_deteccion_mw: {
        $cond: [
          {
            $gt: [
              "$metricas.detecciones.media_todas",
              0
            ]
          },
          {
            $divide: [
              "$metricas.frp.suma_observada_media_mw",
              "$metricas.detecciones.media_todas"
            ]
          },
          0
        ]
      },

      proporcion_nominal_alta: {
        $cond: [
          {
            $gt: [
              "$metricas.detecciones.media_todas",
              0
            ]
          },
          {
            $divide: [
              "$metricas.detecciones.media_nominal_alta",
              "$metricas.detecciones.media_todas"
            ]
          },
          0
        ]
      }
    }
  },
  {
    $project: {
      _id: 0,
      registro_id: "$_id",
      cell_index: "$celda.cell_index",
      anio: "$periodo.anio",
      mes: "$periodo.mes",
      anio_mes: "$periodo.anio_mes",

      detecciones_media: {
        $round: [
          "$metricas.detecciones.media_todas",
          3
        ]
      },

      frp_total_media_mw: {
        $round: [
          "$metricas.frp.suma_observada_media_mw",
          2
        ]
      },

      frp_maxima_mw: {
        $round: [
          "$metricas.frp.maxima_media_mw",
          2
        ]
      },

      frp_por_deteccion_mw: {
        $round: ["$frp_por_deteccion_mw", 2]
      },

      proporcion_nominal_alta: {
        $round: ["$proporcion_nominal_alta", 3]
      },

      disponibilidad_pct:
        "$calidad_observacion.disponibilidad_pct",

      presencia_fuego: {
        $literal: 1
      }
    }
  },
  {
    $sort: {
      frp_total_media_mw: -1,
      registro_id: 1
    }
  },
  {
    $limit: 15
  }
])
.forEach(printjson);