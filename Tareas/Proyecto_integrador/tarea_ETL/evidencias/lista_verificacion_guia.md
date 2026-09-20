# Lista de verificación de la guía ETL

## Estado general

- Reglas Raw que cumplen: 11 de 14.
- Reglas con observaciones o tratamiento definido: 3.
- Reglas Raw que no cumplen: 0.

## Lista de entrega

- [x] Pregunta analítica, población, periodo y unidad final definidos.
- [x] Tres fuentes relacionadas identificadas y trazables.
- [x] Raw conservado sin alteraciones y verificado mediante hashes.
- [x] Perfilado inicial con tipos, faltantes, duplicados, rangos y relaciones.
- [x] Matriz de calidad con reglas, afectados, tratamiento y evidencia.
- [x] Bitácora inicial de decisiones.
- [x] Diagnóstico de valores atípicos mediante IQR.
- [x] Capa Clean generada sin sobrescribir Raw.
- [x] Registros rechazados o no aptos separados de forma explícita.
- [x] Al menos tres transformaciones implementadas y justificadas.
- [x] Integración uno a uno ejecutada y reconciliada.
- [x] Dataset Curated por `cell_id + anio + mes`.
- [x] Diccionario de datos del Curated.
- [x] Comparación antes y después de Raw a Clean y Curated.
- [x] Al menos seis controles automatizados ejecutados sobre Clean.
- [x] Controles de cardinalidad y reconciliación ejecutados sobre Curated.
- [x] Comando único de ejecución completa desde cero.
- [x] Segunda ejecución completa sin duplicación y con resultados equivalentes.
- [x] Conclusiones y limitaciones finales.

## Decisión aplicada para continuar

El Curated maestro conserva las 95.964 claves esperadas. Las 900 filas sin
observación VIIRS mantienen sus métricas como nulas y llevan una bandera de
cobertura. Para análisis conjunto se filtra `apto_analisis=true`, sin eliminar
las filas del producto maestro ni convertir sus faltantes en cero.
