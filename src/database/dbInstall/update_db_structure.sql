

CREATE OR REPLACE FUNCTION analysis.update_insert_layers(layerid integer, layerlevel character varying, layername character varying, description character varying, filename character varying, layerorderidx integer, layertype character varying, polygon_outlinecolor character varying, polygon_outlinewidth integer, polygon_fillcolor character varying, polygon_fillopacity integer, feature_display_column character varying, feature_highlight_outlinecolor character varying, feature_highlight_outlinewidth integer, feature_highlight_fillcolor character varying, feature_highlight_fillopacity integer, feature_selected_outlinecolor character varying, feature_selected_outlinewidth integer, enabled boolean, deletable boolean, background_legend_image_filename character varying, projection character varying, submenu character varying, menu character varying, defined_by character varying, open_in_mapview boolean, provider character varying, full_copy boolean DEFAULT false)
  RETURNS boolean AS
$BODY$
	DECLARE

	  _layerid 				ALIAS FOR  $1;
	  _layerlevel 				ALIAS FOR  $2;
	  _layername 				ALIAS FOR  $3;
	  _description 				ALIAS FOR  $4;
	  _filename 				ALIAS FOR  $5;
	  _layerorderidx 			ALIAS FOR  $6;
	  _layertype 				ALIAS FOR  $7;
	  _polygon_outlinecolor 		ALIAS FOR  $8;
	  _polygon_outlinewidth 		ALIAS FOR  $9;
	  _polygon_fillcolor 			ALIAS FOR  $10;
	  _polygon_fillopacity 			ALIAS FOR  $11;
	  _feature_display_column 		ALIAS FOR  $12;
	  _feature_highlight_outlinecolor 	ALIAS FOR  $13;
	  _feature_highlight_outlinewidth 	ALIAS FOR  $14;
	  _feature_highlight_fillcolor	  	ALIAS FOR  $15;
	  _feature_highlight_fillopacity  	ALIAS FOR  $16;
	  _feature_selected_outlinecolor  	ALIAS FOR  $17;
	  _feature_selected_outlinewidth  	ALIAS FOR  $18;
	  _enabled 			  	ALIAS FOR  $19;
	  _deletable 			  	ALIAS FOR  $20;
	  _background_legend_image_filename 	ALIAS FOR  $21;
	  _projection 				ALIAS FOR  $22;
	  _submenu 				ALIAS FOR  $23;
	  _menu 				ALIAS FOR  $24;
	  _defined_by 				ALIAS FOR  $25;
	  _open_in_mapview			ALIAS FOR  $26;
	  _provider 				ALIAS FOR  $27;
	  _full_copy 				ALIAS FOR  $28;

	BEGIN
		PERFORM * FROM analysis.layers l WHERE l.layerid = _layerid;
		IF FOUND THEN
			IF _full_copy THEN
				UPDATE analysis.layers l
				SET layerlevel = TRIM(_layerlevel),
				    layername = TRIM(_layername),
				    description = TRIM(_description),
				    filename = TRIM(_filename),
				    layerorderidx = _layerorderidx,
				    layertype = TRIM(_layertype),
				    polygon_outlinecolor = TRIM(_polygon_outlinecolor),
				    polygon_outlinewidth = _polygon_outlinewidth,
				    polygon_fillcolor = TRIM(_polygon_fillcolor),
				    polygon_fillopacity = _polygon_fillopacity,
				    feature_display_column = TRIM(_feature_display_column),
				    feature_highlight_outlinecolor = TRIM(_feature_highlight_outlinecolor),
				    feature_highlight_outlinewidth = _feature_highlight_outlinewidth,
				    feature_highlight_fillcolor = TRIM(_feature_highlight_fillcolor),
				    feature_highlight_fillopacity = _feature_highlight_fillopacity,
				    feature_selected_outlinecolor = TRIM(_feature_selected_outlinecolor),
				    feature_selected_outlinewidth = _feature_selected_outlinewidth,
				    enabled = _enabled,
				    deletable = _deletable,
				    background_legend_image_filename = TRIM(_background_legend_image_filename),
				    projection = TRIM(_projection),
				    submenu = TRIM(_submenu),
				    menu = TRIM(_menu),
				    defined_by = TRIM(_defined_by),
				    open_in_mapview = _open_in_mapview,
				    provider = TRIM(_provider)
				WHERE l.layerid = _layerid;
			ELSE
				UPDATE analysis.layers l
				SET layerlevel = TRIM(_layerlevel),
				    layername = TRIM(_layername),
				    description = TRIM(_description),
				    filename = TRIM(_filename),
				    layerorderidx = _layerorderidx,
				    layertype = TRIM(_layertype),
				    -- polygon_outlinecolor = TRIM(_polygon_outlinecolor),
				    -- polygon_outlinewidth = _polygon_outlinewidth,
				    -- polygon_fillcolor = TRIM(_polygon_fillcolor),
				    -- polygon_fillopacity = _polygon_fillopacity,
				    -- feature_display_column = TRIM(_feature_display_column),
				    -- feature_highlight_outlinecolor = TRIM(_feature_highlight_outlinecolor),
				    -- feature_highlight_outlinewidth = _feature_highlight_outlinewidth,
				    -- feature_highlight_fillcolor = TRIM(_feature_highlight_fillcolor),
				    -- feature_highlight_fillopacity = _feature_highlight_fillopacity,
				    -- feature_selected_outlinecolor = TRIM(_feature_selected_outlinecolor),
				    -- feature_selected_outlinewidth = _feature_selected_outlinewidth,
				    -- enabled = _enabled,
				    deletable = _deletable,
				    background_legend_image_filename = TRIM(_background_legend_image_filename),
				    projection = TRIM(_projection),
				    submenu = TRIM(_submenu),
				    menu = TRIM(_menu),
				    defined_by = TRIM(_defined_by),
				    -- open_in_mapview = _open_in_mapview,
				    provider = TRIM(_provider)
				WHERE l.layerid = _layerid;
			END IF;

		ELSE
			INSERT INTO analysis.layers (
				layerid,
				layerlevel,
				layername,
				description,
				filename,
				layerorderidx,
				layertype,
				polygon_outlinecolor,
				polygon_outlinewidth,
				polygon_fillcolor,
				polygon_fillopacity,
				feature_display_column,
				feature_highlight_outlinecolor,
				feature_highlight_outlinewidth,
				feature_highlight_fillcolor,
				feature_highlight_fillopacity,
				feature_selected_outlinecolor,
				feature_selected_outlinewidth,
				enabled,
				deletable,
				background_legend_image_filename,
				projection,
				submenu,
				menu,
				defined_by,
				open_in_mapview,
				provider
			)
			VALUES (
			    _layerid,
			    TRIM(_layerlevel),
			    TRIM(_layername),
			    TRIM(_description),
			    TRIM(_filename),
			    _layerorderidx,
			    TRIM(_layertype),
			    TRIM(_polygon_outlinecolor),
			    _polygon_outlinewidth,
			    TRIM(_polygon_fillcolor),
			    _polygon_fillopacity,
			    TRIM(_feature_display_column),
			    TRIM(_feature_highlight_outlinecolor),
			    _feature_highlight_outlinewidth,
			    TRIM(_feature_highlight_fillcolor),
			    _feature_highlight_fillopacity,
			    TRIM(_feature_selected_outlinecolor),
			    _feature_selected_outlinewidth,
			    _enabled,
			    _deletable,
			    TRIM(_background_legend_image_filename),
			    TRIM(_projection),
			    TRIM(_submenu),
			    TRIM(_menu),
			    TRIM(_defined_by),
			    _open_in_mapview,
			    TRIM(_provider)
			);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION analysis.update_insert_layers(integer, character varying, character varying, character varying, character varying, integer, character varying, character varying, integer, character varying, integer, character varying, character varying, integer, character varying, integer, character varying, integer, boolean, boolean, character varying, character varying, character varying, character varying, character varying, boolean, character varying, boolean)
  OWNER TO estation;




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



ALTER TABLE analysis.timeseries_drawproperties
  ADD COLUMN aggregation_type character varying DEFAULT 'mean';

ALTER TABLE analysis.timeseries_drawproperties
  ADD COLUMN aggregation_min double precision;

ALTER TABLE analysis.timeseries_drawproperties
  ADD COLUMN aggregation_max double precision;


DROP TABLE IF EXISTS analysis.layers;

CREATE TABLE IF NOT EXISTS analysis.layers
(
  layerid bigserial NOT NULL,
  layerlevel character varying(80),
  layername character varying(80),
  description character varying(255),
  filename character varying(80),
  layerorderidx integer DEFAULT 1,
  layertype character varying(80) DEFAULT 'polygon'::character varying,
  polygon_outlinecolor character varying(11) DEFAULT '0 0 0'::character varying,
  polygon_outlinewidth integer DEFAULT 1,
  polygon_fillcolor character varying(11) DEFAULT '0 0 0'::character varying,
  polygon_fillopacity integer DEFAULT 100,
  feature_display_column character varying(255),
  feature_highlight_outlinecolor character varying(11) DEFAULT '0 0 0'::character varying,
  feature_highlight_outlinewidth integer DEFAULT 1,
  feature_highlight_fillcolor character varying(11) DEFAULT '0 0 0'::character varying,
  feature_highlight_fillopacity integer DEFAULT 100,
  feature_selected_outlinecolor character varying(11) DEFAULT '0 0 0'::character varying,
  feature_selected_outlinewidth integer DEFAULT 1,
  enabled boolean DEFAULT true,
  deletable boolean DEFAULT true,
  background_legend_image_filename character varying(80),
  projection character varying(80),
  submenu character varying(80),
  menu character varying(80),
  defined_by character varying DEFAULT 'USER'::character varying,
  open_in_mapview boolean DEFAULT false,
  provider character varying,
  CONSTRAINT layers_pkey PRIMARY KEY (layerid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.layers
  OWNER TO estation;



CREATE TABLE analysis.chart_drawproperties
(
  chart_type character varying NOT NULL,
  chart_width integer,
  chart_height integer,
  chart_title_font_size integer,
  chart_title_font_color character varying,
  chart_subtitle_font_size integer,
  chart_subtitle_font_color character varying,
  yaxe1_font_size integer,
  yaxe2_font_size integer,
  legend_font_size integer,
  legend_font_color character varying,
  xaxe_font_size integer,
  xaxe_font_color character varying,
  yaxe3_font_size integer,
  CONSTRAINT chart_drawproperties_pk PRIMARY KEY (chart_type)
)
WITH (
  OIDS=TRUE
);
ALTER TABLE analysis.chart_drawproperties
  OWNER TO estation;


-- Function: products.update_insert_product(character varying, character varying, character varying, character varying, boolean, character varying, character varying, character varying, character varying, character varying, character varying, character varying, double precision, double precision, bigint, double precision, double precision, character varying, character varying, boolean, character varying, boolean)

-- DROP FUNCTION products.update_insert_product(character varying, character varying, character varying, character varying, boolean, character varying, character varying, character varying, character varying, character varying, character varying, character varying, double precision, double precision, bigint, double precision, double precision, character varying, character varying, boolean, character varying, boolean);

CREATE OR REPLACE FUNCTION products.update_insert_product(productcode character varying, subproductcode character varying, version character varying, defined_by character varying, activated boolean, category_id character varying, product_type character varying, descriptive_name character varying, description character varying, provider character varying, frequency_id character varying, date_format character varying, scale_factor double precision, scale_offset double precision, nodata bigint, mask_min double precision, mask_max double precision, unit character varying, data_type_id character varying, masked boolean, timeseries_role character varying, full_copy boolean DEFAULT false)
  RETURNS boolean AS
$BODY$
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
					masked = _masked,
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
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION products.update_insert_product(character varying, character varying, character varying, character varying, boolean, character varying, character varying, character varying, character varying, character varying, character varying, character varying, double precision, double precision, bigint, double precision, double precision, character varying, character varying, boolean, character varying, boolean)
  OWNER TO estation;




-- Function: analysis.update_insert_layers(integer, character varying, character varying, character varying, character varying, integer, character varying, character varying, integer, character varying, integer, character varying, character varying, integer, character varying, integer, character varying, integer, boolean, boolean, character varying, character varying, character varying, character varying, character varying, boolean, character varying, boolean)

-- DROP FUNCTION analysis.update_insert_layers(integer, character varying, character varying, character varying, character varying, integer, character varying, character varying, integer, character varying, integer, character varying, character varying, integer, character varying, integer, character varying, integer, boolean, boolean, character varying, character varying, character varying, character varying, character varying, boolean, character varying, boolean);

CREATE OR REPLACE FUNCTION analysis.update_insert_layers(
               layerid integer,
							 layerlevel character varying,
							 layername character varying,
							 description character varying,
							 filename character varying,
							 layerorderidx integer,
							 layertype character varying,
							 polygon_outlinecolor character varying,
							 polygon_outlinewidth integer,
							 polygon_fillcolor character varying,
							 polygon_fillopacity integer,
							 feature_display_column character varying,
							 feature_highlight_outlinecolor character varying,
							 feature_highlight_outlinewidth integer,
							 feature_highlight_fillcolor character varying,
							 feature_highlight_fillopacity integer,
							 feature_selected_outlinecolor character varying,
							 feature_selected_outlinewidth integer,
							 enabled boolean,
							 deletable boolean,
							 background_legend_image_filename character varying,
							 projection character varying,
							 submenu character varying,
							 menu character varying,
							 defined_by character varying,
							 open_in_mapview boolean,
							 provider character varying,
							 full_copy boolean DEFAULT false
							 )
  RETURNS boolean AS
$BODY$
	DECLARE

	  _layerid 				ALIAS FOR  $1;
	  _layerlevel 				ALIAS FOR  $2;
	  _layername 				ALIAS FOR  $3;
	  _description 				ALIAS FOR  $4;
	  _filename 				ALIAS FOR  $5;
	  _layerorderidx 			ALIAS FOR  $6;
	  _layertype 				ALIAS FOR  $7;
	  _polygon_outlinecolor 		ALIAS FOR  $8;
	  _polygon_outlinewidth 		ALIAS FOR  $9;
	  _polygon_fillcolor 			ALIAS FOR  $10;
	  _polygon_fillopacity 			ALIAS FOR  $11;
	  _feature_display_column 		ALIAS FOR  $12;
	  _feature_highlight_outlinecolor 	ALIAS FOR  $13;
	  _feature_highlight_outlinewidth 	ALIAS FOR  $14;
	  _feature_highlight_fillcolor	  	ALIAS FOR  $15;
	  _feature_highlight_fillopacity  	ALIAS FOR  $16;
	  _feature_selected_outlinecolor  	ALIAS FOR  $17;
	  _feature_selected_outlinewidth  	ALIAS FOR  $18;
	  _enabled 			  	ALIAS FOR  $19;
	  _deletable 			  	ALIAS FOR  $20;
	  _background_legend_image_filename 	ALIAS FOR  $21;
	  _projection 				ALIAS FOR  $22;
	  _submenu 				ALIAS FOR  $23;
	  _menu 				ALIAS FOR  $24;
	  _defined_by 				ALIAS FOR  $25;
	  _open_in_mapview			ALIAS FOR  $26;
	  _provider 				ALIAS FOR  $27;
	  _full_copy 				ALIAS FOR  $28;

	BEGIN
		PERFORM * FROM analysis.layers l WHERE l.layerid = _layerid;
		IF FOUND THEN
			IF _full_copy THEN
				UPDATE analysis.layers l
				SET layerlevel = TRIM(_layerlevel),
				    layername = TRIM(_layername),
				    description = TRIM(_description),
				    filename = TRIM(_filename),
				    layerorderidx = _layerorderidx,
				    layertype = TRIM(_layertype),
				    polygon_outlinecolor = TRIM(_polygon_outlinecolor),
				    polygon_outlinewidth = _polygon_outlinewidth,
				    polygon_fillcolor = TRIM(_polygon_fillcolor),
				    polygon_fillopacity = _polygon_fillopacity,
				    feature_display_column = TRIM(_feature_display_column),
				    feature_highlight_outlinecolor = TRIM(_feature_highlight_outlinecolor),
				    feature_highlight_outlinewidth = _feature_highlight_outlinewidth,
				    feature_highlight_fillcolor = TRIM(_feature_highlight_fillcolor),
				    feature_highlight_fillopacity = _feature_highlight_fillopacity,
				    feature_selected_outlinecolor = TRIM(_feature_selected_outlinecolor),
				    feature_selected_outlinewidth = _feature_selected_outlinewidth,
				    enabled = _enabled,
				    deletable = _deletable,
				    background_legend_image_filename = TRIM(_background_legend_image_filename),
				    projection = TRIM(_projection),
				    submenu = TRIM(_submenu),
				    menu = TRIM(_menu),
				    defined_by = TRIM(_defined_by),
				    open_in_mapview = _open_in_mapview,
				    provider = TRIM(_provider)
				WHERE l.layerid = _layerid;
			ELSE
				UPDATE analysis.layers l
				SET layerlevel = TRIM(_layerlevel),
				    layername = TRIM(_layername),
				    description = TRIM(_description),
				    filename = TRIM(_filename),
				    layerorderidx = _layerorderidx,
				    layertype = TRIM(_layertype),
				    -- polygon_outlinecolor = TRIM(_polygon_outlinecolor),
				    -- polygon_outlinewidth = _polygon_outlinewidth,
				    -- polygon_fillcolor = TRIM(_polygon_fillcolor),
				    -- polygon_fillopacity = _polygon_fillopacity,
				    -- feature_display_column = TRIM(_feature_display_column),
				    -- feature_highlight_outlinecolor = TRIM(_feature_highlight_outlinecolor),
				    -- feature_highlight_outlinewidth = _feature_highlight_outlinewidth,
				    -- feature_highlight_fillcolor = TRIM(_feature_highlight_fillcolor),
				    -- feature_highlight_fillopacity = _feature_highlight_fillopacity,
				    -- feature_selected_outlinecolor = TRIM(_feature_selected_outlinecolor),
				    -- feature_selected_outlinewidth = _feature_selected_outlinewidth,
				    -- enabled = _enabled,
				    deletable = _deletable,
				    background_legend_image_filename = TRIM(_background_legend_image_filename),
				    projection = TRIM(_projection),
				    submenu = TRIM(_submenu),
				    menu = TRIM(_menu),
				    defined_by = TRIM(_defined_by),
				    -- open_in_mapview = _open_in_mapview,
				    provider = TRIM(_provider)
				WHERE l.layerid = _layerid;
			END IF;

		ELSE
			INSERT INTO analysis.layers (
				layerlevel,
				layername,
				description,
				filename,
				layerorderidx,
				layertype,
				polygon_outlinecolor,
				polygon_outlinewidth,
				polygon_fillcolor,
				polygon_fillopacity,
				feature_display_column,
				feature_highlight_outlinecolor,
				feature_highlight_outlinewidth,
				feature_highlight_fillcolor,
				feature_highlight_fillopacity,
				feature_selected_outlinecolor,
				feature_selected_outlinewidth,
				enabled,
				deletable,
				background_legend_image_filename,
				projection,
				submenu,
				menu,
				defined_by,
				open_in_mapview,
				provider
			)
			VALUES (
			    TRIM(_layerlevel),
			    TRIM(_layername),
			    TRIM(_description),
			    TRIM(_filename),
			    _layerorderidx,
			    TRIM(_layertype),
			    TRIM(_polygon_outlinecolor),
			    _polygon_outlinewidth,
			    TRIM(_polygon_fillcolor),
			    _polygon_fillopacity,
			    TRIM(_feature_display_column),
			    TRIM(_feature_highlight_outlinecolor),
			    _feature_highlight_outlinewidth,
			    TRIM(_feature_highlight_fillcolor),
			    _feature_highlight_fillopacity,
			    TRIM(_feature_selected_outlinecolor),
			    _feature_selected_outlinewidth,
			    _enabled,
			    _deletable,
			    TRIM(_background_legend_image_filename),
			    TRIM(_projection),
			    TRIM(_submenu),
			    TRIM(_menu),
			    TRIM(_defined_by),
			    _open_in_mapview,
			    TRIM(_provider)
			);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION analysis.update_insert_layers(	integer,
						character varying,
						character varying,
						character varying,
						character varying,
						integer,
						character varying,
						character varying,
						integer,
						character varying,
						integer,
						character varying,
						character varying,
						integer,
						character varying,
						integer,
						character varying,
						integer,
						boolean,
						boolean,
						character varying,
						character varying,
						character varying,
						character varying,
						character varying,
						boolean,
						character varying,
						boolean
					)
  OWNER TO estation;


-- Function: analysis.update_insert_timeseries_drawproperties(character varying, character varying, character varying, character varying, character varying, double precision, double precision, boolean, character varying, character varying, character varying, integer, character varying, character varying, character varying)

-- DROP FUNCTION analysis.update_insert_timeseries_drawproperties(character varying, character varying, character varying, character varying, character varying, double precision, double precision, boolean, character varying, character varying, character varying, integer, character varying, character varying, character varying);

CREATE OR REPLACE FUNCTION analysis.update_insert_timeseries_drawproperties(productcode character varying,
									    subproductcode character varying,
									    version character varying,
									    title character varying,
									    unit character varying,
									    min double precision,
									    max double precision,
									    oposite boolean,
									    tsname_in_legend character varying,
									    charttype character varying,
									    linestyle character varying,
									    linewidth integer,
									    color character varying,
									    yaxes_id character varying,
									    title_color character varying,
									    aggregation_type character varying,
									    aggregation_min double precision,
									    aggregation_max double precision
									    )
  RETURNS boolean AS
$BODY$
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
		_aggregation_type	ALIAS FOR  $16;
		_aggregation_min	ALIAS FOR  $17;
		_aggregation_max	ALIAS FOR  $18;


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
			    title_color = TRIM(_title_color),
			    aggregation_type = TRIM(_aggregation_type),
			    aggregation_min = _aggregation_min,
			    aggregation_max = _aggregation_max
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
									title_color,
									aggregation_type,
									aggregation_min,
									aggregation_max
									)
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
				TRIM(_title_color),
				TRIM(_aggregation_type),
				_aggregation_min,
				_aggregation_max
				);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION analysis.update_insert_timeseries_drawproperties(character varying, character varying, character varying, character varying, character varying, double precision, double precision, boolean, character varying, character varying, character varying, integer, character varying, character varying, character varying)
  OWNER TO estation;



-- Function: analysis.update_insert_chart_drawproperties(character varying, integer, integer, integer, character varying, integer, character varying, integer, integer, integer, character varying, integer, character varying, integer)

-- DROP FUNCTION analysis.update_insert_chart_drawproperties(character varying, integer, integer, integer, character varying, integer, character varying, integer, integer, integer, character varying, integer, character varying, integer);

CREATE OR REPLACE FUNCTION analysis.update_insert_chart_drawproperties(chart_type character varying, chart_width integer, chart_height integer, chart_title_font_size integer, chart_title_font_color character varying, chart_subtitle_font_size integer, chart_subtitle_font_color character varying, yaxe1_font_size integer, yaxe2_font_size integer, legend_font_size integer, legend_font_color character varying, xaxe_font_size integer, xaxe_font_color character varying, yaxe3_font_size integer)
  RETURNS boolean AS
$BODY$
	DECLARE

	  _chart_type 			ALIAS FOR  $1;
	  _chart_width 			ALIAS FOR  $2;
	  _chart_height 		ALIAS FOR  $3;
	  _chart_title_font_size 	ALIAS FOR  $4;
	  _chart_title_font_color 	ALIAS FOR  $5;
	  _chart_subtitle_font_size 	ALIAS FOR  $6;
	  _chart_subtitle_font_color 	ALIAS FOR  $7;
	  _yaxe1_font_size 		ALIAS FOR  $8;
	  _yaxe2_font_size 		ALIAS FOR  $9;
	  _legend_font_size 		ALIAS FOR  $10;
	  _legend_font_color 		ALIAS FOR  $11;
	  _xaxe_font_size 		ALIAS FOR  $12;
	  _xaxe_font_color 		ALIAS FOR  $13;
	  _yaxe3_font_size 		ALIAS FOR  $14;

	BEGIN
		PERFORM * FROM analysis.chart_drawproperties cd WHERE cd.chart_type = _chart_type;
		IF FOUND THEN
			UPDATE analysis.chart_drawproperties cd
			SET chart_width = _chart_width,
			    chart_height = _chart_height,
			    chart_title_font_size = _chart_title_font_size,
			    chart_title_font_color = TRIM(_chart_title_font_color),
			    chart_subtitle_font_size = _chart_subtitle_font_size,
			    chart_subtitle_font_color = TRIM(_chart_subtitle_font_color),
			    yaxe1_font_size = _yaxe1_font_size,
			    yaxe2_font_size = _yaxe2_font_size,
			    legend_font_size = _legend_font_size,
			    legend_font_color = TRIM(_legend_font_color),
			    xaxe_font_size = _xaxe_font_size,
			    xaxe_font_color = TRIM(_xaxe_font_color),
			    yaxe3_font_size = _yaxe3_font_size
			WHERE cd.chart_type = _chart_type;
		ELSE
			INSERT INTO analysis.chart_drawproperties (
				chart_type,
				chart_width,
				chart_height,
				chart_title_font_size,
				chart_title_font_color,
				chart_subtitle_font_size,
				chart_subtitle_font_color,
				yaxe1_font_size,
				yaxe2_font_size,
				legend_font_size,
				legend_font_color,
				xaxe_font_size,
				xaxe_font_color,
				yaxe3_font_size
			)
			VALUES (
			    TRIM(_chart_type),
			    _chart_width,
			    _chart_height,
			    _chart_title_font_size,
			    TRIM(_chart_title_font_color),
			    _chart_subtitle_font_size,
			    TRIM(_chart_subtitle_font_color),
			    _yaxe1_font_size,
			    _yaxe2_font_size,
			    _legend_font_size,
			    TRIM(_legend_font_color),
			    _xaxe_font_size,
			    TRIM(_xaxe_font_color),
			    _yaxe3_font_size
			);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION analysis.update_insert_chart_drawproperties(character varying, integer, integer, integer, character varying, integer, character varying, integer, integer, integer, character varying, integer, character varying, integer)
  OWNER TO estation;



-- Function: products.export_jrc_data(boolean)

-- DROP FUNCTION products.export_jrc_data(boolean);


CREATE OR REPLACE FUNCTION products.export_jrc_data(full_copy boolean DEFAULT false)
  RETURNS SETOF text AS
$BODY$
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



	RETURN QUERY SELECT 'SELECT analysis.update_insert_layers('
		|| ' layerid := ' || layerid
		|| ', layerlevel := ' || COALESCE('''' || layerlevel || '''', 'NULL')
		|| ', layername := ' || COALESCE('''' || layername || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || description || '''', 'NULL')
		|| ', filename := ' || COALESCE('''' || filename || '''', 'NULL')
		|| ', layerorderidx := ' || layerorderidx
		|| ', layertype := ' || COALESCE('''' || layertype || '''', 'NULL')
		|| ', polygon_outlinecolor := ' || COALESCE('''' || polygon_outlinecolor || '''', 'NULL')
		|| ', polygon_outlinewidth := ' || polygon_outlinewidth
		|| ', polygon_fillcolor := ' || COALESCE('''' || polygon_fillcolor || '''', 'NULL')
		|| ', polygon_fillopacity := ' || polygon_fillopacity
		|| ', feature_display_column := ' || COALESCE('''' || feature_display_column || '''', 'NULL')
		|| ', feature_highlight_outlinecolor := ' || COALESCE('''' || feature_highlight_outlinecolor || '''', 'NULL')
		|| ', feature_highlight_outlinewidth := ' || feature_highlight_outlinewidth
		|| ', feature_highlight_fillcolor := ' || COALESCE('''' || feature_highlight_fillcolor || '''', 'NULL')
		|| ', feature_highlight_fillopacity := ' || feature_highlight_fillopacity
		|| ', feature_selected_outlinecolor := ' || COALESCE('''' || feature_selected_outlinecolor || '''', 'NULL')
		|| ', feature_selected_outlinewidth := ' || feature_selected_outlinewidth
		|| ', enabled := ' || enabled
		|| ', deletable := ' || deletable
		|| ', background_legend_image_filename := ' || COALESCE('''' || background_legend_image_filename || '''', 'NULL')
		|| ', projection := ' || COALESCE('''' || projection || '''', 'NULL')
		|| ', submenu := ' || COALESCE('''' || submenu || '''', 'NULL')
		|| ', menu := ' || COALESCE('''' || menu || '''', 'NULL')
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', open_in_mapview := ' || open_in_mapview
		|| ', provider := ' || COALESCE('''' || provider || '''', 'NULL')
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM analysis.layers;



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
		|| ', aggregation_type := ' || COALESCE('''' || aggregation_type || '''', 'NULL')
		|| ', aggregation_min := ' || COALESCE(TRIM(to_char(aggregation_min, '99999999D999999')), 'NULL')
		|| ', aggregation_max := ' || COALESCE(TRIM(to_char(aggregation_max, '99999999D999999')), 'NULL')
		|| ' );'  as inserts
	FROM analysis.timeseries_drawproperties;



	RETURN QUERY SELECT 'SELECT analysis.update_insert_chart_drawproperties('
		|| ' chart_type := ' || COALESCE('''' || chart_type || '''', 'NULL')
		|| ', chart_width := ' || chart_width
		|| ', chart_height := ' || chart_height
		|| ', chart_title_font_size := ' || chart_title_font_size
		|| ', chart_title_font_color := ' || COALESCE('''' || chart_title_font_color || '''', 'NULL')
		|| ', chart_subtitle_font_size := ' || chart_subtitle_font_size
		|| ', chart_subtitle_font_color := ' || COALESCE('''' || chart_subtitle_font_color || '''', 'NULL')
		|| ', yaxe1_font_size := ' || yaxe1_font_size
		|| ', yaxe2_font_size := ' || yaxe2_font_size
		|| ', legend_font_size := ' || legend_font_size
		|| ', legend_font_color := ' || COALESCE('''' || legend_font_color || '''', 'NULL')
		|| ', xaxe_font_size := ' || xaxe_font_size
		|| ', xaxe_font_color := ' || COALESCE('''' || xaxe_font_color || '''', 'NULL')
		|| ', yaxe3_font_size := ' || yaxe3_font_size
		|| ' );'  as inserts
	FROM analysis.chart_drawproperties;



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
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION products.export_jrc_data(boolean)
  OWNER TO estation;





-- Function: products.export_all_data(boolean)

-- DROP FUNCTION products.export_all_data(boolean);

CREATE OR REPLACE FUNCTION products.export_all_data(full_copy boolean DEFAULT true)
  RETURNS SETOF text AS
$BODY$
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



	RETURN QUERY SELECT 'SELECT analysis.update_insert_layers('
		|| ' layerid := ' || layerid
		|| ', layerlevel := ' || COALESCE('''' || layerlevel || '''', 'NULL')
		|| ', layername := ' || COALESCE('''' || layername || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || description || '''', 'NULL')
		|| ', filename := ' || COALESCE('''' || filename || '''', 'NULL')
		|| ', layerorderidx := ' || layerorderidx
		|| ', layertype := ' || COALESCE('''' || layertype || '''', 'NULL')
		|| ', polygon_outlinecolor := ' || COALESCE('''' || polygon_outlinecolor || '''', 'NULL')
		|| ', polygon_outlinewidth := ' || polygon_outlinewidth
		|| ', polygon_fillcolor := ' || COALESCE('''' || polygon_fillcolor || '''', 'NULL')
		|| ', polygon_fillopacity := ' || polygon_fillopacity
		|| ', feature_display_column := ' || COALESCE('''' || feature_display_column || '''', 'NULL')
		|| ', feature_highlight_outlinecolor := ' || COALESCE('''' || feature_highlight_outlinecolor || '''', 'NULL')
		|| ', feature_highlight_outlinewidth := ' || feature_highlight_outlinewidth
		|| ', feature_highlight_fillcolor := ' || COALESCE('''' || feature_highlight_fillcolor || '''', 'NULL')
		|| ', feature_highlight_fillopacity := ' || feature_highlight_fillopacity
		|| ', feature_selected_outlinecolor := ' || COALESCE('''' || polygon_fillcolor || '''', 'NULL')
		|| ', feature_selected_outlinewidth := ' || polygon_fillopacity
		|| ', enabled := ' || enabled
		|| ', deletable := ' || deletable
		|| ', background_legend_image_filename := ' || COALESCE('''' || background_legend_image_filename || '''', 'NULL')
		|| ', projection := ' || COALESCE('''' || projection || '''', 'NULL')
		|| ', submenu := ' || COALESCE('''' || submenu || '''', 'NULL')
		|| ', menu := ' || COALESCE('''' || menu || '''', 'NULL')
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', open_in_mapview := ' || open_in_mapview
		|| ', provider := ' || COALESCE('''' || provider || '''', 'NULL')
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM analysis.layers;



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
		|| ', aggregation_type := ' || COALESCE('''' || aggregation_type || '''', 'NULL')
		|| ', aggregation_min := ' || COALESCE(TRIM(to_char(aggregation_min, '99999999D999999')), 'NULL')
		|| ', aggregation_max := ' || COALESCE(TRIM(to_char(aggregation_max, '99999999D999999')), 'NULL')
		|| ' );'  as inserts
	FROM analysis.timeseries_drawproperties;



	RETURN QUERY SELECT 'SELECT analysis.update_insert_chart_drawproperties('
		|| ' chart_type := ' || COALESCE('''' || chart_type || '''', 'NULL')
		|| ', chart_width := ' || chart_width
		|| ', chart_height := ' || chart_height
		|| ', chart_title_font_size := ' || chart_title_font_size
		|| ', chart_title_font_color := ' || COALESCE('''' || chart_title_font_color || '''', 'NULL')
		|| ', chart_subtitle_font_size := ' || chart_subtitle_font_size
		|| ', chart_subtitle_font_color := ' || COALESCE('''' || chart_subtitle_font_color || '''', 'NULL')
		|| ', yaxe1_font_size := ' || yaxe1_font_size
		|| ', yaxe2_font_size := ' || yaxe2_font_size
		|| ', legend_font_size := ' || legend_font_size
		|| ', legend_font_color := ' || COALESCE('''' || legend_font_color || '''', 'NULL')
		|| ', xaxe_font_size := ' || xaxe_font_size
		|| ', xaxe_font_color := ' || COALESCE('''' || xaxe_font_color || '''', 'NULL')
		|| ', yaxe3_font_size := ' || yaxe3_font_size
		|| ' );'  as inserts
	FROM analysis.chart_drawproperties;



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
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION products.export_all_data(boolean)
  OWNER TO estation;




CREATE OR REPLACE FUNCTION products.export_product_data(product_code character varying, full_copy boolean DEFAULT true)
  RETURNS SETOF text AS
$BODY$
DECLARE
	_productcode 			ALIAS FOR  $1;
	_full_copy 			ALIAS FOR  $2;
BEGIN


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
	WHERE products.product.productcode = _productcode;



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
	WHERE products.processing.process_id in (SELECT process_id FROM products.process_product WHERE products.process_product.productcode = _productcode);



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
	WHERE products.process_product.productcode = _productcode;



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
		|| ', aggregation_type := ' || COALESCE('''' || aggregation_type || '''', 'NULL')
		|| ', aggregation_min := ' || COALESCE(TRIM(to_char(aggregation_min, '99999999D999999')), 'NULL')
		|| ', aggregation_max := ' || COALESCE(TRIM(to_char(aggregation_max, '99999999D999999')), 'NULL')
		|| ' );'  as inserts
	FROM analysis.timeseries_drawproperties
	WHERE analysis.timeseries_drawproperties.productcode = _productcode;


END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION products.export_product_data(character varying, boolean)
  OWNER TO estation;
