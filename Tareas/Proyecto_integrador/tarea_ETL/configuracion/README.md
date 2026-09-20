# Configuración

`perfilado.json` define el año de estudio, las rutas relativas de las tres
fuentes, la capa del GeoPackage y la tolerancia usada para comparar fracciones
decimales.

`reglas_calidad.json` registra las tolerancias, la versión de las reglas y las
políticas para faltantes, ceros, duplicados, celdas parciales, valores atípicos
e integración.

`transformaciones_clean.json` fija el periodo, los conteos esperados, el tamaño
de lectura por bloques, los formatos de salida y las seis transformaciones
implementadas en Clean.

`requirements_etl.txt` fija las dependencias externas verificadas con Python
3.14.7. Los demás módulos usados por los scripts pertenecen a la biblioteca
estándar de Python.

No se almacenan aquí contraseñas, tokens ni otros secretos.
