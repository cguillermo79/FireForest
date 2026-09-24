# Proyecto FireForest

FireForest es un proyecto independiente de arquitectura de datos SQL–NoSQL.

Debe mantenerse completamente separado de FIRELAB_Loja.

## Tecnologías

- Python
- PostgreSQL/PostGIS
- MongoDB
- CSV
- JSON
- Parquet
- Git/GitHub

## Objetivo

Integrar y consultar datos ambientales y de incendios forestales mediante una arquitectura local híbrida.

## Restricciones

FIRELAB_Loja es un proyecto independiente y de alta importancia científica. Por decisión del equipo (2026-09-19) se puede usar una parte de sus datos, solo la estrictamente necesaria para el Proyecto Integrador:

- Acceso de solo lectura. Nunca modificar, mover, renombrar, sobrescribir ni borrar nada dentro de FIRELAB_Loja. Tampoco ejecutar comandos que escriban en él, como `git status` dentro de ese repositorio.
- Los datos se copian a `Tareas/Proyecto_integrador/02_datos/raw/` con `Tareas/Proyecto_integrador/05_ingesta/copiar_desde_firelab.py`, que verifica hashes y deja un manifiesto de procedencia en `05_ingesta/metadatos/`.
- No copiar el dataset completo ni productos que el proyecto no necesite.
- No importar código de FIRELAB_Loja. FireForest debe funcionar solo con sus copias.

Fuera de esos datos, trabajar con datos independientes, muestras controladas o datos simulados.

## Convención de trabajo

Antes de crear código:

1. revisar la estructura existente;
2. explicar qué archivo se modificará;
3. conservar la separación entre datos crudos y procesados;
4. documentar la ejecución;
5. verificar los resultados.
