# Resumen del perfilado inicial

## Alcance ejecutado

- Periodo analítico perfilado: 2023.
- Fuentes: malla, VIIRS mensual y CHIRPS mensual.
- Operación: lectura, inventario y diagnóstico. No se limpiaron, transformaron ni cargaron datos.
- Integridad de archivos: los tres hashes coinciden con el manifiesto de ingesta.

## Conteos principales

| Fuente | Filas completas | Filas de 2023 | Columnas |
|---|---:|---:|---:|
| Malla | 7997 | No aplica | 23 |
| VIIRS | 671748 | 95964 | 19 |
| CHIRPS | 671748 | 95964 | 21 |

## Claves y relaciones

- VIIRS y CHIRPS tienen 95964 claves únicas en 2023.
- Claves VIIRS sin CHIRPS: 0.
- Claves CHIRPS sin VIIRS: 0.
- Celdas VIIRS fuera de la malla: 0.
- Celdas CHIRPS fuera de la malla: 0.
- Correspondencias CHIRPS `cell_index -> cell_id` inconsistentes: 0.
- Controles de claves y relaciones cumplidos: 11 de 11.

## Hallazgos que requieren decisión

- VIIRS tiene 900 filas sin observación en 2023, correspondientes a 75 celdas.
- La malla contiene 828 celdas parciales; 409 tienen menos del 50 % de su área dentro de Loja.
- Las celdas sin observación VIIRS tienen fracciones dentro de Loja entre 0.000000016683 y 0.108275778463.
- `chirps_valid_coverage` presenta diferencias de punto flotante alrededor de 1. Con tolerancia 1e-05, existen 0 incumplimientos.
- Se registran 747 celda-meses con evidencia de fuego y 709 con evidencia nominal/alta.

## Siguiente paso

Construir la matriz de calidad y acordar las reglas de tratamiento. En particular, se debe decidir cómo representar las 75 celdas sin observación VIIRS antes de implementar la capa Clean.
