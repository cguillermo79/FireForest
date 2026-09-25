# Instrucciones del proyecto FireForest

## Propósito

FireForest es un proyecto académico independiente para diseñar una arquitectura híbrida SQL–NoSQL aplicada al análisis de datos de incendios forestales.

## Protección de FIRELAB_Loja

FIRELAB_Loja es un proyecto independiente y de alta importancia científica.

- No modificar archivos de FIRELAB_Loja.
- No mover, renombrar ni sobrescribir archivos originales.
- No modificar scripts, datos, assets, logs ni configuraciones.
- No ejecutar comandos de escritura dentro de FIRELAB_Loja.
- Utilizar únicamente copias independientes y controladas.
- No copiar el dataset completo de FIRELAB_Loja.

Excepción autorizada por el equipo (2026-09-19): se puede copiar, en modo solo lectura, la parte de los datos estrictamente necesaria para el Proyecto Integrador. La copia se hace únicamente con `Tareas/Proyecto_integrador/05_ingesta/copiar_desde_firelab.py`, que verifica hashes, no escribe nada en FIRELAB_Loja y registra la procedencia en `Tareas/Proyecto_integrador/05_ingesta/metadatos/manifiesto_firelab_loja.json`. No ejecutar `git status` ni ningún otro comando dentro de FIRELAB_Loja, porque puede escribir en su repositorio.

## Alcance de FireForest

El proyecto utilizará un subconjunto controlado de datos para demostrar:

- diseño relacional en PostgreSQL/PostGIS;
- almacenamiento documental en MongoDB;
- integración de archivos CSV y JSON;
- consultas SQL y agregaciones NoSQL;
- inventario de fuentes;
- control de calidad y trazabilidad.

## Unidad de análisis

La unidad de análisis será una celda espacial de 500 m × 500 m observada durante un mes.

La identificación principal del dataset analítico (celda-mes) será:

```text
celda_id + anio + mes
```

En MongoDB (detección individual) y en las tablas de hechos de PostgreSQL (`fact_incendio`, `fact_clima`) el dato se carga a grano diario (`celda_id + fecha`); el dataset analítico celda-mes se obtiene agregando esos registros diarios por `anio` y `mes` en la consulta SQL.