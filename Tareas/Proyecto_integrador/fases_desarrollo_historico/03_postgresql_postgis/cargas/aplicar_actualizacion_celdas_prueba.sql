-- ==========================================================================
-- MIGRACION PERMANENTE: sustitucion de celdas controladas del prototipo.
--
-- ADVERTENCIA: este script, si se ejecuta y llega hasta el final sin
-- errores, MODIFICA PERMANENTEMENTE la base de desarrollo `fireforest`
-- (termina en COMMIT, no en ROLLBACK). No es el script de validacion
-- (`03_postgresql_postgis/validacion/validar_celdas_postgis.py`, que
-- siempre termina en ROLLBACK y no se modifico) ni la migracion de
-- prueba original (`actualizacion_celdas_prueba.sql`, tambien sin
-- modificar, tambien terminada en ROLLBACK). Este es un archivo NUEVO
-- e independiente.
--
-- NO SE HA EJECUTADO TODAVIA. Se presenta para revision antes de su
-- ejecucion, junto con las tablas afectadas, el numero esperado de
-- filas, las consultas posteriores de comprobacion y el procedimiento
-- de recuperacion, en el informe de esta fase de auditoria.
--
-- Motivo de la migracion: LJ_04521 y LJ_04522 fueron verificadas
-- espacialmente contra la capa oficial del INEC y quedaron FUERA del
-- canton Loja (dentro del canton Catamayo, parroquia El Tambo). Ver
-- 03_postgresql_postgis/evidencias/verificacion_territorial_celdas.md.
-- Se sustituyen por LJ_TEST_001 y LJ_TEST_002 (identificadores de
-- PRUEBA, el sufijo TEST es literal), verificadas dentro del canton
-- Loja, parroquia El Cisne, con margen >= 1 km al limite cantonal
-- (validado previamente en una transaccion de prueba con ROLLBACK; ver
-- 03_postgresql_postgis/evidencias/salida_validacion_postgis_celdas.txt).
--
-- Tablas afectadas (en orden de escritura, hijos antes que padres para
-- respetar las FK fact_incendio.celda_id / fact_clima.celda_id ->
-- dim_celda.celda_id):
--   1. fact_incendio  (DELETE 2 filas de LJ_04521/LJ_04522; INSERT 2 filas nuevas)
--   2. fact_clima     (DELETE 2 filas de LJ_04521/LJ_04522; INSERT 2 filas nuevas)
--   3. dim_celda      (DELETE 2 filas de LJ_04521/LJ_04522; INSERT 2 filas nuevas + UPDATE de geom)
--   (dim_fecha no se modifica: ya contiene 20230815 y 20230820)
--
-- Numero de filas esperado, ANTES de ejecutar (estado persistido actual,
-- porque la migracion de prueba anterior termino en ROLLBACK):
--   dim_celda:     2 filas con celda_id IN ('LJ_04521','LJ_04522')
--   fact_clima:    2 filas con celda_id IN ('LJ_04521','LJ_04522')
--   fact_incendio: 2 filas con celda_id IN ('LJ_04521','LJ_04522')
--   (y NINGUNA fila con celda_id IN ('LJ_TEST_001','LJ_TEST_002') en
--   ninguna de las tres tablas)
--
-- Numero de filas esperado, DESPUES de un COMMIT exitoso:
--   dim_celda:     0 filas con LJ_04521/LJ_04522; 2 filas con LJ_TEST_001/LJ_TEST_002
--   fact_clima:    0 filas con LJ_04521/LJ_04522; 2 filas con LJ_TEST_001/LJ_TEST_002
--   fact_incendio: 0 filas con LJ_04521/LJ_04522; 2 filas con LJ_TEST_001/LJ_TEST_002
--
-- No se incluyen contrasenas en este archivo. Ejecutar con las
-- credenciales ya configuradas en su propio `.env` local (no
-- versionado), por ejemplo con `psql` usando las variables PGHOST/
-- PGPORT/PGDATABASE/PGUSER/PGPASSWORD ya definidas en su sesion, o
-- introduciendo la contrasena de forma interactiva cuando psql la pida.
--
-- PROCEDIMIENTO DE RECUPERACION SI FALLA:
--   Todas las comprobaciones de este script estan escritas como bloques
--   PL/pgSQL (`DO $$ ... RAISE EXCEPTION ... $$`) que abortan la
--   transaccion en curso ante cualquier incumplimiento. Si cualquier
--   bloque lanza una excepcion, PostgreSQL deja la transaccion en
--   estado "aborted": ninguna sentencia posterior (incluido el COMMIT
--   final) tiene efecto. No hace falta deshacer nada manualmente; la
--   base queda exactamente como estaba antes de ejecutar el script. Si
--   psql queda en estado de transaccion abortada, basta con ejecutar
--   `ROLLBACK;` explicitamente para limpiar la sesion, leer el mensaje
--   de error (indica exactamente que comprobacion fallo), corregir la
--   causa (por ejemplo, si alguien ya aplico la migracion antes, o si
--   los datos de origen cambiaron) y volver a ejecutar el script
--   completo desde el principio.
-- ==========================================================================

BEGIN;

-- --------------------------------------------------------------------
-- 1) Precondiciones: existen las celdas antiguas, no existen las nuevas
-- --------------------------------------------------------------------
DO $$
DECLARE
    n_antiguas INTEGER;
    n_nuevas INTEGER;
BEGIN
    SELECT COUNT(*) INTO n_antiguas FROM dim_celda
        WHERE celda_id IN ('LJ_04521', 'LJ_04522');
    IF n_antiguas <> 2 THEN
        RAISE EXCEPTION 'Precondicion fallida: se esperaban 2 celdas antiguas (LJ_04521, LJ_04522) en dim_celda, se encontraron %. Es posible que la migracion ya se haya aplicado antes; verificar manualmente antes de reintentar.', n_antiguas;
    END IF;

    SELECT COUNT(*) INTO n_nuevas FROM dim_celda
        WHERE celda_id IN ('LJ_TEST_001', 'LJ_TEST_002');
    IF n_nuevas <> 0 THEN
        RAISE EXCEPTION 'Precondicion fallida: ya existen % fila(s) con celda_id LJ_TEST_001/LJ_TEST_002 en dim_celda; no se debe insertar de nuevo (violaria la PK o duplicaria datos).', n_nuevas;
    END IF;
END $$;

-- --------------------------------------------------------------------
-- 2) Eliminar las filas ligadas a las celdas no validas
--    (hijos primero: fact_incendio y fact_clima referencian dim_celda)
-- --------------------------------------------------------------------
DELETE FROM fact_incendio WHERE celda_id IN ('LJ_04521', 'LJ_04522');
DELETE FROM fact_clima    WHERE celda_id IN ('LJ_04521', 'LJ_04522');
DELETE FROM dim_celda     WHERE celda_id IN ('LJ_04521', 'LJ_04522');

-- --------------------------------------------------------------------
-- 3) Insertar las dos celdas nuevas, verificadas dentro del canton Loja
--    (mismo patron que datos_ejemplo.sql / actualizacion_celdas_prueba.sql)
-- --------------------------------------------------------------------
INSERT INTO dim_celda
    (celda_id, longitud, latitud, area_km2)
VALUES
    ('LJ_TEST_001', -79.520851, -3.805328, 0.25),
    ('LJ_TEST_002', -79.516342, -3.809842, 0.25);

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

INSERT INTO fact_clima
    (celda_id, fecha_id, precipitacion_diaria_mm)
VALUES
    ('LJ_TEST_001', 20230815, 12.5),
    ('LJ_TEST_002', 20230820, 8.7);

INSERT INTO fact_incendio
    (incendio_id, celda_id, fecha_id, fuente, numero_detecciones,
     frp_suma_mw, frp_maxima_mw, fire_mask_maximo, incendio_observado)
VALUES
    ('V_2023_TEST_001', 'LJ_TEST_001', 20230815, 'VIIRS', 1, 18.4, 18.4, 7, TRUE),
    ('V_2023_TEST_002', 'LJ_TEST_002', 20230820, 'VIIRS', 1, 9.7, 9.7, 8, TRUE);

-- --------------------------------------------------------------------
-- 4) Postcondiciones: SRID, geometria valida, area; sin huerfanos;
--    sin duplicados. Cualquier incumplimiento aborta la transaccion.
-- --------------------------------------------------------------------
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT celda_id, ST_SRID(geom) AS srid, ST_IsValid(geom) AS valido,
               ST_Area(geom) AS area_m2
        FROM dim_celda
        WHERE celda_id IN ('LJ_TEST_001', 'LJ_TEST_002')
    LOOP
        IF r.srid <> 32717 THEN
            RAISE EXCEPTION 'Postcondicion fallida: % tiene SRID % (se esperaba 32717).', r.celda_id, r.srid;
        END IF;
        IF NOT r.valido THEN
            RAISE EXCEPTION 'Postcondicion fallida: la geometria de % no es valida (ST_IsValid = false).', r.celda_id;
        END IF;
        IF abs(r.area_m2 - 250000.0) > 0.01 THEN
            RAISE EXCEPTION 'Postcondicion fallida: % tiene area % m2 (se esperaban 250000).', r.celda_id, r.area_m2;
        END IF;
    END LOOP;
END $$;

DO $$
DECLARE
    n_huerfanos_incendio INTEGER;
    n_huerfanos_clima INTEGER;
    n_dup_incendio INTEGER;
    n_dup_clima INTEGER;
BEGIN
    SELECT COUNT(*) INTO n_huerfanos_incendio
        FROM fact_incendio fi
        LEFT JOIN dim_celda dc ON dc.celda_id = fi.celda_id
        WHERE dc.celda_id IS NULL;
    IF n_huerfanos_incendio > 0 THEN
        RAISE EXCEPTION 'Postcondicion fallida: % fila(s) huerfana(s) en fact_incendio (sin dim_celda correspondiente).', n_huerfanos_incendio;
    END IF;

    SELECT COUNT(*) INTO n_huerfanos_clima
        FROM fact_clima fc
        LEFT JOIN dim_celda dc ON dc.celda_id = fc.celda_id
        WHERE dc.celda_id IS NULL;
    IF n_huerfanos_clima > 0 THEN
        RAISE EXCEPTION 'Postcondicion fallida: % fila(s) huerfana(s) en fact_clima (sin dim_celda correspondiente).', n_huerfanos_clima;
    END IF;

    SELECT COUNT(*) INTO n_dup_incendio FROM (
        SELECT celda_id, fecha_id FROM fact_incendio
        WHERE celda_id IN ('LJ_TEST_001', 'LJ_TEST_002')
        GROUP BY celda_id, fecha_id HAVING COUNT(*) > 1
    ) t;
    IF n_dup_incendio > 0 THEN
        RAISE EXCEPTION 'Postcondicion fallida: % combinacion(es) celda-fecha duplicada(s) en fact_incendio.', n_dup_incendio;
    END IF;

    SELECT COUNT(*) INTO n_dup_clima FROM (
        SELECT celda_id, fecha_id FROM fact_clima
        WHERE celda_id IN ('LJ_TEST_001', 'LJ_TEST_002')
        GROUP BY celda_id, fecha_id HAVING COUNT(*) > 1
    ) t;
    IF n_dup_clima > 0 THEN
        RAISE EXCEPTION 'Postcondicion fallida: % combinacion(es) celda-fecha duplicada(s) en fact_clima.', n_dup_clima;
    END IF;
END $$;

-- --------------------------------------------------------------------
-- 5) Si se llego hasta aqui, todas las precondiciones y postcondiciones
--    se cumplieron: confirmar permanentemente.
-- --------------------------------------------------------------------
COMMIT;

-- ==========================================================================
-- CONSULTAS POSTERIORES DE COMPROBACION (ejecutar despues del COMMIT,
-- en una sesion nueva, para verificar el estado persistido):
--
-- SELECT celda_id FROM dim_celda WHERE celda_id IN ('LJ_04521','LJ_04522');
--   -- esperado: 0 filas
--
-- SELECT celda_id, ST_SRID(geom), ST_IsValid(geom), ST_Area(geom)
-- FROM dim_celda WHERE celda_id IN ('LJ_TEST_001','LJ_TEST_002');
--   -- esperado: 2 filas, SRID 32717, valido=true, area=250000
--
-- SELECT * FROM fact_incendio WHERE celda_id IN ('LJ_TEST_001','LJ_TEST_002');
-- SELECT * FROM fact_clima    WHERE celda_id IN ('LJ_TEST_001','LJ_TEST_002');
--   -- esperado: 1 fila cada una, por celda
--
-- Verificacion territorial completa (ST_Within contra la capa oficial
-- del INEC, no solo SRID/area): volver a ejecutar
-- 03_postgresql_postgis/validacion/validar_celdas_postgis.py. Ese
-- script re-aplicara la migracion (que ahora fallara la precondicion
-- de "existen las celdas antiguas", porque ya no existiran tras este
-- COMMIT) y terminara igualmente en ROLLBACK: en ese punto debe
-- adaptarse o retirarse, ya que su proposito de "probar antes de
-- aplicar" queda cumplido una vez este script se ejecuta con exito.
-- ==========================================================================
