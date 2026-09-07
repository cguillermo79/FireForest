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

## Matriz de inventario

| Fuente | Procedencia | Tipo de dato | Captura | Formato de entrada | Variables requeridas | Metadatos | Almacenamiento |
|---|---|---|---|---|---|---|---|
| Malla espacial | Datos geoespaciales del área de estudio | Geoespacial estructurado | Generada previamente mediante SIG o Python | GeoJSON, GeoPackage o CSV | `celda_id`, coordenadas, geometría, área, EPSG | Resolución, sistema de referencia, fecha de generación | PostgreSQL/PostGIS |
| VIIRS | Detecciones satelitales de incendios | Observacional y espacio-temporal | Automática | CSV o JSON | `deteccion_id`, `celda_id`, fecha, FRP, `fire_mask`, coordenadas, fuente | Sensor, producto, fecha, unidad de FRP, criterio de calidad | MongoDB y PostgreSQL |
| CHIRPS | Datos de precipitación | Climático espacio-temporal | Automática | CSV, GeoTIFF o Parquet | `celda_id`, fecha, precipitación acumulada, media y máxima | Resolución, unidad, periodo, método de agregación | PostgreSQL y Parquet |
| Configuración | Proyecto FireForest | Técnico | Manual | YAML, JSON o Markdown | Parámetros, rutas, periodo, resolución | Responsable, versión y fecha | GitHub |
| Dataset integrado | FireForest | Analítico | Generada mediante transformación | Parquet o CSV | Variables integradas por celda–mes | Fuentes, transformaciones, versión | `datos/processed/` |

## Riesgos identificados

| Fuente | Riesgo | Control requerido |
|---|---|---|
| Malla espacial | Geometrías inválidas o CRS incorrecto | Validar geometría y EPSG |
| VIIRS | Detecciones duplicadas | Usar identificador y fecha |
| VIIRS | Falsos positivos o baja calidad | Aplicar criterio documentado de `fire_mask` |
| CHIRPS | Valores faltantes | Registrar valores faltantes y cobertura temporal |
| Integración | Diferencias de fechas o celdas | Validar `celda_id + fecha` |
| Archivos | Pérdida de trazabilidad | Mantener nombre, fuente, fecha y versión |
| GitHub | Archivos pesados o credenciales | Usar `.gitignore` y no subir secretos |

## Restricciones de protección

Los datos utilizados en FireForest deben ser copias independientes, muestras controladas o datos simulados.

No se deben modificar, mover, renombrar ni sobrescribir archivos del proyecto FIRELAB_Loja.