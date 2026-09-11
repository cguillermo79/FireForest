# Plan preliminar de implementación

Plan de trabajo para el desarrollo del proyecto FireForest durante el curso. Es preliminar y podrá ajustarse conforme se conozcan mejor los datos y las restricciones técnicas.

| Etapa | Actividad | Resultado esperado | Estado en este avance |
|---|---|---|---|
| 1 | Identificación de fuentes | Fuentes disponibles (malla espacial, VIIRS, CHIRPS) documentadas | Completado — ver `docs/inventario_fuentes.md` |
| 2 | Diseño relacional (SQL) | Esquema `dim_celda`, `dim_fecha`, `fact_incendio`, `fact_clima` con PK/FK | Completado — ver `sql/schema.sql` |
| 3 | Diseño NoSQL | Colección `detecciones_viirs` con documento de ejemplo | Completado — ver `nosql/detecciones_viirs.json` |
| 4 | Ingesta | Carga de datos de ejemplo en PostgreSQL y MongoDB | Preparada — archivos y scripts de carga listos (`sql/datos_ejemplo.sql`, `scripts/cargar_mongodb.py`); ejecución contra bases de datos activas pendiente de verificar |
| 5 | Limpieza y validación | Datos consistentes (sin duplicados, geometría y fechas válidas) | Pendiente |
| 6 | Integración | Dataset consolidado por celda–mes (SQL + NoSQL) | Pendiente |
| 7 | Análisis | Indicadores y/o modelos (relación incendio–precipitación) | Pendiente |
| 8 | Producto final | Reporte, dashboard o modelo reproducible | Pendiente |

## Relación con las entregas del curso

- **Avance 1 (este documento):** etapas 1 a 3 completas; etapa 4 preparada mediante archivos y scripts de datos de prueba, con la carga en bases de datos activas pendiente de verificar.
- **Avance 2 (siguiente entrega):** cerrar etapas 4 y 5, avanzar etapa 6 (integración del dataset celda–mes).
- **Informe final:** etapas 7 y 8, con el dataset integrado, el análisis de la pregunta analítica y el producto final (reporte o dashboard).
