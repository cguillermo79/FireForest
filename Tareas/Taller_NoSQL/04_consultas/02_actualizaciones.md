# Operaciones de actualización — Taller NoSQL (Grupo 04)

Base: `taller_nosql_fireforest` · Colección: `evidencia_viirs_celda_mes`.

**Regla general:** las tres actualizaciones agregan o modifican **únicamente
metadatos operativos del laboratorio** (bandera de revisión, estado de
revisión, bitácora de procesamiento). Ningún valor satelital real (FRP,
detecciones, presencia, calidad de observación) se modifica. Resultado
completo y sin recortar en
`../05_resultados/03_actualizaciones_antes_despues.txt`.

## Actualización 1 — Campo simple con `updateOne()`

**Qué hace:** marca con una bandera booleana el documento de mayor FRP
máxima de toda la muestra, indicando que fue revisado manualmente.

**Código:**
```javascript
const documentoFrpMaxima = coleccion.find(
  {}, { _id: 1, "metricas.frp.maxima_media_mw": 1 }
).sort({ "metricas.frp.maxima_media_mw": -1, _id: 1 }).limit(1).toArray()[0];

coleccion.updateOne(
  { _id: documentoFrpMaxima._id },
  { $set: { revisado_manualmente: true } }
);
```

**Antes:** `{ _id: 'VCM_0073' }` (el campo no existía).

**Después:** `{ _id: 'VCM_0073', revisado_manualmente: true }`.

**Resultado real:** `matched: 1, modified: 1`.

**Efecto:** agrega el metadato operativo booleano `revisado_manualmente`
a un único documento puntual (el de mayor FRP de la muestra); es
coherente con el caso porque documenta que ese registro extremo fue
verificado por el equipo del laboratorio, sin alterar el dato satelital.

## Actualización 2 — Campo anidado con `updateMany()`

**Qué hace:** establece el estado de revisión del laboratorio
(`metadatos.estado_revision`) en todos los documentos con evidencia de
fuego.

**Código:**
```javascript
coleccion.updateMany(
  { evidencias: { $elemMatch: { categoria: "todas", evidencia_fuego: true } } },
  { $set: { "metadatos.estado_revision": "revisado_taller_nosql" } }
);
```

**Antes** (3 de 70 documentos afectados, como muestra):
```text
{ _id: 'VCM_0001', metadatos: {} }
{ _id: 'VCM_0002', metadatos: {} }
{ _id: 'VCM_0005', metadatos: {} }
```

**Después** (mismos 3 documentos):
```text
{ _id: 'VCM_0001', metadatos: { estado_revision: 'revisado_taller_nosql' } }
{ _id: 'VCM_0002', metadatos: { estado_revision: 'revisado_taller_nosql' } }
{ _id: 'VCM_0005', metadatos: { estado_revision: 'revisado_taller_nosql' } }
```

**Resultado real:** `matched: 70, modified: 70`.

**Efecto:** agrega el campo anidado `metadatos.estado_revision` a los
70 documentos con evidencia de fuego; es coherente con el caso porque
distingue, a nivel de metadatos, qué documentos ya pasaron por el
control de calidad del taller sin tocar los campos satelitales.

## Actualización 3 — Incorporación de información nueva con `$push`

**Qué hace:** agrega a todos los documentos un nuevo arreglo de
metadatos operativos (`bitacora_laboratorio`) que registra la acción de
procesamiento, el responsable y la fecha.

**Código:**
```javascript
coleccion.updateMany(
  {},
  { $push: { bitacora_laboratorio: {
      accion: "carga_taller_nosql_fireforest",
      responsable: "Grupo04",
      fecha_procesamiento: new Date()
  } } }
);
```

**Antes:** `{ _id: 'VCM_0001' }` (el arreglo no existía).

**Después:**
```text
{
  _id: 'VCM_0001',
  bitacora_laboratorio: [
    {
      accion: 'carga_taller_nosql_fireforest',
      responsable: 'Grupo04',
      fecha_procesamiento: ISODate('2026-09-13T14:19:06.124Z')
    }
  ]
}
```

**Resultado real:** `matched: 105, modified: 105`.

**Efecto:** incorpora un nuevo arreglo de metadatos operativos en los
105 documentos mediante `$push`, sin modificar los campos satelitales
originales. Es coherente con el modelo documental porque separa
claramente la evidencia satelital (`evidencias`) de la trazabilidad
operativa del laboratorio (`bitacora_laboratorio`).
