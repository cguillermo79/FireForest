# Evidencias

## Resultados disponibles

- `inventario_fuentes.csv`: formato, ruta, procedencia, grano, tamaño, hashes,
  filas y columnas de cada fuente.
- `perfilado_columnas.csv`: tipos, faltantes, porcentajes, cardinalidad, rangos
  y valores frecuentes para el conjunto completo y el periodo 2023.
- `perfilado_claves_relaciones.csv`: controles de unicidad, claves nulas,
  duplicados y correspondencias entre fuentes.
- `hallazgos_perfilado.csv`: problemas o decisiones que debe abordar la futura
  matriz de calidad.
- `resumen_perfilado.md`: síntesis legible de los resultados.
- `prueba_idempotencia_perfilado.txt`: evidencia de dos ejecuciones con salidas
  idénticas.
- `matriz_calidad.csv`: reglas Raw, severidad, registros afectados, porcentaje,
  tratamiento y evidencia posterior requerida.
- `estadisticas_atipicos.csv`: diagnóstico IQR de FRP y precipitación.
- `bitacora_decisiones.csv`: problema, regla, decisión, justificación, filas
  afectadas y versión.
- `matriz_entregables_guia.csv`: correspondencia entre cada entregable de la
  guía, su evidencia y su estado.
- `lista_verificacion_guia.md`: lista viva de requisitos cumplidos y pendientes.
- `prueba_idempotencia_calidad_raw.txt`: evidencia de dos ejecuciones idénticas
  de la evaluación de calidad Raw.
- `controles_clean.csv`: resultado de 16 controles automatizados; todos cumplen.
- `comparacion_antes_despues.csv`: reconciliación Raw-Clean de filas, faltantes,
  duplicados, banderas de atípicos y rechazos.
- `manifiesto_salidas_clean.csv`: filas, tamaño y SHA-256 de cada producto Clean.
- `resumen_clean.md`: síntesis de transformaciones y conteos de Clean.
- `prueba_idempotencia_clean.txt`: evidencia de dos ejecuciones Clean con hashes
  idénticos en CSV, Parquet, excepciones y rechazos.
- `controles_curated.csv`: once controles de cardinalidad, reconciliación,
  unicidad, completitud, consistencia y documentación; todos cumplen.
- `manifiesto_salidas_curated.csv`: filas, tamaño y SHA-256 del dataset final y
  su diccionario.
- `prueba_reproducibilidad_flujo_completo.txt`: comparación de dos ejecuciones
  completas desde Raw; 29 de 29 salidas conservaron hashes idénticos.

La evidencia de trabajo es deliberadamente detallada. El paquete docente
reducido incluye solo los archivos necesarios para evaluar y reproducir la
tarea.
