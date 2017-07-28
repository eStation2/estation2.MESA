SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = products, analysis, pg_catalog;

/*******************************************************************************************
* PRE- update insert JRC data
*
* Put here all the needed TRUNCATE TABLE statements.
********************************************************************************************/
TRUNCATE TABLE analysis.legend CASCADE;


/*******************************************************************************************
* Update insert JRC data
********************************************************************************************/

-- COPY HERE THE FULL RESULT OF THE FUNCTION CALL:
--      select * from products.export_jrc_data();
-- Then CUT the lines of the layer table, which are in the end and look like:
--      PERFORM analysis.update_insert_layers ...
-- and paste these lines in the code indicated below.


DO $$
DECLARE current_layer_id integer;
BEGIN
	-- Save the latest layerid (it could be that the user installed the eStation-Apps-2.0.4 first and created a new layer
	-- before installing the eStation-Layers-2.0.4 package.

	SELECT INTO current_layer_id nextval('analysis.layers_layerid_seq');
	-- raise notice 'current_layer_id set to: %', current_layer_id;

	DELETE FROM analysis.layers WHERE layerid < 100;

	ALTER SEQUENCE analysis.layers_layerid_seq RESTART WITH 1;

  -- COPY HERE ALL THE RECORDS of the layers table, which look like:
  --    PERFORM analysis.update_insert_layers ...

	IF current_layer_id >= 100 THEN
		PERFORM setval('analysis.layers_layerid_seq', current_layer_id);
		--raise notice 'Sequence higher then 100 so the user created a new layer with current_layer_id: %', current_layer_id;
	ELSE
		ALTER SEQUENCE analysis.layers_layerid_seq RESTART WITH 100;
		-- raise notice 'current_layer_id set to: %', 100;
	END IF;
END $$;



/*******************************************************************************************
* POST- update insert JRC data
*
* Put in this section Create Update Delete queries like:
  -- De-activate 'new' products (i.e. products defined after 2.0.4): they are activated afterwards - according to thema_product
  -- Disable a list of products by deactivating them and put defined_by on JRC_test so that they will not appear in the GUI
  -- Delete the wrong modis-pp processing chain. In delete cascade of table products.process_product.
********************************************************************************************/



