# FireForest

## Diseño de una arquitectura híbrida SQL–NoSQL para datos de incendios forestales

FireForest es un proyecto académico independiente desarrollado por tres integrantes para diseñar, integrar y consultar datos ambientales y de incendios forestales mediante una arquitectura híbrida.

El proyecto utiliza PostgreSQL/PostGIS para datos estructurados y geoespaciales, y MongoDB para documentos JSON y metadatos flexibles.

## Objetivo

Diseñar una solución local que permita:

- identificar las fuentes de datos;
- organizar entidades, atributos y relaciones;
- almacenar datos en PostgreSQL/PostGIS;
- almacenar documentos en MongoDB;
- ejecutar consultas SQL y agregaciones NoSQL;
- documentar la calidad, procedencia y trazabilidad de los datos;
- definir una unidad de análisis reproducible.

## Problema de Ciencia de Datos

Los datos de incendios forestales provienen de distintas fuentes y formatos. Esta heterogeneidad dificulta su integración, almacenamiento, consulta y análisis conjunto.

FireForest propone una arquitectura híbrida para organizar datos espaciales, temporales, satelitales y climáticos en una solución local y reproducible.

## Alcance

- Área de referencia: cantón Loja.
- Resolución espacial: 500 m × 500 m.
- Periodo de ejemplo: enero–diciembre de 2023.
- Unidad de análisis: celda espacial–mes.
- Fuentes conceptuales: malla espacial, VIIRS y CHIRPS.
- Trabajo: local en tres computadoras.
- Servidor: no requerido.
- Datos actuales: ejemplos independientes y controlados.

## Arquitectura

```text
CSV / JSON
    ├── PostgreSQL/PostGIS
    └── MongoDB
            ↓
    Consultas SQL y NoSQL
            ↓
    Comparación e integración
```

## Ubicación del proyecto y de las tareas académicas

El **Proyecto Integrador** completo (documentación, datos, código SQL y
NoSQL, Airflow, y demás componentes técnicos) vive en
[`Tareas/Proyecto_integrador/`](Tareas/Proyecto_integrador/README.md),
que es autónomo y contiene su propio `README.md` con propósito,
arquitectura, estructura, requisitos, orden de ejecución, reproducción,
estado y pendientes.

Además, este repositorio contiene dos actividades académicas
**independientes** del Proyecto Integrador, con sus propias bases de
datos y sin dependencias cruzadas:

- [`Tareas/Taller_NoSQL/`](Tareas/Taller_NoSQL/README.md) — Laboratorio
  NoSQL MongoDB (M1721), base `taller_nosql_fireforest`.
- [`Tareas/Taller_SQL_Relacional/`](Tareas/Taller_SQL_Relacional/README.md)
  — Taller SQL Relacional, base `taller_sql_fireforest`.

Ninguno de los tres componentes modifica ni depende de archivos del
proyecto externo FIRELAB_Loja (ver `AGENTS.md` y `CLAUDE.md`).