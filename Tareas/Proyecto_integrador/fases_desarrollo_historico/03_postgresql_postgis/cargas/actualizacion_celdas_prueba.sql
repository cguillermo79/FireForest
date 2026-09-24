-- Sustitucion de las celdas controladas del prototipo FireForest.
--
-- Motivo: LJ_04521 y LJ_04522 fueron verificadas espacialmente contra la
-- capa oficial del INEC y quedaron FUERA del canton Loja (dentro del
-- canton Catamayo, parroquia El Tambo). Ver evidencia completa en
-- 03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md.
-- No se reinterpretan ni se reutilizan esos identificadores: se eliminan
-- sus filas y se insertan dos celdas nuevas, LJ_TEST_001 y LJ_TEST_002,
-- verificadas dentro del canton Loja (ver
-- 03_postgresql_postgis/evidencias/tabla_validacion_celdas_nuevas.csv y el
-- script 01_avance_1/presentacion/scripts/verificacion_territorial_y_malla.py).
--
-- LJ_TEST_001 / LJ_TEST_002 son identificadores de PRUEBA (el sufijo TEST
-- es literal): datos controlados para validacion tecnica del prototipo,
-- no observaciones ambientales reales ni una muestra representativa del
-- canton Loja.
--
-- ESTADO DE EJECUCION: este script fue preparado y revisado, pero NO se
-- ha ejecutado contra ninguna base de datos en este entorno de trabajo
-- (no hay credenciales de PostgreSQL disponibles: .env no esta
-- versionado, solo .env.example sin contrasena). Los valores de
-- verificacion (SRID, validez, area, ST_Within, ST_Distance) fueron
-- calculados de forma equivalente con Shapely/PyProj sobre las mismas
-- geometrias; ver el documento de evidencia para el detalle.
--
-- Relacion con datos_ejemplo.sql: ese script YA fue actualizado para
-- sembrar directamente LJ_TEST_001 / LJ_TEST_002 (una carga nueva, desde
-- cero, no necesita este archivo). Este script de migracion es para una
-- base de desarrollo que YA tiene cargadas las filas antiguas de
-- LJ_04521 / LJ_04522 (con datos_ejemplo.sql en su version anterior) y
-- necesita pasar al estado corregido sin recrear la base.
--
-- Uso previsto:
--   1) Ejecutar TAL CUAL (termina en ROLLBACK) para validar en una
--      transaccion de prueba, sin persistir cambios.
--   2) Si el resultado es correcto, ejecutar de nuevo cambiando la
--      ultima linea de ROLLBACK a COMMIT para aplicar de forma
--      controlada a la base de desarrollo.

BEGIN;

-- 1) Eliminar las filas ligadas a las celdas no validas -------------------
-- (orden: primero las tablas de hechos, por las FK hacia dim_celda)
DELETE FROM fact_incendio WHERE celda_id IN ('LJ_04521', 'LJ_04522');
DELETE FROM fact_clima    WHERE celda_id IN ('LJ_04521', 'LJ_04522');
DELETE FROM dim_celda     WHERE celda_id IN ('LJ_04521', 'LJ_04522');

-- 2) Insertar las dos celdas nuevas, verificadas dentro del canton Loja --
-- Mismo patron que 03_postgresql_postgis/cargas/datos_ejemplo.sql:
-- longitud/latitud en EPSG:4326 tal como llegan del origen; "geom" se
-- calcula aparte, reproyectando a EPSG:32717 (DEFAULT de dim_celda) y
-- construyendo el cuadrado de 500 x 500 m centrado en el punto
-- reproyectado.
--
-- Centroides verificados (ver tabla_validacion_celdas_nuevas.csv):
--   LJ_TEST_001: lon -79.520851, lat -3.805328 -> UTM 32717 (664250.0, 9579250.0)
--   LJ_TEST_002: lon -79.516342, lat -3.809842 -> UTM 32717 (664750.0, 9578750.0)
INSERT INTO dim_celda
    (celda_id, longitud, latitud, area_km2)
VALUES
    ('LJ_TEST_001', -79.520851, -3.805328, 0.25),
    ('LJ_TEST_002', -79.516342, -3.809842, 0.25)
ON CONFLICT (celda_id) DO NOTHING;

UPDATE dim_celda AS dc
SET epsg = 32717,
    geom = ST_MakeEnvelope(
        ST_X(t.punto_utm) - 250, ST_Y(t.punto_utm) - 250,
        ST_X(t.punto_utm) + 250, ST_Y(t.punto_utm) + 250,
        32717
    )
FROM (
    SELECT celda_id,
           ST_Transform(
               ST_SetSRID(ST_MakePoint(longitud, latitud), 4326),
               32717
           ) AS punto_utm
    FROM dim_celda
    WHERE celda_id IN ('LJ_TEST_001', 'LJ_TEST_002')
) AS t
WHERE dc.celda_id = t.celda_id;

-- dim_fecha ya contiene 20230815 y 20230820 (cargados por
-- datos_ejemplo.sql); no se modifica.

-- Mismos valores controlados de precipitacion que las celdas anteriores
-- (son datos de prueba, no observaciones reales; solo cambia el
-- celda_id al que quedan asociados).
INSERT INTO fact_clima
    (celda_id, fecha_id, precipitacion_diaria_mm)
VALUES
    ('LJ_TEST_001', 20230815, 12.5),
    ('LJ_TEST_002', 20230820, 8.7)
ON CONFLICT (celda_id, fecha_id) DO NOTHING;

-- Mismos valores controlados de FRP que las celdas anteriores; nuevos
-- incendio_id (V_2023_TEST_00x) para no reutilizar V_2023_0001/0002 con
-- un significado distinto.
INSERT INTO fact_incendio
    (incendio_id, celda_id, fecha_id, fuente, numero_detecciones,
     frp_suma_mw, frp_maxima_mw, fire_mask_maximo, incendio_observado)
VALUES
    ('V_2023_TEST_001', 'LJ_TEST_001', 20230815, 'VIIRS', 1, 18.4, 18.4, 7, TRUE),
    ('V_2023_TEST_002', 'LJ_TEST_002', 20230820, 'VIIRS', 1, 9.7, 9.7, 8, TRUE)
ON CONFLICT (incendio_id) DO NOTHING;

-- 3) Verificaciones (equivalentes a las de la Tabla 3 de la presentacion) -
-- Validacion espacial: SRID, validez, area.
SELECT celda_id,
       ST_SRID(geom)   AS srid,
       ST_IsValid(geom) AS geometria_valida,
       ST_Area(geom)    AS area_m2
FROM dim_celda
WHERE celda_id IN ('LJ_TEST_001', 'LJ_TEST_002')
ORDER BY celda_id;

-- ST_Within (centroide y poligono completo) contra el limite del canton
-- Loja, y ST_Distance al limite: estas verificaciones, la de integridad
-- de claves foraneas, la de duplicados celda-fecha, la consulta de
-- integracion celda-mes y el caso "clima sin deteccion" (0 vs NULL) estan
-- implementadas de forma ejecutable, cargando la geometria del canton
-- directamente desde la capa oficial (sin tabla auxiliar manual), en:
--   03_postgresql_postgis/validacion/validar_celdas_postgis.py
-- Ese script reutiliza esta misma migracion (ejecuta estas sentencias
-- DELETE/INSERT/UPDATE dentro de su propia transaccion) y termina siempre
-- en ROLLBACK. Es la forma recomendada de validar este archivo; ver
-- 03_postgresql_postgis/evidencias/ para sus resultados una vez ejecutado.

-- Cierre de la transaccion: DEJAR EN ROLLBACK para validar sin persistir.
-- Cambiar a COMMIT solo despues de revisar los resultados anteriores.
ROLLBACK;
