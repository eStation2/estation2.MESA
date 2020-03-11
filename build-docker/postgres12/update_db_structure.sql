SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;


/**********************************************************
  BEGIN TABLE CREATION
 *********************************************************/
 
/**********************************************************
  For version 2.2.0
 *********************************************************/

-- DROP TABLE products.resolution CASCADE;
CREATE TABLE IF NOT EXISTS products.resolution
(
  resolutioncode character varying NOT NULL,
  descriptive_name character varying,
  description character varying,
  pixel_shift_long double precision,
  pixel_shift_lat double precision,
  CONSTRAINT resolution_pk PRIMARY KEY (resolutioncode)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE products.resolution
  OWNER TO estation;


-- DROP TABLE products.projection CASCADE;
CREATE TABLE IF NOT EXISTS products.projection
(
  proj_code character varying NOT NULL,
  descriptive_name character varying,
  description character varying,
  srs_wkt character varying,
  CONSTRAINT projection_pk PRIMARY KEY (proj_code)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE products.projection
  OWNER TO estation;

-- DROP TABLE products.bbox CASCADE;
CREATE TABLE IF NOT EXISTS products.bbox
(
  bboxcode character varying NOT NULL,
  descriptive_name character varying,
  defined_by character varying NOT NULL,
  upper_left_long double precision,
  upper_left_lat double precision,
  lower_right_long double precision,
  lower_right_lat double precision,
  predefined boolean NOT NULL DEFAULT false,
  CONSTRAINT bbox_pk PRIMARY KEY (bboxcode)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE products.bbox
  OWNER TO estation;

-- DROP TABLE products.mapset_new;
CREATE TABLE IF NOT EXISTS products.mapset_new
(
  mapsetcode character varying NOT NULL,
  descriptive_name character varying NOT NULL,
  description character varying,
  defined_by character varying NOT NULL, -- values: JRC or USER
  proj_code character varying,
  resolutioncode character varying,
  bboxcode character varying,
  pixel_size_x integer,
  pixel_size_y integer,
  footprint_image text,
  center_of_pixel boolean DEFAULT false,
  CONSTRAINT mapset_new_pk PRIMARY KEY (mapsetcode),
  CONSTRAINT mapset_new_bbox_fk FOREIGN KEY (bboxcode)
      REFERENCES products.bbox (bboxcode) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT mapset_new_projection_fk FOREIGN KEY (proj_code)
      REFERENCES products.projection (proj_code) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT mapset_new_resolution_fk FOREIGN KEY (resolutioncode)
      REFERENCES products.resolution (resolutioncode) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE SET NULL
)
WITH (
  OIDS=FALSE
);
ALTER TABLE products.mapset_new
  OWNER TO estation;
COMMENT ON COLUMN products.mapset_new.defined_by IS 'values: JRC or USER';


CREATE TABLE IF NOT EXISTS analysis.user_role
(
  role_id integer NOT NULL,
  role_name character varying(50) NOT NULL,
  defined_by character varying DEFAULT 'USER'::character varying,
  CONSTRAINT user_role_pkey PRIMARY KEY (role_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.user_role
  OWNER TO estation;


CREATE TABLE IF NOT EXISTS analysis.logos
(
  logo_id bigserial NOT NULL,
  logo_filename character varying(80),
  logo_description character varying(255),
  active boolean DEFAULT true,
  deletable boolean DEFAULT true,
  defined_by character varying DEFAULT 'USER'::character varying,
  isdefault boolean NOT NULL DEFAULT false,
  orderindex_defaults integer,
  CONSTRAINT logos_pkey PRIMARY KEY (logo_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.logos
  OWNER TO estation;



/**********************************************************
  For version 2.1.2
 *********************************************************/

-- DROP TABLE products.ecoagris;
CREATE TABLE IF NOT EXISTS products.ecoagris
(
  recordid serial NOT NULL,
  productcode character varying NOT NULL,
  subproductcode character varying NOT NULL,
  version character varying NOT NULL,
  mapsetcode character varying NOT NULL,
  product_descriptive_name character varying(255),
  product_description character varying,
  provider character varying,
  regionid character varying,
  regionlevel character varying,
  aggregation_type character varying DEFAULT 'mean'::character varying,
  aggregation_min double precision,
  aggregation_max double precision,
  product_dateformat character varying NOT NULL,
  product_date character varying,
  tsvalue double precision,
  CONSTRAINT ecoagris_pk PRIMARY KEY (recordid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE products.ecoagris
  OWNER TO estation;


-- DROP TABLE analysis.users;
CREATE TABLE IF NOT EXISTS analysis.users
(
  userid character varying(50) NOT NULL,
  username character varying(80) NOT NULL,
  password character varying(32),
  userlevel integer NOT NULL,
  email character varying(50),
  "timestamp" numeric(11,0),
  CONSTRAINT users_pkey PRIMARY KEY (userid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.users
  OWNER TO estation;



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



CREATE TABLE IF NOT EXISTS analysis.chart_drawproperties
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
  OIDS=FALSE
);
ALTER TABLE analysis.chart_drawproperties
  OWNER TO estation;



-- DROP TABLE analysis.map_templates;
CREATE TABLE IF NOT EXISTS analysis.map_templates
(
  templatename character varying(80) NOT NULL,
  userid character varying(50) NOT NULL,
  mapviewposition character varying(10),
  mapviewsize character varying(10),
  productcode character varying,
  subproductcode character varying,
  productversion character varying,
  mapsetcode character varying,
  legendid integer,
  legendlayout character varying(15) DEFAULT 'vertical'::character varying,
  legendobjposition character varying(10),
  showlegend boolean NOT NULL DEFAULT false,
  titleobjposition character varying(10),
  titleobjcontent text,
  disclaimerobjposition character varying(10),
  disclaimerobjcontent text,
  logosobjposition character varying(10),
  logosobjcontent text,
  showobjects boolean NOT NULL DEFAULT false,
  scalelineobjposition character varying(10),
  vectorlayers character varying(20),
  outmask boolean NOT NULL DEFAULT false,
  outmaskfeature text,
  auto_open boolean DEFAULT false,
  CONSTRAINT map_templates_pkey PRIMARY KEY (templatename, userid),
  CONSTRAINT user_map_templates_fkey FOREIGN KEY (userid)
      REFERENCES analysis.users (userid) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.map_templates
  OWNER TO estation;



-- DROP TABLE products.geoserver;
CREATE TABLE IF NOT EXISTS products.geoserver
(
  geoserver_id serial NOT NULL,
  productcode character varying NOT NULL,
  subproductcode character varying NOT NULL,
  version character varying NOT NULL,
  defined_by character varying NOT NULL,
  activated boolean NOT NULL DEFAULT false,
  startdate bigint,
  enddate bigint,
  CONSTRAINT geoserver_pk PRIMARY KEY (geoserver_id),
  CONSTRAINT product_geoserver_fk FOREIGN KEY (productcode, subproductcode, version)
      REFERENCES products.product (productcode, subproductcode, version) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE products.geoserver
  OWNER TO estation;
COMMENT ON TABLE products.geoserver
  IS 'Define which products/versions/subproducts have to be synchronized.';



-- DROP TABLE analysis.user_workspaces;
CREATE TABLE IF NOT EXISTS analysis.user_workspaces
(
  userid character varying(50) NOT NULL,
  workspaceid serial NOT NULL,
  workspacename character varying(80) NOT NULL,
  isdefault boolean NOT NULL DEFAULT false,
  pinned boolean NOT NULL DEFAULT false,
  shownewgraph boolean NOT NULL DEFAULT true,
  showbackgroundlayer boolean NOT NULL DEFAULT false,
  CONSTRAINT user_workspaces_pkey PRIMARY KEY (userid, workspaceid),
  CONSTRAINT user_workspaces_users_fkey FOREIGN KEY (userid)
      REFERENCES analysis.users (userid) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.user_workspaces
  OWNER TO estation;



-- DROP TABLE analysis.user_map_templates;
CREATE TABLE IF NOT EXISTS analysis.user_map_templates
(
  userid character varying(50) NOT NULL,
  workspaceid bigint NOT NULL,
  map_tpl_id serial NOT NULL,
  map_tpl_name character varying(80),
  istemplate boolean NOT NULL DEFAULT true,
  mapviewposition character varying(10),
  mapviewsize character varying(10),
  productcode character varying,
  subproductcode character varying,
  productversion character varying,
  mapsetcode character varying,
  legendid integer,
  legendlayout character varying(15) DEFAULT 'vertical'::character varying,
  legendobjposition character varying(10),
  showlegend boolean NOT NULL DEFAULT false,
  titleobjposition character varying(10),
  titleobjcontent text,
  disclaimerobjposition character varying(10),
  disclaimerobjcontent text,
  logosobjposition character varying(10),
  logosobjcontent text,
  showobjects boolean NOT NULL DEFAULT false,
  showtoolbar boolean NOT NULL DEFAULT true,
  showgraticule boolean NOT NULL DEFAULT false,
  scalelineobjposition character varying(10),
  vectorlayers character varying,
  outmask boolean NOT NULL DEFAULT false,
  outmaskfeature text,
  auto_open boolean DEFAULT false,
  zoomextent character varying,
  mapsize character varying,
  mapcenter character varying,
  parent_tpl_id bigint,
  showtimeline boolean NOT NULL DEFAULT false,
  CONSTRAINT user_map_templates_pkey PRIMARY KEY (userid, workspaceid, map_tpl_id),
  CONSTRAINT user_map_templates_user_workspaces_fkey FOREIGN KEY (userid, workspaceid)
      REFERENCES analysis.user_workspaces (userid, workspaceid) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.user_map_templates
  OWNER TO estation;



-- DROP TABLE analysis.graph_drawproperties;
-- Replaces the old table chart_drawproperties, which is not deleted for backwards compatibility
CREATE TABLE IF NOT EXISTS analysis.graph_drawproperties
(
  graph_type character varying NOT NULL,
  graph_width integer,
  graph_height integer,
  graph_title character varying,  -- new
  graph_title_font_size integer,
  graph_title_font_color character varying,
  graph_subtitle character varying,  -- new
  graph_subtitle_font_size integer,
  graph_subtitle_font_color character varying,
  legend_position character varying,  -- new
  legend_font_size integer,
  legend_font_color character varying,
  xaxe_font_size integer,
  xaxe_font_color character varying,
  CONSTRAINT graph_drawproperties_pk PRIMARY KEY (graph_type)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.graph_drawproperties
  OWNER TO estation;



-- DROP TABLE analysis.graph_yaxes;
CREATE TABLE IF NOT EXISTS analysis.graph_yaxes
(
  yaxe_id character varying NOT NULL,
  title character varying,
  title_color character varying,
  title_font_size integer,
  min double precision,
  max double precision,
  unit character varying,
  opposite boolean NOT NULL DEFAULT false,
  aggregation_type character varying DEFAULT 'mean'::character varying,
  aggregation_min double precision,
  aggregation_max double precision,
  CONSTRAINT graph_yaxes_pk PRIMARY KEY (yaxe_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.graph_yaxes
  OWNER TO estation;




-- DROP TABLE analysis.timeseries_drawproperties_new;
CREATE TABLE IF NOT EXISTS analysis.timeseries_drawproperties_new
(
  productcode character varying NOT NULL,
  subproductcode character varying NOT NULL,
  version character varying NOT NULL,
  tsname_in_legend character varying,
  charttype character varying,
  linestyle character varying,
  linewidth integer,
  color character varying,
  yaxe_id character varying,
  CONSTRAINT timeseries_drawproperties_new_pk PRIMARY KEY (productcode, subproductcode, version),
  CONSTRAINT timeseries_drawproperties_new_yaxe_id_fkey FOREIGN KEY (yaxe_id)
      REFERENCES analysis.graph_yaxes (yaxe_id) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE RESTRICT
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.timeseries_drawproperties_new
  OWNER TO estation;




-- DROP TABLE analysis.user_graph_templates;
CREATE TABLE IF NOT EXISTS analysis.user_graph_templates
(
  userid character varying(50) NOT NULL,
  workspaceid bigint NOT NULL,
  graph_tpl_id serial NOT NULL,
  graph_tpl_name character varying(80),
  istemplate boolean NOT NULL DEFAULT true,
  graphviewposition character varying(10),
  graphviewsize character varying(10),
  graph_type character varying,
  selectedtimeseries character varying,
  yearts character varying,
  tsfromperiod character varying,
  tstoperiod character varying,
  yearstocompare character varying,
  tsfromseason character varying,
  tstoseason character varying,
  wkt_geom character varying,
  selectedregionname character varying,
  disclaimerobjposition character varying(10),
  disclaimerobjcontent text,
  logosobjposition character varying(10),
  logosobjcontent text,
  showobjects boolean NOT NULL DEFAULT false,
  showtoolbar boolean NOT NULL DEFAULT true,
  auto_open boolean DEFAULT false,
  parent_tpl_id bigint,
  CONSTRAINT user_graph_templates_pkey PRIMARY KEY (userid, workspaceid, graph_tpl_id),
  CONSTRAINT user_graph_templates_user_workspaces_fkey FOREIGN KEY (userid, workspaceid)
      REFERENCES analysis.user_workspaces (userid, workspaceid) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT user_graph_templates_graph_tpl_id_unique UNIQUE (graph_tpl_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.user_graph_templates
  OWNER TO estation;


-- DROP TABLE analysis.user_tpl_graph_drawproperties;
CREATE TABLE IF NOT EXISTS analysis.user_graph_tpl_drawproperties
(
  graph_tpl_id bigint NOT NULL,
  graph_type character varying NOT NULL,
  graph_width integer,
  graph_height integer,
  graph_title character varying,
  graph_title_font_size integer,
  graph_title_font_color character varying,
  graph_subtitle character varying,
  graph_subtitle_font_size integer,
  graph_subtitle_font_color character varying,
  legend_position character varying,
  legend_font_size integer,
  legend_font_color character varying,
  xaxe_font_size integer,
  xaxe_font_color character varying,
  CONSTRAINT user_graph_tpl_drawproperties_pk PRIMARY KEY (graph_tpl_id, graph_type),
  CONSTRAINT user_graph_tpl_drawproperties_user_graph_templates_fkey FOREIGN KEY (graph_tpl_id)
      REFERENCES analysis.user_graph_templates (graph_tpl_id) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.user_graph_tpl_drawproperties
  OWNER TO estation;


-- DROP TABLE analysis.user_tpl_graph_yaxes;
CREATE TABLE IF NOT EXISTS analysis.user_graph_tpl_yaxes
(
  graph_tpl_id bigint NOT NULL,
  yaxe_id character varying NOT NULL,
  title character varying,
  title_color character varying,
  title_font_size integer,
  min double precision,
  max double precision,
  unit character varying,
  opposite boolean NOT NULL DEFAULT false,
  aggregation_type character varying DEFAULT 'mean'::character varying,
  aggregation_min double precision,
  aggregation_max double precision,
  CONSTRAINT user_graph_tpl_yaxes_pk PRIMARY KEY (graph_tpl_id, yaxe_id),
  CONSTRAINT user_graph_tpl_yaxes_user_graph_templates_fkey FOREIGN KEY (graph_tpl_id)
      REFERENCES analysis.user_graph_templates (graph_tpl_id) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.user_graph_tpl_yaxes
  OWNER TO estation;



-- DROP TABLE analysis.user_tpl_timeseries_drawproperties;
CREATE TABLE IF NOT EXISTS analysis.user_graph_tpl_timeseries_drawproperties
(
  graph_tpl_id bigint NOT NULL,
  productcode character varying NOT NULL,
  subproductcode character varying NOT NULL,
  version character varying NOT NULL,
  tsname_in_legend character varying,
  charttype character varying,
  linestyle character varying,
  linewidth integer,
  color character varying,
  yaxe_id character varying,
  CONSTRAINT user_graph_tpl_timeseries_drawproperties_pk PRIMARY KEY (graph_tpl_id, productcode, subproductcode, version),
  CONSTRAINT user_graph_tpl_timeseries_drawproperties_graph_yaxes_fkey FOREIGN KEY (yaxe_id)
      REFERENCES analysis.graph_yaxes (yaxe_id) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT user_graph_tpl_ts_drawproperties_user_graph_tpl_fkey FOREIGN KEY (graph_tpl_id)
      REFERENCES analysis.user_graph_templates (graph_tpl_id) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analysis.user_graph_tpl_timeseries_drawproperties
  OWNER TO estation;


/**********************************************************
  END TABLE CREATION
 *********************************************************/


/***************************************************************************************
  BEGIN  ALTER TABLE adding columns, triggers and indexes (always after TABLE CREATION)
 **************************************************************************************/

/**********************************************************
  For version 2.2.0
 *********************************************************/

ALTER TABLE analysis.product_legend
DROP CONSTRAINT IF EXISTS product_legend_product_pkey,
ADD CONSTRAINT product_legend_product_pkey FOREIGN KEY (productcode, subproductcode, version)
      REFERENCES products.product (productcode, subproductcode, version) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE;
 
-- ALTER TABLE analysis.user_workspaces ADD COLUMN IF NOT EXISTS showindefault boolean DEFAULT FALSE;
-- ADD COLUMN IF NOT EXISTS does not work with the Postgresql version of MESA stations!
ALTER TABLE analysis.user_workspaces
ADD COLUMN  showindefault boolean DEFAULT FALSE;


-- DROP INDEX products.ingestion_mapsetcode_idx;

CREATE INDEX ingestion_mapsetcode_idx
  ON products.ingestion
  USING btree
  (mapsetcode COLLATE pg_catalog."default");

-- DROP INDEX products.mapsetcode_idx;

CREATE INDEX mapsetcode_idx
  ON products.mapset
  USING btree
  (mapsetcode COLLATE pg_catalog."default");


ALTER TABLE products.eumetcast_source
  ADD COLUMN  defined_by character varying;
  
  
CREATE OR REPLACE FUNCTION products.check_update_internet_source()
  RETURNS trigger AS
$BODY$
BEGIN
	NEW.update_datetime = now();

	RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE STRICT
  COST 100;
ALTER FUNCTION products.check_update_internet_source()
  OWNER TO estation;


CREATE TRIGGER update_internet_source
  BEFORE UPDATE
  ON products.internet_source
  FOR EACH ROW
  EXECUTE PROCEDURE products.check_update_internet_source();


ALTER TABLE products.process_product
DROP CONSTRAINT product_dependencies_fk,
ADD CONSTRAINT product_dependencies_fk
	FOREIGN KEY (productcode, subproductcode, version)
	REFERENCES products.product (productcode, subproductcode, version) MATCH SIMPLE
	ON UPDATE CASCADE ON DELETE CASCADE;
	
	
/**********************************************************
  For version 2.1.2
 *********************************************************/
 
ALTER TABLE products.internet_source ADD COLUMN  https_params character varying;

ALTER TABLE products.spirits ADD COLUMN out_data_type character varying;
ALTER TABLE products.spirits ADD COLUMN out_scale_factor double precision;
ALTER TABLE products.spirits ADD COLUMN out_offset double precision;

ALTER TABLE analysis.layers ALTER COLUMN polygon_fillcolor SET DEFAULT 'Transparent'::character varying;
ALTER TABLE analysis.layers ALTER COLUMN feature_highlight_fillcolor SET DEFAULT 'Transparent'::character varying;
   
   
ALTER TABLE products.product ADD COLUMN display_index integer;

ALTER TABLE products.thema ADD COLUMN activated boolean DEFAULT FALSE::boolean;

UPDATE products.thema set activated = FALSE;

-- Done: In Postinst of RPM, READ themaid from /eStation2/settings/system_settings.ini
-- systemsettings = functions.getSystemSettings()
-- themaid = systemsettings['thema'];
-- UPDATE products.thema set activated = TRUE WHERE thema_id = themaid;
-- SELECT * FROM products.set_thema(themaid);

ALTER TABLE analysis.timeseries_drawproperties ADD COLUMN aggregation_type character varying DEFAULT 'mean';
ALTER TABLE analysis.timeseries_drawproperties ADD COLUMN aggregation_min double precision;
ALTER TABLE analysis.timeseries_drawproperties ADD COLUMN aggregation_max double precision;


ALTER TABLE products.sub_datasource_description ADD COLUMN scale_type character varying DEFAULT 'linear';

ALTER TABLE analysis.users ADD COLUMN prefered_language character varying DEFAULT 'eng';

ALTER TABLE analysis.user_map_templates ADD COLUMN productdate character varying;


/**********************************************************
  For version 2.1.1
 *********************************************************/

ALTER TABLE analysis.legend ADD COLUMN defined_by character varying DEFAULT 'USER';
ALTER TABLE analysis.legend ALTER COLUMN step_type SET DEFAULT 'irregular';

ALTER TABLE analysis.chart_drawproperties ADD COLUMN yaxe4_font_size integer;
UPDATE analysis.chart_drawproperties SET yaxe4_font_size = 26;

ALTER TABLE analysis.map_templates ALTER COLUMN vectorlayers TYPE character varying;
ALTER TABLE analysis.map_templates ADD COLUMN zoomextent character varying;
ALTER TABLE analysis.map_templates ADD COLUMN mapsize character varying;
ALTER TABLE analysis.map_templates ADD COLUMN mapcenter character varying;

-- The following columns in the analysis.layers table are not added when going from version 2.0.3 to 2.1.x
-- These columns were added in version 2.0.4 and thus will give errors with the layers because of these missing columns.
ALTER TABLE analysis.layers ADD COLUMN defined_by character varying DEFAULT 'USER'::character varying;
ALTER TABLE analysis.layers ADD COLUMN open_in_mapview boolean DEFAULT false;
ALTER TABLE analysis.layers ADD COLUMN provider character varying;


/***************************************************************************************
  END  ALTER TABLE adding columns, triggers and indexes (always after TABLE CREATION)
 **************************************************************************************/
 
 

/**********************************************************
  BEGIN update insert all functions
 *********************************************************/

CREATE OR REPLACE FUNCTION analysis.update_insert_logo(
    logo_id integer,
    logo_filename character varying,
    logo_description character varying,
    active boolean,
    deletable boolean,
    defined_by character varying,
    isdefault boolean,
    orderindex_defaults integer)
  RETURNS boolean AS
$BODY$
	DECLARE
		_logo_id 		ALIAS FOR  $1;
		_logo_filename 		ALIAS FOR  $2;
		_logo_description 	ALIAS FOR  $3;
		_active 		ALIAS FOR  $4;
		_deletable 		ALIAS FOR  $5;
		_defined_by 		ALIAS FOR  $6;
		_isdefault 		ALIAS FOR  $7;
		_orderindex_defaults 	ALIAS FOR  $8;

	BEGIN
		PERFORM * FROM analysis.logos l WHERE l.logo_id = _logo_id;
		IF FOUND THEN
			UPDATE analysis.logos l
			SET logo_filename = TRIM(_logo_filename),
			    logo_description = TRIM(_logo_description),
			    active = _active,
			    deletable = _deletable,
			    defined_by = TRIM(_defined_by),
			    isdefault = _isdefault,
			    orderindex_defaults = _orderindex_defaults
			WHERE l.logo_id = _logo_id;
		ELSE
			INSERT INTO analysis.logos (logo_id, logo_filename, logo_description, active, deletable, defined_by, isdefault, orderindex_defaults)
			VALUES (_logo_id,
				TRIM(_logo_filename),
				TRIM(_logo_description),
				_active,
				_deletable,
				TRIM(_defined_by),
				_isdefault,
				_orderindex_defaults);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION analysis.update_insert_logo(integer, character varying, character varying, boolean, boolean, character varying, boolean, integer)
  OWNER TO estation;



CREATE OR REPLACE FUNCTION products.update_insert_mapset_new(
    mapsetcode character varying,
    descriptive_name character varying,
    description character varying,
    defined_by character varying,
    proj_code character varying,
    resolutioncode character varying,
    bboxcode character varying,
    pixel_size_x integer,
    pixel_size_y integer,
    footprint_image text,
    center_of_pixel boolean DEFAULT false,
    full_copy boolean DEFAULT false)
  RETURNS boolean AS
$BODY$
	DECLARE
		_mapsetcode 	  	ALIAS FOR  $1;
		_descriptive_name 	ALIAS FOR  $2;
		_description   		ALIAS FOR  $3;
		_defined_by  		ALIAS FOR  $4;
		_proj_code 	  	ALIAS FOR  $5;
		_resolutioncode 	ALIAS FOR  $6;
		_bboxcode  		ALIAS FOR  $7;
		_pixel_size_x  		ALIAS FOR  $8;
		_pixel_size_y 	  	ALIAS FOR  $9;
		_footprint_image   	ALIAS FOR  $10;
		_center_of_pixel   	ALIAS FOR  $11;
		_full_copy   		ALIAS FOR  $12;

	BEGIN
		IF _footprint_image = 'NULL' THEN
			_footprint_image = NULL;
		END IF;

		PERFORM * FROM products.mapset_new m WHERE m.mapsetcode = TRIM(_mapsetcode);

		IF FOUND THEN
			IF _full_copy THEN
				UPDATE products.mapset_new m
				SET defined_by = TRIM(_defined_by),
				    descriptive_name = TRIM(_descriptive_name),
				    description = TRIM(_description),
				    proj_code = TRIM(_proj_code),
				    resolutioncode = TRIM(_resolutioncode),
				    bboxcode = TRIM(_bboxcode),
				    pixel_size_x = _pixel_size_x,
				    pixel_size_y = _pixel_size_y,
				    footprint_image = TRIM(_footprint_image),
				    center_of_pixel = _center_of_pixel
				WHERE m.mapsetcode = TRIM(_mapsetcode);
			ELSE
				RAISE NOTICE 'Of existing JRC mapsets all columns can be updated by the User, do not overwrite!';
				/*
				UPDATE products.mapset_new m
				SET defined_by = TRIM(_defined_by),
				    descriptive_name = TRIM(_descriptive_name),
				    description = TRIM(_description),
				    proj_code = TRIM(_proj_code),
				    resolutioncode = TRIM(_resolutioncode),
				    bboxcode = TRIM(_bboxcode),
				    pixel_size_x = _pixel_size_x,
				    pixel_size_y = _pixel_size_y,
				    footprint_image = TRIM(_footprint_image),
				    center_of_pixel = TRIM(_center_of_pixel)
				WHERE m.mapsetcode = TRIM(_mapsetcode);
				*/
			END IF;
		ELSE
			INSERT INTO products.mapset_new (
				mapsetcode,
				descriptive_name,
				description,
				defined_by,
				proj_code,
				resolutioncode,
				bboxcode,
				pixel_size_x,
				pixel_size_y,
				footprint_image,
				center_of_pixel
			)
			VALUES (
				TRIM(_mapsetcode),
				TRIM(_descriptive_name),
				TRIM(_description),
				TRIM(_defined_by),
				TRIM(_proj_code),
				TRIM(_resolutioncode),
				TRIM(_bboxcode),
				_pixel_size_x,
				_pixel_size_y,
				_footprint_image,
				_center_of_pixel
			);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION products.update_insert_mapset_new(
    character varying,
    character varying,
    character varying,
    character varying,
    character varying,
    character varying,
    character varying,
    integer,
    integer,
    text,
    boolean,
    boolean
)
  OWNER TO estation;


CREATE OR REPLACE FUNCTION products.update_insert_projection(
    proj_code character varying,
    descriptive_name character varying,
    description character varying,
    srs_wkt character varying,
    full_copy boolean DEFAULT false)
  RETURNS boolean AS
$BODY$
	DECLARE
		_proj_code 	  	ALIAS FOR  $1;
		_descriptive_name 	ALIAS FOR  $2;
		_description   		ALIAS FOR  $3;
		_srs_wkt  		ALIAS FOR  $4;
		_full_copy   		ALIAS FOR  $5;

	BEGIN
		IF _srs_wkt = 'NULL' THEN
			_srs_wkt = NULL;
		END IF;

		PERFORM * FROM products.projection p WHERE p.proj_code = TRIM(_proj_code);

		IF FOUND THEN
			IF _full_copy THEN
				UPDATE products.projection p
				SET descriptive_name = TRIM(_descriptive_name),
				    description = TRIM(_description),
				    srs_wkt = _srs_wkt
				WHERE p.proj_code = TRIM(_proj_code);
			ELSE
				RAISE NOTICE 'Of existing JRC projections all columns can be updated by the User, do not overwrite!';
				/*
				UPDATE products.projection p
				SET descriptive_name = TRIM(_descriptive_name),
				    description = TRIM(_description),
				    srs_wkt = _srs_wkt
				WHERE p.proj_code = TRIM(_proj_code);
				*/
			END IF;
		ELSE
			INSERT INTO products.projection (
				proj_code,
				descriptive_name,
				description,
				srs_wkt
			)
			VALUES (
				TRIM(_proj_code),
				TRIM(_descriptive_name),
				TRIM(_description),
				TRIM(_srs_wkt)
			);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION products.update_insert_projection(
    character varying,
    character varying,
    character varying,
    character varying,
    boolean
)
  OWNER TO estation;


CREATE OR REPLACE FUNCTION products.update_insert_resolution(
    resolutioncode character varying,
    descriptive_name character varying,
    description character varying,
    pixel_shift_long double precision,
    pixel_shift_lat double precision,
    full_copy boolean DEFAULT false)
  RETURNS boolean AS
$BODY$
	DECLARE
		_resolutioncode	  	ALIAS FOR  $1;
		_descriptive_name 	ALIAS FOR  $2;
		_description   		ALIAS FOR  $3;
		_pixel_shift_long  	ALIAS FOR  $4;
		_pixel_shift_lat  	ALIAS FOR  $5;
		_full_copy   		ALIAS FOR  $6;

	BEGIN

		PERFORM * FROM products.resolution p WHERE p.resolutioncode = TRIM(_resolutioncode);

		IF FOUND THEN
			IF _full_copy THEN
				UPDATE products.resolution p
				SET descriptive_name = TRIM(_descriptive_name),
				    description = TRIM(_description),
				    pixel_shift_long = _pixel_shift_long,
				    pixel_shift_lat = _pixel_shift_lat
				WHERE p.resolutioncode = TRIM(_resolutioncode);
			ELSE
				RAISE NOTICE 'Of existing JRC resolutions all columns can be updated by the User, do not overwrite!';
				/*
				UPDATE products.resolution p
				SET descriptive_name = TRIM(_descriptive_name),
				    description = TRIM(_description),
				    pixel_shift_long = _pixel_shift_long,
				    pixel_shift_lat = _pixel_shift_lat
				WHERE p.resolutioncode = TRIM(_resolutioncode);
				*/
			END IF;
		ELSE
			INSERT INTO products.resolution (
				resolutioncode,
				descriptive_name,
				description,
				pixel_shift_long,
				pixel_shift_lat
			)
			VALUES (
				TRIM(_resolutioncode),
				TRIM(_descriptive_name),
				TRIM(_description),
				_pixel_shift_long,
				_pixel_shift_lat
			);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION products.update_insert_resolution(
    character varying,
    character varying,
    character varying,
    double precision,
    double precision,
    boolean
)
  OWNER TO estation;


CREATE OR REPLACE FUNCTION products.update_insert_bbox(
    bboxcode character varying,
    descriptive_name character varying,
    defined_by character varying,
    upper_left_long double precision,
    upper_left_lat double precision,
    lower_right_long double precision,
    lower_right_lat double precision,
    predefined boolean DEFAULT false,
    full_copy boolean DEFAULT false)
  RETURNS boolean AS
$BODY$
	DECLARE
		_bboxcode	  	ALIAS FOR  $1;
		_descriptive_name 	ALIAS FOR  $2;
		_defined_by   		ALIAS FOR  $3;
		_upper_left_long  	ALIAS FOR  $4;
		_upper_left_lat  	ALIAS FOR  $5;
		_lower_right_long  	ALIAS FOR  $6;
		_lower_right_lat  	ALIAS FOR  $7;
		_predefined   		ALIAS FOR  $8;
		_full_copy   		ALIAS FOR  $9;

	BEGIN

		PERFORM * FROM products.bbox p WHERE p.bboxcode = TRIM(_bboxcode);

		IF FOUND THEN
			IF _full_copy THEN
				UPDATE products.bbox bb
				SET descriptive_name = TRIM(_descriptive_name),
				    defined_by = TRIM(_defined_by),
				    upper_left_long = _upper_left_long,
				    upper_left_lat = _upper_left_lat,
				    lower_right_long = _lower_right_long,
				    lower_right_lat = _lower_right_lat,
				    predefined = _predefined
				WHERE bb.bboxcode = TRIM(_bboxcode);
			ELSE
				RAISE NOTICE 'Of existing JRC bboxes all columns can be updated by the User, do not overwrite!';
				/*
				UPDATE products.bbox bb
				SET descriptive_name = TRIM(_descriptive_name),
				    defined_by = TRIM(_defined_by),
				    upper_left_long = _upper_left_long,
				    upper_left_lat = _upper_left_lat,
				    lower_right_long = _lower_right_long,
				    lower_right_lat = _lower_right_lat,
				    predefined = _predefined
				WHERE bb.bboxcode = TRIM(_bboxcode);
				*/
			END IF;
		ELSE
			INSERT INTO products.bbox (
				bboxcode,
				descriptive_name,
				defined_by,
				upper_left_long,
				upper_left_lat,
				lower_right_long,
				lower_right_lat,
				predefined
			)
			VALUES (
				TRIM(_bboxcode),
				TRIM(_descriptive_name),
				TRIM(_defined_by),
				_upper_left_long,
				_upper_left_lat,
				_lower_right_long,
				_lower_right_lat,
				_predefined
			);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION products.update_insert_bbox(
    character varying,
    character varying,
    character varying,
    double precision,
    double precision,
    double precision,
    double precision,
    boolean ,
    boolean
)
  OWNER TO estation;



CREATE OR REPLACE FUNCTION products.update_insert_spirits(
    productcode character varying,
    subproductcode character varying,
    version character varying,
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
    activated boolean,
	  out_data_type character varying,
	  out_scale_factor double precision,
	  out_offset double precision
	)
  RETURNS boolean AS
$BODY$
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
		_out_data_type					ALIAS FOR  $17;
		_out_scale_factor				ALIAS FOR  $18;
		_out_offset						ALIAS FOR  $19;

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
				activated = _activated,
				out_data_type = TRIM(_out_data_type),
				out_scale_factor = _out_scale_factor,
				out_offset = _out_offset
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
										activated,
										out_data_type,
										out_scale_factor,
										out_offset
										)
			VALUES (TRIM(_productcode), TRIM(_subproductcode), TRIM(_version), TRIM(_mapsetcode), TRIM(_prod_values), TRIM(_flags), _data_ignore_value, _days, _start_date, _end_date, TRIM(_sensor_type),
					TRIM(_comment), TRIM(_sensor_filename_prefix), TRIM(_frequency_filename_prefix), TRIM(_product_anomaly_filename_prefix), _activated, TRIM(_out_data_type), _out_scale_factor, _out_offset);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION products.update_insert_spirits(character varying, character varying, character varying, character varying, character varying, character varying,
											  integer, integer, integer, integer, character varying, character varying, character varying, character varying,
											  character varying, boolean, character varying, double precision, double precision)
  OWNER TO estation;



CREATE OR REPLACE FUNCTION analysis.update_insert_legend(
    legend_id integer,
    legend_name character varying,
    step_type character varying,
    min_value double precision,
    max_value double precision,
    min_real_value character varying,
    max_real_value text,
    colorbar text,
    step double precision,
    step_range_from double precision,
    step_range_to double precision,
    unit character varying,
    defined_by character varying)
  RETURNS boolean AS
$BODY$
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
		_defined_by 		ALIAS FOR  $13;

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
			    unit = TRIM(_unit),
			    defined_by = TRIM(_defined_by)
			WHERE l.legend_id = _legend_id;
		ELSE
			INSERT INTO analysis.legend (legend_id, legend_name, step_type, min_value, max_value, min_real_value, max_real_value, colorbar, step, step_range_from, step_range_to, unit, defined_by)
			VALUES (_legend_id, TRIM(legend_name), TRIM(_step_type), _min_value, _max_value, TRIM(_min_real_value), TRIM(_max_real_value), TRIM(_colorbar), _step, _step_range_from, _step_range_to, _unit, _defined_by);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION analysis.update_insert_legend(integer, character varying, character varying, double precision, double precision, character varying, text, text, double precision, double precision, double precision, character varying, character varying)
  OWNER TO estation;




CREATE OR REPLACE FUNCTION analysis.copylegend(
    tocopylegendid bigint,
    newlegendname text)
  RETURNS integer AS
$BODY$
DECLARE
    newlegendid INT8;
BEGIN

  PERFORM nextval('analysis.legend_legend_id_seq');
  SELECT INTO newlegendid currval('analysis.legend_legend_id_seq');

  INSERT INTO analysis.legend (legend_id, legend_name, step_type, min_value, max_value, min_real_value, max_real_value, colorbar, step, step_range_from, step_range_to, unit )
  (SELECT newlegendid, legend_name, step_type, min_value, max_value, min_real_value, max_real_value, newlegendname, step, step_range_from, step_range_to, unit
   FROM analysis.legend
   WHERE legend_id = tocopylegendid );

  INSERT INTO analysis.legend_step ( legend_id, from_step, to_step, color_rgb, color_label, group_label )
  (SELECT newlegendid, from_step, to_step, color_rgb, color_label, group_label
   FROM analysis.legend_step
   WHERE legend_id = tocopylegendid);

  RETURN newlegendid;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION analysis.copylegend(bigint, text)
  OWNER TO estation;



-- Function: analysis.update_insert_chart_drawproperties(character varying, integer, integer, integer, character varying, integer, character varying, integer, integer, integer, character varying, integer, character varying, integer)

-- DROP FUNCTION analysis.update_insert_chart_drawproperties(character varying, integer, integer, integer, character varying, integer, character varying, integer, integer, integer, character varying, integer, character varying, integer);

CREATE OR REPLACE FUNCTION analysis.update_insert_chart_drawproperties(
    chart_type character varying,
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
    yaxe4_font_size integer)
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
	  _yaxe4_font_size 		ALIAS FOR  $15;

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
			    yaxe3_font_size = _yaxe3_font_size,
			    yaxe4_font_size = _yaxe4_font_size
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
				yaxe3_font_size,
				yaxe4_font_size
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
			    _yaxe3_font_size,
			    _yaxe4_font_size
			);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION analysis.update_insert_chart_drawproperties(character varying, integer, integer, integer, character varying, integer, character varying, integer, integer, integer, character varying, integer, character varying, integer, integer)
  OWNER TO estation;




DROP TRIGGER IF EXISTS update_product ON products.product;

-- CREATE OR REPLACE FUNCTION products.activate_deactivate_ingestion_pads_processing() RETURNS TRIGGER
--     LANGUAGE plpgsql STRICT
--     AS $$
-- BEGIN
-- 	IF TG_OP='UPDATE' THEN
-- 		IF (OLD.activated IS DISTINCT FROM NEW.activated AND NEW.product_type = 'Native') THEN
-- 			UPDATE products.ingestion i
-- 			SET activated = NEW.activated,
-- 				  enabled = NEW.activated
-- 			WHERE i.productcode = NEW.productcode
-- 			AND i.version = NEW.version
-- 			AND i.mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product
--                            WHERE thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
--                              AND activated = TRUE
--                              AND productcode = NEW.productcode
--                              AND version = NEW.version);
--
-- 			UPDATE products.process_product pp
-- 			SET activated = NEW.activated
-- 			WHERE pp.productcode = NEW.productcode
-- 			AND pp.version = NEW.version
-- 			AND pp.mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product
--                             WHERE thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
--                               AND activated = TRUE
--                               AND productcode = NEW.productcode
--                               AND version = NEW.version);
--
-- 			UPDATE products.processing p
-- 			SET activated = NEW.activated,
-- 				  enabled = NEW.activated
-- 			WHERE (p.process_id) in (SELECT process_id
--                                FROM products.process_product pp
--                                WHERE pp.type = 'INPUT'
--                                  AND pp.productcode = NEW.productcode
--                                  AND pp.version = NEW.version
--                                  AND pp.mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product
--                                                        WHERE thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
--                                                          AND activated = TRUE
--                                                          AND productcode = NEW.productcode
--                                                          AND version = NEW.version));
--
-- 			UPDATE products.product_acquisition_data_source pads
-- 			SET activated = NEW.activated
-- 			WHERE pads.productcode = NEW.productcode AND pads.version = NEW.version;
-- 		END IF;
-- 	END IF;
--
-- 	RETURN NEW;
-- END;
-- $$;
--
-- CREATE TRIGGER update_product
-- 	BEFORE UPDATE ON products.product
-- 	FOR EACH ROW
-- 	WHEN (OLD.activated IS DISTINCT FROM NEW.activated AND NEW.product_type = 'Native')
-- 	EXECUTE PROCEDURE products.activate_deactivate_ingestion_pads_processing();




-- Function: products.activate_deactivate_product_ingestion_pads_processing(character varying, character varying, boolean, boolean)
DROP FUNCTION products.activate_deactivate_product_ingestion_pads_processing(character varying, character varying, boolean, boolean);

CREATE OR REPLACE FUNCTION products.activate_deactivate_product_ingestion_pads_processing(
    productcode character varying,
    version character varying,
    activate boolean DEFAULT false,
    forse boolean DEFAULT false)
  RETURNS boolean AS
$BODY$
DECLARE
    _productcode  ALIAS FOR  $1;
    _version  ALIAS FOR  $2;
    _activate  ALIAS FOR  $3;
    _forse  ALIAS FOR  $4;
BEGIN
    IF TRIM(_productcode) != '' AND TRIM(_version) != '' THEN
        -- BEGIN
      IF _forse = TRUE THEN
    UPDATE products.product p
    SET activated = _activate
    WHERE p.product_type = 'Native'
    AND p.productcode = _productcode
    AND p.version = _version
    AND (p.productcode, p.version) IN (SELECT DISTINCT tp.productcode, tp.version FROM products.thema_product tp
                 WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                 -- AND activated = TRUE
                 AND tp.productcode = _productcode
                 AND tp.version = _version);

    UPDATE products.ingestion i
    SET activated = _activate,
        enabled = _activate
    WHERE i.productcode = _productcode
    AND i.version = _version
    AND i.mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product tp
                 WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                 -- AND activated = TRUE
                 AND tp.productcode = _productcode
                 AND tp.version = _version);

    UPDATE products.process_product pp
    SET activated = _activate
    WHERE pp.productcode = _productcode
    AND pp.version = _version
    AND pp.mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product tp
                  WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                  -- AND activated = TRUE
                  AND tp.productcode = _productcode
                  AND tp.version = _version);

    UPDATE products.processing p
    SET activated = _activate,
        enabled = _activate
    WHERE (p.process_id) in (SELECT distinct process_id
           FROM products.process_product pp
           WHERE pp.productcode = _productcode
         AND pp.version = _version)
     AND p.output_mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product tp
                     WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                    -- AND tp.activated = TRUE
                    AND tp.productcode = _productcode
                    AND tp.version = _version);

    /*
    -- wrong update query, updates all mapsets!
    UPDATE products.processing p
    SET activated = _activate,
        enabled = _activate
    WHERE (p.process_id) in (SELECT process_id
           FROM products.process_product pp
           WHERE pp.productcode = _productcode
         AND pp.version = _version
         AND pp.mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product tp
                       WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                     -- AND activated = TRUE
                     AND tp.productcode = _productcode
                     AND tp.version = _version));

    UPDATE products.product_acquisition_data_source pads
    SET activated = _activate
    WHERE pads.productcode = _productcode AND pads.version = _version
    AND (pads.productcode, pads.version) in (SELECT tp.productcode, tp.version
                         FROM products.thema_product tp
                         WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)); */


      ELSE
    UPDATE products.product p
    SET activated = _activate
    WHERE p.product_type = 'Native'
    AND p.productcode = _productcode
    AND p.version = _version
    AND (p.productcode, p.version) IN (SELECT DISTINCT tp.productcode, tp.version FROM products.thema_product tp
                 WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                 AND activated = TRUE
                 AND tp.productcode = _productcode
                 AND tp.version = _version);

    UPDATE products.ingestion i
    SET activated = _activate,
        enabled = _activate
    WHERE i.productcode = _productcode
    AND i.version = _version
    AND i.mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product tp
                 WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                 AND tp.activated = TRUE
                 AND tp.productcode = _productcode
                 AND tp.version = _version);

    UPDATE products.process_product pp
    SET activated = _activate
    WHERE pp.productcode = _productcode
    AND pp.version = _version
    AND pp.mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product tp
                  WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                  AND tp.activated = TRUE
                  AND tp.productcode = _productcode
                  AND tp.version = _version);

    UPDATE products.processing p
    SET activated = _activate,
        enabled = _activate
    WHERE (p.process_id) in (SELECT distinct process_id
           FROM products.process_product pp
           WHERE pp.productcode = _productcode
         AND pp.version = _version)
     AND p.output_mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product tp
                     WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                    AND tp.activated = TRUE
                    AND tp.productcode = _productcode
                    AND tp.version = _version);

    /*
    -- wrong update query, updates all mapsets!
    UPDATE products.processing p
    SET activated = _activate,
        enabled = _activate
    WHERE (p.process_id) in (SELECT process_id
           FROM products.process_product pp
           WHERE pp.productcode = _productcode
         AND pp.version = _version
         AND pp.mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product tp
                       WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                     AND tp.activated = TRUE
                     AND tp.productcode = _productcode
                     AND tp.version = _version));

    UPDATE products.product_acquisition_data_source pads
    SET activated = _activate
    WHERE pads.productcode = _productcode AND pads.version = _version
    AND (pads.productcode, pads.version) in (SELECT tp.productcode, tp.version
                         FROM products.thema_product tp
                         WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                         AND tp.activated = TRUE); */

      END IF;

      RETURN TRUE;

    ELSE
        RETURN FALSE;
    END IF;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE STRICT
  COST 100;
ALTER FUNCTION products.activate_deactivate_product_ingestion_pads_processing(character varying, character varying, boolean, boolean)
  OWNER TO estation;




CREATE OR REPLACE FUNCTION products.activate_deactivate_product(
    productcode character varying,
    version character varying,
    activate boolean DEFAULT false)
  RETURNS boolean AS
$BODY$
DECLARE
    _productcode  ALIAS FOR  $1;
    _version  ALIAS FOR  $2;
    _activate  ALIAS FOR  $3;
BEGIN
    IF TRIM(_productcode) != '' AND TRIM(_version) != '' THEN
        UPDATE products.product p
        SET activated = _activate
        WHERE p.product_type = 'Native'
        AND p.productcode = _productcode
        AND p.version = _version;


        UPDATE products.ingestion i
        SET activated = _activate,
            enabled = _activate
        WHERE i.productcode = _productcode
        AND i.version = _version
        AND i.mapsetcode IN (
          SELECT tp.mapsetcode FROM products.thema_product tp
          WHERE tp.thema_id IN (SELECT t.thema_id FROM products.thema t WHERE t.activated IS TRUE)
          AND tp.productcode = _productcode
          AND tp.version = _version);


        UPDATE products.process_product pp
        SET activated = _activate
        WHERE pp.productcode = _productcode
        AND pp.version = _version
        AND pp.mapsetcode IN (
          SELECT tp.mapsetcode FROM products.thema_product tp
          WHERE tp.thema_id IN (SELECT t.thema_id FROM products.thema t WHERE t.activated IS TRUE)
          AND tp.productcode = _productcode
          AND tp.version = _version);


        UPDATE products.processing p
        SET activated = _activate,
            enabled = _activate
        WHERE (p.process_id) in (SELECT distinct process_id
               FROM products.process_product pp
               WHERE pp.productcode = _productcode
             AND pp.version = _version)
         AND p.output_mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product tp
                         WHERE tp.thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                        AND tp.activated = TRUE
                        AND tp.productcode = _productcode
                        AND tp.version = _version);

        /* UPDATE products.processing p
        SET activated = _activate,
            enabled = _activate
        WHERE (p.process_id) in (SELECT process_id
                                 FROM products.process_product pp
                                 WHERE pp.productcode = _productcode
                                   AND pp.version = _version
                                   AND pp.mapsetcode IN (
                                      SELECT tp.mapsetcode FROM products.thema_product tp
                                      WHERE tp.thema_id IN (SELECT t.thema_id FROM products.thema t WHERE t.activated IS TRUE)
                                      AND tp.productcode = _productcode
                                      AND tp.version = _version));  */

        UPDATE products.product_acquisition_data_source pads
        SET activated = _activate
        WHERE pads.productcode = _productcode AND pads.version = _version;

      RETURN TRUE;

    ELSE
        RETURN FALSE;
    END IF;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE STRICT
  COST 100;
ALTER FUNCTION products.activate_deactivate_product(character varying, character varying, boolean)
  OWNER TO estation;



-- Function: products.set_thema(character varying)
-- DROP FUNCTION products.set_thema(character varying);
CREATE OR REPLACE FUNCTION products.set_thema(themaid character varying)
  RETURNS boolean AS
$BODY$
DECLARE
    themaid   ALIAS FOR  $1;
BEGIN
    IF themaid != '' THEN
        -- BEGIN
      UPDATE products.thema set activated = FALSE;
      UPDATE products.thema set activated = TRUE WHERE thema_id = themaid;

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

      /* UPDATE products.product_acquisition_data_source
      SET activated = FALSE
      WHERE defined_by = 'JRC'; */


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

          /* UPDATE products.product_acquisition_data_source pads
          SET activated = TRUE
          WHERE (pads.productcode, pads.version) in (SELECT productcode, version FROM products.thema_product WHERE thema_id = themaid AND activated = TRUE); */

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

          /* UPDATE products.product_acquisition_data_source pads
          SET activated = TRUE
          WHERE (pads.productcode, pads.version) in (SELECT productcode, version FROM products.thema_product WHERE thema_id != themaid AND activated = TRUE); */
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






CREATE OR REPLACE FUNCTION products.populate_geoserver(full_copy boolean DEFAULT false)
  RETURNS boolean AS
$BODY$
DECLARE

	_full_copy	ALIAS FOR  $1;

	prods CURSOR FOR SELECT productcode, subproductcode, version, defined_by, FALSE as activated, NULL as "startdate", NULL as "enddate"
		     FROM products.product
		     WHERE product_type != 'Native'
		     AND defined_by = 'JRC';

	prods_row RECORD;

	_productcode VARCHAR;
	_subproductcode VARCHAR;
	_version VARCHAR;
	_defined_by VARCHAR;
	_activated BOOLEAN;
	_startdate BIGINT;
	_enddate BIGINT;
BEGIN
	OPEN prods;

	LOOP
	FETCH prods INTO prods_row;
		EXIT WHEN NOT FOUND;

		_productcode = prods_row.productcode;
		_subproductcode = prods_row.subproductcode;
		_version  = prods_row.version;
		_defined_by  = prods_row.defined_by;
		_activated  = prods_row.activated;
		_startdate  = prods_row.startdate;
		_enddate = prods_row.enddate;

		PERFORM * FROM products.geoserver g
		WHERE g.productcode = TRIM(_productcode)
		  AND g.subproductcode = TRIM(_subproductcode)
		  AND g.version = TRIM(_version);

		IF FOUND THEN
			-- RAISE NOTICE 'START UPDATING Product';
			IF _full_copy THEN
				UPDATE products.geoserver g
				SET defined_by = TRIM(_defined_by),
				    activated = _activated,
				    startdate = _startdate,
				    enddate = _enddate
				WHERE g.productcode = TRIM(_productcode)
				  AND g.subproductcode = TRIM(_subproductcode)
				  AND g.version = TRIM(_version);
			ELSE
				UPDATE products.geoserver g
				SET defined_by = TRIM(_defined_by)
				 -- activated = _activated,
				 -- startdate = _startdate,
				 -- enddate = _enddate
				WHERE g.productcode = TRIM(_productcode)
				  AND g.subproductcode = TRIM(_subproductcode)
				  AND g.version = TRIM(_version);
			END IF;
			-- RAISE NOTICE 'Product updated';
		ELSE
			-- RAISE NOTICE 'START INSERTING Product';

			INSERT INTO products.geoserver (
				productcode,
				subproductcode,
				version,
				defined_by,
				activated,
				startdate,
				enddate
			)
			VALUES (
			  TRIM(_productcode),
			  TRIM(_subproductcode),
			  TRIM(_version),
			  TRIM(_defined_by),
			  _activated,
			  _startdate,
			  _enddate
			);

			-- RAISE NOTICE 'Product inserted';
		END IF;
	END LOOP;
	CLOSE prods;

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
ALTER FUNCTION products.populate_geoserver(boolean)
  OWNER TO estation;



/**********************************
 Functions of SCHEMA "products"
***********************************/
CREATE OR REPLACE FUNCTION products.update_insert_sub_datasource_description(
    productcode character varying,
    subproductcode character varying,
    version character varying,
    datasource_descr_id character varying,
    scale_factor double precision,
    scale_offset double precision,
    no_data double precision,
    data_type_id character varying,
    mask_min double precision,
    mask_max double precision,
    re_process character varying,
    re_extract character varying,
    scale_type character varying,
    full_copy boolean DEFAULT false)
  RETURNS boolean AS
$BODY$
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
		_scale_type  			ALIAS FOR  $13;
		_full_copy  			ALIAS FOR  $14;
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
					re_extract = TRIM(_re_extract),
					scale_type = TRIM(_scale_type)
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
			  re_extract,
			  scale_type
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
				TRIM(_re_extract),
				TRIM(_scale_type)
			);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION products.update_insert_sub_datasource_description(character varying, character varying, character varying, character varying, double precision, double precision, double precision, character varying, double precision, double precision, character varying, character varying, character varying, boolean)
  OWNER TO estation;


-- products.update_insert_internet_source for VERSION 2.1.2
CREATE OR REPLACE FUNCTION products.update_insert_internet_source(
    internet_id character varying,
    defined_by character varying,
    descriptive_name character varying,
    description character varying,
    modified_by character varying,
    update_datetime timestamp without time zone,
    url character varying,
    user_name character varying,
    password character varying,
    type character varying,
    include_files_expression character varying,
    files_filter_expression character varying,
    status boolean,
    pull_frequency integer,
    datasource_descr_id character varying,
    frequency_id character varying,
    start_date bigint,
    end_date bigint,
    https_params character varying,
    full_copy boolean DEFAULT false)
  RETURNS boolean AS
$BODY$
	DECLARE
		_internet_id 	  		ALIAS FOR  $1;
		_defined_by  			ALIAS FOR  $2;
		_descriptive_name 		ALIAS FOR  $3;
		_description   			ALIAS FOR  $4;
		_modified_by 	  		ALIAS FOR  $5;
		_update_datetime 	  	ALIAS FOR  $6;
		_url  				ALIAS FOR  $7;
		_user_name 			ALIAS FOR  $8;
		_password  			ALIAS FOR  $9;
		_type 	  			ALIAS FOR  $10;
		_include_files_expression 	ALIAS FOR  $11;
		_files_filter_expression  	ALIAS FOR  $12;
		_status 	  		ALIAS FOR  $13;
		_pull_frequency   		ALIAS FOR  $14;
		_datasource_descr_id   		ALIAS FOR  $15;
		_frequency_id   		ALIAS FOR  $16;
		_start_date   			ALIAS FOR  $17;
		_end_date   			ALIAS FOR  $18;
		_https_params   		ALIAS FOR  $19;
		_full_copy   			ALIAS FOR  $20;
	BEGIN
		PERFORM * FROM products.internet_source i WHERE i.internet_id = TRIM(_internet_id);

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
					end_date = _end_date,
					https_params = _https_params
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
					-- , https_params = _https_params
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
				end_date,
				https_params
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
				_end_date,
				TRIM(_https_params)
			);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION products.update_insert_internet_source(character varying, character varying, character varying, character varying, character varying, timestamp without time zone, character varying, character varying, character varying, character varying, character varying, character varying, boolean, integer, character varying, character varying, bigint, bigint, character varying, boolean)
  OWNER TO estation;



-- products.update_insert_internet_source for VERSION 2.1.1
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




-- Function: products.update_insert_product(character varying, character varying, character varying, character varying, boolean, character varying, character varying, character varying, character varying, character varying, character varying, character varying, double precision, double precision, bigint, double precision, double precision, character varying, character varying, boolean, character varying, boolean)

-- DROP FUNCTION products.update_insert_product(character varying, character varying, character varying, character varying, boolean, character varying, character varying, character varying, character varying, character varying, character varying, character varying, double precision, double precision, bigint, double precision, double precision, character varying, character varying, boolean, character varying, boolean);

CREATE OR REPLACE FUNCTION products.update_insert_product(productcode character varying, subproductcode character varying, version character varying, defined_by character varying, activated boolean,
							  category_id character varying, product_type character varying, descriptive_name character varying, description character varying,
							  provider character varying, frequency_id character varying, date_format character varying, scale_factor double precision, scale_offset double precision,
							  nodata bigint, mask_min double precision, mask_max double precision, unit character varying, data_type_id character varying,
							  masked boolean, timeseries_role character varying, display_index integer, full_copy boolean DEFAULT false)
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
		_display_index		ALIAS FOR  $22;
		_full_copy	  		ALIAS FOR  $23;

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
					timeseries_role = TRIM(_timeseries_role),
					display_index = _display_index
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
					timeseries_role = TRIM(_timeseries_role),
					display_index = _display_index
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
				timeseries_role,
				display_index
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
			  TRIM(_timeseries_role),
			  _display_index
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
ALTER FUNCTION products.update_insert_product(character varying, character varying, character varying, character varying, boolean, character varying, character varying, character varying, character varying, character varying, character varying, character varying, double precision, double precision, bigint, double precision, double precision, character varying, character varying, boolean, character varying, integer, boolean)
  OWNER TO estation;



/**********************************
 Functions of SCHEMA "analysis"
***********************************/

CREATE OR REPLACE FUNCTION products.update_insert_thema(thema_id character varying, description character varying, activated boolean)
  RETURNS boolean AS
$BODY$
	DECLARE
		_thema_id 	  ALIAS FOR  $1;
		_description  ALIAS FOR  $2;
		_activated  ALIAS FOR  $3;
	BEGIN
		PERFORM * FROM products.thema t WHERE t.thema_id = TRIM(_thema_id);
		IF FOUND THEN
			UPDATE products.thema t SET description = TRIM(_description) WHERE t.thema_id = TRIM(_thema_id);
		ELSE
			INSERT INTO products.thema (thema_id, description, activated) VALUES (TRIM(_thema_id), TRIM(_description), FALSE);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION products.update_insert_thema(character varying, character varying, boolean)
  OWNER TO estation;



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
			  -- layerid,
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
			    -- _layerid,
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



-- Function: analysis.update_insert_timeseries_drawproperties(character varying, character varying, character varying, character varying, character varying, double precision, double precision, boolean, character varying, character varying, character varying, integer, character varying, character varying, character varying)

-- DROP FUNCTION analysis.update_insert_timeseries_drawproperties(character varying, character varying, character varying, character varying, character varying, double precision, double precision, boolean, character varying, character varying, character varying, integer, character varying, character varying, character varying);

CREATE OR REPLACE FUNCTION analysis.update_insert_timeseries_drawproperties(productcode character varying, subproductcode character varying, version character varying, title character varying, unit character varying, min double precision, max double precision, oposite boolean, tsname_in_legend character varying, charttype character varying, linestyle character varying, linewidth integer, color character varying, yaxes_id character varying, title_color character varying, aggregation_type character varying, aggregation_min double precision, aggregation_max double precision)
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
ALTER FUNCTION analysis.update_insert_timeseries_drawproperties(character varying, character varying, character varying, character varying, character varying, double precision, double precision, boolean, character varying, character varying, character varying, integer, character varying, character varying, character varying, character varying, double precision, double precision)
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



-- Function: analysis.update_insert_timeseries_drawproperties_new(character varying, character varying, character varying, character varying, character varying, character varying, integer, character varying, character varying)

-- DROP FUNCTION analysis.update_insert_timeseries_drawproperties_new(character varying, character varying, character varying, character varying, character varying, character varying, integer, character varying, character varying);

CREATE OR REPLACE FUNCTION analysis.update_insert_timeseries_drawproperties_new(
    productcode character varying,
    subproductcode character varying,
    version character varying,
    tsname_in_legend character varying,
    charttype character varying,
    linestyle character varying,
    linewidth integer,
    color character varying,
    yaxe_id character varying)
  RETURNS boolean AS
$BODY$
	DECLARE
		_productcode 		ALIAS FOR  $1;
		_subproductcode 	ALIAS FOR  $2;
		_version 		ALIAS FOR  $3;
		_tsname_in_legend 	ALIAS FOR  $4;
		_charttype 		ALIAS FOR  $5;
		_linestyle 		ALIAS FOR  $6;
		_linewidth 		ALIAS FOR  $7;
		_color 			ALIAS FOR  $8;
		_yaxe_id 		ALIAS FOR  $9;


	BEGIN
		PERFORM * FROM analysis.timeseries_drawproperties_new tsdp WHERE tsdp.productcode = TRIM(_productcode) AND tsdp.subproductcode = TRIM(_subproductcode) AND tsdp.version = TRIM(_version);
		IF FOUND THEN
			UPDATE analysis.timeseries_drawproperties_new tsdp
			SET tsname_in_legend = TRIM(_tsname_in_legend),
    			charttype = TRIM(_charttype),
			    linestyle = TRIM(_linestyle),
			    linewidth = _linewidth,
			    color = TRIM(_color),
			    yaxe_id = TRIM(_yaxe_id)
			WHERE tsdp.productcode = TRIM(_productcode) AND tsdp.subproductcode = TRIM(_subproductcode) AND tsdp.version = TRIM(_version);
		ELSE
			INSERT INTO analysis.timeseries_drawproperties_new (productcode,
									subproductcode,
									version,
									tsname_in_legend,
									charttype,
									linestyle,
									linewidth,
									color,
									yaxe_id
									)
			VALUES (TRIM(_productcode),
				TRIM(_subproductcode),
				TRIM(_version),
				TRIM(_tsname_in_legend),
				TRIM(_charttype),
				TRIM(_linestyle),
				_linewidth,
				TRIM(_color),
				TRIM(_yaxe_id)
				);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION analysis.update_insert_timeseries_drawproperties_new(character varying, character varying, character varying, character varying, character varying, character varying, integer, character varying, character varying)
  OWNER TO estation;



-- Function: analysis.update_insert_graph_drawproperties(character varying, integer, integer, character varying, integer, character varying, character varying, integer, character varying, character varying, integer, character varying, integer, character varying)

-- DROP FUNCTION analysis.update_insert_graph_drawproperties(character varying, integer, integer, character varying, integer, character varying, character varying, integer, character varying, character varying, integer, character varying, integer, character varying);

CREATE OR REPLACE FUNCTION analysis.update_insert_graph_drawproperties(
    graph_type character varying,
    graph_width integer,
    graph_height integer,
    graph_title character varying,
    graph_title_font_size integer,
    graph_title_font_color character varying,
    graph_subtitle character varying,
    graph_subtitle_font_size integer,
    graph_subtitle_font_color character varying,
    legend_position character varying,
    legend_font_size integer,
    legend_font_color character varying,
    xaxe_font_size integer,
    xaxe_font_color character varying)
  RETURNS boolean AS
$BODY$
	DECLARE

	  _graph_type 					ALIAS FOR  $1;
	  _graph_width 					ALIAS FOR  $2;
	  _graph_height 				ALIAS FOR  $3;
	  _graph_title 					ALIAS FOR  $4;
	  _graph_title_font_size 		ALIAS FOR  $5;
	  _graph_title_font_color 		ALIAS FOR  $6;
	  _graph_subtitle 				ALIAS FOR  $7;
	  _graph_subtitle_font_size 	ALIAS FOR  $8;
	  _graph_subtitle_font_color 	ALIAS FOR  $9;
	  _legend_position 				ALIAS FOR  $10;
	  _legend_font_size 			ALIAS FOR  $11;
	  _legend_font_color 			ALIAS FOR  $12;
	  _xaxe_font_size 				ALIAS FOR  $13;
	  _xaxe_font_color 				ALIAS FOR  $14;


	BEGIN
		PERFORM * FROM analysis.graph_drawproperties gd WHERE gd.graph_type = _graph_type;
		IF FOUND THEN
			UPDATE analysis.graph_drawproperties cd
			SET graph_width = _graph_width,
			    graph_height = _graph_height,
				graph_title = TRIM(_graph_title),
			    graph_title_font_size = _graph_title_font_size,
			    graph_title_font_color = TRIM(_graph_title_font_color),
				graph_subtitle = TRIM(_graph_subtitle),
			    graph_subtitle_font_size = _graph_subtitle_font_size,
			    graph_subtitle_font_color = TRIM(_graph_subtitle_font_color),
				legend_position = TRIM(_legend_position),
			    legend_font_size = _legend_font_size,
			    legend_font_color = TRIM(_legend_font_color),
			    xaxe_font_size = _xaxe_font_size,
			    xaxe_font_color = TRIM(_xaxe_font_color)
			WHERE cd.graph_type = _graph_type;
		ELSE
			INSERT INTO analysis.graph_drawproperties (
			  graph_type,
			  graph_width,
			  graph_height,
			  graph_title,
			  graph_title_font_size,
			  graph_title_font_color,
			  graph_subtitle,
			  graph_subtitle_font_size,
			  graph_subtitle_font_color,
			  legend_position,
			  legend_font_size ,
			  legend_font_color,
			  xaxe_font_size ,
			  xaxe_font_color
			)
			VALUES (
			    TRIM(_graph_type),
			    _graph_width,
			    _graph_height,
				TRIM(_graph_title),
			    _graph_title_font_size,
			    TRIM(_graph_title_font_color),
				TRIM(_graph_subtitle),
			    _graph_subtitle_font_size,
			    TRIM(_graph_subtitle_font_color),
				TRIM(_legend_position),
			    _legend_font_size,
			    TRIM(_legend_font_color),
			    _xaxe_font_size,
			    TRIM(_xaxe_font_color)
			);
		END IF;
		RETURN TRUE;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION analysis.update_insert_graph_drawproperties(character varying, integer, integer, character varying, integer, character varying, character varying, integer, character varying, character varying, integer, character varying, integer, character varying)
  OWNER TO estation;



-- Function: analysis.update_insert_graph_yaxes(character varying, character varying, character varying, integer, double precision, double precision, character varying, boolean, character varying, double precision, double precision)

-- DROP FUNCTION analysis.update_insert_graph_yaxes(character varying, character varying, character varying, integer, double precision, double precision, character varying, boolean, character varying, double precision, double precision);

CREATE OR REPLACE FUNCTION analysis.update_insert_graph_yaxes(
    yaxe_id character varying,
    title character varying,
    title_color character varying,
    title_font_size integer,
    min double precision,
    max double precision,
    unit character varying,
    opposite boolean,
    aggregation_type character varying,
    aggregation_min double precision,
    aggregation_max double precision)
  RETURNS boolean AS
$BODY$
	DECLARE
		_yaxe_id 			ALIAS FOR  $1;
		_title 				ALIAS FOR  $2;
		_title_color 		ALIAS FOR  $3;
		_title_font_size 	ALIAS FOR  $4;
		_min 				ALIAS FOR  $5;
		_max 				ALIAS FOR  $6;
		_unit 				ALIAS FOR  $7;
		_opposite 			ALIAS FOR  $8;
		_aggregation_type	ALIAS FOR  $9;
		_aggregation_min	ALIAS FOR  $10;
		_aggregation_max	ALIAS FOR  $11;

	BEGIN
		PERFORM * FROM analysis.graph_yaxes gy WHERE gy.yaxe_id = TRIM(_yaxe_id);
		IF FOUND THEN
			UPDATE analysis.graph_yaxes gy
			SET title = TRIM(_title),
			    title_color = TRIM(_title_color),
				title_font_size = _title_font_size,
			    min = _min,
			    max = _max,
			    unit = TRIM(_unit),
			    opposite = _opposite,
			    aggregation_type = TRIM(_aggregation_type),
			    aggregation_min = _aggregation_min,
			    aggregation_max = _aggregation_max
			WHERE gy.yaxe_id = TRIM(_yaxe_id);
		ELSE
			INSERT INTO analysis.graph_yaxes (
				yaxe_id,
				title,
				title_color,
				title_font_size,
				min,
				max,
				unit,
				opposite,
				aggregation_type,
				aggregation_min,
				aggregation_max
				)
			VALUES (
				TRIM(_yaxe_id),
				TRIM(_title),
				TRIM(_title_color),
				_title_font_size,
				_min,
				_max,
				TRIM(_unit),
				_opposite,
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
ALTER FUNCTION analysis.update_insert_graph_yaxes(character varying, character varying, character varying, integer, double precision, double precision, character varying, boolean, character varying, double precision, double precision)
  OWNER TO estation;




/**********************************
 EXPORT DATA FUNCTIONS
***********************************/

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
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ' );'  as inserts
	FROM products.product_category;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_frequency('
		|| 'frequency_id := ''' || frequency_id || ''''
		|| ', time_unit := ''' || time_unit || ''''
		|| ', frequency := ' || frequency
		|| ', frequency_type := ' || COALESCE('''' || frequency_type || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ' );'  as inserts
	FROM products.frequency;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_date_format('
		|| 'date_format := ''' || date_format || ''''
		|| ', definition := ' || COALESCE('''' || definition || '''', 'NULL')
		|| ' );'  as inserts
	FROM products.date_format;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_data_type('
		|| 'data_type_id := ''' || data_type_id || ''''
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ' );'  as inserts
	FROM products.data_type;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_projection('
		|| 'proj_code := ''' || proj_code || ''''
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', srs_wkt := ' || COALESCE('''' || srs_wkt || '''', 'NULL')
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM products.projection;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);

	RETURN QUERY SELECT 'SELECT products.update_insert_resolution('
		|| 'resolutioncode := ''' || resolutioncode || ''''
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', pixel_shift_long := ' || pixel_shift_long
		|| ', pixel_shift_lat := ' || pixel_shift_lat
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM products.resolution;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);

	RETURN QUERY SELECT 'SELECT products.update_insert_bbox('
		|| 'bboxcode := ''' || bboxcode || ''''
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', defined_by := ''' || defined_by || ''''
		|| ', upper_left_long := ' || upper_left_long
		|| ', upper_left_lat := ' || upper_left_lat
		|| ', lower_right_long := ' || lower_right_long
		|| ', lower_right_lat := ' || lower_right_lat
		|| ', predefined := ' || predefined
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM products.bbox;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_mapset_new('
		|| 'mapsetcode := ''' || mapsetcode || ''''
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', defined_by := ''' || defined_by || ''''
		|| ', proj_code := ''' || proj_code || ''''
		|| ', resolutioncode := ''' || resolutioncode || ''''
		|| ', bboxcode := ''' || bboxcode || ''''
		|| ', pixel_size_x := ' || pixel_size_x
		|| ', pixel_size_y:= ' || pixel_size_y
		|| ', footprint_image := ''' || COALESCE(footprint_image, 'NULL') || ''''
		|| ', center_of_pixel:= ' || center_of_pixel
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM products.mapset_new
	WHERE defined_by = 'JRC';


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_mapset('
		|| 'mapsetcode := ''' || mapsetcode || ''''
		|| ', defined_by := ''' || defined_by || ''''
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
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


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_thema('
		|| 'thema_id := ''' || thema_id || ''''
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ' );'  as inserts
	FROM products.thema;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_product('
		|| '  productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', activated := ' || activated
		|| ', category_id := ' || COALESCE('''' || category_id || '''', 'NULL')
		|| ', product_type := ' || COALESCE('''' || product_type || '''', 'NULL')
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
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
		|| ', display_index := ' || COALESCE(TRIM(to_char(display_index, '99999999')), 'NULL')
		|| ', full_copy := ' || FALSE
		|| ' );'  as inserts
	FROM products.product
	WHERE defined_by = 'JRC'
	ORDER BY productcode, version;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_thema_product('
		|| 'thema_id := ''' || thema_id || ''''
		|| ', productcode := ''' || productcode || ''''
		|| ', version := ''' || version || ''''
		|| ', mapsetcode := ''' || mapsetcode || ''''
		|| ', activated := ' || activated
		|| ' );'  as inserts
	FROM products.thema_product tp
	WHERE (tp.productcode, tp.version) in (SELECT productcode, version FROM products.product WHERE defined_by = 'JRC')
	ORDER BY thema_id;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	-- insert into products.datasource_description (datasource_descr_id) select internet_id from products.internet_source where internet_id not in (select datasource_descr_id from products.datasource_description)

	RETURN QUERY SELECT 'SELECT products.update_insert_internet_source('
		|| 'internet_id := ''' || internet_id || ''''
		|| ', defined_by := ''' || defined_by || ''''
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
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
		|| ', https_params := ' || COALESCE('''' || https_params || '''', 'NULL')
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM products.internet_source
	WHERE defined_by = 'JRC';


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	-- insert into products.datasource_description (datasource_descr_id) select eumetcast_id from products.eumetcast_source where eumetcast_id not in (select datasource_descr_id from products.datasource_description)

	RETURN QUERY SELECT 'SELECT products.update_insert_eumetcast_source('
		|| '  eumetcast_id := ' || COALESCE('''' || eumetcast_id || '''', 'NULL')
		|| ', filter_expression_jrc := ' || COALESCE('''' || filter_expression_jrc || '''', 'NULL')
		|| ', collection_name := ' || COALESCE('''' || collection_name || '''', 'NULL')
		|| ', status := ' || status
		|| ', internal_identifier := ' || COALESCE('''' || internal_identifier || '''', 'NULL')
		|| ', collection_reference := ' || COALESCE('''' || collection_reference || '''', 'NULL')
		|| ', acronym := ' || COALESCE('''' || acronym || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
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
		|| ', online_resources := ' || COALESCE('''' || replace(replace(online_resources,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', distribution := ' || COALESCE('''' || distribution || '''', 'NULL')
		|| ', channels := ' || COALESCE('''' || channels || '''', 'NULL')
		|| ', data_access := ' || COALESCE('''' || replace(replace(data_access,'"',''''), '''', '''''') || '''', 'NULL')
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


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_product_acquisition_data_source('
		|| ' productcode := ''' || productcode || ''''
		|| ', subproductcode := ''' || subproductcode || ''''
		|| ', version := ''' || version || ''''
		|| ', data_source_id := ''' || data_source_id || ''''
		|| ', defined_by := ''' || defined_by || ''''
		|| ', type := ''' || type || ''''
		|| ', activated := ' || activated
		|| ', store_original_data := ' || store_original_data
		|| ', full_copy := ' || TRUE
		|| ' );'  as inserts
	FROM products.product_acquisition_data_source pads
	WHERE defined_by = 'JRC'
	AND (pads.productcode, pads.version, pads.subproductcode) in (SELECT productcode, version, subproductcode FROM products.product WHERE defined_by = 'JRC');


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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
		|| ', scale_type := ' || COALESCE('''' || scale_type || '''', 'NULL')
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM products.sub_datasource_description sdd
	WHERE (sdd.productcode, sdd.version, sdd.subproductcode) in (SELECT productcode, version, subproductcode FROM products.product WHERE defined_by = 'JRC')
	  AND (sdd.datasource_descr_id in (SELECT eumetcast_id FROM products.eumetcast_source)
	       OR sdd.datasource_descr_id in (SELECT internet_id FROM products.internet_source WHERE defined_by = 'JRC'));


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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
		|| ', full_copy := ' || FALSE
		|| ' );'  as inserts
	FROM products.ingestion i
	WHERE defined_by = 'JRC'
	AND (i.productcode, i.version, i.subproductcode) in (SELECT productcode, version, subproductcode FROM products.product WHERE defined_by = 'JRC');


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_processing('
		|| ' process_id := ' || process_id
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', output_mapsetcode := ' || COALESCE('''' || output_mapsetcode || '''', 'NULL')
		|| ', activated := ' || activated
		|| ', derivation_method := ' || COALESCE('''' || derivation_method || '''', 'NULL')
		|| ', algorithm := ' || COALESCE('''' || algorithm || '''', 'NULL')
		|| ', priority := ' || COALESCE('''' || priority || '''', 'NULL')
		|| ', enabled := ' || enabled
		|| ', full_copy := ' || FALSE
		|| ' );'  as inserts
	FROM products.processing
	WHERE defined_by = 'JRC';


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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
	FROM products.process_product pp
	WHERE process_id IN (SELECT process_id FROM products.processing WHERE defined_by = 'JRC')
	AND (pp.productcode, pp.version, pp.subproductcode) in (SELECT productcode, version, subproductcode FROM products.product WHERE defined_by = 'JRC');


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_i18n('
		|| ' label := ' || COALESCE('''' || label || '''', 'NULL')
		|| ', eng := ''' || COALESCE(replace(replace(eng,'"',''''), '''', ''''''), 'NULL') || ''''
		|| ', fra := ''' || COALESCE(replace(replace(fra,'"',''''), '''', ''''''), 'NULL') || ''''
		|| ', por := ''' || COALESCE(replace(replace(por,'"',''''), '''', ''''''), 'NULL') || ''''
		|| ', lang1 := ''' || COALESCE(replace(replace(lang1,'"',''''), '''', ''''''), 'NULL') || ''''
		|| ', lang2 := ''' || COALESCE(replace(replace(lang2,'"',''''), '''', ''''''), 'NULL') || ''''
		|| ', lang3 := ''' || COALESCE(replace(replace(lang3,'"',''''), '''', ''''''), 'NULL') || ''''
		|| ' );'  as inserts
	FROM analysis.i18n;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_languages('
		|| ' langcode := ' || COALESCE('''' || langcode || '''', 'NULL')
		|| ', langdescription := ' || COALESCE('''' || langdescription || '''', 'NULL')
		|| ', active := ' || active
		|| ' );'  as inserts
	FROM analysis.languages;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'PERFORM analysis.update_insert_logo('
		|| ' logo_id := ' || logo_id
		|| ', logo_filename := ' || COALESCE('''' || logo_filename || '''', 'NULL')
		|| ', logo_description := ' || COALESCE('''' || replace(replace(logo_description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', active :=  ' || active
		|| ', deletable :=  ' || deletable
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', isdefault :=  ' || isdefault
		|| ', orderindex_defaults := ' || COALESCE(TRIM(to_char(orderindex_defaults, '99999999')), 'NULL')
		|| ' );'  as inserts
	FROM analysis.logos
	WHERE logo_id < 100
	ORDER BY logo_id;

	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'PERFORM analysis.update_insert_legend('
		|| ' legend_id := ' || legend_id
		|| ', legend_name := ' || COALESCE('''' || replace(replace(legend_name,'"',''''), '''', '''''') || '''', 'NULL')
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
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ' );'  as inserts
	FROM analysis.legend
	WHERE legend_id < 400
	AND defined_by = 'JRC'
	ORDER BY legend_id;

	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_legend_step('
		|| ' legend_id := ' || legend_id
		|| ', from_step :=  ' || from_step
		|| ', to_step :=  ' || to_step
		|| ', color_rgb := ' || COALESCE('''' || color_rgb || '''', 'NULL')
		|| ', color_label := ' || COALESCE('''' || color_label || '''', 'NULL')
		|| ', group_label := ' || COALESCE('''' || group_label || '''', 'NULL')
		|| ' );'  as inserts
	FROM analysis.legend_step
	ORDER BY legend_id;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_product_legend('
		|| ' productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', legend_id := ' || legend_id
		|| ', default_legend := ' || default_legend
		|| ' );'  as inserts
	FROM analysis.product_legend pl
	WHERE (pl.productcode, pl.version, pl.subproductcode) in (SELECT productcode, version, subproductcode FROM products.product WHERE defined_by = 'JRC');


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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
		|| ', yaxe4_font_size := ' || yaxe4_font_size
		|| ' );'  as inserts
	FROM analysis.chart_drawproperties;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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
		|| ', out_data_type := ' || COALESCE('''' || out_data_type || '''', 'NULL')
		|| ', out_scale_factor := ' || COALESCE(TRIM(to_char(out_scale_factor, '99999999D999999')), 'NULL')
		|| ', out_offset := ' || COALESCE(TRIM(to_char(out_offset, '99999999D999999')), 'NULL')
		|| ' );'  as inserts
	FROM products.spirits;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'PERFORM analysis.update_insert_layers('
		|| ' layerid := ' || layerid
		|| ', layerlevel := ' || COALESCE('''' || layerlevel || '''', 'NULL')
		|| ', layername := ' || COALESCE('''' || layername || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
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
	FROM analysis.layers
	WHERE layerid < 100
	ORDER BY layerid;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_graph_yaxes('
		|| ' yaxe_id := ' || COALESCE('''' || yaxe_id || '''', 'NULL')
		|| ', title := ' || COALESCE('''' || title || '''', 'NULL')
		|| ', title_color := ' || COALESCE('''' || title_color || '''', 'NULL')
		|| ', title_font_size := ' || COALESCE(TRIM(to_char(title_font_size, '99999999')), 'NULL')
		|| ', min := ' || COALESCE(TRIM(to_char(min, '99999999D999999')), 'NULL')
		|| ', max := ' || COALESCE(TRIM(to_char(max, '99999999D999999')), 'NULL')
		|| ', unit := ' || COALESCE('''' || unit || '''', 'NULL')
		|| ', opposite := ' || opposite
		|| ', aggregation_type := ' || COALESCE('''' || aggregation_type || '''', 'NULL')
		|| ', aggregation_min := ' || COALESCE(TRIM(to_char(aggregation_min, '99999999D999999')), 'NULL')
		|| ', aggregation_max := ' || COALESCE(TRIM(to_char(aggregation_max, '99999999D999999')), 'NULL')
		|| ' );'  as inserts
	FROM analysis.graph_yaxes;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_timeseries_drawproperties_new('
		|| ' productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', tsname_in_legend := ' || COALESCE('''' || tsname_in_legend || '''', 'NULL')
		|| ', charttype := ' || COALESCE('''' || charttype || '''', 'NULL')
		|| ', linestyle := ' || COALESCE('''' || linestyle || '''', 'NULL')
		|| ', linewidth := ' || COALESCE(TRIM(to_char(linewidth, '99999999')), 'NULL')
		|| ', color := ' || COALESCE('''' || color || '''', 'NULL')
		|| ', yaxe_id := ' || COALESCE('''' || yaxe_id || '''', 'NULL')
		|| ' );'  as inserts
	FROM analysis.timeseries_drawproperties_new;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_graph_drawproperties('
		|| ' graph_type := ' || COALESCE('''' || graph_type || '''', 'NULL')
		|| ', graph_width := ' || graph_width
		|| ', graph_height := ' || graph_height
		|| ', graph_title := ' || COALESCE('''' || graph_title || '''', 'NULL')
		|| ', graph_title_font_size := ' || graph_title_font_size
		|| ', graph_title_font_color := ' || COALESCE('''' || graph_title_font_color || '''', 'NULL')
		|| ', graph_subtitle := ' || COALESCE('''' || graph_subtitle || '''', 'NULL')
		|| ', graph_subtitle_font_size := ' || graph_subtitle_font_size
		|| ', graph_subtitle_font_color := ' || COALESCE('''' || graph_subtitle_font_color || '''', 'NULL')
		|| ', legend_position := ' || COALESCE('''' || legend_position || '''', 'NULL')
		|| ', legend_font_size := ' || legend_font_size
		|| ', legend_font_color := ' || COALESCE('''' || legend_font_color || '''', 'NULL')
		|| ', xaxe_font_size := ' || xaxe_font_size
		|| ', xaxe_font_color := ' || COALESCE('''' || xaxe_font_color || '''', 'NULL')
		|| ' );'  as inserts
	FROM analysis.graph_drawproperties;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION products.export_jrc_data(boolean)
  OWNER TO estation;




-- Function: products.export_all_data(boolean)
-- DROP FUNCTION products.export_all_data(boolean);

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
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ' );'  as inserts
	FROM products.product_category;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_frequency('
		|| 'frequency_id := ''' || frequency_id || ''''
		|| ', time_unit := ''' || time_unit || ''''
		|| ', frequency := ' || frequency
		|| ', frequency_type := ' || COALESCE('''' || frequency_type || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ' );'  as inserts
	FROM products.frequency;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_date_format('
		|| 'date_format := ''' || date_format || ''''
		|| ', definition := ' || COALESCE('''' || definition || '''', 'NULL')
		|| ' );'  as inserts
	FROM products.date_format;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_data_type('
		|| 'data_type_id := ''' || data_type_id || ''''
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ' );'  as inserts
	FROM products.data_type;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_projection('
		|| 'proj_code := ''' || proj_code || ''''
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', srs_wkt := ' || COALESCE('''' || srs_wkt || '''', 'NULL')
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM products.projection;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);

	RETURN QUERY SELECT 'SELECT products.update_insert_resolution('
		|| 'resolutioncode := ''' || resolutioncode || ''''
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', pixel_shift_long := ' || pixel_shift_long
		|| ', pixel_shift_lat := ' || pixel_shift_lat
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM products.resolution;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);

	RETURN QUERY SELECT 'SELECT products.update_insert_bbox('
		|| 'bboxcode := ''' || bboxcode || ''''
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', defined_by := ''' || defined_by || ''''
		|| ', upper_left_long := ' || upper_left_long
		|| ', upper_left_lat := ' || upper_left_lat
		|| ', lower_right_long := ' || lower_right_long
		|| ', lower_right_lat := ' || lower_right_lat
		|| ', predefined := ' || predefined
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM products.bbox;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_mapset_new('
		|| 'mapsetcode := ''' || mapsetcode || ''''
		|| ', defined_by := ''' || defined_by || ''''
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', defined_by := ''' || defined_by || ''''
		|| ', proj_code := ''' || proj_code || ''''
		|| ', resolutioncode := ''' || resolutioncode || ''''
		|| ', bboxcode := ''' || bboxcode || ''''
		|| ', pixel_size_x := ' || pixel_size_x
		|| ', pixel_size_y:= ' || pixel_size_y
		|| ', footprint_image := ''' || COALESCE(footprint_image, 'NULL') || ''''
		|| ', center_of_pixel:= ' || center_of_pixel
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM products.mapset_new;

	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_mapset('
		|| 'mapsetcode := ''' || mapsetcode || ''''
		|| ', defined_by := ''' || defined_by || ''''
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
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


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_thema('
		|| 'thema_id := ''' || thema_id || ''''
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ' );'  as inserts
	FROM products.thema;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_product('
		|| '  productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', activated := ' || activated
		|| ', category_id := ' || COALESCE('''' || category_id || '''', 'NULL')
		|| ', product_type := ' || COALESCE('''' || product_type || '''', 'NULL')
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
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
		|| ', display_index := ' || COALESCE(TRIM(to_char(display_index, '99999999')), 'NULL')
		|| ', full_copy := ' || FALSE
		|| ' );'  as inserts
	FROM products.product
	ORDER BY productcode, version;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_thema_product('
		|| 'thema_id := ''' || thema_id || ''''
		|| ', productcode := ''' || productcode || ''''
		|| ', version := ''' || version || ''''
		|| ', mapsetcode := ''' || mapsetcode || ''''
		|| ', activated := ' || activated
		|| ' );'  as inserts
	FROM products.thema_product tp
	ORDER BY thema_id;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	-- insert into products.datasource_description (datasource_descr_id) select internet_id from products.internet_source where internet_id not in (select datasource_descr_id from products.datasource_description)

	RETURN QUERY SELECT 'SELECT products.update_insert_internet_source('
		|| 'internet_id := ''' || internet_id || ''''
		|| ', defined_by := ''' || defined_by || ''''
		|| ', descriptive_name := ' || COALESCE('''' || replace(replace(descriptive_name,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
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
		|| ', https_params := ' || COALESCE('''' || https_params || '''', 'NULL')
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM products.internet_source;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	-- insert into products.datasource_description (datasource_descr_id) select eumetcast_id from products.eumetcast_source where eumetcast_id not in (select datasource_descr_id from products.datasource_description)

	RETURN QUERY SELECT 'SELECT products.update_insert_eumetcast_source('
		|| '  eumetcast_id := ' || COALESCE('''' || eumetcast_id || '''', 'NULL')
		|| ', filter_expression_jrc := ' || COALESCE('''' || filter_expression_jrc || '''', 'NULL')
		|| ', collection_name := ' || COALESCE('''' || collection_name || '''', 'NULL')
		|| ', status := ' || status
		|| ', internal_identifier := ' || COALESCE('''' || internal_identifier || '''', 'NULL')
		|| ', collection_reference := ' || COALESCE('''' || collection_reference || '''', 'NULL')
		|| ', acronym := ' || COALESCE('''' || acronym || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
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
		|| ', online_resources := ' || COALESCE('''' || replace(replace(online_resources,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', distribution := ' || COALESCE('''' || distribution || '''', 'NULL')
		|| ', channels := ' || COALESCE('''' || channels || '''', 'NULL')
		|| ', data_access := ' || COALESCE('''' || replace(replace(data_access,'"',''''), '''', '''''') || '''', 'NULL')
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


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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
	  OR dd.datasource_descr_id in (SELECT internet_id FROM products.internet_source);


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_product_acquisition_data_source('
		|| ' productcode := ''' || productcode || ''''
		|| ', subproductcode := ''' || subproductcode || ''''
		|| ', version := ''' || version || ''''
		|| ', data_source_id := ''' || data_source_id || ''''
		|| ', defined_by := ''' || defined_by || ''''
		|| ', type := ''' || type || ''''
		|| ', activated := ' || activated
		|| ', store_original_data := ' || store_original_data
		|| ', full_copy := ' || TRUE
		|| ' );'  as inserts
	FROM products.product_acquisition_data_source pads
	WHERE (pads.productcode, pads.version, pads.subproductcode) in (SELECT productcode, version, subproductcode FROM products.product);


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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
		|| ', scale_type := ' || COALESCE('''' || scale_type || '''', 'NULL')
		|| ', full_copy := ' || _full_copy
		|| ' );'  as inserts
	FROM products.sub_datasource_description sdd
	WHERE (sdd.productcode, sdd.version, sdd.subproductcode) in (SELECT productcode, version, subproductcode FROM products.product)
	  AND (sdd.datasource_descr_id in (SELECT eumetcast_id FROM products.eumetcast_source)
	       OR sdd.datasource_descr_id in (SELECT internet_id FROM products.internet_source));


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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
		|| ', full_copy := ' || FALSE
		|| ' );'  as inserts
	FROM products.ingestion i
	WHERE (i.productcode, i.version, i.subproductcode) in (SELECT productcode, version, subproductcode FROM products.product);


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT products.update_insert_processing('
		|| ' process_id := ' || process_id
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', output_mapsetcode := ' || COALESCE('''' || output_mapsetcode || '''', 'NULL')
		|| ', activated := ' || activated
		|| ', derivation_method := ' || COALESCE('''' || derivation_method || '''', 'NULL')
		|| ', algorithm := ' || COALESCE('''' || algorithm || '''', 'NULL')
		|| ', priority := ' || COALESCE('''' || priority || '''', 'NULL')
		|| ', enabled := ' || enabled
		|| ', full_copy := ' || FALSE
		|| ' );'  as inserts
	FROM products.processing;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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
		|| ', full_copy := ' || FALSE
		|| ' );'  as inserts
	FROM products.process_product pp
	WHERE process_id IN (SELECT process_id FROM products.processing)
	AND (pp.productcode, pp.version, pp.subproductcode) in (SELECT productcode, version, subproductcode FROM products.product);


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_i18n('
		|| ' label := ' || COALESCE('''' || label || '''', 'NULL')
		|| ', eng := ''' || COALESCE(replace(replace(eng,'"',''''), '''', ''''''), 'NULL') || ''''
		|| ', fra := ''' || COALESCE(replace(replace(fra,'"',''''), '''', ''''''), 'NULL') || ''''
		|| ', por := ''' || COALESCE(replace(replace(por,'"',''''), '''', ''''''), 'NULL') || ''''
		|| ', lang1 := ''' || COALESCE(replace(replace(lang1,'"',''''), '''', ''''''), 'NULL') || ''''
		|| ', lang2 := ''' || COALESCE(replace(replace(lang2,'"',''''), '''', ''''''), 'NULL') || ''''
		|| ', lang3 := ''' || COALESCE(replace(replace(lang3,'"',''''), '''', ''''''), 'NULL') || ''''
		|| ' );'  as inserts
	FROM analysis.i18n;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_languages('
		|| ' langcode := ' || COALESCE('''' || langcode || '''', 'NULL')
		|| ', langdescription := ' || COALESCE('''' || langdescription || '''', 'NULL')
		|| ', active := ' || active
		|| ' );'  as inserts
	FROM analysis.languages;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'PERFORM analysis.update_insert_logo('
		|| ' logo_id := ' || logo_id
		|| ', logo_filename := ' || COALESCE('''' || logo_filename || '''', 'NULL')
		|| ', logo_description := ' || COALESCE('''' || replace(replace(logo_description,'"',''''), '''', '''''') || '''', 'NULL')
		|| ', active :=  ' || active
		|| ', deletable :=  ' || deletable
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ', isdefault :=  ' || isdefault
		|| ', orderindex_defaults := ' || COALESCE(TRIM(to_char(orderindex_defaults, '99999999')), 'NULL')
		|| ' );'  as inserts
	FROM analysis.logos
	WHERE logo_id < 100
	ORDER BY logo_id;

	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'PERFORM analysis.update_insert_legend('
		|| ' legend_id := ' || legend_id
		|| ', legend_name := ' || COALESCE('''' || replace(replace(legend_name,'"',''''), '''', '''''') || '''', 'NULL')
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
		|| ', defined_by := ' || COALESCE('''' || defined_by || '''', 'NULL')
		|| ' );'  as inserts
	FROM analysis.legend
	WHERE legend_id < 400
	ORDER BY legend_id;

	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_legend_step('
		|| ' legend_id := ' || legend_id
		|| ', from_step :=  ' || from_step
		|| ', to_step :=  ' || to_step
		|| ', color_rgb := ' || COALESCE('''' || color_rgb || '''', 'NULL')
		|| ', color_label := ' || COALESCE('''' || color_label || '''', 'NULL')
		|| ', group_label := ' || COALESCE('''' || group_label || '''', 'NULL')
		|| ' );'  as inserts
	FROM analysis.legend_step
	ORDER BY legend_id;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_product_legend('
		|| ' productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', legend_id := ' || legend_id
		|| ', default_legend := ' || default_legend
		|| ' );'  as inserts
	FROM analysis.product_legend pl
	WHERE (pl.productcode, pl.version, pl.subproductcode) in (SELECT productcode, version, subproductcode FROM products.product);


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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
		|| ', yaxe4_font_size := ' || yaxe4_font_size
		|| ' );'  as inserts
	FROM analysis.chart_drawproperties;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


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
		|| ', out_data_type := ' || COALESCE('''' || out_data_type || '''', 'NULL')
		|| ', out_scale_factor := ' || COALESCE(TRIM(to_char(out_scale_factor, '99999999D999999')), 'NULL')
		|| ', out_offset := ' || COALESCE(TRIM(to_char(out_offset, '99999999D999999')), 'NULL')
		|| ' );'  as inserts
	FROM products.spirits;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'PERFORM analysis.update_insert_layers('
		|| ' layerid := ' || layerid
		|| ', layerlevel := ' || COALESCE('''' || layerlevel || '''', 'NULL')
		|| ', layername := ' || COALESCE('''' || layername || '''', 'NULL')
		|| ', description := ' || COALESCE('''' || replace(replace(description,'"',''''), '''', '''''') || '''', 'NULL')
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
	FROM analysis.layers
	WHERE layerid < 100
	ORDER BY layerid;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_graph_yaxes('
		|| ' yaxe_id := ' || COALESCE('''' || yaxe_id || '''', 'NULL')
		|| ', title := ' || COALESCE('''' || title || '''', 'NULL')
		|| ', title_color := ' || COALESCE('''' || title_color || '''', 'NULL')
		|| ', title_font_size := ' || COALESCE(TRIM(to_char(title_font_size, '99999999')), 'NULL')
		|| ', min := ' || COALESCE(TRIM(to_char(min, '99999999D999999')), 'NULL')
		|| ', max := ' || COALESCE(TRIM(to_char(max, '99999999D999999')), 'NULL')
		|| ', unit := ' || COALESCE('''' || unit || '''', 'NULL')
		|| ', opposite := ' || opposite
		|| ', aggregation_type := ' || COALESCE('''' || aggregation_type || '''', 'NULL')
		|| ', aggregation_min := ' || COALESCE(TRIM(to_char(aggregation_min, '99999999D999999')), 'NULL')
		|| ', aggregation_max := ' || COALESCE(TRIM(to_char(aggregation_max, '99999999D999999')), 'NULL')
		|| ' );'  as inserts
	FROM analysis.graph_yaxes;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_timeseries_drawproperties_new('
		|| ' productcode := ' || COALESCE('''' || productcode || '''', 'NULL')
		|| ', subproductcode := ' || COALESCE('''' || subproductcode || '''', 'NULL')
		|| ', version := ' || COALESCE('''' || version || '''', 'NULL')
		|| ', tsname_in_legend := ' || COALESCE('''' || tsname_in_legend || '''', 'NULL')
		|| ', charttype := ' || COALESCE('''' || charttype || '''', 'NULL')
		|| ', linestyle := ' || COALESCE('''' || linestyle || '''', 'NULL')
		|| ', linewidth := ' || COALESCE(TRIM(to_char(linewidth, '99999999')), 'NULL')
		|| ', color := ' || COALESCE('''' || color || '''', 'NULL')
		|| ', yaxe_id := ' || COALESCE('''' || yaxe_id || '''', 'NULL')
		|| ' );'  as inserts
	FROM analysis.timeseries_drawproperties_new;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


	RETURN QUERY SELECT 'SELECT analysis.update_insert_graph_drawproperties('
		|| ' graph_type := ' || COALESCE('''' || graph_type || '''', 'NULL')
		|| ', graph_width := ' || graph_width
		|| ', graph_height := ' || graph_height
		|| ', graph_title := ' || COALESCE('''' || graph_title || '''', 'NULL')
		|| ', graph_title_font_size := ' || graph_title_font_size
		|| ', graph_title_font_color := ' || COALESCE('''' || graph_title_font_color || '''', 'NULL')
		|| ', graph_subtitle := ' || COALESCE('''' || graph_subtitle || '''', 'NULL')
		|| ', graph_subtitle_font_size := ' || graph_subtitle_font_size
		|| ', graph_subtitle_font_color := ' || COALESCE('''' || graph_subtitle_font_color || '''', 'NULL')
		|| ', legend_position := ' || COALESCE('''' || legend_position || '''', 'NULL')
		|| ', legend_font_size := ' || legend_font_size
		|| ', legend_font_color := ' || COALESCE('''' || legend_font_color || '''', 'NULL')
		|| ', xaxe_font_size := ' || xaxe_font_size
		|| ', xaxe_font_color := ' || COALESCE('''' || xaxe_font_color || '''', 'NULL')
		|| ' );'  as inserts
	FROM analysis.graph_drawproperties;


	RETURN QUERY SELECT chr(10);
	RETURN QUERY SELECT chr(10);


END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION products.export_all_data(boolean)
  OWNER TO estation;



/**********************************************************
  END update insert all functions
 *********************************************************/