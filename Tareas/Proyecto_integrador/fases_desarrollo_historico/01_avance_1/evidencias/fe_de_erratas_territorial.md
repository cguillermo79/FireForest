# Fe de erratas territorial — celdas controladas del Avance 1

Proyecto: FireForest (independiente). Este documento **no modifica** el
informe aprobado del Avance 1 (`01_avance_1/fuente/avance1.tex`,
`01_avance_1/fuente/avance1_corregido.tex` ni
`01_avance_1/entrega/Grupo04_AvanceProyectoIntegrador.pdf`, todos
intactos). Es una aclaración posterior, independiente, sobre la
ubicación territorial de las celdas controladas usadas como datos de
ejemplo en ese informe.

## Qué dice el informe aprobado

El informe aprobado del Avance 1 utiliza como celdas controladas del
prototipo los identificadores `LJ_04521` y `LJ_04522` (coordenadas
−79.241, −4.082 y −79.236, −4.079), presentadas como datos controlados
de ejemplo dentro del dominio previsto del proyecto, el cantón Loja.

## Qué determinó la validación posterior

Con posterioridad a la aprobación del informe, se realizó una
validación espacial de esas dos celdas contra una capa cartográfica
oficial — el Marco Geoestadístico Nacional del INEC (Instituto
Nacional de Estadística y Censos de Ecuador), reproyectado de su SRID
nativo EPSG:31992 a EPSG:32717 —, algo que no se había hecho antes.
Esa validación determinó que `LJ_04521` y `LJ_04522` **no pertenecen al
cantón Loja**: están dentro del cantón **Catamayo**, en la parroquia
**El Tambo**, cantón vecino de Loja dentro de la misma provincia. El
hallazgo se verificó por dos vías independientes de cálculo
(reconstrucción propia de los límites cantonales y una comprobación
complementaria contra otra publicación de los mismos datos del INEC) y
posteriormente se confirmó ejecutando la verificación en PostgreSQL/
PostGIS real. Detalle completo, reproducible, en
`03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`.

## Qué se hizo con ese hallazgo

- `LJ_04521` y `LJ_04522` **fueron descartadas** como celdas de
  referencia territorial: no se reinterpretan ni se redefine el
  dominio del proyecto para "encajarlas".
- Se generaron dos celdas nuevas, `LJ_TEST_001` y `LJ_TEST_002`
  (identificadores de **prueba**: el sufijo `TEST` es literal),
  mediante una malla sistemática de 500×500 m anclada a múltiplos de
  500 en EPSG:32717, seleccionadas de forma determinista (ordenando por
  coordenada X y luego Y, sin intervención visual), conservando solo
  celdas con el polígono completo dentro del cantón y un margen de
  seguridad ≥ 1 km al límite cantonal.
- **Ambas celdas nuevas están completamente dentro del cantón Loja, en
  la parroquia El Cisne** — verificado con `ST_Within` del centroide y
  del polígono completo, y `ST_Distance` al límite (1085,00 m y
  1066,01 m respectivamente), contra la misma capa oficial del INEC.
  Se confirmó primero en una transacción de prueba con `ROLLBACK`, y
  después mediante una **migración permanente con `COMMIT` real**
  ejecutada el 2026-09-14, verificada a su vez en una conexión nueva de
  solo lectura contra el estado ya persistido.

## Alcance de los resultados: sigue sin cambiar

Igual que con las celdas anteriores, los resultados obtenidos con
`LJ_TEST_001` y `LJ_TEST_002` siguen siendo **datos controlados usados
únicamente para validación técnica** del prototipo (almacenamiento,
reproyección, agregación temporal, consultas de integración SQL/NoSQL).
Dos celdas dentro de una sola parroquia **no constituyen una muestra
representativa** de la variabilidad ambiental, altitudinal o climática
del cantón Loja, y esta fe de erratas no cambia esa limitación
declarada desde el Avance 1.

## Qué se conserva y qué se actualizó

- El **informe entregado y aprobado se conserva intacto**, como
  registro académico de lo efectivamente evaluado y calificado en su
  momento. Esta fe de erratas no lo sustituye ni lo corrige en su
  archivo original.
- La **presentación** (`01_avance_1/presentacion/main.tex`/`.pdf`,
  `Grupo04_Presentacion_AvanceProyectoIntegrador.pdf`), el **guion de
  exposición** (`guion_exposicion.md`/`.tex`/`.pdf`) y la **matriz de
  fuentes** (`matriz_fuentes.md`) sí se actualizaron para usar
  exclusivamente `LJ_TEST_001`/`LJ_TEST_002`, e incorporan una
  diapositiva territorial ("Ámbito territorial y localización de las
  celdas del prototipo") con el mapa y la evidencia de esta validación.
- Los datos controlados vigentes del repositorio (`datos_ejemplo.sql`,
  `detecciones_viirs.json`) también se actualizaron. La migración a
  `LJ_TEST_001`/`LJ_TEST_002` se aplicó en tres etapas documentadas en
  `03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`
  §5: (a) prueba transaccional con `ROLLBACK` (solo validó, sin
  persistir); (b) migración permanente con `COMMIT` real, ejecutada
  localmente por el equipo el 2026-09-14; (c) verificación del estado
  ya persistido en una conexión nueva de solo lectura. **PostgreSQL y
  MongoDB usan ahora, de forma permanente, `LJ_TEST_001` y
  `LJ_TEST_002`**; `LJ_04521`/`LJ_04522` no existen en el estado
  persistido de ninguna de las dos bases.

## Referencias cruzadas

- `03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md`
  — evidencia técnica completa y reproducible del hallazgo.
- `02_datos/metadatos/README_fuente_inec.md` — procedencia de la capa
  oficial del INEC.
- `01_avance_1/evidencias/evaluacion_cumplimiento_guia.md` — evaluación
  de cumplimiento de la guía del Avance 1, enlazada a esta fe de
  erratas.
- `14_gestion/decisiones_metodologicas.md`, §6 — decisión metodológica
  completa sobre la sustitución de celdas.
- `14_gestion/matriz_entregables.md` — estado de este entregable.
