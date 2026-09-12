# Caso aplicado — Taller SQL (Práctica 2, M1721)

## Procedencia

Este taller es una práctica **independiente** del Proyecto Integrador FireForest (curso M1721,
Práctica 2 — Taller SQL, 3 puntos). Reutiliza el mismo dominio temático (incendios forestales,
cantón Loja) y adapta ideas conceptuales del esquema relacional de FireForest
(`sql/schema.sql`, `docs/inventario_fuentes.md`), pero con un esquema propio, datos propios y
una base de datos PostgreSQL propia (`taller_sql_fireforest`), sin modificar los archivos del
Proyecto Integrador ni del proyecto FIRELAB_Loja.

## Problema

Las detecciones satelitales de incendio (tipo VIIRS) y los registros de precipitación de una
zona se analizan hoy por separado, sin relacionarlos entre sí ni con la cobertura vegetal de
cada celda del territorio. Esto dificulta responder preguntas simples como "¿qué celdas con
cierto tipo de cobertura vegetal concentran más detecciones?" o "¿hay meses con muchas
detecciones y poca lluvia?".

## Propósito de la base de datos

Diseñar e implementar una base de datos relacional en PostgreSQL que permita almacenar, de forma
íntegra y sin redundancia, detecciones de incendio, precipitación diaria y cobertura vegetal por
celda espacial y fecha, y consultarlas mediante SQL para responder preguntas operativas y
analíticas sencillas.

## Usuarios potenciales

- Estudiantes/docentes del curso, como ejercicio de modelado y SQL.
- Gestores de riesgo o personal técnico ambiental que quisieran una primera aproximación
  relacional antes de escalar a un sistema real (mismo perfil de usuario que en el Proyecto
  Integrador, aquí solo como referencia, sin convenio real).

## Entidades principales

- **Celda espacial** (`dim_celda`): unidad territorial de referencia (500 m × 500 m).
- **Fecha** (`dim_fecha`): calendario diario del periodo de estudio.
- **Cobertura vegetal** (`dim_cobertura_vegetal`): tipo de cobertura del suelo (bosque, pastizal,
  matorral, cultivo, área urbana).
- **Celda–Cobertura** (`celda_cobertura`): relación muchos-a-muchos entre celda y cobertura
  vegetal, porque una celda puede tener más de un tipo de cobertura registrado en un mismo año
  (mosaico de uso de suelo) y un tipo de cobertura aplica a muchas celdas.
- **Incendio** (`fact_incendio`): registro diario de detección de incendio por celda.
- **Clima** (`fact_clima`): registro diario de precipitación por celda.

## Preguntas operativas

1. ¿Qué detecciones de incendio existen para una celda y un periodo específicos?
2. ¿Cuál fue la precipitación registrada para una celda y una fecha determinadas?
3. ¿Qué celdas no tienen registro de precipitación para alguna fecha con incendio observado?
4. ¿Qué días tuvieron incendio observado (`incendio_observado = TRUE`)?

## Preguntas analíticas

1. ¿Cuántas detecciones y qué FRP promedio/máximo presenta cada celda por mes?
2. ¿Cuál es la precipitación mensual acumulada por celda?
3. ¿Qué meses combinan varias detecciones de incendio con precipitación mensual baja?
4. ¿Qué celdas tienen mayor recurrencia de detecciones (ranking)?
5. ¿Qué tipo de cobertura vegetal concentra más detecciones de incendio? (usa la relación N:M)

Estas preguntas son descriptivas: el taller **no** busca construir un modelo predictivo ni
establecer relaciones de causalidad entre precipitación, cobertura vegetal e incendios, solo
asociaciones observables en los datos de ejemplo.

## Datos utilizados

Exclusivamente datos de ejemplo controlados, generados para este taller (no son datos reales de
VIIRS/CHIRPS ni provienen de archivos de FIRELAB_Loja). Ver `03_datos/datos_ejemplo.sql`.
