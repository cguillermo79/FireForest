# Resumen de la capa Clean

## Resultado

- Periodo procesado: 2023.
- Malla: 7,997 celdas.
- VIIRS: 95,964 filas celda-mes.
- CHIRPS: 95,964 filas celda-mes.
- Observaciones VIIRS sin cobertura: 900.
- Rechazos criticos: 0.
- Controles Clean cumplidos: 16 de 16.

## Tratamientos aplicados

1. Se selecciono 2023 mediante codigo y se conservaron intactos los archivos Raw.
2. Se tiparon identificadores, numeros, fechas y booleanos.
3. Se incorporaron `cell_id` y atributos territoriales desde la malla.
4. Se construyeron banderas de cobertura y aptitud VIIRS.
5. Se calculo `fraccion_dias_humedos` sin reemplazar mediciones originales.
6. Se marcaron valores atipicos mediante los limites IQR ya documentados.

La capa Clean mantiene cada fuente por separado. El mismo script utiliza estas
salidas logicas para construir Curated con cardinalidad uno a uno.
