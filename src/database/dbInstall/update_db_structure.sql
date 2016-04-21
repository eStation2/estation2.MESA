CREATE OR REPLACE FUNCTION products.update_insert_internet_source(internet_id character varying, defined_by character varying, descriptive_name character varying, description character varying, modified_by character varying, update_datetime timestamp without time zone, url character varying, user_name character varying, password character varying, type character varying, include_files_expression character varying, files_filter_expression character varying, status boolean, pull_frequency integer, datasource_descr_id character varying, frequency_id character varying, start_date bigint, end_date bigint, full_copy boolean DEFAULT false)
  RETURNS boolean AS
$BODY$
	DECLARE
		_internet_id 	  			ALIAS FOR  $1;
		_defined_by  				ALIAS FOR  $2;
		_descriptive_name 			ALIAS FOR  $3;
		_description   				ALIAS FOR  $4;
		_modified_by 	  			ALIAS FOR  $5;
		_update_datetime 	  		ALIAS FOR  $6;
		_url  						ALIAS FOR  $7;
		_user_name 					ALIAS FOR  $8;
		_password  					ALIAS FOR  $9;
		_type 	  					ALIAS FOR  $10;
		_include_files_expression 	ALIAS FOR  $11;
		_files_filter_expression  	ALIAS FOR  $12;
		_status 	  				ALIAS FOR  $13;
		_pull_frequency   			ALIAS FOR  $14;
		_datasource_descr_id   		ALIAS FOR  $15;
		_frequency_id   			ALIAS FOR  $16;
		_start_date   				ALIAS FOR  $17;
		_end_date   				ALIAS FOR  $18;

		_full_copy   				ALIAS FOR  $19;
	BEGIN
		PERFORM * FROM products.internet_source i WHERE i.internet_id = TRIM(_internet_id) AND i.defined_by = 'JRC';

		-- IF _start_date < 1 THEN _start_date = NULL; END IF;
		-- IF _end_date < 1 THEN _end_date = NULL; END IF;

		IF FOUND THEN
			IF _full_copy THEN
				UPDATE products.internet_source i
				SET defined_by = TRIM(_defined_by),
					descriptive_name = TRIM(_descriptive_name),
					description = TRIM(_description),
					modified_by = TRIM(_modified_by),
					update_datetime = _update_datetime,
					url = TRIM(_url),
					user_name = TRIM(_user_name),
					password = TRIM(_password),
					type = TRIM(_type),
					include_files_expression = TRIM(_include_files_expression),
					files_filter_expression = TRIM(_files_filter_expression),
					status = _status,
					pull_frequency = _pull_frequency,
					datasource_descr_id = TRIM(_datasource_descr_id),
					frequency_id = TRIM(_frequency_id),
					start_date = _start_date,
					end_date = _end_date
				WHERE i.internet_id = TRIM(_internet_id);
			ELSE
				UPDATE products.internet_source i
				SET defined_by = TRIM(_defined_by),
					-- descriptive_name = TRIM(_descriptive_name),
					-- description = TRIM(_description),
					modified_by = TRIM(_modified_by),
					update_datetime = _update_datetime,
					-- url = TRIM(_url),
					-- user_name = TRIM(_user_name),
					-- password = TRIM(_password),
					type = TRIM(_type),
					-- include_files_expression = TRIM(_include_files_expression),
					-- files_filter_expression = TRIM(_files_filter_expression),
					status = _status,
					-- pull_frequency = _pull_frequency,
					datasource_descr_id = TRIM(_datasource_descr_id),
					frequency_id = TRIM(_frequency_id)
					-- , start_date = _start_date
					-- , end_date = _end_date
				WHERE i.internet_id = TRIM(_internet_id);
			END IF;
		ELSE
			INSERT INTO products.internet_source (
				internet_id,
				defined_by,
				descriptive_name,
				description,
				modified_by,
				update_datetime,
				url,
				user_name,
				password,
				type,
				include_files_expression,
				files_filter_expression,
				status,
				pull_frequency,
				datasource_descr_id,
				frequency_id,
				start_date,
				end_date
			)
			VALUES (
				TRIM(_internet_id),
				TRIM(_defined_by),
				TRIM(_descriptive_name),
				TRIM(_description),
				TRIM(_modified_by),
				_update_datetime,
				TRIM(_url),
				TRIM(_user_name),
				TRIM(_password),
				TRIM(_type),
				TRIM(_include_files_expression),
				TRIM(_files_filter_expression),
				_status,
				_pull_frequency,
				TRIM(_datasource_descr_id),
				TRIM(_frequency_id),
				_start_date,
				_end_date
			);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION products.update_insert_internet_source(character varying, character varying, character varying, character varying, character varying, timestamp without time zone, character varying, character varying, character varying, character varying, character varying, character varying, boolean, integer, character varying, character varying, bigint, bigint, boolean)
  OWNER TO estation;



CREATE OR REPLACE FUNCTION products.set_thema(themaid character varying)
  RETURNS boolean AS
$BODY$
DECLARE
    themaid   ALIAS FOR  $1;
BEGIN
    IF themaid != '' THEN
        -- BEGIN
            UPDATE products.product
            SET activated = FALSE
            WHERE defined_by = 'JRC';

            UPDATE products.ingestion
            SET activated = FALSE,
                enabled = FALSE
            WHERE defined_by = 'JRC';

            UPDATE products.processing
            SET activated = FALSE,
                enabled = FALSE
            WHERE defined_by = 'JRC';

            UPDATE products.process_product pp
            SET activated = FALSE
            WHERE (pp.process_id) in (SELECT process_id FROM
            products.processing WHERE defined_by = 'JRC');

            UPDATE products.product_acquisition_data_source
            SET activated = FALSE
            WHERE defined_by = 'JRC';


	    IF themaid != 'ALL' THEN
		    UPDATE products.product p
		    SET activated = TRUE
		    WHERE p.product_type = 'Native'
		      AND (p.productcode, p.version) in (SELECT productcode, version FROM products.thema_product WHERE thema_id = themaid AND activated = TRUE);

		    UPDATE products.ingestion i
		    SET activated = TRUE,
			enabled = TRUE
		    WHERE (i.productcode, i.version, i.mapsetcode) in (SELECT productcode, version, mapsetcode FROM products.thema_product WHERE thema_id = themaid AND activated = TRUE);

		    UPDATE products.process_product pp
		    SET activated = TRUE
		    WHERE (pp.productcode, pp.version, pp.mapsetcode) in (SELECT productcode, version, mapsetcode FROM products.thema_product WHERE thema_id = themaid AND activated = TRUE);

		    UPDATE products.processing p
		    SET activated = TRUE,
			enabled = TRUE
		    WHERE (p.process_id) in (SELECT process_id
				 FROM products.process_product pp
				 WHERE pp.type = 'INPUT'
				   AND (pp.productcode, pp.version, pp.mapsetcode) in (SELECT productcode, version, mapsetcode FROM products.thema_product WHERE thema_id = themaid AND activated = TRUE));

		    UPDATE products.product_acquisition_data_source pads
		    SET activated = TRUE
		    WHERE (pads.productcode, pads.version) in (SELECT productcode, version FROM products.thema_product WHERE thema_id = themaid AND activated = TRUE);

	    ELSE
		    UPDATE products.product p
		    SET activated = TRUE
		    WHERE p.product_type = 'Native'
		      AND (p.productcode, p.version) in (SELECT productcode, version FROM products.thema_product WHERE thema_id != themaid AND activated = TRUE);

		    UPDATE products.ingestion i
		    SET activated = TRUE,
			enabled = TRUE
		    WHERE (i.productcode, i.version, i.mapsetcode) in (SELECT productcode, version, mapsetcode FROM products.thema_product WHERE thema_id != themaid AND activated = TRUE);

		    UPDATE products.process_product pp
		    SET activated = TRUE
		    WHERE (pp.productcode, pp.version, pp.mapsetcode) in (SELECT productcode, version, mapsetcode FROM products.thema_product WHERE thema_id != themaid AND activated = TRUE);

		    UPDATE products.processing p
		    SET activated = TRUE,
			enabled = TRUE
		    WHERE (p.process_id) in (SELECT process_id
				 FROM products.process_product pp
				 WHERE pp.type = 'INPUT'
				   AND (pp.productcode, pp.version, pp.mapsetcode) in (SELECT productcode, version, mapsetcode FROM products.thema_product WHERE thema_id != themaid AND activated = TRUE));

		    UPDATE products.product_acquisition_data_source pads
		    SET activated = TRUE
		    WHERE (pads.productcode, pads.version) in (SELECT productcode, version FROM products.thema_product WHERE thema_id != themaid AND activated = TRUE);
	    END IF;

            RETURN TRUE;

    ELSE
        RETURN FALSE;
    END IF;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE STRICT
  COST 100;
ALTER FUNCTION products.set_thema(character varying)
  OWNER TO estation;