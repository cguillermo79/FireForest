# Inventario de fuentes de datos

## Proyecto

FireForest: diseño de una arquitectura híbrida SQL–NoSQL para la integración y consulta de datos de incendios forestales en el cantón Loja.

## Alcance inicial

- Área: cantón Loja.
- Resolución espacial: 500 m × 500 m.
- Periodo de trabajo: enero–diciembre de 2023.
- Unidad de análisis: celda espacial–mes.
- Fuentes iniciales: malla espacial, VIIRS y CHIRPS.
- Uso: demostración académica de integración SQL–NoSQL.
- Servidor: no requerido; procesamiento local en tres computadoras.

## Ficha técnica de las fuentes satelitales

| Aspecto | VIIRS | CHIRPS |
|---|---|---|
| Nombre completo | Visible Infrared Imaging Radiometer Suite — producto de incendio activo (Active Fire) | Climate Hazards Group InfraRed Precipitation with Station data |
| Institución responsable | NASA / NASA FIRMS (Fire Information for Resource Management System) | Climate Hazards Center, UC Santa Barbara (UCSB) |
| Producto / colección | VIIRS Active Fire, resolución nativa ~375 m (NRT/Standard) | CHIRPS v2.0 |
| Resolución espacial | ~375 m (agregado a la malla de 500 m del proyecto) | ~0.05° (~5 km) nativa; asignada a la malla de 500 m por conveniencia de integración, **sin** aumentar su resolución real (varias celdas vecinas comparten el mismo valor de precipitación) |
| Resolución temporal | Diaria (varios pasos por día según órbita) | Diaria (agregable a mensual) |
| Periodo de referencia del proyecto | Enero–diciembre de 2023 | Enero–diciembre de 2023 |
| Acceso / referencia | NASA FIRMS (firms.modaps.eosdis.nasa.gov) | UCSB Climate Hazards Center (chc.ucsb.edu/data/chirps) |
| Variables usadas | FRP (potencia radiativa del fuego), `fire_mask`/confianza, coordenadas, fecha y hora de detección | Precipitación diaria (mm), agregada a acumulada/media/máxima mensual |
| Fecha de descarga | Por definir en la fase de ingesta (Avance 2); en este avance se usan datos de ejemplo controlados | Por definir en la fase de ingesta (Avance 2); en este avance se usan datos de ejemplo controlados |

## Matriz de inventario

| Fuente | Procedencia | Tipo de dato | Captura | Formato de entrada | Variables requeridas | Metadatos | Almacenamiento |
|---|---|---|---|---|---|---|---|
| Malla espacial | Fuente institucional oficial del límite cantonal, pendiente de selección y validación durante la fase de ingesta (candidatas: Instituto Geográfico Militar, GAD Provincial de Loja) | Geoespacial estructurado | Generada una única vez mediante SIG o Python (EPSG 32717, UTM 17S) | GeoJSON, GeoPackage o CSV | `celda_id`, coordenadas, geometría, área, EPSG | Resolución, sistema de referencia, fecha de generación | PostgreSQL/PostGIS |
| VIIRS | Detecciones satelitales de incendios | Observacional y espacio-temporal | Automática | CSV o JSON | `deteccion_id`, `celda_id`, fecha, FRP, `fire_mask`, coordenadas, fuente | Sensor, producto, fecha, unidad de FRP, criterio de calidad | MongoDB y PostgreSQL |
| CHIRPS | Datos de precipitación | Climático espacio-temporal | Automática | CSV, GeoTIFF o Parquet | `celda_id`, fecha, precipitación diaria (mm); acumulada/media/máxima se calculan al agregar por mes | Resolución, unidad, periodo, método de agregación | PostgreSQL (consulta integrada con incendio) y Parquet (respaldo/procesamiento por lotes) |
| Configuración | Proyecto FireForest | Técnico | Manual | YAML, JSON o Markdown | Parámetros, rutas, periodo, resolución | Responsable, versión y fecha | GitHub |
| Dataset integrado | FireForest | Analítico | Generada mediante transformación | Parquet o CSV | Variables integradas por celda–mes | Fuentes, transformaciones, versión | `02_datos/processed/` |

## Riesgos identificados

| Fuente | Categoría | Riesgo | Control requerido |
|---|---|---|---|
| Malla espacial | Calidad | Geometrías inválidas o CRS incorrecto | Validar geometría y EPSG |
| VIIRS | Calidad | Detecciones duplicadas | Usar identificador y fecha |
| VIIRS | Calidad | Falsos positivos o baja calidad | Aplicar criterio documentado de `fire_mask` |
| VIIRS / CHIRPS | Disponibilidad | Cambios en la API, límites de cuota o caída del servicio de origen | Guardar copia local de cada descarga; registrar versión y fecha de acceso |
| VIIRS / CHIRPS | Actualización | El producto se revisa o corrige después de publicado (reprocesamiento) | Registrar versión/colección usada y fecha de descarga; documentar si se reemplaza |
| CHIRPS | Calidad | Valores faltantes | Registrar valores faltantes y cobertura temporal |
| Integración | Calidad | Diferencias de fecha o celda entre fuentes | Validar `celda_id + anio + mes` antes de consolidar |
| Archivos | Disponibilidad | Pérdida de trazabilidad o de archivos | Mantener nombre, fuente, fecha y versión; conservar respaldo en `02_datos/raw/` |
| GitHub | Seguridad | Archivos pesados o credenciales expuestas | Usar `.gitignore` y no subir secretos |
| Proyecto | Privacidad | — | No se prevé el uso de datos personales; los datos son geoespaciales, satelitales y climáticos. Aun así, se mantiene control de acceso sobre los archivos y bases de datos del proyecto. |
| CHIRPS | Interpretación | Falsa precisión espacial: asignar CHIRPS (~5 km) a la malla de 500 m puede leerse como si aumentara su resolución real | Documentar explícitamente que varias celdas comparten el mismo valor de precipitación (no hay downscaling real) |

## Restricciones de protección

Los datos utilizados en FireForest deben ser copias independientes, muestras controladas o datos simulados.

No se deben modificar, mover, renombrar ni sobrescribir archivos del proyecto FIRELAB_Loja.