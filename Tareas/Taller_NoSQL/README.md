# Taller NoSQL — MongoDB (M1721) — Grupo 04

## Advertencia importante

**Esta es una tarea independiente del Proyecto Integrador FireForest.**
Reutiliza conceptualmente la unidad de análisis celda-mes definida en
`AGENTS.md`, pero:

- usa su **propia base de datos MongoDB** (`taller_nosql_fireforest`,
  distinta de `fireforest`);
- **no modifica** las colecciones `fireforest.evidencia_viirs_celda_mes`
  ni `fireforest.detecciones_viirs`, que pertenecen al Proyecto
  Integrador y permanecen intactas;
- puede ejecutarse y revisarse sin tocar ningún archivo de la fuente
  externa de solo lectura de la que provienen los datos, ni de otras
  tareas de FireForest.

## Propósito

Diseñar e implementar una solución documental en MongoDB para un caso de
evidencia de fuego VIIRS por celda-mes, justificar las decisiones de
embebido/referencia, cargar datos reales de prueba y construir consultas
y agregaciones que respondan preguntas operativas y analíticas. Ver la
guía en `00_guia/` y el planteamiento del caso en
`01_documentacion/01_planteamiento_caso.md`.

## Fuente de datos

Muestra estratificada de registros reales de VIIRS (NASA FIRMS)
procesados previamente, extraída de una fuente externa de solo
lectura (versión v1.0.3, periodo 2019-2025). **No son datos
simulados.** Ver el detalle completo, método de muestreo y advertencia
de representatividad en `03_datos/README.md`.

## Arquitectura de carpetas

```
Taller_NoSQL/
├── 00_guia/              Guía original del laboratorio (PDF, sin modificar)
├── 01_documentacion/     Planteamiento, diseño documental, diccionario de datos,
│                         embebido vs. referencia, conexión con Ciencia de Datos,
│                         interpretación de resultados y auditoría contra la guía
├── 02_mongodb/           Scripts técnicos: extracción, transformación, validación,
│                         carga, índices y actualizaciones (auxiliares/desarrollo)
├── 03_datos/             Muestra CSV, documentos JSON y manifiesto de procedencia
├── 04_consultas/         Las 10 consultas y las actualizaciones, con pregunta,
│                         código, resultado real e interpretación
├── 05_resultados/        Salidas reales de la ejecución (carga, consultas,
│                         pipelines, actualizaciones, resumen analítico, auditoría técnica)
├── 06_capturas/          Capturas reales o, si no existen, capturas_pendientes.md
├── 07_entrega/           Entregables finales: PDF, .js definitivo y fuente .tex
└── README.md             Este archivo
```

## Requisitos

- MongoDB corriendo localmente en `localhost:27017` (ya disponible en
  este equipo; verificado con `mongosh --eval "db.runCommand({ping:1})"`).
- `mongosh` 2.9+ y `mongoimport` (opcional, para carga alternativa).
- Python 3.10+ con el entorno virtual de FireForest (`../../.venv`), que
  ya incluye `pandas` (ver `../../requirements.txt`).
- Para compilar el informe: `pdflatex` (MiKTeX) o `pandoc`.

## Orden exacto de ejecución

Todos los comandos se ejecutan **desde la raíz de FireForest**.

1. (Opcional, ya generado) Regenerar la muestra y el JSON documental:
   ```bash
   .venv\Scripts\python.exe Tareas\Taller_NoSQL\02_mongodb\01_extraer_muestra_viirs.py
   .venv\Scripts\python.exe Tareas\Taller_NoSQL\02_mongodb\02_transformar_viirs_a_json.py
   .venv\Scripts\python.exe Tareas\Taller_NoSQL\02_mongodb\03_validar_json.py
   ```
2. **Comando de carga y ejecución completa (script definitivo,
   autosuficiente, incluye carga + índices + verificación + 10 consultas
   + actualizaciones):**
   ```bash
   mongosh "mongodb://localhost:27017" Tareas\Taller_NoSQL\07_entrega\Grupo04_Laboratorio_NoSQL_MongoDB.js
   ```
3. (Opcional) Ejecutar solo la validación de la colección ya cargada:
   ```bash
   mongosh "mongodb://localhost:27017" Tareas\Taller_NoSQL\02_mongodb\05_validar_coleccion.js
   ```
4. **Comando para compilar el informe PDF** (desde
   `Tareas\Taller_NoSQL\07_entrega`):
   ```bash
   pdflatex -interaction=nonstopmode Grupo04_Laboratorio_NoSQL_MongoDB.tex
   pdflatex -interaction=nonstopmode Grupo04_Laboratorio_NoSQL_MongoDB.tex
   ```

## Entregables finales

- `07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.pdf` — informe.
- `07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.js` — script MongoDB
  definitivo y autosuficiente (105 documentos embebidos, índices,
  verificación, 10 consultas y 3 actualizaciones).
- `07_entrega/Grupo04_Laboratorio_NoSQL_MongoDB.tex` — fuente editable
  del informe.

## Advertencias

- **Independencia:** este taller no depende de ningún archivo de la
  fuente externa de solo lectura para ejecutarse (los datos ya están
  extraídos en `03_datos/` como copia independiente), y no debe usarse
  para modificar, mover ni sobrescribir nada en esa fuente externa.
- **Muestra estratificada:** los 105 registros (70 con fuego, 35 sin
  fuego) siguen un muestreo estratificado por año y evidencia de fuego,
  no un muestreo aleatorio simple. **Los resultados de esta muestra no
  deben interpretarse como una estimación de la prevalencia real de
  incendios en el cantón Loja.** Ver `03_datos/README.md`.
