# Entrega para el profesor

## Archivo que debe enviarse

Enviar `FireForest_Tarea_ETL_entrega_completa_2026-09-20.zip`. Este paquete
incluye la geometría de la malla, los subconjuntos Raw de VIIRS y CHIRPS
limitados a 2023, los productos Clean, el dataset Curated, el diccionario, los
tres scripts que ejecutan el flujo, la configuración y las evidencias mínimas
exigidas por la guía.

El ZIP se genera de forma reproducible con:

```powershell
.venv\Scripts\python.exe Tareas\Proyecto_integrador\tarea_ETL\codigo\generar_paquete_entrega.py
```

El generador valida el número de filas, la unicidad de las claves principales
y el hash de la malla antes de crear el archivo. El paquete contiene un solo
documento de entrada: `README.md`.

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

## Comando de reproducción del ETL

Desde la raíz de FireForest:

```powershell
.venv\Scripts\python.exe Tareas\Proyecto_integrador\tarea_ETL\codigo\etl_fireforest.py --desde-cero
```

El comando ejecuta perfilado, calidad Raw, Clean, Curated y actualización del
seguimiento. Los archivos originales de `02_datos/raw/` se leen sin modificarse.

Los CSV Raw históricos 2019-2025 de VIIRS y CHIRPS superan los 100 MB cada uno
y no se duplican dentro del paquete. En su lugar se incluyen subconjuntos Raw
de 2023 con todas las columnas y filas necesarias para reproducir el resultado
entregado. La malla GeoPackage también se incluye. Por tanto, después de
descomprimir e instalar las dependencias, el ETL puede ejecutarse desde cero
sin acceso a FIRELAB_Loja.

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
intermedias porque permiten auditar el proceso. El ZIP no incluye la guía PDF,
el generador del paquete, listas de verificación, matrices administrativas,
README auxiliares, manifiestos de salidas, pruebas intermedias ni archivos
Parquet. Esos elementos permanecen en el repositorio de trabajo, pero no son
necesarios para la revisión del profesor.
