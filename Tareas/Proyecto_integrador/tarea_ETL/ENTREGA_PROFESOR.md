# Entrega reducida para el profesor

## Qué exige la guía

La guía exige productos y evidencias, no que cada diagnóstico interno se
presente como un entregable independiente. La entrega se organiza en siete
bloques:

1. Alcance y documentación.
2. Código reproducible.
3. Configuración y dependencias.
4. Instrucciones de acceso a Raw.
5. Productos Clean.
6. Dataset Curated y diccionario.
7. Evidencias consolidadas de calidad y reproducibilidad.

## Comando de reproducción

Desde la raíz de FireForest:

```powershell
.venv\Scripts\python.exe Tareas\Proyecto_integrador\tarea_ETL\codigo\etl_fireforest.py --desde-cero
```

El comando ejecuta perfilado, calidad Raw, Clean, Curated y actualización del
seguimiento. Los archivos originales de `02_datos/raw/` se leen sin modificarse.

## Resultado esperado

- 7.997 celdas espaciales.
- 95.964 filas VIIRS Clean.
- 95.964 filas CHIRPS Clean.
- 95.964 filas Curated.
- 95.064 filas con `apto_analisis=true`.
- 900 filas con VIIRS faltante conservadas como nulas.
- 0 duplicados en `cell_id + anio + mes`.
- 16 controles Clean y 11 controles Curated cumplidos.

## Archivos auxiliares

La carpeta de trabajo contiene perfiles por columna, manifiestos y pruebas
intermedias porque permiten auditar el proceso. El profesor no necesita abrir
cada archivo. La matriz `evidencias/matriz_entregables_guia.csv` indica qué
archivo respalda cada requisito.
