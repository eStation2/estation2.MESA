
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


DO $$
DECLARE layer_id integer; 
BEGIN
	-- Save the latest layerid (it could be that the user installed the eStation-Apps-2.0.4 first and created a new layer
	-- before installing the eStation-Layers-2.0.4 package.
	
	select into layer_id nextval('analysis.layers_layerid_seq');
	
	ALTER SEQUENCE analysis.layers_layerid_seq RESTART WITH 1;
	
	PERFORM analysis.update_insert_layers( layerid := 1, layerlevel := 'congobasin0', layername := 'Border of Congo Oubangui Sangha basin', description := 'Border of Congo Oubangui Sangha basin', filename := 'waterbasins/CICOS_bassin_0.geojson', layerorderidx := 4, layertype := 'polygon', polygon_outlinecolor := '#000000', polygon_outlinewidth := 1, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'Nom', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'Congo Oubangui Sangha basin', menu := 'other', defined_by := 'JRC', open_in_mapview := false, provider := NULL, full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 2, layerlevel := 'congobasin1', layername := 'Large basin', description := 'Large basin', filename := 'waterbasins/CICOS_bassin_1.geojson', layerorderidx := 3, layertype := 'polygon', polygon_outlinecolor := '#000000', polygon_outlinewidth := 1, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'NOM', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'Congo Oubangui Sangha basin', menu := 'other', defined_by := 'JRC', open_in_mapview := false, provider := NULL, full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 3, layerlevel := 'congobasin2', layername := 'Sub basin', description := 'Sub basin', filename := 'waterbasins/CICOS_bassin_2.geojson', layerorderidx := 2, layertype := 'polygon', polygon_outlinecolor := '#000000', polygon_outlinewidth := 1, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'MAJ_NAME, BASIN, SUB_NAME', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'Congo Oubangui Sangha basin', menu := 'other', defined_by := 'JRC', open_in_mapview := false, provider := NULL, full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 4, layerlevel := 'congobasin3', layername := 'Sub sub basin', description := 'Sub sub basin', filename := 'waterbasins/CICOS_bassin_3.geojson', layerorderidx := 1, layertype := 'polygon', polygon_outlinecolor := '#000000', polygon_outlinewidth := 1, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'AF_BAS_ID', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'Congo Oubangui Sangha basin', menu := 'other', defined_by := 'JRC', open_in_mapview := false, provider := NULL, full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 5, layerlevel := 'africabasin2', layername := 'Africa basin level 2', description := 'Africa basin level 2', filename := 'hydrosheds/h1k_lev2.geojson', layerorderidx := 1, layertype := 'polygon', polygon_outlinecolor := '#000000', polygon_outlinewidth := 1, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'LEVEL2', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'HydroSHEDS', menu := 'other', defined_by := 'JRC', open_in_mapview := false, provider := NULL, full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 6, layerlevel := 'africabasin1', layername := 'Africa basin level 1', description := 'Africa basin level 1', filename := 'hydrosheds/h1k_lev1.geojson', layerorderidx := 1, layertype := 'polygon', polygon_outlinecolor := '#000000', polygon_outlinewidth := 1, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'LEVEL1', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'HydroSHEDS', menu := 'other', defined_by := 'JRC', open_in_mapview := false, provider := NULL, full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 7, layerlevel := 'africabasin3', layername := 'Africa basin level 3', description := 'Africa basin level 3', filename := 'hydrosheds/h1k_lev3.geojson', layerorderidx := 1, layertype := 'polygon', polygon_outlinecolor := '#000000', polygon_outlinewidth := 1, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'LEVEL3', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'HydroSHEDS', menu := 'other', defined_by := 'JRC', open_in_mapview := false, provider := NULL, full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 8, layerlevel := 'admin0', layername := 'IGAD level 0', description := 'IGAD level 0', filename := 'RIC_IGAD_0_g2015_2014.geojson', layerorderidx := 4, layertype := 'polygon', polygon_outlinecolor := '#319FD3', polygon_outlinewidth := 2, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADM0_NAME', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'IGAD MESA', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 9, layerlevel := 'admin2', layername := 'IGAD level 2', description := 'IGAD level 2', filename := 'RIC_IGAD_2_g2015_2014.geojson', layerorderidx := 2, layertype := 'polygon', polygon_outlinecolor := '#808080', polygon_outlinewidth := 1, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADM0_NAME, ADM1_NAME, ADM2_NAME', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'IGAD MESA', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 10, layerlevel := 'admin1', layername := 'IGAD level 1', description := 'IGAD level 1', filename := 'RIC_IGAD_1_g2015_2014.geojson', layerorderidx := 3, layertype := 'polygon', polygon_outlinecolor := '#ffcc00', polygon_outlinewidth := 2, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADM0_NAME, ADM1_NAME', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'IGAD MESA', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 11, layerlevel := 'admin00', layername := 'IGAD area', description := 'IGAD area', filename := 'RIC_IGAD_00_g2015_2014.geojson', layerorderidx := 5, layertype := 'polygon', polygon_outlinecolor := '#319FD3', polygon_outlinewidth := 2, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADMN00NAME', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'IGAD MESA', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 12, layerlevel := 'admin00', layername := 'UoG area', description := 'UoG area', filename := 'RIC_UOG_00_g2015_2014.geojson', layerorderidx := 5, layertype := 'polygon', polygon_outlinecolor := '#319FD3', polygon_outlinewidth := 2, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADM00_NAME', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'UoG', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 13, layerlevel := 'admin00', layername := 'AGRHYMET area', description := 'AGRHYMET area', filename := 'RIC_CRA_00_g2015_2014.geojson', layerorderidx := 5, layertype := 'polygon', polygon_outlinecolor := '#003366', polygon_outlinewidth := 2, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADMIN00_NA', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'AGRHYMET', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 14, layerlevel := 'admin00', layername := 'Africa area', description := 'Africa area', filename := 'AFR_00_g2015_2014.geojson', layerorderidx := 5, layertype := 'polygon', polygon_outlinecolor := '#FF9900', polygon_outlinewidth := 2, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADM00_NAME', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#0000FF', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'Africa', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 15, layerlevel := 'admin00', layername := 'ICPAC area', description := 'ICPAC area', filename := 'RIC_ICPAC_00_g2015_2014.geojson', layerorderidx := 5, layertype := 'polygon', polygon_outlinecolor := '#000000', polygon_outlinewidth := 2, polygon_fillcolor := 'Transparent', polygon_fillopacity := 100, feature_display_column := 'ADM00_NAME', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := '', projection := NULL, submenu := 'ICPAC', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 16, layerlevel := 'admin00', layername := 'BDMS area', description := 'BDMS area', filename := 'RIC_BDMS_00_g2015_2014.geojson', layerorderidx := 5, layertype := 'polygon', polygon_outlinecolor := '#319FD3', polygon_outlinewidth := 2, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADM00_NAME', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'BDMS', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 17, layerlevel := 'admin00', layername := 'MOI area', description := 'MOI area', filename := 'RIC_MOI_00_g2015_2014.geojson', layerorderidx := 5, layertype := 'polygon', polygon_outlinecolor := '#319FD3', polygon_outlinewidth := 2, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADMIN00_NA', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'MOI', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 18, layerlevel := 'admin00', layername := 'CICOS area', description := 'CICOS area', filename := 'RIC_CICOS_00_g2015_2014.geojson', layerorderidx := 5, layertype := 'polygon', polygon_outlinecolor := '#319FD3', polygon_outlinewidth := 2, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADM00_NA', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'CICOS', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	
	ALTER SEQUENCE analysis.layers_layerid_seq RESTART WITH 39;

	PERFORM analysis.update_insert_layers( layerid := 39, layerlevel := 'fishingareas', layername := 'Fishing Areas', description := 'Fishing Areas', filename := 'AFR_MARINE/AFR_FAO_FISHING_AREA.geojson', layerorderidx := 1, layertype := 'polygon', polygon_outlinecolor := '#000000', polygon_outlinewidth := 1, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'F_LEVEL, F_CODE, OCEAN', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := NULL, menu := 'marine', defined_by := 'JRC', open_in_mapview := false, provider := NULL, full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 40, layerlevel := 'admin0', layername := 'ICPAC level 0', description := 'ICPAC level 0', filename := 'RIC_ICPAC_0_g2015_2014a.geojson', layerorderidx := 4, layertype := 'polygon', polygon_outlinecolor := '#319FD3', polygon_outlinewidth := 2, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADM0_NAME', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'ICPAC', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 41, layerlevel := 'admin1', layername := 'ICPAC level 1', description := 'ICPAC level 1', filename := 'RIC_ICPAC_1_g2015_2014a.geojson', layerorderidx := 3, layertype := 'polygon', polygon_outlinecolor := '#ffcc00', polygon_outlinewidth := 2, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADM0_NAME, ADM1_NAME', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'ICPAC', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	PERFORM analysis.update_insert_layers( layerid := 42, layerlevel := 'admin2', layername := 'ICPAC level 2', description := 'ICPAC level 2', filename := 'RIC_ICPAC_2_g2015_2014a.geojson', layerorderidx := 2, layertype := 'polygon', polygon_outlinecolor := '#808080', polygon_outlinewidth := 1, polygon_fillcolor := 'Transparent', polygon_fillopacity := 1, feature_display_column := 'ADM0_NAME, ADM1_NAME, ADM2_NAME', feature_highlight_outlinecolor := '#319FD3', feature_highlight_outlinewidth := 2, feature_highlight_fillcolor := '#319FD3', feature_highlight_fillopacity := 10, feature_selected_outlinecolor := '#FF0000', feature_selected_outlinewidth := 2, enabled := true, deletable := false, background_legend_image_filename := NULL, projection := NULL, submenu := 'ICPAC', menu := 'border', defined_by := 'JRC', open_in_mapview := false, provider := 'FAO Gaul 2015', full_copy := false );
	
	-- ALTER SEQUENCE analysis.layers_layerid_seq RESTART WITH 100;
	
	IF layer_id >= 100 THEN
		PERFORM setval('analysis.layers_layerid_seq', layer_id);
		-- raise notice 'Sequence higher then 100 so the user created a new layer with layer_id: %', layer_id;
	ELSE
		ALTER SEQUENCE analysis.layers_layerid_seq RESTART WITH 100;		
		-- raise notice 'layer_id set to: %', 100;
	END IF;
END $$;	


