# Selección y definición del problema

## Proyecto

FireForest: diseño de una arquitectura híbrida SQL–NoSQL para la integración y consulta de datos de incendios forestales en el cantón Loja.

## Contexto y situación que motiva el proyecto

Los incendios forestales en el cantón Loja se concentran en temporadas secas y afectan ecosistemas, biodiversidad y comunidades rurales cercanas a zonas de bosque y pastizal. La información necesaria para entender estos eventos proviene de fuentes muy distintas entre sí: detecciones satelitales de focos de calor (VIIRS), registros climáticos de precipitación (CHIRPS) y una malla espacial de referencia del territorio. Cada fuente tiene su propio formato, resolución y frecuencia de actualización, y hoy no existe una forma sencilla de integrarlas para responder preguntas conjuntas (por ejemplo, relacionar déficit de lluvia con ocurrencia de incendios en una misma zona y mes).

## Población, institución, proceso o sistema involucrado

El proceso involucrado es el de monitoreo y análisis de riesgo de incendios forestales a nivel territorial, en el que intervienen típicamente actores como los GAD municipal y provincial, el Cuerpo de Bomberos y el Ministerio del Ambiente, Agua y Transición Ecológica (MAAE), así como las comunidades rurales asentadas cerca de zonas boscosas del cantón Loja.

*Nota: FireForest es un ejercicio académico. No existe actualmente un convenio con estas instituciones; se usan como referencia del tipo de actor que se beneficiaría de una solución de este tipo, y se trabaja únicamente con datos de ejemplo, muestras controladas o simulados, tal como exige la restricción del proyecto.*

## Objetivo general del proyecto

Diseñar e implementar una arquitectura híbrida SQL–NoSQL que integre detecciones satelitales de incendios (VIIRS) y datos climáticos de precipitación (CHIRPS) sobre una malla espacial del cantón Loja, para construir un dataset analítico por celda espacial y mes que permita estudiar la relación entre condiciones climáticas y ocurrencia de incendios.

## Usuarios o beneficiarios potenciales de la solución

- Gestores de riesgo y personal técnico de instituciones ambientales o de emergencia (GAD, Bomberos, MAAE).
- Investigadores y estudiantes que analicen patrones espacio-temporales de incendios forestales.
- Comunidades rurales interesadas en conocer zonas de mayor recurrencia de incendios cerca de sus localidades.

## Preguntas que podrían responderse con los datos

1. ¿Qué celdas espaciales presentan mayor número o intensidad (FRP) de detecciones de incendio en el periodo analizado?
2. ¿Existe relación entre la precipitación acumulada mensual y la ocurrencia de incendios en una misma celda?
3. ¿En qué meses del año se concentra la mayor cantidad de detecciones de incendio en el cantón Loja?

Estas preguntas son la base de la pregunta analítica formal y la unidad de análisis definidas en la sección correspondiente del avance (celda espacial–mes).
