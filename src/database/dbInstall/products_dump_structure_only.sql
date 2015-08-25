--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.4
-- Dumped by pg_dump version 9.3.4
-- Started on 2015-08-19 18:58:59 CEST

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

SET search_path = products, pg_catalog;

--
-- TOC entry 210 (class 1255 OID 17266)
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
-- TOC entry 211 (class 1255 OID 17267)
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
-- TOC entry 212 (class 1255 OID 18427)
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
			SET activated = FALSE 
			WHERE defined_by = 'JRC';

			UPDATE products.processing
			SET activated = FALSE 
			WHERE defined_by = 'JRC';

			UPDATE products.process_product pp
			SET activated = FALSE 
			WHERE (pp.process_id) in (SELECT process_id FROM products.processing WHERE defined_by = 'JRC'); 

									
			UPDATE products.product p
			SET activated = TRUE 
			WHERE p.product_type = 'Native'
			  AND (p.productcode, p.version) in (SELECT productcode, version FROM products.thema_product WHERE thema_id = themaid);
			
			UPDATE products.ingestion i
			SET activated = TRUE 
			WHERE (i.productcode, i.version, i.mapsetcode) in (SELECT productcode, version, mapsetcode FROM products.thema_product WHERE thema_id = themaid); 

			UPDATE products.process_product pp
			SET activated = TRUE 
			WHERE (pp.productcode, pp.version, pp.mapsetcode) in (SELECT productcode, version, mapsetcode FROM products.thema_product WHERE thema_id = themaid); 

			UPDATE products.processing p
			SET activated = TRUE 
			WHERE (p.process_id) in (SELECT process_id 
						 FROM products.process_product pp
						 WHERE pp.type = 'INPUT' 
						   AND (pp.productcode, pp.version, pp.mapsetcode) in (SELECT productcode, version, mapsetcode FROM products.thema_product WHERE thema_id = themaid)); 

			-- COMMIT;
		
		-- EXCEPTION WHEN data_exception THEN RETURN FALSE;
				

			-- COMMIT;
			RETURN TRUE;	
		-- END;
	
	ELSE
		RETURN FALSE;
	END IF;
	
END;
$_$;


ALTER FUNCTION products.set_thema(themaid character varying) OWNER TO estation;

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

SET default_with_oids = true;

--
-- TOC entry 174 (class 1259 OID 17277)
-- Name: layers; Type: TABLE; Schema: analysis; Owner: estation; Tablespace: 
--

CREATE TABLE layers (
    layerid bigint NOT NULL,
    code character varying(80) NOT NULL,
    label character varying(255),
    infotext text,
    initstatus character varying(80),
    layerpath character varying(255),
    filename character varying(80),
    projection character varying(80),
    datatype character varying(80) DEFAULT 'polygon'::character varying,
    default_drawproperties text DEFAULT '<drawproperties><polygonfillcolor>transparent</polygonfillcolor><polygonoutlinecolor>0 0 0</polygonoutlinecolor><polygonfillopacity>100</polygonfillopacity></drawproperties>'::text,
    enabled boolean DEFAULT true,
    deletable boolean DEFAULT true,
    pointdata_column character varying(255),
    background_legend_image_name character varying(255),
    background_legend_image oid
);


ALTER TABLE analysis.layers OWNER TO estation;

--
-- TOC entry 175 (class 1259 OID 17287)
-- Name: layers_layerid_seq; Type: SEQUENCE; Schema: analysis; Owner: estation
--

CREATE SEQUENCE layers_layerid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE analysis.layers_layerid_seq OWNER TO estation;

--
-- TOC entry 2198 (class 0 OID 0)
-- Dependencies: 175
-- Name: layers_layerid_seq; Type: SEQUENCE OWNED BY; Schema: analysis; Owner: estation
--

ALTER SEQUENCE layers_layerid_seq OWNED BY layers.layerid;


SET default_with_oids = false;

--
-- TOC entry 176 (class 1259 OID 17289)
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
-- TOC entry 177 (class 1259 OID 17295)
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
-- TOC entry 2199 (class 0 OID 0)
-- Dependencies: 177
-- Name: legend_legend_id_seq; Type: SEQUENCE OWNED BY; Schema: analysis; Owner: estation
--

ALTER SEQUENCE legend_legend_id_seq OWNED BY legend.legend_id;


--
-- TOC entry 178 (class 1259 OID 17297)
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
-- TOC entry 2200 (class 0 OID 0)
-- Dependencies: 178
-- Name: COLUMN legend_step.color_rgb; Type: COMMENT; Schema: analysis; Owner: estation
--

COMMENT ON COLUMN legend_step.color_rgb IS 'a string of 3 bytes, in decimal format, comma separated, eg. 128, 36, 64';


--
-- TOC entry 179 (class 1259 OID 17303)
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

SET default_with_oids = true;

--
-- TOC entry 194 (class 1259 OID 18354)
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
    yaxes_id character varying
);


ALTER TABLE analysis.timeseries_drawproperties OWNER TO estation;

SET search_path = products, pg_catalog;

SET default_with_oids = false;

--
-- TOC entry 180 (class 1259 OID 17310)
-- Name: data_type; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE data_type (
    data_type_id character varying NOT NULL,
    description character varying NOT NULL
);


ALTER TABLE products.data_type OWNER TO estation;

--
-- TOC entry 181 (class 1259 OID 17316)
-- Name: datasource_description; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE datasource_description (
    datasource_descr_id character varying NOT NULL,
    format_type character varying,
    file_extension character varying,
    delimiter character varying,
    date_type character varying NOT NULL,
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
    native_mapset character varying,
    CONSTRAINT check_mapset_chk CHECK (check_mapset(native_mapset))
);


ALTER TABLE products.datasource_description OWNER TO estation;

--
-- TOC entry 2201 (class 0 OID 0)
-- Dependencies: 181
-- Name: COLUMN datasource_description.format_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.format_type IS 'Values:
- DELIMITED
- FIXED';


--
-- TOC entry 2202 (class 0 OID 0)
-- Dependencies: 181
-- Name: COLUMN datasource_description.date_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.date_type IS 'A string, case insensitive, in YYYYMMDD, YYYYMMDDHHMM,YYYY,MMDD,HHMM. HHMM (may be used for MSG 15 minutes synthesis). This list may change with the project life. It is maintained by JRC';


--
-- TOC entry 2203 (class 0 OID 0)
-- Dependencies: 181
-- Name: COLUMN datasource_description.product_identifier; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.product_identifier IS 'Comma-separated list of strings present in the filename that form the Product Identifier';


--
-- TOC entry 2204 (class 0 OID 0)
-- Dependencies: 181
-- Name: COLUMN datasource_description.prod_id_position; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.prod_id_position IS 'In case of:
FIXED - integer value of the start position of the Product Identifier

DELIMITED - comma-separated integers indicating the delimiter positions of the Product Identifier to concatinate.';


--
-- TOC entry 2205 (class 0 OID 0)
-- Dependencies: 181
-- Name: COLUMN datasource_description.prod_id_length; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.prod_id_length IS 'In case of FIXED format this field indicates the string length to take starting from the prod_id_position.';


--
-- TOC entry 2206 (class 0 OID 0)
-- Dependencies: 181
-- Name: COLUMN datasource_description.area_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.area_type IS 'Values:
- REGION
- SEGMENT
- TILE
- GLOBAL';


--
-- TOC entry 2207 (class 0 OID 0)
-- Dependencies: 181
-- Name: COLUMN datasource_description.area_position; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.area_position IS 'In case of:
FIXED - integer value of the start position of the Area

DELIMITED - comma-separated integers indicating the delimiter positions of the Area to concatinate.';


--
-- TOC entry 2208 (class 0 OID 0)
-- Dependencies: 181
-- Name: COLUMN datasource_description.area_length; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.area_length IS 'In case of FIXED format this field indicates the string length to take starting from the area_position.';


--
-- TOC entry 2209 (class 0 OID 0)
-- Dependencies: 181
-- Name: COLUMN datasource_description.product_release; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.product_release IS 'String indicating the Product Release present in the filename.';


--
-- TOC entry 2210 (class 0 OID 0)
-- Dependencies: 181
-- Name: COLUMN datasource_description.release_position; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.release_position IS 'In case of:
FIXED - integer value of the start position of the Release

DELIMITED - comma-separated integers indicating the delimiter positions of the Release to concatinate.';


--
-- TOC entry 2211 (class 0 OID 0)
-- Dependencies: 181
-- Name: COLUMN datasource_description.release_length; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.release_length IS 'In case of FIXED format this field indicates the string length to take starting from the release_position.';


--
-- TOC entry 182 (class 1259 OID 17323)
-- Name: date_format; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE date_format (
    date_format character varying NOT NULL,
    definition character varying
);


ALTER TABLE products.date_format OWNER TO estation;

--
-- TOC entry 2212 (class 0 OID 0)
-- Dependencies: 182
-- Name: COLUMN date_format.date_format; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN date_format.date_format IS 'A string, case insensitive, in YYYYMMDD, YYYYMMDDHHMM,YYYY,MMDD,HHMM. HHMM (may be used for MSG 15 minutes synthesis). This list may change with the project life. It is maintained by JRC';


--
-- TOC entry 2213 (class 0 OID 0)
-- Dependencies: 182
-- Name: COLUMN date_format.definition; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN date_format.definition IS 'A text defining the date type.';


--
-- TOC entry 183 (class 1259 OID 17329)
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
-- TOC entry 2214 (class 0 OID 0)
-- Dependencies: 183
-- Name: COLUMN eumetcast_source.status; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN eumetcast_source.status IS 'On/Off
Active/Non active';


--
-- TOC entry 184 (class 1259 OID 17336)
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
-- TOC entry 2215 (class 0 OID 0)
-- Dependencies: 184
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
-- TOC entry 2216 (class 0 OID 0)
-- Dependencies: 184
-- Name: COLUMN frequency.frequency_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN frequency.frequency_type IS 'Binary flag indicating:
- every Nth ''Time Unit'' (every 15th  = ogni 15 min) 
- N per ''Time Unit'' (4 per hour) 

Values:
E = every
P = per';


--
-- TOC entry 185 (class 1259 OID 17343)
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
-- TOC entry 2217 (class 0 OID 0)
-- Dependencies: 185
-- Name: COLUMN ingestion.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN ingestion.defined_by IS 'values: JRC or USER';


--
-- TOC entry 2218 (class 0 OID 0)
-- Dependencies: 185
-- Name: COLUMN ingestion.wait_for_all_files; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN ingestion.wait_for_all_files IS 'When incomming files need to be mosaicked 
this boolean when TRUE, will indicate to ingestion to wait for all the needed files to come in before mosaicking. When FALSE mosaicking will be done even if not all files arrived.';


--
-- TOC entry 186 (class 1259 OID 17350)
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
-- TOC entry 2219 (class 0 OID 0)
-- Dependencies: 186
-- Name: COLUMN internet_source.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN internet_source.defined_by IS 'values: JRC or USER';


--
-- TOC entry 2220 (class 0 OID 0)
-- Dependencies: 186
-- Name: COLUMN internet_source.modified_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN internet_source.modified_by IS 'Username as value';


--
-- TOC entry 2221 (class 0 OID 0)
-- Dependencies: 186
-- Name: COLUMN internet_source.status; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN internet_source.status IS 'On/Off
Active/Non active';


--
-- TOC entry 2222 (class 0 OID 0)
-- Dependencies: 186
-- Name: COLUMN internet_source.pull_frequency; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN internet_source.pull_frequency IS 'In seconds';


--
-- TOC entry 187 (class 1259 OID 17358)
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
-- TOC entry 2223 (class 0 OID 0)
-- Dependencies: 187
-- Name: COLUMN mapset.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN mapset.defined_by IS 'values: JRC or USER';


--
-- TOC entry 188 (class 1259 OID 17364)
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
-- TOC entry 189 (class 1259 OID 17370)
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
-- TOC entry 190 (class 1259 OID 17377)
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
-- TOC entry 2224 (class 0 OID 0)
-- Dependencies: 190
-- Name: COLUMN product.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.defined_by IS 'values: JRC or USER';


--
-- TOC entry 2225 (class 0 OID 0)
-- Dependencies: 190
-- Name: COLUMN product.product_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.product_type IS 'A product can be of type Native, Ingest or Derived.';


--
-- TOC entry 2226 (class 0 OID 0)
-- Dependencies: 190
-- Name: COLUMN product.descriptive_name; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.descriptive_name IS 'A clear and descriptive name of the product.';


--
-- TOC entry 2227 (class 0 OID 0)
-- Dependencies: 190
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
-- TOC entry 2228 (class 0 OID 0)
-- Dependencies: 190
-- Name: COLUMN product.date_format; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.date_format IS 'A string, case insensitive, in YYYYMMDD, YYYYMMDDHHMM,YYYY,MMDD,HHMM. HHMM (may be used for MSG 15 minutes synthesis). This list may change with the project life. It is maintained by JRC';


--
-- TOC entry 2229 (class 0 OID 0)
-- Dependencies: 190
-- Name: COLUMN product.timeseries_role; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.timeseries_role IS 'Defines the role of the product in TS:
<empty> or Null -> not considered
''Initial'' -> it is represented as ''base'' TS (YYYYMMDD date type)
<subproductcode> -> it is represented as ''derived'' from the <subproductcode> (which must be ''Initial'')';


--
-- TOC entry 191 (class 1259 OID 17384)
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
-- TOC entry 2230 (class 0 OID 0)
-- Dependencies: 191
-- Name: COLUMN product_acquisition_data_source.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product_acquisition_data_source.defined_by IS 'values: JRC or USER';


--
-- TOC entry 2231 (class 0 OID 0)
-- Dependencies: 191
-- Name: COLUMN product_acquisition_data_source.type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product_acquisition_data_source.type IS 'Values: EUMETCAST, INTERNET, OTHER';


--
-- TOC entry 192 (class 1259 OID 17392)
-- Name: product_category; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE product_category (
    category_id character varying NOT NULL,
    descriptive_name character varying,
    order_index integer
);


ALTER TABLE products.product_category OWNER TO estation;

--
-- TOC entry 193 (class 1259 OID 17398)
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
-- TOC entry 195 (class 1259 OID 18380)
-- Name: thema; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE thema (
    thema_id character varying NOT NULL,
    description character varying NOT NULL
);


ALTER TABLE products.thema OWNER TO estation;

--
-- TOC entry 196 (class 1259 OID 18388)
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
-- TOC entry 1994 (class 2604 OID 17991)
-- Name: layerid; Type: DEFAULT; Schema: analysis; Owner: estation
--

ALTER TABLE ONLY layers ALTER COLUMN layerid SET DEFAULT nextval('layers_layerid_seq'::regclass);


--
-- TOC entry 1995 (class 2604 OID 17992)
-- Name: legend_id; Type: DEFAULT; Schema: analysis; Owner: estation
--

ALTER TABLE ONLY legend ALTER COLUMN legend_id SET DEFAULT nextval('legend_legend_id_seq'::regclass);


--
-- TOC entry 2023 (class 2606 OID 17407)
-- Name: Primary key violation; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY legend_step
    ADD CONSTRAINT "Primary key violation" PRIMARY KEY (legend_id, from_step, to_step);


--
-- TOC entry 2019 (class 2606 OID 17409)
-- Name: Uniqueness of legend violation; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY legend
    ADD CONSTRAINT "Uniqueness of legend violation" UNIQUE (legend_name);


--
-- TOC entry 2013 (class 2606 OID 17411)
-- Name: i18n_pkey; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY i18n
    ADD CONSTRAINT i18n_pkey PRIMARY KEY (label);


--
-- TOC entry 2015 (class 2606 OID 17413)
-- Name: languages_pkey; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY languages
    ADD CONSTRAINT languages_pkey PRIMARY KEY (langcode);


--
-- TOC entry 2017 (class 2606 OID 17415)
-- Name: layers_pkey; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY layers
    ADD CONSTRAINT layers_pkey PRIMARY KEY (layerid);


--
-- TOC entry 2021 (class 2606 OID 17417)
-- Name: legend_pkey; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY legend
    ADD CONSTRAINT legend_pkey PRIMARY KEY (legend_id);


--
-- TOC entry 2025 (class 2606 OID 17419)
-- Name: product_legend_pkey; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY product_legend
    ADD CONSTRAINT product_legend_pkey PRIMARY KEY (productcode, subproductcode, version, legend_id);


--
-- TOC entry 2057 (class 2606 OID 18362)
-- Name: timeseries_drawproperties_pk; Type: CONSTRAINT; Schema: analysis; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY timeseries_drawproperties
    ADD CONSTRAINT timeseries_drawproperties_pk PRIMARY KEY (productcode, subproductcode, version);


SET search_path = products, pg_catalog;

--
-- TOC entry 2010 (class 2606 OID 17420)
-- Name: check_datasource_chk; Type: CHECK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE product_acquisition_data_source
    ADD CONSTRAINT check_datasource_chk CHECK (check_datasource(data_source_id, type)) NOT VALID;


--
-- TOC entry 2027 (class 2606 OID 17422)
-- Name: data_type_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY data_type
    ADD CONSTRAINT data_type_pk PRIMARY KEY (data_type_id);


--
-- TOC entry 2029 (class 2606 OID 17424)
-- Name: datasource_description_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY datasource_description
    ADD CONSTRAINT datasource_description_pk PRIMARY KEY (datasource_descr_id);


--
-- TOC entry 2031 (class 2606 OID 17426)
-- Name: date_format_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY date_format
    ADD CONSTRAINT date_format_pk PRIMARY KEY (date_format);


--
-- TOC entry 2033 (class 2606 OID 17428)
-- Name: eumetcast_source_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY eumetcast_source
    ADD CONSTRAINT eumetcast_source_pk PRIMARY KEY (eumetcast_id);


--
-- TOC entry 2035 (class 2606 OID 17430)
-- Name: frequency_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY frequency
    ADD CONSTRAINT frequency_pk PRIMARY KEY (frequency_id);


--
-- TOC entry 2037 (class 2606 OID 17432)
-- Name: ingestion_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY ingestion
    ADD CONSTRAINT ingestion_pk PRIMARY KEY (productcode, subproductcode, version, mapsetcode);


--
-- TOC entry 2039 (class 2606 OID 17434)
-- Name: internet_source_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY internet_source
    ADD CONSTRAINT internet_source_pk PRIMARY KEY (internet_id);


--
-- TOC entry 2041 (class 2606 OID 17436)
-- Name: mapset_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY mapset
    ADD CONSTRAINT mapset_pk PRIMARY KEY (mapsetcode);


--
-- TOC entry 2043 (class 2606 OID 17438)
-- Name: process_input_product_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY process_product
    ADD CONSTRAINT process_input_product_pk PRIMARY KEY (process_id, productcode, subproductcode, version, mapsetcode);


--
-- TOC entry 2045 (class 2606 OID 17440)
-- Name: processing_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY processing
    ADD CONSTRAINT processing_pk PRIMARY KEY (process_id);


--
-- TOC entry 2049 (class 2606 OID 17442)
-- Name: product_acquisition_data_source_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY product_acquisition_data_source
    ADD CONSTRAINT product_acquisition_data_source_pk PRIMARY KEY (productcode, subproductcode, version, data_source_id);


--
-- TOC entry 2052 (class 2606 OID 17444)
-- Name: product_category_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY product_category
    ADD CONSTRAINT product_category_pk PRIMARY KEY (category_id);


--
-- TOC entry 2047 (class 2606 OID 17446)
-- Name: product_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY product
    ADD CONSTRAINT product_pk PRIMARY KEY (productcode, subproductcode, version);


--
-- TOC entry 2055 (class 2606 OID 17448)
-- Name: sub_datasource_description_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY sub_datasource_description
    ADD CONSTRAINT sub_datasource_description_pk PRIMARY KEY (productcode, subproductcode, version, datasource_descr_id);


--
-- TOC entry 2059 (class 2606 OID 18387)
-- Name: thema_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY thema
    ADD CONSTRAINT thema_pk PRIMARY KEY (thema_id);


--
-- TOC entry 2061 (class 2606 OID 18395)
-- Name: thema_product_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY thema_product
    ADD CONSTRAINT thema_product_pk PRIMARY KEY (thema_id, productcode, version, mapsetcode);


--
-- TOC entry 2050 (class 1259 OID 17449)
-- Name: product_categories_order_index_key; Type: INDEX; Schema: products; Owner: estation; Tablespace: 
--

CREATE UNIQUE INDEX product_categories_order_index_key ON product_category USING btree (order_index);


--
-- TOC entry 2053 (class 1259 OID 17450)
-- Name: unique_product_category_name; Type: INDEX; Schema: products; Owner: estation; Tablespace: 
--

CREATE UNIQUE INDEX unique_product_category_name ON product_category USING btree (descriptive_name);


SET search_path = analysis, pg_catalog;

--
-- TOC entry 2063 (class 2606 OID 17451)
-- Name: legend_pkey; Type: FK CONSTRAINT; Schema: analysis; Owner: estation
--

ALTER TABLE ONLY product_legend
    ADD CONSTRAINT legend_pkey FOREIGN KEY (legend_id) REFERENCES legend(legend_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2062 (class 2606 OID 17456)
-- Name: legend_step_legend_id_fkey; Type: FK CONSTRAINT; Schema: analysis; Owner: estation
--

ALTER TABLE ONLY legend_step
    ADD CONSTRAINT legend_step_legend_id_fkey FOREIGN KEY (legend_id) REFERENCES legend(legend_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 2064 (class 2606 OID 17461)
-- Name: product_legend_product_pkey; Type: FK CONSTRAINT; Schema: analysis; Owner: estation
--

ALTER TABLE ONLY product_legend
    ADD CONSTRAINT product_legend_product_pkey FOREIGN KEY (productcode, subproductcode, version) REFERENCES products.product(productcode, subproductcode, version) ON UPDATE CASCADE;


SET search_path = products, pg_catalog;

--
-- TOC entry 2077 (class 2606 OID 17466)
-- Name: data_type_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product
    ADD CONSTRAINT data_type_product_fk FOREIGN KEY (data_type_id) REFERENCES data_type(data_type_id) ON UPDATE CASCADE;


--
-- TOC entry 2082 (class 2606 OID 17471)
-- Name: data_type_sub_datasource_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY sub_datasource_description
    ADD CONSTRAINT data_type_sub_datasource_description_fk FOREIGN KEY (data_type_id) REFERENCES data_type(data_type_id) ON UPDATE CASCADE;


--
-- TOC entry 2067 (class 2606 OID 17476)
-- Name: datasource_description_eumetcast_source_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY eumetcast_source
    ADD CONSTRAINT datasource_description_eumetcast_source_fk FOREIGN KEY (datasource_descr_id) REFERENCES datasource_description(datasource_descr_id) ON UPDATE CASCADE;


--
-- TOC entry 2070 (class 2606 OID 17481)
-- Name: datasource_description_internet_source_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY internet_source
    ADD CONSTRAINT datasource_description_internet_source_fk FOREIGN KEY (datasource_descr_id) REFERENCES datasource_description(datasource_descr_id) ON UPDATE CASCADE;


--
-- TOC entry 2083 (class 2606 OID 17486)
-- Name: datasource_description_sub_datasource_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY sub_datasource_description
    ADD CONSTRAINT datasource_description_sub_datasource_description_fk FOREIGN KEY (datasource_descr_id) REFERENCES datasource_description(datasource_descr_id) ON UPDATE CASCADE;


--
-- TOC entry 2072 (class 2606 OID 17491)
-- Name: date_format_process_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY process_product
    ADD CONSTRAINT date_format_process_product_fk FOREIGN KEY (date_format) REFERENCES date_format(date_format) ON UPDATE CASCADE;


--
-- TOC entry 2065 (class 2606 OID 17496)
-- Name: datetype_filename_format_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY datasource_description
    ADD CONSTRAINT datetype_filename_format_fk FOREIGN KEY (date_type) REFERENCES date_format(date_format) ON UPDATE CASCADE;


--
-- TOC entry 2078 (class 2606 OID 17501)
-- Name: datetype_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product
    ADD CONSTRAINT datetype_product_fk FOREIGN KEY (date_format) REFERENCES date_format(date_format) ON UPDATE CASCADE;


--
-- TOC entry 2079 (class 2606 OID 17506)
-- Name: distribution_frequency_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product
    ADD CONSTRAINT distribution_frequency_product_fk FOREIGN KEY (frequency_id) REFERENCES frequency(frequency_id) ON UPDATE CASCADE;


--
-- TOC entry 2071 (class 2606 OID 17620)
-- Name: frequency_internet_source_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY internet_source
    ADD CONSTRAINT frequency_internet_source_fk FOREIGN KEY (frequency_id) REFERENCES frequency(frequency_id) ON UPDATE CASCADE;


--
-- TOC entry 2066 (class 2606 OID 17511)
-- Name: mapset_filename_format_config_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY datasource_description
    ADD CONSTRAINT mapset_filename_format_config_fk FOREIGN KEY (native_mapset) REFERENCES mapset(mapsetcode) ON UPDATE CASCADE;


--
-- TOC entry 2068 (class 2606 OID 17516)
-- Name: mapset_ingestion_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY ingestion
    ADD CONSTRAINT mapset_ingestion_fk FOREIGN KEY (mapsetcode) REFERENCES mapset(mapsetcode) ON UPDATE CASCADE;


--
-- TOC entry 2073 (class 2606 OID 17521)
-- Name: mapset_process_input_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY process_product
    ADD CONSTRAINT mapset_process_input_product_fk FOREIGN KEY (mapsetcode) REFERENCES mapset(mapsetcode) ON UPDATE CASCADE;


--
-- TOC entry 2076 (class 2606 OID 17526)
-- Name: mapset_processing_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY processing
    ADD CONSTRAINT mapset_processing_fk FOREIGN KEY (output_mapsetcode) REFERENCES mapset(mapsetcode) ON UPDATE CASCADE;


--
-- TOC entry 2085 (class 2606 OID 18396)
-- Name: mapset_thema_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY thema_product
    ADD CONSTRAINT mapset_thema_product_fk FOREIGN KEY (mapsetcode) REFERENCES mapset(mapsetcode) ON UPDATE CASCADE;


--
-- TOC entry 2074 (class 2606 OID 17531)
-- Name: processing_dependencies_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY process_product
    ADD CONSTRAINT processing_dependencies_fk FOREIGN KEY (process_id) REFERENCES processing(process_id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- TOC entry 2080 (class 2606 OID 17536)
-- Name: product_categories_products_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product
    ADD CONSTRAINT product_categories_products_description_fk FOREIGN KEY (category_id) REFERENCES product_category(category_id) ON UPDATE CASCADE;


--
-- TOC entry 2075 (class 2606 OID 17541)
-- Name: product_dependencies_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY process_product
    ADD CONSTRAINT product_dependencies_fk FOREIGN KEY (productcode, subproductcode, version) REFERENCES product(productcode, subproductcode, version) ON UPDATE CASCADE;


--
-- TOC entry 2069 (class 2606 OID 17546)
-- Name: product_ingestion_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY ingestion
    ADD CONSTRAINT product_ingestion_fk FOREIGN KEY (productcode, subproductcode, version) REFERENCES product(productcode, subproductcode, version) ON UPDATE CASCADE;


--
-- TOC entry 2084 (class 2606 OID 17551)
-- Name: product_sub_datasource_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY sub_datasource_description
    ADD CONSTRAINT product_sub_datasource_description_fk FOREIGN KEY (productcode, subproductcode, version) REFERENCES product(productcode, subproductcode, version) ON UPDATE CASCADE;


--
-- TOC entry 2081 (class 2606 OID 17556)
-- Name: products_description_product_acquisition_data_sources_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product_acquisition_data_source
    ADD CONSTRAINT products_description_product_acquisition_data_sources_fk FOREIGN KEY (subproductcode, productcode, version) REFERENCES product(subproductcode, productcode, version) ON UPDATE CASCADE;


--
-- TOC entry 2086 (class 2606 OID 18401)
-- Name: thema_thema_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY thema_product
    ADD CONSTRAINT thema_thema_product_fk FOREIGN KEY (thema_id) REFERENCES thema(thema_id) ON UPDATE CASCADE;


-- Completed on 2015-08-19 18:58:59 CEST

--
-- PostgreSQL database dump complete
--

