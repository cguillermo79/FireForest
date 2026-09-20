# Capa Raw

Los datos Raw originales se conservan en `../../02_datos/raw/` y no se
duplican en esta carpeta.

Su procedencia y sus hashes están registrados en
`../../05_ingesta/metadatos/manifiesto_firelab_loja.json`.

El futuro ETL deberá abrir esos archivos únicamente para lectura y nunca
sobrescribirlos.
