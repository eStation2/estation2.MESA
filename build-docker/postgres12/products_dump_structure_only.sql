--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.4
-- Dumped by pg_dump version 9.3.4
-- Started on 2016-02-02 10:57:22 CET

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 7 (class 2615 OID 17264)
-- Name: analysis; Type: SCHEMA; Schema: -; Owner: estation
--

CREATE SCHEMA analysis;


ALTER SCHEMA analysis OWNER TO estation;

--
-- TOC entry 8 (class 2615 OID 17265)
-- Name: products; Type: SCHEMA; Schema: -; Owner: estation
--

CREATE SCHEMA products;


ALTER SCHEMA products OWNER TO estation;

SET search_path = analysis, pg_catalog;

--
-- TOC entry 218 (class 1255 OID 18670)
-- Name: update_insert_i18n(character varying, text, text, text, text, text, text); Type: FUNCTION; Schema: analysis; Owner: estation
--

CREATE FUNCTION update_insert_i18n(label character varying, eng text, fra text, por text, lang1 text, lang2 text, lang3 text) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_label  ALIAS FOR  $1;
		_eng  	ALIAS FOR  $2;
		_fra   	ALIAS FOR  $3;
		_por   	ALIAS FOR  $4;		
		_lang1  ALIAS FOR  $5;
		_lang2  ALIAS FOR  $6;
		_lang3  ALIAS FOR  $7;
  
	BEGIN	
		IF _eng= 'NULL' THEN
			_eng = NULL;
		END IF;
		IF _fra = 'NULL' THEN
			_fra = NULL;
		END IF;			
		IF _por = 'NULL' THEN
			_por = NULL;
		END IF;
		IF _lang1 = 'NULL' THEN
			_lang1 = NULL;
		END IF;
		IF _lang2 = 'NULL' THEN
			_lang2 = NULL;
		END IF;
		IF _lang3 = 'NULL' THEN
			_lang3 = NULL;
		END IF;	
			
		PERFORM * FROM analysis.i18n WHERE i18n.label = TRIM(_label);
		IF FOUND THEN
			UPDATE analysis.i18n 
			SET eng = TRIM(_eng), 
			    fra = TRIM(_fra),  
			    por = TRIM(_por), 
			    lang1 = TRIM(_lang1), 
			    lang2 = TRIM(_lang2), 
			    lang3 = TRIM(_lang3)				
			WHERE i18n.label = TRIM(_label);
		ELSE
			INSERT INTO analysis.i18n (label, eng, fra, por, lang1, lang2, lang3) 
			VALUES (TRIM(_label), TRIM(_eng), TRIM(_fra), TRIM(_por), TRIM(_lang1), TRIM(_lang2), TRIM(_lang3));
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION analysis.update_insert_i18n(label character varying, eng text, fra text, por text, lang1 text, lang2 text, lang3 text) OWNER TO estation;

--
-- TOC entry 222 (class 1255 OID 18671)
-- Name: update_insert_languages(character varying, character varying, boolean); Type: FUNCTION; Schema: analysis; Owner: estation
--

CREATE FUNCTION update_insert_languages(langcode character varying, langdescription character varying, active boolean) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_langcode  		ALIAS FOR  $1;
		_langdescription  	ALIAS FOR  $2;
		_active   		ALIAS FOR  $3;
  
	BEGIN	
		PERFORM * FROM analysis.languages l WHERE l.langcode = TRIM(_langcode);
		IF FOUND THEN
			UPDATE analysis.languages l
			SET langdescription = TRIM(_langdescription),  
			    active = _active		
			WHERE l.langcode = TRIM(_langcode);
		ELSE
			INSERT INTO analysis.languages (langcode, langdescription, active) 
			VALUES (TRIM(_langcode), TRIM(_langdescription), _active);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION analysis.update_insert_languages(langcode character varying, langdescription character varying, active boolean) OWNER TO estation;

--
-- TOC entry 226 (class 1255 OID 18672)
-- Name: update_insert_legend(integer, character varying, character varying, double precision, double precision, character varying, text, text, double precision, double precision, double precision, character varying); Type: FUNCTION; Schema: analysis; Owner: estation
--

CREATE FUNCTION update_insert_legend(legend_id integer, legend_name character varying, step_type character varying, min_value double precision, max_value double precision, min_real_value character varying, max_real_value text, colorbar text, step double precision, step_range_from double precision, step_range_to double precision, unit character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_legend_id 		ALIAS FOR  $1;
		_legend_name 		ALIAS FOR  $2;
		_step_type 		ALIAS FOR  $3;
		_min_value 		ALIAS FOR  $4;
		_max_value 		ALIAS FOR  $5;
		_min_real_value 	ALIAS FOR  $6;
		_max_real_value 	ALIAS FOR  $7;
		_colorbar 		ALIAS FOR  $8;
		_step 			ALIAS FOR  $9;
		_step_range_from	ALIAS FOR  $10;
		_step_range_to 		ALIAS FOR  $11;
		_unit 			ALIAS FOR  $12;
  
	BEGIN	
		IF _max_real_value= 'NULL' THEN
			_max_real_value = NULL;
		END IF;
		IF _colorbar= 'NULL' THEN
			_colorbar = NULL;
		END IF;
		
		PERFORM * FROM analysis.legend l WHERE l.legend_id = _legend_id;
		IF FOUND THEN
			UPDATE analysis.legend l
			SET legend_name = TRIM(_legend_name),  
			    step_type = TRIM(_step_type),
			    min_value = _min_value,
			    max_value = _max_value,
			    min_real_value = TRIM(_min_real_value),
			    max_real_value = TRIM(_max_real_value),
			    colorbar = TRIM(_colorbar),
			    step = _step,
			    step_range_from = _step_range_from,
			    step_range_to = _step_range_to,
			    unit = TRIM(_unit)
			WHERE l.legend_id = _legend_id;
		ELSE
			INSERT INTO analysis.legend (legend_id, legend_name, step_type, min_value, max_value, min_real_value, max_real_value, colorbar, step, step_range_from, step_range_to, unit) 
			VALUES (_legend_id, TRIM(legend_name), TRIM(_step_type), _min_value, _max_value, TRIM(_min_real_value), TRIM(_max_real_value), TRIM(_colorbar), _step, _step_range_from, _step_range_to, _unit);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION analysis.update_insert_legend(legend_id integer, legend_name character varying, step_type character varying, min_value double precision, max_value double precision, min_real_value character varying, max_real_value text, colorbar text, step double precision, step_range_from double precision, step_range_to double precision, unit character varying) OWNER TO estation;

--
-- TOC entry 220 (class 1255 OID 18673)
-- Name: update_insert_legend_step(integer, double precision, double precision, character varying, character varying, character varying); Type: FUNCTION; Schema: analysis; Owner: estation
--

CREATE FUNCTION update_insert_legend_step(legend_id integer, from_step double precision, to_step double precision, color_rgb character varying, color_label character varying, group_label character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_legend_id 	ALIAS FOR  $1;
		_from_step 	ALIAS FOR  $2;
		_to_step 	ALIAS FOR  $3;
		_color_rgb 	ALIAS FOR  $4;
		_color_label 	ALIAS FOR  $5;
		_group_label 	ALIAS FOR  $6;
  
	BEGIN	
		IF _color_rgb = 'NULL' THEN
			_color_rgb = NULL;
		END IF;
		IF _color_label = 'NULL' THEN
			_color_label = NULL;
		END IF;
		IF _group_label = 'NULL' THEN
			_group_label = NULL;
		END IF;
		
		PERFORM * FROM analysis.legend_step ls WHERE ls.legend_id = _legend_id AND ls.from_step = _from_step AND ls.to_step = _to_step;
		IF FOUND THEN
			UPDATE analysis.legend_step ls
			SET color_rgb = TRIM(_color_rgb),  
			    color_label = TRIM(_color_label),
			    group_label = TRIM(_group_label)
			WHERE ls.legend_id = _legend_id AND ls.from_step = _from_step AND ls.to_step = _to_step;
		ELSE
			INSERT INTO analysis.legend_step (legend_id, from_step, to_step, color_rgb, color_label, group_label) 
			VALUES (_legend_id, _from_step, _to_step, TRIM(_color_rgb), TRIM(_color_label), TRIM(_group_label));
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION analysis.update_insert_legend_step(legend_id integer, from_step double precision, to_step double precision, color_rgb character varying, color_label character varying, group_label character varying) OWNER TO estation;

--
-- TOC entry 227 (class 1255 OID 18674)
-- Name: update_insert_product_legend(character varying, character varying, character varying, bigint, boolean); Type: FUNCTION; Schema: analysis; Owner: estation
--

CREATE FUNCTION update_insert_product_legend(productcode character varying, subproductcode character varying, version character varying, legend_id bigint, default_legend boolean) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_productcode 		ALIAS FOR  $1;
		_subproductcode 	ALIAS FOR  $2;
		_version 		ALIAS FOR  $3;
		_legend_id 		ALIAS FOR  $4;
		_default_legend 	ALIAS FOR  $5;
  
	BEGIN	
		PERFORM * FROM analysis.product_legend pl WHERE pl.productcode = TRIM(_productcode) AND pl.subproductcode = TRIM(_subproductcode) AND pl.version = TRIM(_version) AND pl.legend_id = _legend_id;
		IF FOUND THEN
			UPDATE analysis.product_legend pl
			SET default_legend = _default_legend
			WHERE pl.productcode = TRIM(_productcode) AND pl.subproductcode = TRIM(_subproductcode) AND pl.version = TRIM(_version) AND pl.legend_id = _legend_id;
		ELSE
			INSERT INTO analysis.product_legend (productcode, subproductcode, version, legend_id, default_legend) 
			VALUES (TRIM(_productcode), TRIM(_subproductcode), TRIM(_version), _legend_id, _default_legend);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION analysis.update_insert_product_legend(productcode character varying, subproductcode character varying, version character varying, legend_id bigint, default_legend boolean) OWNER TO estation;

--
-- TOC entry 223 (class 1255 OID 18675)
-- Name: update_insert_timeseries_drawproperties(character varying, character varying, character varying, character varying, character varying, double precision, double precision, boolean, character varying, character varying, character varying, integer, character varying, character varying, character varying); Type: FUNCTION; Schema: analysis; Owner: estation
--

CREATE FUNCTION update_insert_timeseries_drawproperties(productcode character varying, subproductcode character varying, version character varying, title character varying, unit character varying, min double precision, max double precision, oposite boolean, tsname_in_legend character varying, charttype character varying, linestyle character varying, linewidth integer, color character varying, yaxes_id character varying, title_color character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_productcode 		ALIAS FOR  $1;
		_subproductcode 	ALIAS FOR  $2;
		_version 		ALIAS FOR  $3;
		_title 			ALIAS FOR  $4;
		_unit 			ALIAS FOR  $5;
		_min 			ALIAS FOR  $6;
		_max 			ALIAS FOR  $7;
		_oposite 		ALIAS FOR  $8;
		_tsname_in_legend 	ALIAS FOR  $9;
		_charttype 		ALIAS FOR  $10;
		_linestyle 		ALIAS FOR  $11;
		_linewidth 		ALIAS FOR  $12;
		_color 			ALIAS FOR  $13;
		_yaxes_id 		ALIAS FOR  $14;
		_title_color 		ALIAS FOR  $15;
  
	BEGIN	
		PERFORM * FROM analysis.timeseries_drawproperties tsdp WHERE tsdp.productcode = TRIM(_productcode) AND tsdp.subproductcode = TRIM(_subproductcode) AND tsdp.version = TRIM(_version);
		IF FOUND THEN
			UPDATE analysis.timeseries_drawproperties tsdp
			SET title = TRIM(_title),
			    unit = TRIM(_unit),
			    min = _min,
			    max = _max,
			    oposite = _oposite,
			    tsname_in_legend = TRIM(_tsname_in_legend),
    			    charttype = TRIM(_charttype),
			    linestyle = TRIM(_linestyle),
			    linewidth = _linewidth,
			    color = TRIM(_color),
			    yaxes_id = TRIM(_yaxes_id),
			    title_color = TRIM(_title_color)				
			WHERE tsdp.productcode = TRIM(_productcode) AND tsdp.subproductcode = TRIM(_subproductcode) AND tsdp.version = TRIM(_version);
		ELSE
			INSERT INTO analysis.timeseries_drawproperties (productcode, 
									subproductcode, 
									version, 
									title,
									unit,
									min,
									max,
									oposite,
									tsname_in_legend,
									charttype,
									linestyle,
									linewidth,
									color,
									yaxes_id,
									title_color) 
			VALUES (TRIM(_productcode), 
				TRIM(_subproductcode), 
				TRIM(_version), 
				TRIM(_title), 
				TRIM(_unit), 
				_min, 
				_max, 
				_oposite, 
				TRIM(_tsname_in_legend), 
				TRIM(_charttype), 
				TRIM(_linestyle), 
				_linewidth, 
				TRIM(_color), 
				TRIM(_yaxes_id), 
				TRIM(_title_color));
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION analysis.update_insert_timeseries_drawproperties(productcode character varying, subproductcode character varying, version character varying, title character varying, unit character varying, min double precision, max double precision, oposite boolean, tsname_in_legend character varying, charttype character varying, linestyle character varying, linewidth integer, color character varying, yaxes_id character varying, title_color character varying) OWNER TO estation;

SET search_path = products, pg_catalog;

--
-- TOC entry 209 (class 1255 OID 17266)
-- Name: check_datasource(character varying, character varying); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION check_datasource(datasourceid character varying, type character varying) RETURNS boolean
    LANGUAGE plpgsql STRICT
    AS $_$
	DECLARE
       datasourceid   ALIAS FOR  $1;
       type   		  ALIAS FOR  $2;
	BEGIN
       IF $2 = 'EUMETCAST' THEN
          PERFORM * FROM products.eumetcast_source WHERE eumetcast_id = $1;
       ELSIF $2 = 'INTERNET' THEN
          PERFORM * FROM products.internet_source WHERE internet_id = $1;
       ELSE
          -- PERFORM * FROM other WHERE other_id = $1;
       END IF;
       RETURN FOUND;
	END;
$_$;


ALTER FUNCTION products.check_datasource(datasourceid character varying, type character varying) OWNER TO estation;

--
-- TOC entry 211 (class 1255 OID 18591)
-- Name: check_eumetcast_source_datasource_description(); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION check_eumetcast_source_datasource_description() RETURNS trigger
    LANGUAGE plpgsql STRICT
    AS $$
BEGIN
	PERFORM * FROM products.datasource_description dd WHERE dd.datasource_descr_id = NEW.eumetcast_id;

	IF NOT FOUND THEN 		
		 NEW.datasource_descr_id = NEW.eumetcast_id;
		 	
		 INSERT INTO products.datasource_description(datasource_descr_id)
		 VALUES(NEW.eumetcast_id);
	END IF;
 
	RETURN NEW;
END;
$$;


ALTER FUNCTION products.check_eumetcast_source_datasource_description() OWNER TO estation;

--
-- TOC entry 212 (class 1255 OID 18589)
-- Name: check_internet_source_datasource_description(); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION check_internet_source_datasource_description() RETURNS trigger
    LANGUAGE plpgsql STRICT
    AS $$
BEGIN
	PERFORM * FROM products.datasource_description dd WHERE dd.datasource_descr_id = NEW.internet_id;

	--		OR TRIM(NEW.datasource_descr_id) != NEW.internet_id) THEN
	IF NOT FOUND THEN		
		 NEW.datasource_descr_id = NEW.internet_id;
		 	
		 INSERT INTO products.datasource_description(datasource_descr_id)
		 VALUES(NEW.internet_id);
	END IF;
 
	RETURN NEW;
END;
$$;


ALTER FUNCTION products.check_internet_source_datasource_description() OWNER TO estation;

--
-- TOC entry 210 (class 1255 OID 17267)
-- Name: check_mapset(character varying); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION check_mapset(mapsetid character varying) RETURNS boolean
    LANGUAGE plpgsql STRICT
    AS $_$
	DECLARE
       mapset_id   ALIAS FOR  $1;
	BEGIN
       PERFORM * FROM products.mapset WHERE mapsetcode = mapset_id;
       RETURN FOUND;
	END;
$_$;


ALTER FUNCTION products.check_mapset(mapsetid character varying) OWNER TO estation;

--
-- TOC entry 217 (class 1255 OID 18660)
-- Name: deactivate_ingestion_when_disabled(); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION deactivate_ingestion_when_disabled() RETURNS trigger
    LANGUAGE plpgsql STRICT
    AS $$
BEGIN
	IF TG_OP='UPDATE' THEN
		-- If both enabled and activated are updated
		IF (OLD.enabled IS DISTINCT FROM NEW.enabled) AND (OLD.activated IS DISTINCT FROM NEW.activated) THEN
			IF NOT NEW.enabled AND NEW.activated THEN
				NEW.activated = FALSE;
			END IF;
		END IF;

		-- If enabled is updated but activated is not updated (not present in update statement)
		IF (OLD.enabled IS DISTINCT FROM NEW.enabled) AND (OLD.activated IS NOT DISTINCT FROM NEW.activated) THEN
			IF NOT NEW.enabled AND OLD.activated THEN
				NEW.activated = FALSE;
			END IF;
		END IF;

		-- If enabled is not updated (not present in update statement) and activated is updated 
		IF (OLD.enabled IS NOT DISTINCT FROM NEW.enabled) AND (OLD.activated IS DISTINCT FROM NEW.activated) THEN
			IF NOT OLD.enabled AND NEW.activated THEN
				NEW.activated = FALSE;
			END IF;
		END IF;
	ELSE
		-- If a new ingestion is inserted
		IF NOT NEW.enabled AND NEW.activated THEN
			NEW.activated = FALSE;
		END IF;
	END IF;
				 
	RETURN NEW;
END;
$$;


ALTER FUNCTION products.deactivate_ingestion_when_disabled() OWNER TO estation;

--
-- TOC entry 221 (class 1255 OID 18676)
-- Name: export_all_data(boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION export_all_data(full_copy boolean DEFAULT true) RETURNS SETOF text
    LANGUAGE plpgsql
    AS $_$
DECLARE 
	_full_copy 			ALIAS FOR  $1;
BEGIN

	RETURN QUERY SELECT 'SELECT products.update_insert_product_category('
		|| 'category_id := ''' || category_id || ''''
		|| ', order_index := ' || order_index 
		|| ', descriptive_name := ' || COALESCE('''' || descriptive_name || '''', 'NULL') 
		|| ' );'  as inserts	   
	FROM products.product_category;


	RETURN QUERY SELECT 'SELECT products.update_insert_frequency('
		|| 'frequency_id := ''' || frequency_id || ''''
		|| ', time_unit := ''' || time_unit || ''''	
		|| ', frequency := ' || frequency 
		|| ', frequency_type := ' || COALESCE('''' || frequency_type || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || description || '''', 'NULL')	
		|| ' );'  as inserts	   
	FROM products.frequency;


	RETURN QUERY SELECT 'SELECT products.update_insert_date_format('
		|| 'date_format := ''' || date_format || ''''
		|| ', definition := ' || COALESCE('''' || definition || '''', 'NULL')	
		|| ' );'  as inserts	   
	FROM products.date_format;


	RETURN QUERY SELECT 'SELECT products.update_insert_data_type('
		|| 'data_type_id := ''' || data_type_id || ''''
		|| ', description := ' || COALESCE('''' || description || '''', 'NULL')	
		|| ' );'  as inserts	   
	FROM products.data_type;


	RETURN QUERY SELECT 'SELECT products.update_insert_mapset('
		|| 'mapsetcode := ''' || mapsetcode || ''''
		|| ', defined_by := ''' || defined_by || ''''	
		|| ', descriptive_name := ' || COALESCE('''' || descriptive_name || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || description || '''', 'NULL')	
		|| ', srs_wkt := ' || COALESCE('''' || srs_wkt || '''', 'NULL')		
		|| ', upper_left_long := ' || upper_left_long 	
		|| ', pixel_shift_long := ' || pixel_shift_long 	
		|| ', rotation_factor_long := ' || rotation_factor_long 	
		|| ', upper_left_lat := ' || upper_left_lat 	
		|| ', pixel_shift_lat := ' || pixel_shift_lat 	
		|| ', rotation_factor_lat := ' || rotation_factor_lat 	
		|| ', pixel_size_x := ' || pixel_size_x 	
		|| ', pixel_size_y:= ' || pixel_size_y 	
		|| ', footprint_image := ''' || COALESCE(footprint_image, 'NULL') || ''''	
		|| ', full_copy := ' || _full_copy		
		|| ' );'  as inserts	   
	FROM products.mapset;


	RETURN QUERY SELECT 'SELECT products.update_insert_thema('
		|| 'thema_id := ''' || thema_id || ''''
		|| ', description := ' || COALESCE('''' || description || '''', 'NULL')	
		|| ' );'  as inserts	   
	FROM products.thema;


	  
	RETURN QUERY SELECT 'SELECT products.update_insert_product('
		|| '  productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', activated := ' || activated	
		|| ', category_id := ' || COALESCE('''' || category_id || '''', 'NULL')	
		|| ', product_type := ' || COALESCE('''' || product_type || '''', 'NULL')
		|| ', descriptive_name := ' || COALESCE('''' || replace(descriptive_name, '''', '"') || '''', 'NULL')	
		|| ', description := ' || COALESCE('''' || replace(description, '''', '"') || '''', 'NULL')	
		|| ', provider := ' || COALESCE('''' || provider || '''', 'NULL')	
		|| ', frequency_id := ' || COALESCE('''' || frequency_id || '''', '''undefined''')
		|| ', date_format := ' || COALESCE('''' || date_format || '''', '''undefined''')
		|| ', scale_factor := ' || COALESCE(TRIM(to_char(scale_factor, '99999999D999999')), 'NULL')
		|| ', scale_offset := ' || COALESCE(TRIM(to_char(scale_offset, '99999999D999999')), 'NULL')
		|| ', nodata := ' || COALESCE(TRIM(to_char(nodata, '99999999')), 'NULL')
		|| ', mask_min := ' || COALESCE(TRIM(to_char(mask_min, '99999999D999999')), 'NULL')
		|| ', mask_max := ' || COALESCE(TRIM(to_char(mask_max, '99999999D999999')), 'NULL')	
		|| ', unit := ' || COALESCE('''' || unit || '''', 'NULL')
		|| ', data_type_id := ' || COALESCE('''' || data_type_id || '''', '''undefined''')
		|| ', masked := ' || masked
		|| ', timeseries_role := ' || COALESCE('''' || timeseries_role || '''', 'NULL')		
		|| ', full_copy := ' || _full_copy				
		|| ' );'  as inserts	   
	FROM products.product;


	  
	RETURN QUERY SELECT 'SELECT products.update_insert_thema_product('
		|| 'thema_id := ''' || thema_id || ''''
		|| ', productcode := ''' || productcode || ''''	
		|| ', version := ''' || version || ''''	
		|| ', mapsetcode := ''' || mapsetcode || ''''	
		|| ', activated := ' || activated 	
		|| ' );'  as inserts	   
	FROM products.thema_product;


	

	RETURN QUERY SELECT 'SELECT products.update_insert_internet_source('
		|| 'internet_id := ''' || internet_id || ''''
		|| ', defined_by := ''' || defined_by || ''''	
		|| ', descriptive_name := ' || COALESCE('''' || descriptive_name || '''', 'NULL')	
		|| ', description := ' || COALESCE('''' || description || '''', 'NULL')	
		|| ', modified_by := ' || COALESCE('''' || modified_by || '''', 'NULL')			
		|| ', update_datetime := ''' || COALESCE(update_datetime, now()) || ''''			
		|| ', url := ' || COALESCE('''' || url || '''', 'NULL')	
		|| ', user_name := ' || COALESCE('''' || user_name || '''', 'NULL')	
		|| ', password := ' || COALESCE('''' || password || '''', 'NULL')	
		|| ', type := ' || COALESCE('''' || type || '''', 'NULL')	
		|| ', include_files_expression := ' || COALESCE('''' || include_files_expression || '''', 'NULL')	
		|| ', files_filter_expression := ' || COALESCE('''' || files_filter_expression || '''', 'NULL')		
		|| ', status := ' || status 		
		|| ', pull_frequency:= ' || pull_frequency 	
		|| ', datasource_descr_id := ' || COALESCE('''' || internet_id || '''', 'NULL')		
		|| ', frequency_id := ' || COALESCE('''' || frequency_id || '''', '''undefined''') 					
		|| ', start_date:=   ' || COALESCE(TRIM(to_char(start_date, '999999999999')), 'NULL')	  
		|| ', end_date:= ' || COALESCE(TRIM(to_char(end_date, '999999999999')), 'NULL')
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.internet_source;




	RETURN QUERY SELECT 'SELECT products.update_insert_eumetcast_source('
		|| '  eumetcast_id := ' || COALESCE('''' || eumetcast_id || '''', 'NULL')
		|| ', filter_expression_jrc := ' || COALESCE('''' || filter_expression_jrc || '''', 'NULL')
		|| ', collection_name := ' || COALESCE('''' || collection_name || '''', 'NULL')
		|| ', status := ' || status	
		|| ', internal_identifier := ' || COALESCE('''' || internal_identifier || '''', 'NULL')	
		|| ', collection_reference := ' || COALESCE('''' || collection_reference || '''', 'NULL')	
		|| ', acronym := ' || COALESCE('''' || acronym || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(description, '''', '"') || '''', 'NULL')	
		|| ', product_status := ' || COALESCE('''' || product_status || '''', 'NULL')
		|| ', date_creation := ' || COALESCE('''' || to_char(date_creation, 'YYYY-MM-DD') || '''', 'NULL') 	
		|| ', date_revision := ' || COALESCE('''' || to_char(date_revision, 'YYYY-MM-DD') || '''', 'NULL') 		
		|| ', date_publication := ' || COALESCE('''' || to_char(date_publication, 'YYYY-MM-DD') || '''', 'NULL') 	
		|| ', west_bound_longitude := ' || COALESCE(TRIM(to_char(west_bound_longitude, '99999999D999999')), 'NULL')
		|| ', east_bound_longitude := ' || COALESCE(TRIM(to_char(east_bound_longitude, '99999999D999999')), 'NULL')
		|| ', north_bound_latitude := ' || COALESCE(TRIM(to_char(north_bound_latitude, '99999999D999999')), 'NULL')
		|| ', south_bound_latitude := ' || COALESCE(TRIM(to_char(south_bound_latitude, '99999999D999999')), 'NULL')
		|| ', provider_short_name := ' || COALESCE('''' || provider_short_name || '''', 'NULL')
		|| ', collection_type := ' || COALESCE('''' || collection_type || '''', 'NULL')
		|| ', keywords_distribution := ' || COALESCE('''' || keywords_distribution || '''', 'NULL')	
		|| ', keywords_theme := ' || COALESCE('''' || keywords_theme || '''', 'NULL')
		|| ', keywords_societal_benefit_area := ' || COALESCE('''' || keywords_societal_benefit_area || '''', 'NULL')
		|| ', orbit_type := ' || COALESCE('''' || orbit_type || '''', 'NULL')
		|| ', satellite := ' || COALESCE('''' || satellite || '''', 'NULL')
		|| ', satellite_description := ' || COALESCE('''' || satellite_description || '''', 'NULL')	
		|| ', instrument := ' || COALESCE('''' || instrument || '''', 'NULL')
		|| ', spatial_coverage := ' || COALESCE('''' || spatial_coverage || '''', 'NULL')
		|| ', thumbnails := ' || COALESCE('''' || thumbnails || '''', 'NULL')
		|| ', online_resources := ' || COALESCE('''' || replace(online_resources, '''', '"') || '''', 'NULL')
		|| ', distribution := ' || COALESCE('''' || distribution || '''', 'NULL')
		|| ', channels := ' || COALESCE('''' || channels || '''', 'NULL')
		|| ', data_access := ' || COALESCE('''' || replace(data_access, '''', '"') || '''', 'NULL')
		|| ', available_format := ' || COALESCE('''' || available_format || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', typical_file_name := ' || COALESCE('''' || typical_file_name || '''', 'NULL')
		|| ', average_file_size := ' || COALESCE('''' || average_file_size || '''', 'NULL')
		|| ', frequency := ' || COALESCE('''' || frequency || '''', 'NULL')
		|| ', legal_constraints_access_constraint := ' || COALESCE('''' || legal_constraints_access_constraint || '''', 'NULL')
		|| ', legal_use_constraint := ' || COALESCE('''' || legal_use_constraint || '''', 'NULL')
		|| ', legal_constraints_data_policy := ' || COALESCE('''' || legal_constraints_data_policy || '''', 'NULL')	
		|| ', entry_date := ' || COALESCE('''' || to_char(entry_date, 'YYYY-MM-DD') || '''', 'NULL')
		|| ', reference_file := ' || COALESCE('''' || reference_file || '''', 'NULL')
		|| ', datasource_descr_id := ' || COALESCE('''' || eumetcast_id || '''', 'NULL')	
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.eumetcast_source;

	  
	  
	RETURN QUERY SELECT 'SELECT products.update_insert_datasource_description('
		|| '  datasource_descr_id := ' || COALESCE('''' || datasource_descr_id || '''', 'NULL')
		|| ', format_type := ' || COALESCE('''' || format_type || '''', 'NULL')
		|| ', file_extension := ' || COALESCE('''' || file_extension || '''', 'NULL')
		|| ', delimiter := ' || COALESCE('''' || delimiter || '''', 'NULL')
		|| ', date_format := ' || COALESCE('''' || date_format || '''', '''undefined''') 
		|| ', date_position := ' || COALESCE('''' || date_position || '''', 'NULL')	
		|| ', product_identifier := ' || COALESCE('''' || product_identifier || '''', 'NULL')
		|| ', prod_id_position := ' || COALESCE(TRIM(to_char(prod_id_position, '99999999')), 'NULL')
		|| ', prod_id_length := ' || COALESCE(TRIM(to_char(prod_id_length, '99999999')), 'NULL')
		|| ', area_type := ' || COALESCE('''' || area_type || '''', 'NULL')	
		|| ', area_position := ' || COALESCE('''' || area_position || '''', 'NULL')
		|| ', area_length := ' || COALESCE(TRIM(to_char(area_length, '99999999')), 'NULL')
		|| ', preproc_type := ' || COALESCE('''' || preproc_type || '''', 'NULL')	
		|| ', product_release := ' || COALESCE('''' || product_release || '''', 'NULL')
		|| ', release_position := ' || COALESCE('''' || release_position || '''', 'NULL')
		|| ', release_length := ' || COALESCE(TRIM(to_char(release_length, '99999999')), 'NULL')
		|| ', native_mapset := ' || COALESCE('''' || native_mapset || '''', 'NULL')	
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.datasource_description dd;



	RETURN QUERY SELECT 'SELECT products.update_insert_product_acquisition_data_source('
		|| ' productcode := ''' || productcode || ''''	
		|| ', subproductcode := ''' || subproductcode || ''''		
		|| ', version := ''' || version || ''''	
		|| ', data_source_id := ''' || data_source_id || ''''	
		|| ', defined_by := ''' || defined_by || ''''	
		|| ', type := ''' || type || ''''		
		|| ', activated := ' || activated 	
		|| ', store_original_data := ' || store_original_data 	
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.product_acquisition_data_source;



	RETURN QUERY SELECT 'SELECT products.update_insert_sub_datasource_description('
		|| '  productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', datasource_descr_id := ' || COALESCE('''' || datasource_descr_id || '''', 'NULL')
		|| ', scale_factor := ' || COALESCE(TRIM(to_char(scale_factor, '99999999D999999')), 'NULL')
		|| ', scale_offset := ' || COALESCE(TRIM(to_char(scale_offset, '99999999D999999')), 'NULL')
		|| ', no_data := ' || COALESCE(TRIM(to_char(no_data, '99999999D999999')), 'NULL')
		|| ', data_type_id := ' || COALESCE('''' || data_type_id || '''', '''undefined''')	
		|| ', mask_min := ' || COALESCE(TRIM(to_char(mask_min, '99999999D999999')), 'NULL')
		|| ', mask_max := ' || COALESCE(TRIM(to_char(mask_max, '99999999D999999')), 'NULL')	
		|| ', re_process := ' || COALESCE('''' || re_process || '''', 'NULL')
		|| ', re_extract := ' || COALESCE('''' || re_extract || '''', 'NULL')		
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.sub_datasource_description;



	RETURN QUERY SELECT 'SELECT products.update_insert_ingestion('
		|| '  productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', mapsetcode := ' || COALESCE('''' || mapsetcode || '''', 'NULL')
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', activated := ' || activated 	
		|| ', wait_for_all_files := ' || wait_for_all_files 		
		|| ', input_to_process_re := ' || COALESCE('''' || input_to_process_re || '''', 'NULL')
		|| ', enabled := ' || enabled 		
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.ingestion;



	RETURN QUERY SELECT 'SELECT products.update_insert_processing('
		|| ' process_id := ' || process_id
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', output_mapsetcode := ' || COALESCE('''' || output_mapsetcode || '''', 'NULL')
		|| ', activated := ' || activated 	
		|| ', derivation_method := ' || COALESCE('''' || derivation_method || '''', 'NULL')
		|| ', algorithm := ' || COALESCE('''' || algorithm || '''', 'NULL')
		|| ', priority := ' || COALESCE('''' || priority || '''', 'NULL')
		|| ', enabled := ' || enabled 	
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.processing;



	RETURN QUERY SELECT 'SELECT products.update_insert_process_product('
		|| ' process_id := ' || process_id
		|| ', productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', mapsetcode := ' || COALESCE('''' || mapsetcode || '''', 'NULL')
		|| ', type := ' || COALESCE('''' || type || '''', 'NULL')
		|| ', activated := ' || activated 	
		|| ', final := ' || final 		
		|| ', date_format := ' || COALESCE('''' || date_format || '''', '''undefined''')
		|| ', start_date:=   ' || COALESCE(TRIM(to_char(start_date, '999999999999')), 'NULL')	  
		|| ', end_date:= ' || COALESCE(TRIM(to_char(end_date, '999999999999')), 'NULL')	
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.process_product;

		
	RETURN QUERY SELECT 'SELECT analysis.update_insert_i18n('
		|| ' label := ' || COALESCE('''' || label || '''', 'NULL') 
		|| ', eng := ''' || COALESCE(replace(eng, '''', '"'), 'NULL') || ''''
		|| ', fra := ''' || COALESCE(replace(fra, '''', '"'), 'NULL') || ''''
		|| ', por := ''' || COALESCE(replace(por, '''', '"'), 'NULL') || ''''
		|| ', lang1 := ''' || COALESCE(replace(lang1, '''', '"'), 'NULL') || ''''
		|| ', lang2 := ''' || COALESCE(replace(lang2, '''', '"'), 'NULL') || ''''
		|| ', lang3 := ''' || COALESCE(replace(lang3, '''', '"'), 'NULL') || ''''
		|| ' );'  as inserts	   
	FROM analysis.i18n;


	RETURN QUERY SELECT 'SELECT analysis.update_insert_languages('
		|| ' langcode := ' || COALESCE('''' || langcode || '''', 'NULL')
		|| ', langdescription := ' || COALESCE('''' || langdescription || '''', 'NULL')
		|| ', active := ' || active 	
		|| ' );'  as inserts	   
	FROM analysis.languages;
	

														  
	RETURN QUERY SELECT 'SELECT analysis.update_insert_legend('
		|| ' legend_id := ' || legend_id
		|| ', legend_name := ' || COALESCE('''' || legend_name || '''', 'NULL')
		|| ', step_type := ' || COALESCE('''' || step_type || '''', 'NULL')
		|| ', min_value := ' || COALESCE(TRIM(to_char(min_value, '99999999D999999')), 'NULL')
		|| ', max_value := ' || COALESCE(TRIM(to_char(max_value, '99999999D999999')), 'NULL')	
		|| ', min_real_value := ' || COALESCE('''' || min_real_value || '''', 'NULL')
		|| ', max_real_value := ''' || COALESCE(max_real_value, 'NULL') || ''''
		|| ', colorbar := ''' || COALESCE(colorbar, 'NULL') || ''''		
		|| ', step := ' || COALESCE(TRIM(to_char(step, '99999999D999999')), 'NULL')
		|| ', step_range_from := ' || COALESCE(TRIM(to_char(step_range_from, '99999999D999999')), 'NULL')
		|| ', step_range_to := ' || COALESCE(TRIM(to_char(step_range_to, '99999999D999999')), 'NULL')
		|| ', unit := ' || COALESCE('''' || unit || '''', 'NULL')
		|| ' );'  as inserts	   
	FROM analysis.legend;

	

	RETURN QUERY SELECT 'SELECT analysis.update_insert_legend_step('
		|| ' legend_id := ' || legend_id
		|| ', from_step :=  ' || from_step
		|| ', to_step :=  ' || to_step		
		|| ', color_rgb := ' || COALESCE('''' || color_rgb || '''', 'NULL')
		|| ', color_label := ' || COALESCE('''' || color_label || '''', 'NULL')
		|| ', group_label := ' || COALESCE('''' || group_label || '''', 'NULL')
		|| ' );'  as inserts	   
	FROM analysis.legend_step;


	
	RETURN QUERY SELECT 'SELECT analysis.update_insert_product_legend('	
		|| ' productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', legend_id := ' || legend_id
		|| ', default_legend := ' || default_legend			
		|| ' );'  as inserts	   
	FROM analysis.product_legend;

	
																			
	RETURN QUERY SELECT 'SELECT analysis.update_insert_timeseries_drawproperties('
		|| ' productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')		
		|| ', title := ' || COALESCE('''' || title || '''', 'NULL')
		|| ', unit := ' || COALESCE('''' || unit || '''', 'NULL')		
		|| ', min := ' || COALESCE(TRIM(to_char(min, '99999999D999999')), 'NULL')
		|| ', max := ' || COALESCE(TRIM(to_char(max, '99999999D999999')), 'NULL')		
		|| ', oposite := ' || oposite				
		|| ', tsname_in_legend := ' || COALESCE('''' || tsname_in_legend || '''', 'NULL')
		|| ', charttype := ' || COALESCE('''' || charttype || '''', 'NULL')
		|| ', linestyle := ' || COALESCE('''' || linestyle || '''', 'NULL')
		|| ', linewidth := ' || COALESCE(TRIM(to_char(linewidth, '99999999')), 'NULL')
		|| ', color := ' || COALESCE('''' || color || '''', 'NULL')
		|| ', yaxes_id := ' || COALESCE('''' || yaxes_id || '''', 'NULL')
		|| ', title_color := ' || COALESCE('''' || title_color || '''', 'NULL')
		|| ' );'  as inserts	   
	FROM analysis.timeseries_drawproperties;	
	
	
	
	RETURN QUERY SELECT 'SELECT products.update_insert_spirits('
		|| '  productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', mapsetcode := ' || COALESCE('''' || mapsetcode || '''', 'NULL')
		|| ', prod_values := ' || COALESCE('''' || prod_values || '''', 'NULL')
		|| ', flags := ' || COALESCE('''' || flags || '''', 'NULL')
		|| ', data_ignore_value := ' || COALESCE(TRIM(to_char(data_ignore_value, '99999999')), 'NULL')
		|| ', days := ' || COALESCE(TRIM(to_char(days, '99999999')), 'NULL')
		|| ', start_date := ' || COALESCE(TRIM(to_char(start_date, '99999999')), 'NULL')
		|| ', end_date := ' || COALESCE(TRIM(to_char(end_date, '99999999')), 'NULL')	
		|| ', sensor_type := ' || COALESCE('''' || sensor_type || '''', 'NULL')
		|| ', comment := ' || COALESCE('''' || comment || '''', 'NULL')				
		|| ', sensor_filename_prefix := ' || COALESCE('''' || sensor_filename_prefix || '''', 'NULL')		
		|| ', frequency_filename_prefix := ' || COALESCE('''' || frequency_filename_prefix || '''', 'NULL')		
		|| ', product_anomaly_filename_prefix := ' || COALESCE('''' || product_anomaly_filename_prefix || '''', 'NULL')
		|| ', activated := ' || activated						
		|| ' );'  as inserts	   
	FROM products.spirits;	
	
END;
$_$;


ALTER FUNCTION products.export_all_data(full_copy boolean) OWNER TO estation;

--
-- TOC entry 216 (class 1255 OID 18610)
-- Name: export_jrc_data(boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION export_jrc_data(full_copy boolean DEFAULT false) RETURNS SETOF text
    LANGUAGE plpgsql
    AS $_$
DECLARE 
	_full_copy 			ALIAS FOR  $1;
BEGIN
	-- full_copy := FALSE;

	RETURN QUERY SELECT 'SELECT products.update_insert_product_category('
		|| 'category_id := ''' || category_id || ''''
		|| ', order_index := ' || order_index 
		|| ', descriptive_name := ' || COALESCE('''' || descriptive_name || '''', 'NULL') 
		|| ' );'  as inserts	   
	FROM products.product_category;


	RETURN QUERY SELECT 'SELECT products.update_insert_frequency('
		|| 'frequency_id := ''' || frequency_id || ''''
		|| ', time_unit := ''' || time_unit || ''''	
		|| ', frequency := ' || frequency 
		|| ', frequency_type := ' || COALESCE('''' || frequency_type || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || description || '''', 'NULL')	
		|| ' );'  as inserts	   
	FROM products.frequency;


	RETURN QUERY SELECT 'SELECT products.update_insert_date_format('
		|| 'date_format := ''' || date_format || ''''
		|| ', definition := ' || COALESCE('''' || definition || '''', 'NULL')	
		|| ' );'  as inserts	   
	FROM products.date_format;


	RETURN QUERY SELECT 'SELECT products.update_insert_data_type('
		|| 'data_type_id := ''' || data_type_id || ''''
		|| ', description := ' || COALESCE('''' || description || '''', 'NULL')	
		|| ' );'  as inserts	   
	FROM products.data_type;


	RETURN QUERY SELECT 'SELECT products.update_insert_mapset('
		|| 'mapsetcode := ''' || mapsetcode || ''''
		|| ', defined_by := ''' || defined_by || ''''	
		|| ', descriptive_name := ' || COALESCE('''' || descriptive_name || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || description || '''', 'NULL')	
		|| ', srs_wkt := ' || COALESCE('''' || srs_wkt || '''', 'NULL')		
		|| ', upper_left_long := ' || upper_left_long 	
		|| ', pixel_shift_long := ' || pixel_shift_long 	
		|| ', rotation_factor_long := ' || rotation_factor_long 	
		|| ', upper_left_lat := ' || upper_left_lat 	
		|| ', pixel_shift_lat := ' || pixel_shift_lat 	
		|| ', rotation_factor_lat := ' || rotation_factor_lat 	
		|| ', pixel_size_x := ' || pixel_size_x 	
		|| ', pixel_size_y:= ' || pixel_size_y 	
		|| ', footprint_image := ''' || COALESCE(footprint_image, 'NULL') || ''''	
		|| ', full_copy := ' || _full_copy		
		|| ' );'  as inserts	   
	FROM products.mapset
	WHERE defined_by = 'JRC';


	RETURN QUERY SELECT 'SELECT products.update_insert_thema('
		|| 'thema_id := ''' || thema_id || ''''
		|| ', description := ' || COALESCE('''' || description || '''', 'NULL')	
		|| ' );'  as inserts	   
	FROM products.thema;


	  
	RETURN QUERY SELECT 'SELECT products.update_insert_product('
		|| '  productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', activated := ' || activated	
		|| ', category_id := ' || COALESCE('''' || category_id || '''', 'NULL')	
		|| ', product_type := ' || COALESCE('''' || product_type || '''', 'NULL')
		|| ', descriptive_name := ' || COALESCE('''' || replace(descriptive_name, '''', '"') || '''', 'NULL')	
		|| ', description := ' || COALESCE('''' || replace(description, '''', '"') || '''', 'NULL')	
		|| ', provider := ' || COALESCE('''' || provider || '''', 'NULL')	
		|| ', frequency_id := ' || COALESCE('''' || frequency_id || '''', '''undefined''')
		|| ', date_format := ' || COALESCE('''' || date_format || '''', '''undefined''')
		|| ', scale_factor := ' || COALESCE(TRIM(to_char(scale_factor, '99999999D999999')), 'NULL')
		|| ', scale_offset := ' || COALESCE(TRIM(to_char(scale_offset, '99999999D999999')), 'NULL')
		|| ', nodata := ' || COALESCE(TRIM(to_char(nodata, '99999999')), 'NULL')
		|| ', mask_min := ' || COALESCE(TRIM(to_char(mask_min, '99999999D999999')), 'NULL')
		|| ', mask_max := ' || COALESCE(TRIM(to_char(mask_max, '99999999D999999')), 'NULL')	
		|| ', unit := ' || COALESCE('''' || unit || '''', 'NULL')
		|| ', data_type_id := ' || COALESCE('''' || data_type_id || '''', '''undefined''')
		|| ', masked := ' || masked
		|| ', timeseries_role := ' || COALESCE('''' || timeseries_role || '''', 'NULL')		
		|| ', full_copy := ' || _full_copy				
		|| ' );'  as inserts	   
	FROM products.product
	WHERE defined_by = 'JRC';


	  
	RETURN QUERY SELECT 'SELECT products.update_insert_thema_product('
		|| 'thema_id := ''' || thema_id || ''''
		|| ', productcode := ''' || productcode || ''''	
		|| ', version := ''' || version || ''''	
		|| ', mapsetcode := ''' || mapsetcode || ''''	
		|| ', activated := ' || activated 	
		|| ' );'  as inserts	   
	FROM products.thema_product;


	  
	-- insert into products.datasource_description (datasource_descr_id) select internet_id from products.internet_source where internet_id not in (select datasource_descr_id from products.datasource_description)

	RETURN QUERY SELECT 'SELECT products.update_insert_internet_source('
		|| 'internet_id := ''' || internet_id || ''''
		|| ', defined_by := ''' || defined_by || ''''	
		|| ', descriptive_name := ' || COALESCE('''' || descriptive_name || '''', 'NULL')	
		|| ', description := ' || COALESCE('''' || description || '''', 'NULL')	
		|| ', modified_by := ' || COALESCE('''' || modified_by || '''', 'NULL')			
		|| ', update_datetime := ''' || COALESCE(update_datetime, now()) || ''''			
		|| ', url := ' || COALESCE('''' || url || '''', 'NULL')	
		|| ', user_name := ' || COALESCE('''' || user_name || '''', 'NULL')	
		|| ', password := ' || COALESCE('''' || password || '''', 'NULL')	
		|| ', type := ' || COALESCE('''' || type || '''', 'NULL')	
		|| ', include_files_expression := ' || COALESCE('''' || include_files_expression || '''', 'NULL')	
		|| ', files_filter_expression := ' || COALESCE('''' || files_filter_expression || '''', 'NULL')		
		|| ', status := ' || status 		
		|| ', pull_frequency:= ' || pull_frequency 	
		|| ', datasource_descr_id := ' || COALESCE('''' || internet_id || '''', 'NULL')		
		|| ', frequency_id := ' || COALESCE('''' || frequency_id || '''', '''undefined''') 					
		|| ', start_date:=   ' || COALESCE(TRIM(to_char(start_date, '999999999999')), 'NULL')	  
		|| ', end_date:= ' || COALESCE(TRIM(to_char(end_date, '999999999999')), 'NULL')
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.internet_source
	WHERE defined_by = 'JRC';


	-- insert into products.datasource_description (datasource_descr_id) select eumetcast_id from products.eumetcast_source where eumetcast_id not in (select datasource_descr_id from products.datasource_description)

	RETURN QUERY SELECT 'SELECT products.update_insert_eumetcast_source('
		|| '  eumetcast_id := ' || COALESCE('''' || eumetcast_id || '''', 'NULL')
		|| ', filter_expression_jrc := ' || COALESCE('''' || filter_expression_jrc || '''', 'NULL')
		|| ', collection_name := ' || COALESCE('''' || collection_name || '''', 'NULL')
		|| ', status := ' || status	
		|| ', internal_identifier := ' || COALESCE('''' || internal_identifier || '''', 'NULL')	
		|| ', collection_reference := ' || COALESCE('''' || collection_reference || '''', 'NULL')	
		|| ', acronym := ' || COALESCE('''' || acronym || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(description, '''', '"') || '''', 'NULL')	
		|| ', product_status := ' || COALESCE('''' || product_status || '''', 'NULL')
		|| ', date_creation := ' || COALESCE('''' || to_char(date_creation, 'YYYY-MM-DD') || '''', 'NULL') 	
		|| ', date_revision := ' || COALESCE('''' || to_char(date_revision, 'YYYY-MM-DD') || '''', 'NULL') 		
		|| ', date_publication := ' || COALESCE('''' || to_char(date_publication, 'YYYY-MM-DD') || '''', 'NULL') 	
		|| ', west_bound_longitude := ' || COALESCE(TRIM(to_char(west_bound_longitude, '99999999D999999')), 'NULL')
		|| ', east_bound_longitude := ' || COALESCE(TRIM(to_char(east_bound_longitude, '99999999D999999')), 'NULL')
		|| ', north_bound_latitude := ' || COALESCE(TRIM(to_char(north_bound_latitude, '99999999D999999')), 'NULL')
		|| ', south_bound_latitude := ' || COALESCE(TRIM(to_char(south_bound_latitude, '99999999D999999')), 'NULL')
		|| ', provider_short_name := ' || COALESCE('''' || provider_short_name || '''', 'NULL')
		|| ', collection_type := ' || COALESCE('''' || collection_type || '''', 'NULL')
		|| ', keywords_distribution := ' || COALESCE('''' || keywords_distribution || '''', 'NULL')	
		|| ', keywords_theme := ' || COALESCE('''' || keywords_theme || '''', 'NULL')
		|| ', keywords_societal_benefit_area := ' || COALESCE('''' || keywords_societal_benefit_area || '''', 'NULL')
		|| ', orbit_type := ' || COALESCE('''' || orbit_type || '''', 'NULL')
		|| ', satellite := ' || COALESCE('''' || satellite || '''', 'NULL')
		|| ', satellite_description := ' || COALESCE('''' || satellite_description || '''', 'NULL')	
		|| ', instrument := ' || COALESCE('''' || instrument || '''', 'NULL')
		|| ', spatial_coverage := ' || COALESCE('''' || spatial_coverage || '''', 'NULL')
		|| ', thumbnails := ' || COALESCE('''' || thumbnails || '''', 'NULL')
		|| ', online_resources := ' || COALESCE('''' || replace(online_resources, '''', '"') || '''', 'NULL')
		|| ', distribution := ' || COALESCE('''' || distribution || '''', 'NULL')
		|| ', channels := ' || COALESCE('''' || channels || '''', 'NULL')
		|| ', data_access := ' || COALESCE('''' || replace(data_access, '''', '"') || '''', 'NULL')
		|| ', available_format := ' || COALESCE('''' || available_format || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', typical_file_name := ' || COALESCE('''' || typical_file_name || '''', 'NULL')
		|| ', average_file_size := ' || COALESCE('''' || average_file_size || '''', 'NULL')
		|| ', frequency := ' || COALESCE('''' || frequency || '''', 'NULL')
		|| ', legal_constraints_access_constraint := ' || COALESCE('''' || legal_constraints_access_constraint || '''', 'NULL')
		|| ', legal_use_constraint := ' || COALESCE('''' || legal_use_constraint || '''', 'NULL')
		|| ', legal_constraints_data_policy := ' || COALESCE('''' || legal_constraints_data_policy || '''', 'NULL')	
		|| ', entry_date := ' || COALESCE('''' || to_char(entry_date, 'YYYY-MM-DD') || '''', 'NULL')
		|| ', reference_file := ' || COALESCE('''' || reference_file || '''', 'NULL')
		|| ', datasource_descr_id := ' || COALESCE('''' || eumetcast_id || '''', 'NULL')	
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.eumetcast_source;

	  
	  
	RETURN QUERY SELECT 'SELECT products.update_insert_datasource_description('
		|| '  datasource_descr_id := ' || COALESCE('''' || datasource_descr_id || '''', 'NULL')
		|| ', format_type := ' || COALESCE('''' || format_type || '''', 'NULL')
		|| ', file_extension := ' || COALESCE('''' || file_extension || '''', 'NULL')
		|| ', delimiter := ' || COALESCE('''' || delimiter || '''', 'NULL')
		|| ', date_format := ' || COALESCE('''' || date_format || '''', '''undefined''') 
		|| ', date_position := ' || COALESCE('''' || date_position || '''', 'NULL')	
		|| ', product_identifier := ' || COALESCE('''' || product_identifier || '''', 'NULL')
		|| ', prod_id_position := ' || COALESCE(TRIM(to_char(prod_id_position, '99999999')), 'NULL')
		|| ', prod_id_length := ' || COALESCE(TRIM(to_char(prod_id_length, '99999999')), 'NULL')
		|| ', area_type := ' || COALESCE('''' || area_type || '''', 'NULL')	
		|| ', area_position := ' || COALESCE('''' || area_position || '''', 'NULL')
		|| ', area_length := ' || COALESCE(TRIM(to_char(area_length, '99999999')), 'NULL')
		|| ', preproc_type := ' || COALESCE('''' || preproc_type || '''', 'NULL')	
		|| ', product_release := ' || COALESCE('''' || product_release || '''', 'NULL')
		|| ', release_position := ' || COALESCE('''' || release_position || '''', 'NULL')
		|| ', release_length := ' || COALESCE(TRIM(to_char(release_length, '99999999')), 'NULL')
		|| ', native_mapset := ' || COALESCE('''' || native_mapset || '''', 'NULL')	
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts		   
	FROM products.datasource_description dd 
	WHERE dd.datasource_descr_id in (SELECT eumetcast_id FROM products.eumetcast_source)
	  OR dd.datasource_descr_id in (SELECT internet_id FROM products.internet_source WHERE defined_by = 'JRC');



	RETURN QUERY SELECT 'SELECT products.update_insert_product_acquisition_data_source('
		|| ' productcode := ''' || productcode || ''''	
		|| ', subproductcode := ''' || subproductcode || ''''		
		|| ', version := ''' || version || ''''	
		|| ', data_source_id := ''' || data_source_id || ''''	
		|| ', defined_by := ''' || defined_by || ''''	
		|| ', type := ''' || type || ''''		
		|| ', activated := ' || activated 	
		|| ', store_original_data := ' || store_original_data 	
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts		   
	FROM products.product_acquisition_data_source
	WHERE defined_by = 'JRC';



	RETURN QUERY SELECT 'SELECT products.update_insert_sub_datasource_description('
		|| '  productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', datasource_descr_id := ' || COALESCE('''' || datasource_descr_id || '''', 'NULL')
		|| ', scale_factor := ' || COALESCE(TRIM(to_char(scale_factor, '99999999D999999')), 'NULL')
		|| ', scale_offset := ' || COALESCE(TRIM(to_char(scale_offset, '99999999D999999')), 'NULL')
		|| ', no_data := ' || COALESCE(TRIM(to_char(no_data, '99999999D999999')), 'NULL')
		|| ', data_type_id := ' || COALESCE('''' || data_type_id || '''', '''undefined''')	
		|| ', mask_min := ' || COALESCE(TRIM(to_char(mask_min, '99999999D999999')), 'NULL')
		|| ', mask_max := ' || COALESCE(TRIM(to_char(mask_max, '99999999D999999')), 'NULL')	
		|| ', re_process := ' || COALESCE('''' || re_process || '''', 'NULL')
		|| ', re_extract := ' || COALESCE('''' || re_extract || '''', 'NULL')		
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts		   
	FROM products.sub_datasource_description;



	RETURN QUERY SELECT 'SELECT products.update_insert_ingestion('
		|| '  productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', mapsetcode := ' || COALESCE('''' || mapsetcode || '''', 'NULL')
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', activated := ' || activated 	
		|| ', wait_for_all_files := ' || wait_for_all_files 		
		|| ', input_to_process_re := ' || COALESCE('''' || input_to_process_re || '''', 'NULL')
		|| ', enabled := ' || enabled 		
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.ingestion
	WHERE defined_by = 'JRC';



	RETURN QUERY SELECT 'SELECT products.update_insert_processing('
		|| ' process_id := ' || process_id
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', output_mapsetcode := ' || COALESCE('''' || output_mapsetcode || '''', 'NULL')
		|| ', activated := ' || activated 	
		|| ', derivation_method := ' || COALESCE('''' || derivation_method || '''', 'NULL')
		|| ', algorithm := ' || COALESCE('''' || algorithm || '''', 'NULL')
		|| ', priority := ' || COALESCE('''' || priority || '''', 'NULL')
		|| ', enabled := ' || enabled 	
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.processing
	WHERE defined_by = 'JRC';



	RETURN QUERY SELECT 'SELECT products.update_insert_process_product('
		|| ' process_id := ' || process_id
		|| ', productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', mapsetcode := ' || COALESCE('''' || mapsetcode || '''', 'NULL')
		|| ', type := ' || COALESCE('''' || type || '''', 'NULL')
		|| ', activated := ' || activated 	
		|| ', final := ' || final 		
		|| ', date_format := ' || COALESCE('''' || date_format || '''', '''undefined''')
		|| ', start_date:=   ' || COALESCE(TRIM(to_char(start_date, '999999999999')), 'NULL')	  
		|| ', end_date:= ' || COALESCE(TRIM(to_char(end_date, '999999999999')), 'NULL')	
		|| ', full_copy := ' || _full_copy						
		|| ' );'  as inserts	   
	FROM products.process_product
	WHERE process_id IN (SELECT process_id FROM products.processing WHERE defined_by = 'JRC');

	
	RETURN QUERY SELECT 'SELECT analysis.update_insert_i18n('
		|| ' label := ' || COALESCE('''' || label || '''', 'NULL') 
		|| ', eng := ''' || COALESCE(replace(eng, '''', '"'), 'NULL') || ''''
		|| ', fra := ''' || COALESCE(replace(fra, '''', '"'), 'NULL') || ''''
		|| ', por := ''' || COALESCE(replace(por, '''', '"'), 'NULL') || ''''
		|| ', lang1 := ''' || COALESCE(replace(lang1, '''', '"'), 'NULL') || ''''
		|| ', lang2 := ''' || COALESCE(replace(lang2, '''', '"'), 'NULL') || ''''
		|| ', lang3 := ''' || COALESCE(replace(lang3, '''', '"'), 'NULL') || ''''
		|| ' );'  as inserts	   
	FROM analysis.i18n;


	RETURN QUERY SELECT 'SELECT analysis.update_insert_languages('
		|| ' langcode := ' || COALESCE('''' || langcode || '''', 'NULL')
		|| ', langdescription := ' || COALESCE('''' || langdescription || '''', 'NULL')
		|| ', active := ' || active 	
		|| ' );'  as inserts	   
	FROM analysis.languages;
	

														  
	RETURN QUERY SELECT 'SELECT analysis.update_insert_legend('
		|| ' legend_id := ' || legend_id
		|| ', legend_name := ' || COALESCE('''' || legend_name || '''', 'NULL')
		|| ', step_type := ' || COALESCE('''' || step_type || '''', 'NULL')
		|| ', min_value := ' || COALESCE(TRIM(to_char(min_value, '99999999D999999')), 'NULL')
		|| ', max_value := ' || COALESCE(TRIM(to_char(max_value, '99999999D999999')), 'NULL')	
		|| ', min_real_value := ' || COALESCE('''' || min_real_value || '''', 'NULL')
		|| ', max_real_value := ''' || COALESCE(max_real_value, 'NULL') || ''''
		|| ', colorbar := ''' || COALESCE(colorbar, 'NULL') || ''''		
		|| ', step := ' || COALESCE(TRIM(to_char(step, '99999999D999999')), 'NULL')
		|| ', step_range_from := ' || COALESCE(TRIM(to_char(step_range_from, '99999999D999999')), 'NULL')
		|| ', step_range_to := ' || COALESCE(TRIM(to_char(step_range_to, '99999999D999999')), 'NULL')
		|| ', unit := ' || COALESCE('''' || unit || '''', 'NULL')
		|| ' );'  as inserts	   
	FROM analysis.legend;

	

	RETURN QUERY SELECT 'SELECT analysis.update_insert_legend_step('
		|| ' legend_id := ' || legend_id
		|| ', from_step :=  ' || from_step
		|| ', to_step :=  ' || to_step		
		|| ', color_rgb := ' || COALESCE('''' || color_rgb || '''', 'NULL')
		|| ', color_label := ' || COALESCE('''' || color_label || '''', 'NULL')
		|| ', group_label := ' || COALESCE('''' || group_label || '''', 'NULL')
		|| ' );'  as inserts	   
	FROM analysis.legend_step;


	
	RETURN QUERY SELECT 'SELECT analysis.update_insert_product_legend('	
		|| ' productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', legend_id := ' || legend_id
		|| ', default_legend := ' || default_legend			
		|| ' );'  as inserts	   
	FROM analysis.product_legend;

	
																			
	RETURN QUERY SELECT 'SELECT analysis.update_insert_timeseries_drawproperties('
		|| ' productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')		
		|| ', title := ' || COALESCE('''' || title || '''', 'NULL')
		|| ', unit := ' || COALESCE('''' || unit || '''', 'NULL')		
		|| ', min := ' || COALESCE(TRIM(to_char(min, '99999999D999999')), 'NULL')
		|| ', max := ' || COALESCE(TRIM(to_char(max, '99999999D999999')), 'NULL')		
		|| ', oposite := ' || oposite				
		|| ', tsname_in_legend := ' || COALESCE('''' || tsname_in_legend || '''', 'NULL')
		|| ', charttype := ' || COALESCE('''' || charttype || '''', 'NULL')
		|| ', linestyle := ' || COALESCE('''' || linestyle || '''', 'NULL')
		|| ', linewidth := ' || COALESCE(TRIM(to_char(linewidth, '99999999')), 'NULL')
		|| ', color := ' || COALESCE('''' || color || '''', 'NULL')
		|| ', yaxes_id := ' || COALESCE('''' || yaxes_id || '''', 'NULL')
		|| ', title_color := ' || COALESCE('''' || title_color || '''', 'NULL')
		|| ' );'  as inserts	   
	FROM analysis.timeseries_drawproperties;	
	
	
	
	RETURN QUERY SELECT 'SELECT products.update_insert_spirits('
		|| '  productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', mapsetcode := ' || COALESCE('''' || mapsetcode || '''', 'NULL')
		|| ', prod_values := ' || COALESCE('''' || prod_values || '''', 'NULL')
		|| ', flags := ' || COALESCE('''' || flags || '''', 'NULL')
		|| ', data_ignore_value := ' || COALESCE(TRIM(to_char(data_ignore_value, '99999999')), 'NULL')
		|| ', days := ' || COALESCE(TRIM(to_char(days, '99999999')), 'NULL')
		|| ', start_date := ' || COALESCE(TRIM(to_char(start_date, '99999999')), 'NULL')
		|| ', end_date := ' || COALESCE(TRIM(to_char(end_date, '99999999')), 'NULL')	
		|| ', sensor_type := ' || COALESCE('''' || sensor_type || '''', 'NULL')
		|| ', comment := ' || COALESCE('''' || comment || '''', 'NULL')				
		|| ', sensor_filename_prefix := ' || COALESCE('''' || sensor_filename_prefix || '''', 'NULL')		
		|| ', frequency_filename_prefix := ' || COALESCE('''' || frequency_filename_prefix || '''', 'NULL')		
		|| ', product_anomaly_filename_prefix := ' || COALESCE('''' || product_anomaly_filename_prefix || '''', 'NULL')
		|| ', activated := ' || activated						
		|| ' );'  as inserts	   
	FROM products.spirits;	

	
END;
$_$;


ALTER FUNCTION products.export_jrc_data(full_copy boolean) OWNER TO estation;

--
-- TOC entry 219 (class 1255 OID 18427)
-- Name: set_thema(character varying); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION set_thema(themaid character varying) RETURNS boolean
    LANGUAGE plpgsql STRICT
    AS $_$
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
            WHERE (pp.process_id) in (SELECT process_id FROM products.processing WHERE defined_by = 'JRC'); 

                                    
	    IF themaid != 'JRC' THEN
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
	    END IF;
	    
            RETURN TRUE;    
    
    ELSE
        RETURN FALSE;
    END IF;
    
END;
$_$;


ALTER FUNCTION products.set_thema(themaid character varying) OWNER TO estation;

--
-- TOC entry 228 (class 1255 OID 18596)
-- Name: update_insert_data_type(character varying, character varying); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_data_type(data_type_id character varying, description character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_data_type_id ALIAS FOR  $1;
		_description  ALIAS FOR  $2;
	BEGIN	
		PERFORM * FROM products.data_type dt WHERE dt.data_type_id = TRIM(_data_type_id);
		IF FOUND THEN
			UPDATE products.data_type dt SET description = TRIM(_description) WHERE dt.data_type_id = TRIM(_data_type_id);
		ELSE
			INSERT INTO products.data_type (data_type_id, description) VALUES (TRIM(_data_type_id), TRIM(_description));
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_data_type(data_type_id character varying, description character varying) OWNER TO estation;

--
-- TOC entry 235 (class 1255 OID 18606)
-- Name: update_insert_datasource_description(character varying, character varying, character varying, character varying, character varying, character varying, character varying, integer, integer, character varying, character varying, integer, character varying, character varying, character varying, integer, character varying, boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_datasource_description(datasource_descr_id character varying, format_type character varying, file_extension character varying, delimiter character varying, date_format character varying, date_position character varying, product_identifier character varying, prod_id_position integer, prod_id_length integer, area_type character varying, area_position character varying, area_length integer, preproc_type character varying, product_release character varying, release_position character varying, release_length integer, native_mapset character varying, full_copy boolean DEFAULT false) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_datasource_descr_id	ALIAS FOR  $1;
		_format_type			ALIAS FOR  $2;
		_file_extension			ALIAS FOR  $3;
		_delimiter				ALIAS FOR  $4;
		_date_format			ALIAS FOR  $5;
		_date_position			ALIAS FOR  $6;
		_product_identifier		ALIAS FOR  $7;
		_prod_id_position		ALIAS FOR  $8;
		_prod_id_length			ALIAS FOR  $9;
		_area_type				ALIAS FOR  $10;
		_area_position			ALIAS FOR  $11;
		_area_length			ALIAS FOR  $12;
		_preproc_type			ALIAS FOR  $13;
		_product_release		ALIAS FOR  $14;
		_release_position		ALIAS FOR  $15;
		_release_length			ALIAS FOR  $16;
		_native_mapset			ALIAS FOR  $17;
		_full_copy				ALIAS FOR  $18;

	BEGIN	
		PERFORM * FROM products.datasource_description dd WHERE dd.datasource_descr_id = TRIM(_datasource_descr_id);
		  
		IF FOUND THEN
			IF _full_copy THEN
				UPDATE products.datasource_description dd 
				SET format_type = TRIM(_format_type),
					file_extension = TRIM(_file_extension),
					delimiter = TRIM(_delimiter),
					date_format = TRIM(_date_format),
					date_position = TRIM(_date_position),
					product_identifier = TRIM(_product_identifier),
					prod_id_position = _prod_id_position,
					prod_id_length = _prod_id_length,
					area_type = TRIM(_area_type),
					area_position = TRIM(_area_position),
					area_length = _area_length,
					preproc_type = TRIM(_preproc_type),
					product_release = TRIM(_product_release),
					release_position = TRIM(_release_position),
					release_length = _release_length,
					native_mapset = TRIM(_native_mapset)			
				WHERE dd.datasource_descr_id = TRIM(_datasource_descr_id);
			ELSE
				RAISE NOTICE 'Of existing JRC datasource descriptions  all columns can be updated by the User, do not overwrite!';
				/*
				UPDATE products.datasource_description dd 
				SET format_type = TRIM(_format_type),
					file_extension = TRIM(_file_extension),
					delimiter = TRIM(_delimiter),
					date_format = TRIM(_date_format),
					date_position = TRIM(_date_position),
					product_identifier = TRIM(_product_identifier),
					prod_id_position = _prod_id_position,
					prod_id_length = _prod_id_length,
					area_type = TRIM(_area_type),
					area_position = TRIM(_area_position),
					area_length = _area_length,
					preproc_type = TRIM(_preproc_type),
					product_release = TRIM(_product_release),
					release_position = TRIM(_release_position),
					release_length = _release_length,
					native_mapset = TRIM(_native_mapset)			
				WHERE dd.datasource_descr_id = TRIM(_datasource_descr_id);		
				*/
			END IF;
		ELSE
			INSERT INTO products.datasource_description (
				datasource_descr_id,
				format_type, 
				file_extension,
				delimiter,
				date_format, 
				date_position,
				product_identifier, 
				prod_id_position, 
				prod_id_length, 
				area_type, 
				area_position, 
				area_length, 
				preproc_type,
				product_release,
				release_position, 
				release_length, 
				native_mapset
			) 
			VALUES (
				TRIM(_datasource_descr_id),
				TRIM(_format_type), 
				TRIM(_file_extension),
				TRIM(_delimiter),
				TRIM(_date_format), 
				TRIM(_date_position),
				TRIM(_product_identifier), 
				_prod_id_position, 
				_prod_id_length, 
				TRIM(_area_type), 
				TRIM(_area_position), 
				_area_length, 
				TRIM(_preproc_type),
				TRIM(_product_release),
				TRIM(_release_position), 
				_release_length, 
				TRIM(_native_mapset)
			);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_datasource_description(datasource_descr_id character varying, format_type character varying, file_extension character varying, delimiter character varying, date_format character varying, date_position character varying, product_identifier character varying, prod_id_position integer, prod_id_length integer, area_type character varying, area_position character varying, area_length integer, preproc_type character varying, product_release character varying, release_position character varying, release_length integer, native_mapset character varying, full_copy boolean) OWNER TO estation;

--
-- TOC entry 215 (class 1255 OID 18595)
-- Name: update_insert_date_format(character varying, character varying); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_date_format(date_format character varying, definition character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_date_format ALIAS FOR  $1;
		_definition  ALIAS FOR  $2;
	BEGIN	
		PERFORM * FROM products.date_format df WHERE df.date_format = TRIM(_date_format);
		IF FOUND THEN
			UPDATE products.date_format df SET definition = TRIM(_definition) WHERE df.date_format = TRIM(_date_format);
		ELSE
			INSERT INTO products.date_format (date_format, definition) VALUES (TRIM(_date_format), TRIM(_definition));
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_date_format(date_format character varying, definition character varying) OWNER TO estation;

--
-- TOC entry 232 (class 1255 OID 18601)
-- Name: update_insert_eumetcast_source(character varying, character varying, character varying, boolean, character varying, character varying, character varying, character varying, character varying, date, date, date, double precision, double precision, double precision, double precision, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, character varying, date, character varying, character varying, boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_eumetcast_source(eumetcast_id character varying, filter_expression_jrc character varying, collection_name character varying, status boolean, internal_identifier character varying, collection_reference character varying, acronym character varying, description character varying, product_status character varying, date_creation date, date_revision date, date_publication date, west_bound_longitude double precision, east_bound_longitude double precision, north_bound_latitude double precision, south_bound_latitude double precision, provider_short_name character varying, collection_type character varying, keywords_distribution character varying, keywords_theme character varying, keywords_societal_benefit_area character varying, orbit_type character varying, satellite character varying, satellite_description character varying, instrument character varying, spatial_coverage character varying, thumbnails character varying, online_resources character varying, distribution character varying, channels character varying, data_access character varying, available_format character varying, version character varying, typical_file_name character varying, average_file_size character varying, frequency character varying, legal_constraints_access_constraint character varying, legal_use_constraint character varying, legal_constraints_data_policy character varying, entry_date date, reference_file character varying, datasource_descr_id character varying, full_copy boolean DEFAULT false) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_eumetcast_id 	  						ALIAS FOR  $1;
		_filter_expression_jrc 	  				ALIAS FOR  $2;
		_collection_name 	  					ALIAS FOR  $3;
		_status 	  							ALIAS FOR  $4;
		_internal_identifier 	  				ALIAS FOR  $5;
		_collection_reference 	  				ALIAS FOR  $6;
		_acronym 	  							ALIAS FOR  $7;
		_description 	  						ALIAS FOR  $8;
		_product_status 	  					ALIAS FOR  $9;
		_date_creation 	  						ALIAS FOR  $10;
		_date_revision 	  						ALIAS FOR  $11;
		_date_publication 	  					ALIAS FOR  $12;
		_west_bound_longitude 	  				ALIAS FOR  $13;
		_east_bound_longitude 	  				ALIAS FOR  $14;
		_north_bound_latitude 	  				ALIAS FOR  $15;
		_south_bound_latitude 	  				ALIAS FOR  $16;
		_provider_short_name 	  				ALIAS FOR  $17;
		_collection_type 	  					ALIAS FOR  $18;
		_keywords_distribution 	  				ALIAS FOR  $19;
		_keywords_theme 	  					ALIAS FOR  $20;
		_keywords_societal_benefit_area 		ALIAS FOR  $21;
		_orbit_type 	  						ALIAS FOR  $22;
		_satellite 	  							ALIAS FOR  $23;
		_satellite_description 	  				ALIAS FOR  $24;
		_instrument 	  						ALIAS FOR  $25;
		_spatial_coverage 	  					ALIAS FOR  $26;
		_thumbnails 	  						ALIAS FOR  $27;
		_online_resources 	  					ALIAS FOR  $28;
		_distribution 	  						ALIAS FOR  $29;
		_channels 	  							ALIAS FOR  $30;
		_data_access 	  						ALIAS FOR  $31;
		_available_format 	  					ALIAS FOR  $32;
		_version 	  							ALIAS FOR  $33;
		_typical_file_name 	  					ALIAS FOR  $34;
		_average_file_size 	  					ALIAS FOR  $35;
		_frequency 	  							ALIAS FOR  $36;
		_legal_constraints_access_constraint	ALIAS FOR  $37;
		_legal_use_constraint 	  				ALIAS FOR  $38;
		_legal_constraints_data_policy 	  		ALIAS FOR  $39;
		_entry_date 	  						ALIAS FOR  $40;
		_reference_file 	  					ALIAS FOR  $41;
		_datasource_descr_id 	  				ALIAS FOR  $42;	
		
		_full_copy   							ALIAS FOR  $43;
		
	BEGIN	
		PERFORM * FROM products.eumetcast_source i WHERE i.eumetcast_id = TRIM(_eumetcast_id);
		  
		IF FOUND THEN
			IF _full_copy THEN		
				UPDATE products.eumetcast_source i 
				SET eumetcast_id = TRIM(_eumetcast_id),
					filter_expression_jrc = _filter_expression_jrc,
					collection_name = TRIM(_collection_name),
					status = _status,
					internal_identifier = TRIM(_internal_identifier),
					collection_reference = TRIM(_collection_reference),
					acronym = TRIM(_acronym),
					description = TRIM(_description),
					product_status = TRIM(_product_status),
					date_creation = _date_creation,
					date_revision = _date_revision,
					date_publication = _date_publication,
					west_bound_longitude = _west_bound_longitude,
					east_bound_longitude = _east_bound_longitude,
					north_bound_latitude = _north_bound_latitude,
					south_bound_latitude = _south_bound_latitude,
					provider_short_name = TRIM(_provider_short_name),
					collection_type = TRIM(_collection_type),
					keywords_distribution = TRIM(_keywords_distribution),
					keywords_theme = TRIM(_keywords_theme),
					keywords_societal_benefit_area = TRIM(_keywords_societal_benefit_area),
					orbit_type = TRIM(_orbit_type),
					satellite = TRIM(_satellite),
					satellite_description = TRIM(_satellite_description),
					instrument = TRIM(_instrument),
					spatial_coverage = TRIM(_spatial_coverage),
					thumbnails = TRIM(_thumbnails),
					online_resources = TRIM(_online_resources),
					distribution = TRIM(_distribution),
					channels = TRIM(_channels),
					data_access = TRIM(_data_access),
					available_format = TRIM(_available_format),
					version = TRIM(_version),
					typical_file_name = TRIM(_typical_file_name),
					average_file_size = TRIM(_average_file_size),
					frequency = TRIM(_frequency),
					legal_constraints_access_constraint = TRIM(_legal_constraints_access_constraint),
					legal_use_constraint = TRIM(_legal_use_constraint),
					legal_constraints_data_policy = TRIM(_legal_constraints_data_policy),
					entry_date = _entry_date,
					reference_file = TRIM(_reference_file),
					datasource_descr_id = TRIM(_datasource_descr_id	)			
				WHERE i.eumetcast_id = TRIM(_eumetcast_id);
			ELSE
				UPDATE products.eumetcast_source i 
				SET eumetcast_id = TRIM(_eumetcast_id),
					-- filter_expression_jrc = _filter_expression_jrc,
					collection_name = TRIM(_collection_name),
					status = _status,
					internal_identifier = TRIM(_internal_identifier),
					collection_reference = TRIM(_collection_reference),
					acronym = TRIM(_acronym),
					description = TRIM(_description),
					product_status = TRIM(_product_status),
					date_creation = _date_creation,
					date_revision = _date_revision,
					date_publication = _date_publication,
					west_bound_longitude = _west_bound_longitude,
					east_bound_longitude = _east_bound_longitude,
					north_bound_latitude = _north_bound_latitude,
					south_bound_latitude = _south_bound_latitude,
					provider_short_name = TRIM(_provider_short_name),
					collection_type = TRIM(_collection_type),
					keywords_distribution = TRIM(_keywords_distribution),
					keywords_theme = TRIM(_keywords_theme),
					keywords_societal_benefit_area = TRIM(_keywords_societal_benefit_area),
					orbit_type = TRIM(_orbit_type),
					satellite = TRIM(_satellite),
					satellite_description = TRIM(_satellite_description),
					instrument = TRIM(_instrument),
					spatial_coverage = TRIM(_spatial_coverage),
					thumbnails = TRIM(_thumbnails),
					online_resources = TRIM(_online_resources),
					distribution = TRIM(_distribution),
					channels = TRIM(_channels),
					data_access = TRIM(_data_access),
					available_format = TRIM(_available_format),
					version = TRIM(_version),
					typical_file_name = TRIM(_typical_file_name),
					average_file_size = TRIM(_average_file_size),
					frequency = TRIM(_frequency),
					legal_constraints_access_constraint = TRIM(_legal_constraints_access_constraint),
					legal_use_constraint = TRIM(_legal_use_constraint),
					legal_constraints_data_policy = TRIM(_legal_constraints_data_policy),
					entry_date = _entry_date,
					reference_file = TRIM(_reference_file),
					datasource_descr_id = TRIM(_datasource_descr_id	)			
				WHERE i.eumetcast_id = TRIM(_eumetcast_id);			
			END IF;
		ELSE
			INSERT INTO products.eumetcast_source (
				eumetcast_id,
				filter_expression_jrc,
				collection_name,
				status,
				internal_identifier,
				collection_reference,
				acronym,
				description,
				product_status,
				date_creation,
				date_revision,
				date_publication,
				west_bound_longitude,
				east_bound_longitude,
				north_bound_latitude,
				south_bound_latitude,
				provider_short_name,
				collection_type,
				keywords_distribution,
				keywords_theme,
				keywords_societal_benefit_area,
				orbit_type,
				satellite,
				satellite_description,
				instrument,
				spatial_coverage,
				thumbnails,
				online_resources,
				distribution,
				channels,
				data_access,
				available_format,
				version,
				typical_file_name,
				average_file_size,
				frequency,
				legal_constraints_access_constraint,
				legal_use_constraint,
				legal_constraints_data_policy,
				entry_date,
				reference_file,
				datasource_descr_id
			) 
			VALUES (
				TRIM(_eumetcast_id),
				TRIM(_filter_expression_jrc),
				TRIM(_collection_name),
				_status,
				TRIM(_internal_identifier),
				TRIM(_collection_reference),
				TRIM(_acronym),
				TRIM(_description),
				TRIM(_product_status),
				_date_creation,
				_date_revision,
				_date_publication,
				_west_bound_longitude,
				_east_bound_longitude,
				_north_bound_latitude,
				_south_bound_latitude,
				TRIM(_provider_short_name),
				TRIM(_collection_type),
				TRIM(_keywords_distribution),
				TRIM(_keywords_theme),
				TRIM(_keywords_societal_benefit_area),
				TRIM(_orbit_type),
				TRIM(_satellite),
				TRIM(_satellite_description),
				TRIM(_instrument),
				TRIM(_spatial_coverage),
				TRIM(_thumbnails),
				TRIM(_online_resources),
				TRIM(_distribution),
				TRIM(_channels),
				TRIM(_data_access),
				TRIM(_available_format),
				TRIM(_version),
				TRIM(_typical_file_name),
				TRIM(_average_file_size),
				TRIM(_frequency),
				TRIM(_legal_constraints_access_constraint),
				TRIM(_legal_use_constraint),
				TRIM(_legal_constraints_data_policy),
				_entry_date,
				TRIM(_reference_file),
				TRIM(_datasource_descr_id)	
			);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_eumetcast_source(eumetcast_id character varying, filter_expression_jrc character varying, collection_name character varying, status boolean, internal_identifier character varying, collection_reference character varying, acronym character varying, description character varying, product_status character varying, date_creation date, date_revision date, date_publication date, west_bound_longitude double precision, east_bound_longitude double precision, north_bound_latitude double precision, south_bound_latitude double precision, provider_short_name character varying, collection_type character varying, keywords_distribution character varying, keywords_theme character varying, keywords_societal_benefit_area character varying, orbit_type character varying, satellite character varying, satellite_description character varying, instrument character varying, spatial_coverage character varying, thumbnails character varying, online_resources character varying, distribution character varying, channels character varying, data_access character varying, available_format character varying, version character varying, typical_file_name character varying, average_file_size character varying, frequency character varying, legal_constraints_access_constraint character varying, legal_use_constraint character varying, legal_constraints_data_policy character varying, entry_date date, reference_file character varying, datasource_descr_id character varying, full_copy boolean) OWNER TO estation;

--
-- TOC entry 214 (class 1255 OID 18594)
-- Name: update_insert_frequency(character varying, character varying, real, character varying, character varying); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_frequency(frequency_id character varying, time_unit character varying, frequency real, frequency_type character varying, description character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_frequency_id   ALIAS FOR  $1;
		_time_unit  	ALIAS FOR  $2;
		_frequency   	ALIAS FOR  $3;
		_frequency_type	ALIAS FOR  $4;
		_description	ALIAS FOR  $5;
	BEGIN	
		PERFORM * FROM products.frequency f WHERE f.frequency_id = TRIM(_frequency_id);
		IF FOUND THEN
			UPDATE products.frequency f 
			SET time_unit = TRIM(_time_unit), 
			    frequency = _frequency,
			    frequency_type = TRIM(_frequency_type),
			    description = TRIM(_description)
			WHERE f.frequency_id = TRIM(_frequency_id);
		ELSE
			INSERT INTO products.frequency (frequency_id, time_unit, frequency, frequency_type, description) 
			VALUES (TRIM(_frequency_id), TRIM(_time_unit), _frequency, TRIM(_frequency_type), TRIM(_description));
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_frequency(frequency_id character varying, time_unit character varying, frequency real, frequency_type character varying, description character varying) OWNER TO estation;

--
-- TOC entry 239 (class 1255 OID 18603)
-- Name: update_insert_ingestion(character varying, character varying, character varying, character varying, character varying, boolean, boolean, character varying, boolean, boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_ingestion(productcode character varying, subproductcode character varying, version character varying, mapsetcode character varying, defined_by character varying, activated boolean, wait_for_all_files boolean, input_to_process_re character varying, enabled boolean, full_copy boolean DEFAULT false) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_productcode 	  		ALIAS FOR  $1;
		_subproductcode  		ALIAS FOR  $2;
		_version 				ALIAS FOR  $3;
		_mapsetcode   			ALIAS FOR  $4;
		_defined_by 	  		ALIAS FOR  $5;
		_activated 	  			ALIAS FOR  $6;
		_wait_for_all_files  	ALIAS FOR  $7;
		_input_to_process_re 	ALIAS FOR  $8;
		_enabled  				ALIAS FOR  $9;
		_full_copy  			ALIAS FOR  $10;

	BEGIN	
		PERFORM * FROM products.ingestion i 
		WHERE i.productcode = TRIM(_productcode)
		  AND i.subproductcode = TRIM(_subproductcode)
		  AND i.version = TRIM(_version)
		  AND i.mapsetcode = TRIM(_mapsetcode);
		  -- AND i.defined_by = TRIM(_defined_by);
		  
		IF FOUND THEN		
			IF _full_copy THEN
				UPDATE products.ingestion i 
				SET defined_by = TRIM(_defined_by),
					activated = _activated,
					wait_for_all_files = _wait_for_all_files,				
					input_to_process_re = TRIM(_input_to_process_re),
					enabled = _enabled
				WHERE i.productcode = TRIM(_productcode)
				  AND i.subproductcode = TRIM(_subproductcode)
				  AND i.version = TRIM(_version)
				  AND i.mapsetcode = TRIM(_mapsetcode);
			ELSE
				UPDATE products.ingestion i 
				SET input_to_process_re = TRIM(_input_to_process_re)
					-- ,enabled = _enabled	
					-- ,defined_by = TRIM(_defined_by)
					-- ,activated = _activated
					-- ,wait_for_all_files = _wait_for_all_files
				WHERE i.productcode = TRIM(_productcode)
				  AND i.subproductcode = TRIM(_subproductcode)
				  AND i.version = TRIM(_version)
				  AND i.mapsetcode = TRIM(_mapsetcode);
				  -- AND i.defined_by = TRIM(_defined_by);			
			END IF;			  
		ELSE
			INSERT INTO products.ingestion (
			  productcode,
			  subproductcode,
			  version,
			  mapsetcode,
			  defined_by, 
			  activated,
			  wait_for_all_files, 
			  input_to_process_re,
			  enabled		
			) 
			VALUES (
				TRIM(_productcode), 
				TRIM(_subproductcode), 
				TRIM(_version), 
				TRIM(_mapsetcode), 
				TRIM(_defined_by),  
				_activated,
				_wait_for_all_files,
				TRIM(_input_to_process_re),
				_enabled
			);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_ingestion(productcode character varying, subproductcode character varying, version character varying, mapsetcode character varying, defined_by character varying, activated boolean, wait_for_all_files boolean, input_to_process_re character varying, enabled boolean, full_copy boolean) OWNER TO estation;

--
-- TOC entry 231 (class 1255 OID 18600)
-- Name: update_insert_internet_source(character varying, character varying, character varying, character varying, character varying, timestamp without time zone, character varying, character varying, character varying, character varying, character varying, character varying, boolean, integer, character varying, character varying, bigint, bigint, boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_internet_source(internet_id character varying, defined_by character varying, descriptive_name character varying, description character varying, modified_by character varying, update_datetime timestamp without time zone, url character varying, user_name character varying, password character varying, type character varying, include_files_expression character varying, files_filter_expression character varying, status boolean, pull_frequency integer, datasource_descr_id character varying, frequency_id character varying, start_date bigint, end_date bigint, full_copy boolean DEFAULT false) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
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
		  
		IF _start_date < 1 THEN _start_date = NULL; END IF;
		IF _end_date < 1 THEN _end_date = NULL; END IF;
		
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
$_$;


ALTER FUNCTION products.update_insert_internet_source(internet_id character varying, defined_by character varying, descriptive_name character varying, description character varying, modified_by character varying, update_datetime timestamp without time zone, url character varying, user_name character varying, password character varying, type character varying, include_files_expression character varying, files_filter_expression character varying, status boolean, pull_frequency integer, datasource_descr_id character varying, frequency_id character varying, start_date bigint, end_date bigint, full_copy boolean) OWNER TO estation;

--
-- TOC entry 225 (class 1255 OID 18599)
-- Name: update_insert_mapset(character varying, character varying, character varying, character varying, character varying, double precision, double precision, double precision, double precision, double precision, double precision, integer, integer, text, boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_mapset(mapsetcode character varying, defined_by character varying, descriptive_name character varying, description character varying, srs_wkt character varying, upper_left_long double precision, pixel_shift_long double precision, rotation_factor_long double precision, upper_left_lat double precision, pixel_shift_lat double precision, rotation_factor_lat double precision, pixel_size_x integer, pixel_size_y integer, footprint_image text, full_copy boolean DEFAULT false) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_mapsetcode 	  		ALIAS FOR  $1;
		_defined_by  			ALIAS FOR  $2;
		_descriptive_name 		ALIAS FOR  $3;
		_description   			ALIAS FOR  $4;
		_srs_wkt 	  			ALIAS FOR  $5;
		_upper_left_long 	  	ALIAS FOR  $6;
		_pixel_shift_long  		ALIAS FOR  $7;
		_rotation_factor_long 	ALIAS FOR  $8;
		_upper_left_lat  		ALIAS FOR  $9;
		_pixel_shift_lat 	  	ALIAS FOR  $10;
		_rotation_factor_lat 	ALIAS FOR  $11;
		_pixel_size_x  			ALIAS FOR  $12;
		_pixel_size_y 	  		ALIAS FOR  $13;
		_footprint_image   		ALIAS FOR  $14;
		_full_copy   			ALIAS FOR  $15;

	BEGIN	
		IF _footprint_image= 'NULL' THEN
			_footprint_image = NULL;
		END IF;
		
		PERFORM * FROM products.mapset m WHERE m.mapsetcode = TRIM(_mapsetcode);
		  
		IF FOUND THEN
			IF _full_copy THEN
				UPDATE products.mapset m 
				SET defined_by = TRIM(_defined_by),
					descriptive_name = TRIM(_descriptive_name),
					description = TRIM(_description),
					srs_wkt = TRIM(_srs_wkt),
					upper_left_long = _upper_left_long,
					pixel_shift_long = _pixel_shift_long,
					rotation_factor_long = _rotation_factor_long,
					upper_left_lat = _upper_left_lat,
					pixel_shift_lat = _pixel_shift_lat,
					rotation_factor_lat = _rotation_factor_lat,
					pixel_size_x = _pixel_size_x,
					pixel_size_y = _pixel_size_y,
					footprint_image = TRIM(_footprint_image)			
				WHERE m.mapsetcode = TRIM(_mapsetcode);
			ELSE
				RAISE NOTICE 'Of existing JRC mapsets all columns can be updated by the User, do not overwrite!';			
				/*
				UPDATE products.mapset m 
				SET defined_by = TRIM(_defined_by),
					descriptive_name = TRIM(_descriptive_name),
					description = TRIM(_description),
					srs_wkt = TRIM(_srs_wkt),
					upper_left_long = _upper_left_long,
					pixel_shift_long = _pixel_shift_long,
					rotation_factor_long = _rotation_factor_long,
					upper_left_lat = _upper_left_lat,
					pixel_shift_lat = _pixel_shift_lat,
					rotation_factor_lat = _rotation_factor_lat,
					pixel_size_x = _pixel_size_x,
					pixel_size_y = _pixel_size_y,
					footprint_image = TRIM(_footprint_image)			
				WHERE m.mapsetcode = TRIM(_mapsetcode);
				*/			
			END IF;
		ELSE
			INSERT INTO products.mapset (
				mapsetcode,
				defined_by,
				descriptive_name,
				description,
				srs_wkt,
				upper_left_long,
				pixel_shift_long,
				rotation_factor_long,
				upper_left_lat,
				pixel_shift_lat,
				rotation_factor_lat,
				pixel_size_x,
				pixel_size_y,
				footprint_image			
			) 
			VALUES (
				TRIM(_mapsetcode), 
				TRIM(_defined_by), 
				TRIM(_descriptive_name), 
				TRIM(_description), 
				TRIM(_srs_wkt),  
				_upper_left_long,
				_pixel_shift_long,
				_rotation_factor_long,
				_upper_left_lat,
				_pixel_shift_lat,
				_rotation_factor_lat,
				_pixel_size_x,
				_pixel_size_y,
				TRIM(_footprint_image)
			);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_mapset(mapsetcode character varying, defined_by character varying, descriptive_name character varying, description character varying, srs_wkt character varying, upper_left_long double precision, pixel_shift_long double precision, rotation_factor_long double precision, upper_left_lat double precision, pixel_shift_lat double precision, rotation_factor_lat double precision, pixel_size_x integer, pixel_size_y integer, footprint_image text, full_copy boolean) OWNER TO estation;

--
-- TOC entry 237 (class 1255 OID 18608)
-- Name: update_insert_process_product(integer, character varying, character varying, character varying, character varying, character varying, boolean, boolean, character varying, bigint, bigint, boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_process_product(process_id integer, productcode character varying, subproductcode character varying, version character varying, mapsetcode character varying, type character varying, activated boolean, final boolean, date_format character varying, start_date bigint, end_date bigint, full_copy boolean DEFAULT false) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_process_id		ALIAS FOR  $1;
		_productcode  	ALIAS FOR  $2;
		_subproductcode ALIAS FOR  $3;
		_version   		ALIAS FOR  $4;
		_mapsetcode 	ALIAS FOR  $5;
		_type 	  		ALIAS FOR  $6;
		_activated  	ALIAS FOR  $7;
		_final 			ALIAS FOR  $8;
		_date_format 	ALIAS FOR  $9;
		_start_date 	ALIAS FOR  $10;
		_end_date 		ALIAS FOR  $11;
		_full_copy 		ALIAS FOR  $12;

	BEGIN	
		PERFORM * FROM products.process_product pp 
		WHERE pp.process_id = _process_id
		  AND pp.productcode = TRIM(_productcode)
		  AND pp.subproductcode = TRIM(_subproductcode)
		  AND pp.version = TRIM(_version)
		  AND pp.mapsetcode = TRIM(_mapsetcode);
		  
		IF FOUND THEN		
			IF _full_copy THEN
				UPDATE products.process_product pp
				SET type = TRIM(_type),				
					final = _final,
					date_format = TRIM(_date_format),
					start_date = _start_date,
					end_date = _end_date
					,activated = _activated
				WHERE pp.process_id = _process_id
				  AND pp.productcode = TRIM(_productcode)
				  AND pp.subproductcode = TRIM(_subproductcode)
				  AND pp.version = TRIM(_version)
				  AND pp.mapsetcode = TRIM(_mapsetcode);
			ELSE
				UPDATE products.process_product pp
				SET type = TRIM(_type),				
					final = _final,
					date_format = TRIM(_date_format),
					start_date = _start_date,
					end_date = _end_date
					-- ,activated = _activated
				WHERE pp.process_id = _process_id
				  AND pp.productcode = TRIM(_productcode)
				  AND pp.subproductcode = TRIM(_subproductcode)
				  AND pp.version = TRIM(_version)
				  AND pp.mapsetcode = TRIM(_mapsetcode);

			END IF;
		ELSE
			INSERT INTO products.process_product (
			  process_id,
			  productcode,
			  subproductcode,
			  version,
			  mapsetcode,
			  type,
			  activated,
			  final,
			  date_format,
			  start_date,
			  end_date
			) 
			VALUES (
				_process_id,
				TRIM(_productcode), 
				TRIM(_subproductcode), 
				TRIM(_version), 
				TRIM(_mapsetcode), 
				TRIM(_type),
				_activated,
				_final,
				TRIM(_date_format),
				_start_date,
				_end_date				
			);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_process_product(process_id integer, productcode character varying, subproductcode character varying, version character varying, mapsetcode character varying, type character varying, activated boolean, final boolean, date_format character varying, start_date bigint, end_date bigint, full_copy boolean) OWNER TO estation;

--
-- TOC entry 236 (class 1255 OID 18607)
-- Name: update_insert_processing(integer, character varying, character varying, boolean, character varying, character varying, character varying, boolean, boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_processing(process_id integer, defined_by character varying, output_mapsetcode character varying, activated boolean, derivation_method character varying, algorithm character varying, priority character varying, enabled boolean, full_copy boolean DEFAULT false) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_process_id 	  	ALIAS FOR  $1;
		_defined_by  		ALIAS FOR  $2;
		_output_mapsetcode 	ALIAS FOR  $3;
		_activated   		ALIAS FOR  $4;
		_derivation_method 	ALIAS FOR  $5;
		_algorithm 	  		ALIAS FOR  $6;
		_priority  			ALIAS FOR  $7;
		_enabled 			ALIAS FOR  $8;
		_full_copy 			ALIAS FOR  $9;

	BEGIN	
		PERFORM * FROM products.processing p 
		WHERE p.process_id = _process_id;
		  -- AND p.defined_by = TRIM(_defined_by);
		  
		IF FOUND THEN
			IF _full_copy THEN
				UPDATE products.processing p
				SET output_mapsetcode = TRIM(_output_mapsetcode),
					derivation_method = TRIM(_derivation_method),
					algorithm = TRIM(_algorithm),
					priority = TRIM(_priority),
					enabled = _enabled
					,defined_by = _defined_by
					,activated = _activated
				WHERE p.process_id = _process_id;
			ELSE
				UPDATE products.processing p
				SET output_mapsetcode = TRIM(_output_mapsetcode),
					derivation_method = TRIM(_derivation_method),
					algorithm = TRIM(_algorithm),
					priority = TRIM(_priority)
					-- ,enabled = _enabled
					-- ,defined_by = _defined_by
					-- ,activated = _activated
				WHERE p.process_id = _process_id;
			END IF;
		ELSE
			INSERT INTO products.processing (
			  process_id,
			  defined_by,
			  output_mapsetcode,
			  activated,
			  derivation_method, 
			  algorithm,
			  priority,
			  enabled	
			) 
			VALUES (
			  _process_id,
			  TRIM(_defined_by),
			  TRIM(_output_mapsetcode),
			  _activated,
			  TRIM(_derivation_method), 
			  TRIM(_algorithm),
			  TRIM(_priority),
			  _enabled	
			);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_processing(process_id integer, defined_by character varying, output_mapsetcode character varying, activated boolean, derivation_method character varying, algorithm character varying, priority character varying, enabled boolean, full_copy boolean) OWNER TO estation;

--
-- TOC entry 238 (class 1255 OID 18609)
-- Name: update_insert_product(character varying, character varying, character varying, character varying, boolean, character varying, character varying, character varying, character varying, character varying, character varying, character varying, double precision, double precision, bigint, double precision, double precision, character varying, character varying, boolean, character varying, boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_product(productcode character varying, subproductcode character varying, version character varying, defined_by character varying, activated boolean, category_id character varying, product_type character varying, descriptive_name character varying, description character varying, provider character varying, frequency_id character varying, date_format character varying, scale_factor double precision, scale_offset double precision, nodata bigint, mask_min double precision, mask_max double precision, unit character varying, data_type_id character varying, masked boolean, timeseries_role character varying, full_copy boolean DEFAULT false) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_productcode 	  	ALIAS FOR  $1;
		_subproductcode  	ALIAS FOR  $2;
		_version 			ALIAS FOR  $3;
		_defined_by   		ALIAS FOR  $4;
		_activated 	  		ALIAS FOR  $5;
		_category_id 	  	ALIAS FOR  $6;
		_product_type  		ALIAS FOR  $7;
		_descriptive_name 	ALIAS FOR  $8;
		_description  		ALIAS FOR  $9;
		_provider  			ALIAS FOR  $10;
		_frequency_id		ALIAS FOR  $11;
		_date_format  		ALIAS FOR  $12;	
		_scale_factor  		ALIAS FOR  $13;		
		_scale_offset  		ALIAS FOR  $14;
		_nodata  			ALIAS FOR  $15;
		_mask_min  			ALIAS FOR  $16;
		_mask_max  			ALIAS FOR  $17;
		_unit  				ALIAS FOR  $18;
		_data_type_id  		ALIAS FOR  $19;
		_masked  			ALIAS FOR  $20;
		_timeseries_role  	ALIAS FOR  $21;
		_full_copy	  		ALIAS FOR  $22;
		
	BEGIN	
		PERFORM * FROM products.product p
		WHERE p.productcode = TRIM(_productcode)
		  AND p.subproductcode = TRIM(_subproductcode)
		  AND p.version = TRIM(_version);
		  -- AND p.defined_by = TRIM(_defined_by);
		  
		IF FOUND THEN		
			-- RAISE NOTICE 'START UPDATING Product';
			IF _full_copy THEN
				UPDATE products.product p 
				SET defined_by = TRIM(_defined_by),
					activated = _activated,
					category_id = TRIM(_category_id),
					product_type = TRIM(_product_type),
					descriptive_name = TRIM(_descriptive_name),
					description = TRIM(_description),
					provider = TRIM(_provider),				
					frequency_id = TRIM(_frequency_id),
					date_format = TRIM(_date_format),
					scale_factor = _scale_factor,
					scale_offset = _scale_offset,	
					nodata = _nodata,
					mask_min = _mask_min,
					mask_max = _mask_max,
					unit = TRIM(_unit),
					data_type_id = TRIM(_data_type_id),
					masked = _masked,
					timeseries_role = TRIM(_timeseries_role)			
				WHERE p.productcode = TRIM(_productcode)
				  AND p.subproductcode = TRIM(_subproductcode)
				  AND p.version = TRIM(_version);
			ELSE
				UPDATE products.product p 
				SET defined_by = TRIM(_defined_by),
					-- activated = _activated,
					category_id = TRIM(_category_id),
					product_type = TRIM(_product_type),
					descriptive_name = TRIM(_descriptive_name),
					description = TRIM(_description),
					provider = TRIM(_provider),				
					frequency_id = TRIM(_frequency_id),
					date_format = TRIM(_date_format),
					scale_factor = _scale_factor,
					scale_offset = _scale_offset,	
					nodata = _nodata,
					mask_min = _mask_min,
					mask_max = _mask_max,
					unit = TRIM(_unit),
					data_type_id = TRIM(_data_type_id),
					-- masked = _masked,
					timeseries_role = TRIM(_timeseries_role)				
				WHERE p.productcode = TRIM(_productcode)
				  AND p.subproductcode = TRIM(_subproductcode)
				  AND p.version = TRIM(_version);
			
			END IF;
			-- RAISE NOTICE 'Product updated';			  
		ELSE
			-- RAISE NOTICE 'START INSERTING Product';
			
			INSERT INTO products.product (
				productcode,
				subproductcode,
				version,
				defined_by, 
				activated,
				category_id,
				product_type, 
				descriptive_name, 
				description,
				provider,
				frequency_id, 
				date_format, 
				scale_factor,
				scale_offset,
				nodata,
				mask_min,
				mask_max,
				unit,
				data_type_id,
				masked,
				timeseries_role
			) 
			VALUES (
			  TRIM(_productcode),
			  TRIM(_subproductcode),
			  TRIM(_version),
			  TRIM(_defined_by), 
			  _activated,
			  TRIM(_category_id),
			  TRIM(_product_type), 
			  TRIM(_descriptive_name), 
			  TRIM(_description),
			  TRIM(_provider),
			  TRIM(_frequency_id), 
			  TRIM(_date_format), 
			  _scale_factor,
			  _scale_offset,
			  _nodata,
			  _mask_min,
			  _mask_max,
			  TRIM(_unit),
			  TRIM(_data_type_id),
			  _masked,
			  TRIM(_timeseries_role)
			);

			-- RAISE NOTICE 'Product inserted';
		END IF;	   
		RETURN TRUE;

	EXCEPTION
		WHEN numeric_value_out_of_range THEN
			RAISE NOTICE 'ERROR: numeric_value_out_of_range.';
			RETURN FALSE;

		WHEN OTHERS THEN  
			RAISE NOTICE 'ERROR...';
			RAISE NOTICE '% %', SQLERRM, SQLSTATE;
			RETURN FALSE;		
	END;
$_$;


ALTER FUNCTION products.update_insert_product(productcode character varying, subproductcode character varying, version character varying, defined_by character varying, activated boolean, category_id character varying, product_type character varying, descriptive_name character varying, description character varying, provider character varying, frequency_id character varying, date_format character varying, scale_factor double precision, scale_offset double precision, nodata bigint, mask_min double precision, mask_max double precision, unit character varying, data_type_id character varying, masked boolean, timeseries_role character varying, full_copy boolean) OWNER TO estation;

--
-- TOC entry 234 (class 1255 OID 18605)
-- Name: update_insert_product_acquisition_data_source(character varying, character varying, character varying, character varying, character varying, character varying, boolean, boolean, boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_product_acquisition_data_source(productcode character varying, subproductcode character varying, version character varying, data_source_id character varying, defined_by character varying, type character varying, activated boolean, store_original_data boolean, full_copy boolean DEFAULT false) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_productcode 	  		ALIAS FOR  $1;
		_subproductcode  		ALIAS FOR  $2;
		_version 				ALIAS FOR  $3;
		_data_source_id   		ALIAS FOR  $4;
		_defined_by 	  		ALIAS FOR  $5;
		_type 	  				ALIAS FOR  $6;
		_activated  			ALIAS FOR  $7;
		_store_original_data 	ALIAS FOR  $8;
		_full_copy 				ALIAS FOR  $9;

	BEGIN	
		PERFORM * FROM products.product_acquisition_data_source pads 
		WHERE pads.productcode = TRIM(_productcode)
		  AND pads.subproductcode = TRIM(_subproductcode)
		  AND pads.version = TRIM(_version)
		  AND pads.data_source_id = TRIM(_data_source_id);
		  -- AND pads.defined_by = TRIM(_defined_by);
		  
		IF FOUND THEN	
			IF _full_copy THEN
				UPDATE products.product_acquisition_data_source pads
				SET type = TRIM(_type)
					,defined_by = _defined_by
					,activated = _activated
					,store_original_data = _store_original_data
				WHERE pads.productcode = TRIM(_productcode)
				  AND pads.subproductcode = TRIM(_subproductcode)
				  AND pads.version = TRIM(_version)
				  AND pads.data_source_id = TRIM(_data_source_id);			
			ELSE
				RAISE NOTICE 'Of existing JRC PADS all columns can be updated by the User, do not overwrite!';
				/*
				UPDATE products.product_acquisition_data_source pads
				SET type = TRIM(_type)
					-- ,defined_by = _defined_by
					-- ,activated = _activated
					-- ,store_original_data = _store_original_data
				WHERE pads.productcode = TRIM(_productcode)
				  AND pads.subproductcode = TRIM(_subproductcode)
				  AND pads.version = TRIM(_version)
				  AND pads.data_source_id = TRIM(_data_source_id);
				*/  
			END IF;
		ELSE
			INSERT INTO products.product_acquisition_data_source (
			  productcode,
			  subproductcode,
			  version,
			  data_source_id,
			  defined_by, 
			  type,
			  activated,
			  store_original_data	
			) 
			VALUES (
				TRIM(_productcode), 
				TRIM(_subproductcode), 
				TRIM(_version), 
				TRIM(_data_source_id), 
				TRIM(_defined_by),  
				TRIM(_type),
				_activated,
				_store_original_data
			);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_product_acquisition_data_source(productcode character varying, subproductcode character varying, version character varying, data_source_id character varying, defined_by character varying, type character varying, activated boolean, store_original_data boolean, full_copy boolean) OWNER TO estation;

--
-- TOC entry 213 (class 1255 OID 18593)
-- Name: update_insert_product_category(character varying, character varying, integer); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_product_category(category_id character varying, descriptive_name character varying, order_index integer) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_category_id   	  ALIAS FOR  $1;
		_descriptive_name  ALIAS FOR  $2;
		_order_index   	  ALIAS FOR  $3;
	BEGIN	
		PERFORM * FROM products.product_category pc WHERE pc.category_id = TRIM(_category_id);
		IF FOUND THEN
			UPDATE products.product_category pc 
			SET descriptive_name = TRIM(_descriptive_name), 
			    order_index = _order_index 
			WHERE pc.category_id = TRIM(_category_id);
		ELSE
			INSERT INTO products.product_category (category_id, descriptive_name, order_index) 
			VALUES (TRIM(_category_id), TRIM(_descriptive_name), _order_index);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_product_category(category_id character varying, descriptive_name character varying, order_index integer) OWNER TO estation;

--
-- TOC entry 224 (class 1255 OID 18827)
-- Name: update_insert_spirits(character varying, character varying, character varying, character varying, character varying, character varying, integer, integer, integer, integer, character varying, character varying, character varying, character varying, character varying, boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_spirits(productcode character varying, subproductcode character varying, version character varying, mapsetcode character varying, prod_values character varying, flags character varying, data_ignore_value integer, days integer, start_date integer, end_date integer, sensor_type character varying, comment character varying, sensor_filename_prefix character varying, frequency_filename_prefix character varying, product_anomaly_filename_prefix character varying, activated boolean) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_productcode					ALIAS FOR  $1;
		_subproductcode					ALIAS FOR  $2;
		_version						ALIAS FOR  $3;
		_mapsetcode						ALIAS FOR  $4;
		_prod_values					ALIAS FOR  $5;
		_flags							ALIAS FOR  $6;
		_data_ignore_value				ALIAS FOR  $7;
		_days							ALIAS FOR  $8;
		_start_date						ALIAS FOR  $9;
		_end_date						ALIAS FOR  $10;
		_sensor_type					ALIAS FOR  $11;
		_comment						ALIAS FOR  $12;
		_sensor_filename_prefix			ALIAS FOR  $13;
		_frequency_filename_prefix		ALIAS FOR  $14;
		_product_anomaly_filename_prefix	ALIAS FOR  $15;
		_activated						ALIAS FOR  $16;
  
	BEGIN	
		PERFORM * FROM products.spirits s 
		WHERE s.productcode = TRIM(_productcode)
		  AND s.subproductcode = TRIM(_subproductcode)		
		  AND s.version = TRIM(_version);
		  
		IF FOUND THEN
			UPDATE products.spirits s 
			SET mapsetcode = TRIM(_mapsetcode),
				prod_values = TRIM(_prod_values),
				flags = TRIM(_flags),
				data_ignore_value = _data_ignore_value,
				days = _days,
				start_date = _start_date,
				end_date = _end_date,
				sensor_type = TRIM(_sensor_type),
				comment = TRIM(_comment),
				sensor_filename_prefix = TRIM(_sensor_filename_prefix),
				frequency_filename_prefix = TRIM(_frequency_filename_prefix),
				product_anomaly_filename_prefix = TRIM(_product_anomaly_filename_prefix),				
				activated = _activated				
			WHERE s.productcode = TRIM(_productcode)
			  AND s.subproductcode = TRIM(_subproductcode)			  
			  AND s.version = TRIM(_version);
		ELSE
			INSERT INTO products.spirits (
										productcode,
										subproductcode,
										version,
										mapsetcode,
										prod_values,
										flags,
										data_ignore_value,
										days,
										start_date,
										end_date,
										sensor_type,
										comment,
										sensor_filename_prefix,
										frequency_filename_prefix,
										product_anomaly_filename_prefix,
										activated) 
			VALUES (TRIM(_productcode), TRIM(_subproductcode), TRIM(_version), TRIM(_mapsetcode), TRIM(_prod_values), TRIM(_flags), _data_ignore_value, _days, _start_date, _end_date, TRIM(_sensor_type), 
					TRIM(_comment), TRIM(_sensor_filename_prefix), TRIM(_frequency_filename_prefix), TRIM(_product_anomaly_filename_prefix), _activated);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_spirits(productcode character varying, subproductcode character varying, version character varying, mapsetcode character varying, prod_values character varying, flags character varying, data_ignore_value integer, days integer, start_date integer, end_date integer, sensor_type character varying, comment character varying, sensor_filename_prefix character varying, frequency_filename_prefix character varying, product_anomaly_filename_prefix character varying, activated boolean) OWNER TO estation;

--
-- TOC entry 233 (class 1255 OID 18604)
-- Name: update_insert_sub_datasource_description(character varying, character varying, character varying, character varying, double precision, double precision, double precision, character varying, double precision, double precision, character varying, character varying, boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_sub_datasource_description(productcode character varying, subproductcode character varying, version character varying, datasource_descr_id character varying, scale_factor double precision, scale_offset double precision, no_data double precision, data_type_id character varying, mask_min double precision, mask_max double precision, re_process character varying, re_extract character varying, full_copy boolean DEFAULT false) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_productcode 	  		ALIAS FOR  $1;
		_subproductcode  		ALIAS FOR  $2;
		_version 				ALIAS FOR  $3;
		_datasource_descr_id   	ALIAS FOR  $4;
		_scale_factor 	  		ALIAS FOR  $5;
		_scale_offset 	  		ALIAS FOR  $6;
		_no_data  				ALIAS FOR  $7;
		_data_type_id 			ALIAS FOR  $8;
		_mask_min  				ALIAS FOR  $9;
		_mask_max  				ALIAS FOR  $10;
		_re_process				ALIAS FOR  $11;
		_re_extract  			ALIAS FOR  $12;	
		_full_copy  			ALIAS FOR  $13;
	BEGIN	
		PERFORM * FROM products.sub_datasource_description sdd
		WHERE sdd.productcode = TRIM(_productcode)
		  AND sdd.subproductcode = TRIM(_subproductcode)
		  AND sdd.version = TRIM(_version)
		  AND sdd.datasource_descr_id = TRIM(_datasource_descr_id);
		  -- AND join with product and check if defined_by == 'JRC'
		  -- AND join with datasource_description and join with internet_source and check if defined_by == 'JRC'
		  
		IF FOUND THEN		
			IF _full_copy THEN
				UPDATE products.sub_datasource_description sdd 
				SET scale_factor = _scale_factor,
					scale_offset = _scale_offset,	
					no_data = _no_data,
					data_type_id = TRIM(_data_type_id),
					mask_min = _mask_min,
					mask_max = _mask_max,
					re_process = TRIM(_re_process),
					re_extract = TRIM(_re_extract)
				WHERE sdd.productcode = TRIM(_productcode)
				  AND sdd.subproductcode = TRIM(_subproductcode)
				  AND sdd.version = TRIM(_version)
				  AND sdd.datasource_descr_id = TRIM(_datasource_descr_id);
			ELSE
				RAISE NOTICE 'Of existing JRC sub_datasource_descriptions all columns can be updated by the User, do not overwrite!';			
				/*
				UPDATE products.sub_datasource_description sdd 
				SET -- scale_factor = _scale_factor,
					-- scale_offset = _scale_offset,	
					-- no_data = _no_data,
					-- data_type_id = TRIM(_data_type_id),
					-- mask_min = _mask_min,
					-- mask_max = _mask_max,
					re_process = TRIM(_re_process),
					re_extract = TRIM(_re_extract)
				WHERE sdd.productcode = TRIM(_productcode)
				  AND sdd.subproductcode = TRIM(_subproductcode)
				  AND sdd.version = TRIM(_version)
				  AND sdd.datasource_descr_id = TRIM(_datasource_descr_id);
				*/
			END IF;
		ELSE
			INSERT INTO products.sub_datasource_description (
			  productcode,
			  subproductcode,
			  version,
			  datasource_descr_id,
			  scale_factor, 
			  scale_offset,
			  no_data, 
			  data_type_id,			  
			  mask_min,
			  mask_max,
			  re_process,
			  re_extract
			) 
			VALUES (
				TRIM(_productcode), 
				TRIM(_subproductcode), 
				TRIM(_version), 
				TRIM(_datasource_descr_id), 
				_scale_factor, 
				_scale_offset,
				_no_data, 
				TRIM(_data_type_id), 
			    _mask_min,
			    _mask_max,		
				TRIM(_re_process), 
				TRIM(_re_extract)
			);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_sub_datasource_description(productcode character varying, subproductcode character varying, version character varying, datasource_descr_id character varying, scale_factor double precision, scale_offset double precision, no_data double precision, data_type_id character varying, mask_min double precision, mask_max double precision, re_process character varying, re_extract character varying, full_copy boolean) OWNER TO estation;

--
-- TOC entry 229 (class 1255 OID 18597)
-- Name: update_insert_thema(character varying, character varying); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_thema(thema_id character varying, description character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_thema_id 	  ALIAS FOR  $1;
		_description  ALIAS FOR  $2;
	BEGIN	
		PERFORM * FROM products.thema t WHERE t.thema_id = TRIM(_thema_id);
		IF FOUND THEN
			UPDATE products.thema t SET description = TRIM(_description) WHERE t.thema_id = TRIM(_thema_id);
		ELSE
			INSERT INTO products.thema (thema_id, description) VALUES (TRIM(_thema_id), TRIM(_description));
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_thema(thema_id character varying, description character varying) OWNER TO estation;

--
-- TOC entry 230 (class 1255 OID 18598)
-- Name: update_insert_thema_product(character varying, character varying, character varying, character varying, boolean); Type: FUNCTION; Schema: products; Owner: estation
--

CREATE FUNCTION update_insert_thema_product(thema_id character varying, productcode character varying, version character varying, mapsetcode character varying, activated boolean) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
	DECLARE
		_thema_id 	  ALIAS FOR  $1;
		_productcode  ALIAS FOR  $2;
		_version 	  ALIAS FOR  $3;
		_mapsetcode   ALIAS FOR  $4;
		_activated 	  ALIAS FOR  $5;
	BEGIN	
		PERFORM * FROM products.thema_product tp 
		WHERE tp.thema_id = TRIM(_thema_id) 
		  AND tp.productcode = TRIM(_productcode)
		  AND tp.version = TRIM(_version)
		  AND tp.mapsetcode = TRIM(_mapsetcode);
		  
		IF FOUND THEN
			UPDATE products.thema_product tp 
			SET activated = _activated
			WHERE tp.thema_id = TRIM(_thema_id) 
			  AND tp.productcode = TRIM(_productcode)
			  AND tp.version = TRIM(_version)
			  AND tp.mapsetcode = TRIM(_mapsetcode);
		ELSE
			INSERT INTO products.thema_product (thema_id, productcode, version, mapsetcode, activated) 
			VALUES (TRIM(_thema_id), TRIM(_productcode), TRIM(_version), TRIM(_mapsetcode), _activated);
		END IF;	   
		RETURN TRUE;
	END;
$_$;


ALTER FUNCTION products.update_insert_thema_product(thema_id character varying, productcode character varying, version character varying, mapsetcode character varying, activated boolean) OWNER TO estation;

SET search_path = analysis, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 172 (class 1259 OID 17268)
-- Name: i18n; Type: TABLE; Schema: analysis; Owner: estation; Tablespace: 
--

CREATE TABLE i18n (
    label character varying(255) NOT NULL,
    eng text NOT NULL,
    fra text,
    por text,
    lang1 text,
    lang2 text,
    lang3 text
);


ALTER TABLE analysis.i18n OWNER TO estation;

--
-- TOC entry 173 (class 1259 OID 17274)
-- Name: languages; Type: TABLE; Schema: analysis; Owner: estation; Tablespace: 
--

CREATE TABLE languages (
    langcode character varying(5) NOT NULL,
    langdescription character varying(80),
    active boolean
);


ALTER TABLE analysis.languages OWNER TO estation;

--
-- TOC entry 174 (class 1259 OID 17289)
-- Name: legend; Type: TABLE; Schema: analysis; Owner: estation; Tablespace: 
--

CREATE TABLE legend (
    legend_id integer NOT NULL,
    legend_name character varying(100) NOT NULL,
    step_type character varying(80) NOT NULL,
    min_value double precision,
    max_value double precision,
    min_real_value character varying(20),
    max_real_value text,
    colorbar text,
    step double precision,
    step_range_from double precision,
    step_range_to double precision,
    unit character varying(30)
);


ALTER TABLE analysis.legend OWNER TO estation;

--
-- TOC entry 175 (class 1259 OID 17295)
-- Name: legend_legend_id_seq; Type: SEQUENCE; Schema: analysis; Owner: estation
--

CREATE SEQUENCE legend_legend_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 100000000
    CACHE 1;


ALTER TABLE analysis.legend_legend_id_seq OWNER TO estation;

--
-- TOC entry 2225 (class 0 OID 0)
-- Dependencies: 175
-- Name: legend_legend_id_seq; Type: SEQUENCE OWNED BY; Schema: analysis; Owner: estation
--

ALTER SEQUENCE legend_legend_id_seq OWNED BY legend.legend_id;


--
-- TOC entry 176 (class 1259 OID 17297)
-- Name: legend_step; Type: TABLE; Schema: analysis; Owner: estation; Tablespace: 
--

CREATE TABLE legend_step (
    legend_id integer NOT NULL,
    from_step double precision NOT NULL,
    to_step double precision NOT NULL,
    color_rgb character varying(11) NOT NULL,
    color_label character varying(255),
    group_label character varying(255)
);


ALTER TABLE analysis.legend_step OWNER TO estation;

--
-- TOC entry 2226 (class 0 OID 0)
-- Dependencies: 176
-- Name: COLUMN legend_step.color_rgb; Type: COMMENT; Schema: analysis; Owner: estation
--

COMMENT ON COLUMN legend_step.color_rgb IS 'a string of 3 bytes, in decimal format, comma separated, eg. 128, 36, 64';


--
-- TOC entry 177 (class 1259 OID 17303)
-- Name: product_legend; Type: TABLE; Schema: analysis; Owner: estation; Tablespace: 
--

CREATE TABLE product_legend (
    productcode character varying NOT NULL,
    subproductcode character varying NOT NULL,
    version character varying NOT NULL,
    legend_id bigint NOT NULL,
    default_legend boolean DEFAULT false
);


ALTER TABLE analysis.product_legend OWNER TO estation;

SET default_with_oids = false;

--
-- TOC entry 192 (class 1259 OID 18354)
-- Name: timeseries_drawproperties; Type: TABLE; Schema: analysis; Owner: estation; Tablespace: 
--

CREATE TABLE timeseries_drawproperties (
    productcode character varying NOT NULL,
    subproductcode character varying NOT NULL,
    version character varying NOT NULL,
    title character varying,
    unit character varying,
    min double precision,
    max double precision,
    oposite boolean DEFAULT false NOT NULL,
    tsname_in_legend character varying,
    charttype character varying,
    linestyle character varying,
    linewidth integer,
    color character varying,
    yaxes_id character varying,
    title_color character varying
);


ALTER TABLE analysis.timeseries_drawproperties OWNER TO estation;

SET search_path = products, pg_catalog;

SET default_with_oids = false;

--
-- TOC entry 178 (class 1259 OID 17310)
-- Name: data_type; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE data_type (
    data_type_id character varying NOT NULL,
    description character varying NOT NULL
);


ALTER TABLE products.data_type OWNER TO estation;

--
-- TOC entry 179 (class 1259 OID 17316)
-- Name: datasource_description; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE datasource_description (
    datasource_descr_id character varying NOT NULL,
    format_type character varying,
    file_extension character varying,
    delimiter character varying,
    date_format character varying,
    date_position character varying,
    product_identifier character varying,
    prod_id_position integer,
    prod_id_length integer,
    area_type character varying,
    area_position character varying,
    area_length integer,
    preproc_type character varying,
    product_release character varying,
    release_position character varying,
    release_length integer,
    native_mapset character varying DEFAULT 'default'::character varying,
    CONSTRAINT check_mapset_chk CHECK (check_mapset(native_mapset))
);


ALTER TABLE products.datasource_description OWNER TO estation;

--
-- TOC entry 2227 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN datasource_description.format_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.format_type IS 'Values:
- DELIMITED
- FIXED';


--
-- TOC entry 2228 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN datasource_description.date_format; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.date_format IS 'A string, case insensitive, in YYYYMMDD, YYYYMMDDHHMM,YYYY,MMDD,HHMM. HHMM (may be used for MSG 15 minutes synthesis). This list may change with the project life. It is maintained by JRC';


--
-- TOC entry 2229 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN datasource_description.product_identifier; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.product_identifier IS 'Comma-separated list of strings present in the filename that form the Product Identifier';


--
-- TOC entry 2230 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN datasource_description.prod_id_position; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.prod_id_position IS 'In case of:
FIXED - integer value of the start position of the Product Identifier

DELIMITED - comma-separated integers indicating the delimiter positions of the Product Identifier to concatinate.';


--
-- TOC entry 2231 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN datasource_description.prod_id_length; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.prod_id_length IS 'In case of FIXED format this field indicates the string length to take starting from the prod_id_position.';


--
-- TOC entry 2232 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN datasource_description.area_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.area_type IS 'Values:
- REGION
- SEGMENT
- TILE
- GLOBAL';


--
-- TOC entry 2233 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN datasource_description.area_position; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.area_position IS 'In case of:
FIXED - integer value of the start position of the Area

DELIMITED - comma-separated integers indicating the delimiter positions of the Area to concatinate.';


--
-- TOC entry 2234 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN datasource_description.area_length; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.area_length IS 'In case of FIXED format this field indicates the string length to take starting from the area_position.';


--
-- TOC entry 2235 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN datasource_description.product_release; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.product_release IS 'String indicating the Product Release present in the filename.';


--
-- TOC entry 2236 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN datasource_description.release_position; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.release_position IS 'In case of:
FIXED - integer value of the start position of the Release

DELIMITED - comma-separated integers indicating the delimiter positions of the Release to concatinate.';


--
-- TOC entry 2237 (class 0 OID 0)
-- Dependencies: 179
-- Name: COLUMN datasource_description.release_length; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.release_length IS 'In case of FIXED format this field indicates the string length to take starting from the release_position.';


--
-- TOC entry 180 (class 1259 OID 17323)
-- Name: date_format; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE date_format (
    date_format character varying NOT NULL,
    definition character varying
);


ALTER TABLE products.date_format OWNER TO estation;

--
-- TOC entry 2238 (class 0 OID 0)
-- Dependencies: 180
-- Name: COLUMN date_format.date_format; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN date_format.date_format IS 'A string, case insensitive, in YYYYMMDD, YYYYMMDDHHMM,YYYY,MMDD,HHMM. HHMM (may be used for MSG 15 minutes synthesis). This list may change with the project life. It is maintained by JRC';


--
-- TOC entry 2239 (class 0 OID 0)
-- Dependencies: 180
-- Name: COLUMN date_format.definition; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN date_format.definition IS 'A text defining the date type.';


--
-- TOC entry 181 (class 1259 OID 17329)
-- Name: eumetcast_source; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE eumetcast_source (
    eumetcast_id character varying NOT NULL,
    filter_expression_jrc character varying,
    collection_name character varying,
    status boolean DEFAULT false NOT NULL,
    internal_identifier character varying,
    collection_reference character varying,
    acronym character varying,
    description character varying,
    product_status character varying,
    date_creation date,
    date_revision date,
    date_publication date,
    west_bound_longitude double precision,
    east_bound_longitude double precision,
    north_bound_latitude double precision,
    south_bound_latitude double precision,
    provider_short_name character varying,
    collection_type character varying,
    keywords_distribution character varying,
    keywords_theme character varying,
    keywords_societal_benefit_area character varying,
    orbit_type character varying,
    satellite character varying,
    satellite_description character varying,
    instrument character varying,
    spatial_coverage character varying,
    thumbnails character varying,
    online_resources character varying,
    distribution character varying,
    channels character varying,
    data_access character varying,
    available_format character varying,
    version character varying,
    typical_file_name character varying,
    average_file_size character varying,
    frequency character varying,
    legal_constraints_access_constraint character varying,
    legal_use_constraint character varying,
    legal_constraints_data_policy character varying,
    entry_date date,
    reference_file character varying,
    datasource_descr_id character varying
);


ALTER TABLE products.eumetcast_source OWNER TO estation;

--
-- TOC entry 2240 (class 0 OID 0)
-- Dependencies: 181
-- Name: COLUMN eumetcast_source.status; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN eumetcast_source.status IS 'On/Off
Active/Non active';


--
-- TOC entry 182 (class 1259 OID 17336)
-- Name: frequency; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE frequency (
    frequency_id character varying NOT NULL,
    time_unit character varying(10) NOT NULL,
    frequency real NOT NULL,
    frequency_type character varying(1) DEFAULT 'E'::character varying NOT NULL,
    description character varying
);


ALTER TABLE products.frequency OWNER TO estation;

--
-- TOC entry 2241 (class 0 OID 0)
-- Dependencies: 182
-- Name: COLUMN frequency.frequency_id; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN frequency.frequency_id IS 'A string, case insensitive, indicating the time-span that the product represents (is distributed): 
undefined
INSTANTANEOUS
DEKAD!=10-days
8days
1month
1week
24hours (for MSG products)
1year';


--
-- TOC entry 2242 (class 0 OID 0)
-- Dependencies: 182
-- Name: COLUMN frequency.frequency_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN frequency.frequency_type IS 'Binary flag indicating:
- every Nth ''Time Unit'' (every 15th  = ogni 15 min) 
- N per ''Time Unit'' (4 per hour) 

Values:
E = every
P = per';


--
-- TOC entry 183 (class 1259 OID 17343)
-- Name: ingestion; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE ingestion (
    productcode character varying NOT NULL,
    subproductcode character varying NOT NULL,
    version character varying NOT NULL,
    mapsetcode character varying NOT NULL,
    defined_by character varying NOT NULL,
    activated boolean DEFAULT false NOT NULL,
    wait_for_all_files boolean NOT NULL,
    input_to_process_re character varying,
    enabled boolean DEFAULT false NOT NULL
);


ALTER TABLE products.ingestion OWNER TO estation;

--
-- TOC entry 2243 (class 0 OID 0)
-- Dependencies: 183
-- Name: TABLE ingestion; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON TABLE ingestion IS 'Define which products/versions have to be ingested, and for which mapsets.';


--
-- TOC entry 2244 (class 0 OID 0)
-- Dependencies: 183
-- Name: COLUMN ingestion.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN ingestion.defined_by IS 'values: JRC or USER';


--
-- TOC entry 2245 (class 0 OID 0)
-- Dependencies: 183
-- Name: COLUMN ingestion.wait_for_all_files; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN ingestion.wait_for_all_files IS 'When incomming files need to be mosaicked 
this boolean when TRUE, will indicate to ingestion to wait for all the needed files to come in before mosaicking. When FALSE mosaicking will be done even if not all files arrived.';


--
-- TOC entry 184 (class 1259 OID 17350)
-- Name: internet_source; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE internet_source (
    internet_id character varying NOT NULL,
    defined_by character varying DEFAULT 'JRC'::character varying NOT NULL,
    descriptive_name character varying,
    description character varying,
    modified_by character varying,
    update_datetime timestamp without time zone DEFAULT now(),
    url character varying,
    user_name character varying,
    password character varying,
    type character varying,
    include_files_expression character varying,
    files_filter_expression character varying,
    status boolean DEFAULT false NOT NULL,
    pull_frequency integer,
    datasource_descr_id character varying,
    frequency_id character varying,
    start_date bigint,
    end_date bigint
);


ALTER TABLE products.internet_source OWNER TO estation;

--
-- TOC entry 2246 (class 0 OID 0)
-- Dependencies: 184
-- Name: COLUMN internet_source.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN internet_source.defined_by IS 'values: JRC or USER';


--
-- TOC entry 2247 (class 0 OID 0)
-- Dependencies: 184
-- Name: COLUMN internet_source.modified_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN internet_source.modified_by IS 'Username as value';


--
-- TOC entry 2248 (class 0 OID 0)
-- Dependencies: 184
-- Name: COLUMN internet_source.status; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN internet_source.status IS 'On/Off
Active/Non active';


--
-- TOC entry 2249 (class 0 OID 0)
-- Dependencies: 184
-- Name: COLUMN internet_source.pull_frequency; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN internet_source.pull_frequency IS 'In seconds';


--
-- TOC entry 185 (class 1259 OID 17358)
-- Name: mapset; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE mapset (
    mapsetcode character varying NOT NULL,
    defined_by character varying NOT NULL,
    descriptive_name character varying,
    description character varying,
    srs_wkt character varying,
    upper_left_long double precision,
    pixel_shift_long double precision,
    rotation_factor_long double precision,
    upper_left_lat double precision,
    pixel_shift_lat double precision,
    rotation_factor_lat double precision,
    pixel_size_x integer,
    pixel_size_y integer,
    footprint_image text
);


ALTER TABLE products.mapset OWNER TO estation;

--
-- TOC entry 2250 (class 0 OID 0)
-- Dependencies: 185
-- Name: COLUMN mapset.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN mapset.defined_by IS 'values: JRC or USER';


--
-- TOC entry 186 (class 1259 OID 17364)
-- Name: process_product; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE process_product (
    process_id integer NOT NULL,
    productcode character varying NOT NULL,
    subproductcode character varying NOT NULL,
    version character varying NOT NULL,
    mapsetcode character varying NOT NULL,
    type character varying NOT NULL,
    activated boolean NOT NULL,
    final boolean NOT NULL,
    date_format character varying,
    start_date bigint,
    end_date bigint
);


ALTER TABLE products.process_product OWNER TO estation;

--
-- TOC entry 187 (class 1259 OID 17370)
-- Name: processing; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE processing (
    process_id integer NOT NULL,
    defined_by character varying NOT NULL,
    output_mapsetcode character varying NOT NULL,
    activated boolean DEFAULT false NOT NULL,
    derivation_method character varying NOT NULL,
    algorithm character varying NOT NULL,
    priority character varying NOT NULL,
    enabled boolean DEFAULT false NOT NULL
);


ALTER TABLE products.processing OWNER TO estation;

--
-- TOC entry 188 (class 1259 OID 17377)
-- Name: product; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE product (
    productcode character varying NOT NULL,
    subproductcode character varying NOT NULL,
    version character varying NOT NULL,
    defined_by character varying NOT NULL,
    activated boolean DEFAULT false NOT NULL,
    category_id character varying NOT NULL,
    product_type character varying,
    descriptive_name character varying(255),
    description character varying,
    provider character varying,
    frequency_id character varying NOT NULL,
    date_format character varying NOT NULL,
    scale_factor double precision,
    scale_offset double precision,
    nodata bigint,
    mask_min double precision,
    mask_max double precision,
    unit character varying,
    data_type_id character varying NOT NULL,
    masked boolean NOT NULL,
    timeseries_role character varying
);


ALTER TABLE products.product OWNER TO estation;

--
-- TOC entry 2251 (class 0 OID 0)
-- Dependencies: 188
-- Name: COLUMN product.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.defined_by IS 'values: JRC or USER';


--
-- TOC entry 2252 (class 0 OID 0)
-- Dependencies: 188
-- Name: COLUMN product.product_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.product_type IS 'A product can be of type Native, Ingest or Derived.';


--
-- TOC entry 2253 (class 0 OID 0)
-- Dependencies: 188
-- Name: COLUMN product.descriptive_name; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.descriptive_name IS 'A clear and descriptive name of the product.';


--
-- TOC entry 2254 (class 0 OID 0)
-- Dependencies: 188
-- Name: COLUMN product.frequency_id; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.frequency_id IS 'A string, case insensitive, indicating the time-span that the product represents (is distributed): 
undefined
INSTANTANEOUS
DEKAD!=10-days
8days
1month
1week
24hours (for MSG products)
1year';


--
-- TOC entry 2255 (class 0 OID 0)
-- Dependencies: 188
-- Name: COLUMN product.date_format; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.date_format IS 'A string, case insensitive, in YYYYMMDD, YYYYMMDDHHMM,YYYY,MMDD,HHMM. HHMM (may be used for MSG 15 minutes synthesis). This list may change with the project life. It is maintained by JRC';


--
-- TOC entry 2256 (class 0 OID 0)
-- Dependencies: 188
-- Name: COLUMN product.timeseries_role; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.timeseries_role IS 'Defines the role of the product in TS:
<empty> or Null -> not considered
''Initial'' -> it is represented as ''base'' TS (YYYYMMDD date type)
<subproductcode> -> it is represented as ''derived'' from the <subproductcode> (which must be ''Initial'')';


--
-- TOC entry 189 (class 1259 OID 17384)
-- Name: product_acquisition_data_source; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE product_acquisition_data_source (
    productcode character varying NOT NULL,
    subproductcode character varying NOT NULL,
    version character varying NOT NULL,
    data_source_id character varying NOT NULL,
    defined_by character varying NOT NULL,
    type character varying,
    activated boolean DEFAULT false NOT NULL,
    store_original_data boolean DEFAULT false NOT NULL
);


ALTER TABLE products.product_acquisition_data_source OWNER TO estation;

--
-- TOC entry 2257 (class 0 OID 0)
-- Dependencies: 189
-- Name: COLUMN product_acquisition_data_source.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product_acquisition_data_source.defined_by IS 'values: JRC or USER';


--
-- TOC entry 2258 (class 0 OID 0)
-- Dependencies: 189
-- Name: COLUMN product_acquisition_data_source.type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product_acquisition_data_source.type IS 'Values: EUMETCAST, INTERNET, OTHER';


--
-- TOC entry 190 (class 1259 OID 17392)
-- Name: product_category; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE product_category (
    category_id character varying NOT NULL,
    descriptive_name character varying,
    order_index integer
);


ALTER TABLE products.product_category OWNER TO estation;

--
-- TOC entry 195 (class 1259 OID 18616)
-- Name: spirits; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE spirits (
    productcode character varying NOT NULL,
    subproductcode character varying NOT NULL,
    version character varying NOT NULL,
    mapsetcode character varying,
    prod_values character varying,
    flags character varying,
    data_ignore_value integer,
    days integer,
    start_date integer,
    end_date integer,
    sensor_type character varying,
    comment character varying,
    sensor_filename_prefix character varying,
    frequency_filename_prefix character varying,
    product_anomaly_filename_prefix character varying,
    activated boolean DEFAULT false NOT NULL
);


ALTER TABLE products.spirits OWNER TO estation;

--
-- TOC entry 191 (class 1259 OID 17398)
-- Name: sub_datasource_description; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE sub_datasource_description (
    productcode character varying NOT NULL,
    subproductcode character varying NOT NULL,
    version character varying NOT NULL,
    datasource_descr_id character varying NOT NULL,
    scale_factor double precision NOT NULL,
    scale_offset double precision NOT NULL,
    no_data double precision,
    data_type_id character varying NOT NULL,
    mask_min double precision,
    mask_max double precision,
    re_process character varying,
    re_extract character varying
);


ALTER TABLE products.sub_datasource_description OWNER TO estation;

--
-- TOC entry 193 (class 1259 OID 18380)
-- Name: thema; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE thema (
    thema_id character varying NOT NULL,
    description character varying NOT NULL
);


ALTER TABLE products.thema OWNER TO estation;

--
-- TOC entry 194 (class 1259 OID 18388)
-- Name: thema_product; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE thema_product (
    thema_id character varying NOT NULL,
    productcode character varying NOT NULL,
    version character varying NOT NULL,
    mapsetcode character varying NOT NULL,
    activated boolean NOT NULL
);


ALTER TABLE products.thema_product OWNER TO estation;

SET search_path = analysis, pg_catalog;

--
-- TOC entry 2016 (class 2604 OID 17992)
-- Name: legend_id; Type: DEFAULT; Schema: analysis; Owner: estation
--

ALTER TABLE ONLY legend ALTER COLUMN legend_id SET DEFAULT nextval('legend_legend_id_seq'::regclass);


--
-- TOC entry 2042 (class 2606 OID 17407)
-- Name: Primary key violation; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY legend_step
    ADD CONSTRAINT "Primary key violation" PRIMARY KEY (legend_id, from_step, to_step);


--
-- TOC entry 2036 (class 2606 OID 17411)
-- Name: i18n_pkey; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY i18n
    ADD CONSTRAINT i18n_pkey PRIMARY KEY (label);


--
-- TOC entry 2038 (class 2606 OID 17413)
-- Name: languages_pkey; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY languages
    ADD CONSTRAINT languages_pkey PRIMARY KEY (langcode);


--
-- TOC entry 2040 (class 2606 OID 17417)
-- Name: legend_pkey; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY legend
    ADD CONSTRAINT legend_pkey PRIMARY KEY (legend_id);


--
-- TOC entry 2044 (class 2606 OID 17419)
-- Name: product_legend_pkey; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY product_legend
    ADD CONSTRAINT product_legend_pkey PRIMARY KEY (productcode, subproductcode, version, legend_id);


--
-- TOC entry 2076 (class 2606 OID 18362)
-- Name: timeseries_drawproperties_pk; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY timeseries_drawproperties
    ADD CONSTRAINT timeseries_drawproperties_pk PRIMARY KEY (productcode, subproductcode, version);


SET search_path = products, pg_catalog;

--
-- TOC entry 2032 (class 2606 OID 17420)
-- Name: check_datasource_chk; Type: CHECK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE product_acquisition_data_source
    ADD CONSTRAINT check_datasource_chk CHECK (check_datasource(data_source_id, type)) NOT VALID;


--
-- TOC entry 2046 (class 2606 OID 17422)
-- Name: data_type_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY data_type
    ADD CONSTRAINT data_type_pk PRIMARY KEY (data_type_id);


--
-- TOC entry 2048 (class 2606 OID 17424)
-- Name: datasource_description_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY datasource_description
    ADD CONSTRAINT datasource_description_pk PRIMARY KEY (datasource_descr_id);


--
-- TOC entry 2050 (class 2606 OID 17426)
-- Name: date_format_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY date_format
    ADD CONSTRAINT date_format_pk PRIMARY KEY (date_format);


--
-- TOC entry 2052 (class 2606 OID 17428)
-- Name: eumetcast_source_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY eumetcast_source
    ADD CONSTRAINT eumetcast_source_pk PRIMARY KEY (eumetcast_id);


--
-- TOC entry 2054 (class 2606 OID 17430)
-- Name: frequency_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY frequency
    ADD CONSTRAINT frequency_pk PRIMARY KEY (frequency_id);


--
-- TOC entry 2056 (class 2606 OID 17432)
-- Name: ingestion_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY ingestion
    ADD CONSTRAINT ingestion_pk PRIMARY KEY (productcode, subproductcode, version, mapsetcode);


--
-- TOC entry 2058 (class 2606 OID 17434)
-- Name: internet_source_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY internet_source
    ADD CONSTRAINT internet_source_pk PRIMARY KEY (internet_id);


--
-- TOC entry 2060 (class 2606 OID 17436)
-- Name: mapset_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY mapset
    ADD CONSTRAINT mapset_pk PRIMARY KEY (mapsetcode);


--
-- TOC entry 2062 (class 2606 OID 17438)
-- Name: process_input_product_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY process_product
    ADD CONSTRAINT process_input_product_pk PRIMARY KEY (process_id, productcode, subproductcode, version, mapsetcode);


--
-- TOC entry 2064 (class 2606 OID 17440)
-- Name: processing_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY processing
    ADD CONSTRAINT processing_pk PRIMARY KEY (process_id);


--
-- TOC entry 2068 (class 2606 OID 17442)
-- Name: product_acquisition_data_source_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY product_acquisition_data_source
    ADD CONSTRAINT product_acquisition_data_source_pk PRIMARY KEY (productcode, subproductcode, version, data_source_id);


--
-- TOC entry 2071 (class 2606 OID 17444)
-- Name: product_category_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY product_category
    ADD CONSTRAINT product_category_pk PRIMARY KEY (category_id);


--
-- TOC entry 2066 (class 2606 OID 17446)
-- Name: product_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY product
    ADD CONSTRAINT product_pk PRIMARY KEY (productcode, subproductcode, version);


--
-- TOC entry 2082 (class 2606 OID 18624)
-- Name: spirits_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY spirits
    ADD CONSTRAINT spirits_pk PRIMARY KEY (productcode, subproductcode, version);


--
-- TOC entry 2074 (class 2606 OID 17448)
-- Name: sub_datasource_description_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY sub_datasource_description
    ADD CONSTRAINT sub_datasource_description_pk PRIMARY KEY (productcode, subproductcode, version, datasource_descr_id);


--
-- TOC entry 2078 (class 2606 OID 18387)
-- Name: thema_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY thema
    ADD CONSTRAINT thema_pk PRIMARY KEY (thema_id);


--
-- TOC entry 2080 (class 2606 OID 18395)
-- Name: thema_product_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY thema_product
    ADD CONSTRAINT thema_product_pk PRIMARY KEY (thema_id, productcode, version, mapsetcode);


--
-- TOC entry 2069 (class 1259 OID 17449)
-- Name: product_categories_order_index_key; Type: INDEX; Schema: products; Owner: estation; Tablespace: 
--

CREATE UNIQUE INDEX product_categories_order_index_key ON product_category USING btree (order_index);


--
-- TOC entry 2072 (class 1259 OID 17450)
-- Name: unique_product_category_name; Type: INDEX; Schema: products; Owner: estation; Tablespace: 
--

CREATE UNIQUE INDEX unique_product_category_name ON product_category USING btree (descriptive_name);


--
-- TOC entry 2112 (class 2620 OID 18662)
-- Name: check_update; Type: TRIGGER; Schema: products; Owner: estation
--

CREATE TRIGGER check_update BEFORE UPDATE ON ingestion FOR EACH ROW WHEN (((old.enabled IS DISTINCT FROM new.enabled) OR (old.activated IS DISTINCT FROM new.activated))) EXECUTE PROCEDURE deactivate_ingestion_when_disabled();


--
-- TOC entry 2110 (class 2620 OID 18592)
-- Name: insert_eumetcast_source; Type: TRIGGER; Schema: products; Owner: estation
--

CREATE TRIGGER insert_eumetcast_source BEFORE INSERT ON eumetcast_source FOR EACH ROW EXECUTE PROCEDURE check_eumetcast_source_datasource_description();


--
-- TOC entry 2111 (class 2620 OID 18661)
-- Name: insert_ingestion; Type: TRIGGER; Schema: products; Owner: estation
--

CREATE TRIGGER insert_ingestion BEFORE INSERT ON ingestion FOR EACH ROW EXECUTE PROCEDURE deactivate_ingestion_when_disabled();


--
-- TOC entry 2113 (class 2620 OID 18590)
-- Name: insert_internet_source; Type: TRIGGER; Schema: products; Owner: estation
--

CREATE TRIGGER insert_internet_source BEFORE INSERT ON internet_source FOR EACH ROW EXECUTE PROCEDURE check_internet_source_datasource_description();


SET search_path = analysis, pg_catalog;

--
-- TOC entry 2084 (class 2606 OID 17451)
-- Name: legend_pkey; Type: FK CONSTRAINT; Schema: analysis; Owner: estation
--

ALTER TABLE ONLY product_legend
    ADD CONSTRAINT legend_pkey FOREIGN KEY (legend_id) REFERENCES legend(legend_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2083 (class 2606 OID 17456)
-- Name: legend_step_legend_id_fkey; Type: FK CONSTRAINT; Schema: analysis; Owner: estation
--

ALTER TABLE ONLY legend_step
    ADD CONSTRAINT legend_step_legend_id_fkey FOREIGN KEY (legend_id) REFERENCES legend(legend_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2085 (class 2606 OID 17461)
-- Name: product_legend_product_pkey; Type: FK CONSTRAINT; Schema: analysis; Owner: estation
--

ALTER TABLE ONLY product_legend
    ADD CONSTRAINT product_legend_product_pkey FOREIGN KEY (productcode, subproductcode, version) REFERENCES products.product(productcode, subproductcode, version) ON UPDATE CASCADE;


SET search_path = products, pg_catalog;

--
-- TOC entry 2098 (class 2606 OID 18479)
-- Name: data_type_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product
    ADD CONSTRAINT data_type_product_fk FOREIGN KEY (data_type_id) REFERENCES data_type(data_type_id) ON UPDATE RESTRICT ON DELETE SET NULL;


--
-- TOC entry 2103 (class 2606 OID 18761)
-- Name: data_type_sub_datasource_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY sub_datasource_description
    ADD CONSTRAINT data_type_sub_datasource_description_fk FOREIGN KEY (data_type_id) REFERENCES data_type(data_type_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 2088 (class 2606 OID 18786)
-- Name: datasource_description_eumetcast_source_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY eumetcast_source
    ADD CONSTRAINT datasource_description_eumetcast_source_fk FOREIGN KEY (datasource_descr_id) REFERENCES datasource_description(datasource_descr_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2091 (class 2606 OID 18791)
-- Name: datasource_description_internet_source_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY internet_source
    ADD CONSTRAINT datasource_description_internet_source_fk FOREIGN KEY (datasource_descr_id) REFERENCES datasource_description(datasource_descr_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2105 (class 2606 OID 18549)
-- Name: datasource_description_sub_datasource_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY sub_datasource_description
    ADD CONSTRAINT datasource_description_sub_datasource_description_fk FOREIGN KEY (datasource_descr_id) REFERENCES datasource_description(datasource_descr_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 2093 (class 2606 OID 18524)
-- Name: date_format_process_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY process_product
    ADD CONSTRAINT date_format_process_product_fk FOREIGN KEY (date_format) REFERENCES date_format(date_format) ON UPDATE RESTRICT ON DELETE SET NULL;


--
-- TOC entry 2086 (class 2606 OID 18514)
-- Name: dateformat_datasource_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY datasource_description
    ADD CONSTRAINT dateformat_datasource_description_fk FOREIGN KEY (date_format) REFERENCES date_format(date_format) ON UPDATE RESTRICT ON DELETE SET NULL;


--
-- TOC entry 2099 (class 2606 OID 18484)
-- Name: datetype_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product
    ADD CONSTRAINT datetype_product_fk FOREIGN KEY (date_format) REFERENCES date_format(date_format) ON UPDATE RESTRICT ON DELETE SET NULL;


--
-- TOC entry 2100 (class 2606 OID 18489)
-- Name: distribution_frequency_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product
    ADD CONSTRAINT distribution_frequency_product_fk FOREIGN KEY (frequency_id) REFERENCES frequency(frequency_id) ON UPDATE RESTRICT ON DELETE SET NULL;


--
-- TOC entry 2092 (class 2606 OID 18499)
-- Name: frequency_internet_source_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY internet_source
    ADD CONSTRAINT frequency_internet_source_fk FOREIGN KEY (frequency_id) REFERENCES frequency(frequency_id) ON UPDATE RESTRICT ON DELETE SET NULL;


--
-- TOC entry 2087 (class 2606 OID 18519)
-- Name: mapset_datasource_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY datasource_description
    ADD CONSTRAINT mapset_datasource_description_fk FOREIGN KEY (native_mapset) REFERENCES mapset(mapsetcode) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- TOC entry 2089 (class 2606 OID 18771)
-- Name: mapset_ingestion_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY ingestion
    ADD CONSTRAINT mapset_ingestion_fk FOREIGN KEY (mapsetcode) REFERENCES mapset(mapsetcode) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 2094 (class 2606 OID 18529)
-- Name: mapset_process_input_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY process_product
    ADD CONSTRAINT mapset_process_input_product_fk FOREIGN KEY (mapsetcode) REFERENCES mapset(mapsetcode) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- TOC entry 2097 (class 2606 OID 18569)
-- Name: mapset_processing_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY processing
    ADD CONSTRAINT mapset_processing_fk FOREIGN KEY (output_mapsetcode) REFERENCES mapset(mapsetcode) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- TOC entry 2109 (class 2606 OID 18630)
-- Name: mapset_spirits_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY spirits
    ADD CONSTRAINT mapset_spirits_fk FOREIGN KEY (mapsetcode) REFERENCES mapset(mapsetcode) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- TOC entry 2106 (class 2606 OID 18574)
-- Name: mapset_thema_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY thema_product
    ADD CONSTRAINT mapset_thema_product_fk FOREIGN KEY (mapsetcode) REFERENCES mapset(mapsetcode) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- TOC entry 2095 (class 2606 OID 18534)
-- Name: processing_dependencies_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY process_product
    ADD CONSTRAINT processing_dependencies_fk FOREIGN KEY (process_id) REFERENCES processing(process_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2101 (class 2606 OID 18494)
-- Name: product_category_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product
    ADD CONSTRAINT product_category_product_fk FOREIGN KEY (category_id) REFERENCES product_category(category_id) ON UPDATE RESTRICT ON DELETE SET NULL;


--
-- TOC entry 2096 (class 2606 OID 18539)
-- Name: product_dependencies_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY process_product
    ADD CONSTRAINT product_dependencies_fk FOREIGN KEY (productcode, subproductcode, version) REFERENCES product(productcode, subproductcode, version) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 2090 (class 2606 OID 18776)
-- Name: product_ingestion_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY ingestion
    ADD CONSTRAINT product_ingestion_fk FOREIGN KEY (productcode, subproductcode, version) REFERENCES product(productcode, subproductcode, version) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2104 (class 2606 OID 18766)
-- Name: product_sub_datasource_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY sub_datasource_description
    ADD CONSTRAINT product_sub_datasource_description_fk FOREIGN KEY (productcode, subproductcode, version) REFERENCES product(productcode, subproductcode, version) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2102 (class 2606 OID 18781)
-- Name: products_description_product_acquisition_data_sources_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product_acquisition_data_source
    ADD CONSTRAINT products_description_product_acquisition_data_sources_fk FOREIGN KEY (productcode, subproductcode, version) REFERENCES product(productcode, subproductcode, version) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2108 (class 2606 OID 18625)
-- Name: spirits_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY spirits
    ADD CONSTRAINT spirits_product_fk FOREIGN KEY (productcode, subproductcode, version) REFERENCES product(productcode, subproductcode, version) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 2107 (class 2606 OID 18579)
-- Name: thema_thema_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY thema_product
    ADD CONSTRAINT thema_thema_product_fk FOREIGN KEY (thema_id) REFERENCES thema(thema_id) ON UPDATE CASCADE ON DELETE CASCADE;


-- Completed on 2016-02-02 10:57:22 CET

--
-- PostgreSQL database dump complete
--

