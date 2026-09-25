# Código

## Perfilado inicial

`perfilar_fuentes.py` inventaría y perfila las tres fuentes Raw sin
modificarlas. También verifica sus hashes, la unicidad de las claves y las
relaciones entre malla, VIIRS y CHIRPS.

Ejecución desde la raíz de FireForest:

```powershell
.venv\Scripts\python.exe Tareas\Proyecto_integrador\tarea_ETL\codigo\perfilar_fuentes.py
```

El script solo escribe resultados en `../evidencias/`. Todavía no implementa
la limpieza, la integración Curated ni cargas en bases de datos.

## Evaluación de calidad Raw

`evaluar_calidad_raw.py` ejecuta las reglas iniciales sobre 2023 y genera la
matriz de calidad, estadísticas IQR, bitácora de decisiones y control de los
entregables exigidos por la guía.

```powershell
.venv\Scripts\python.exe Tareas\Proyecto_integrador\tarea_ETL\codigo\evaluar_calidad_raw.py
```

Debe ejecutarse después de `perfilar_fuentes.py`. Este script tampoco modifica
Raw ni genera por sí mismo las capas Clean o Curated.

## Construcción de Clean

`etl_fireforest.py` lee las tres fuentes Raw, selecciona 2023 y genera Clean y
Curated en CSV y Parquet. Implementa seis transformaciones, una integración uno
a uno y controles de reconciliación, unicidad, completitud, consistencia,
validez, integridad referencial y valores atípicos.

```powershell
.venv\Scripts\python.exe Tareas\Proyecto_integrador\tarea_ETL\codigo\etl_fireforest.py
```

Para ejecutar solo las transformaciones debe usarse después de los dos comandos
anteriores porque consume los límites IQR registrados en
`../evidencias/estadisticas_atipicos.csv`. La ejecución reemplaza sus salidas
sin anexar registros.

Para reproducir toda la tarea con un solo comando:

```powershell
.venv\Scripts\python.exe Tareas\Proyecto_integrador\tarea_ETL\codigo\etl_fireforest.py --desde-cero
```

Orden actual desde cero:

1. Activar el entorno virtual del proyecto con Python 3.14.7 y dependencias de
   `../configuracion/requirements_etl.txt`.
2. `perfilar_fuentes.py`
3. `evaluar_calidad_raw.py`
4. `etl_fireforest.py`

El modo `--desde-cero` vuelve a generar el perfilado, la calidad Raw, Clean,
Curated y el seguimiento de los entregables.
