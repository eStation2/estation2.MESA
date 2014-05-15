--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.2
-- Dumped by pg_dump version 9.3.2
-- Started on 2014-05-08 17:16:06 CEST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 9 (class 2615 OID 17843)
-- Name: products; Type: SCHEMA; Schema: -; Owner: estation
--

CREATE SCHEMA products;


ALTER SCHEMA products OWNER TO estation;

SET search_path = products, pg_catalog;

--
-- TOC entry 1356 (class 1255 OID 20995)
-- Name: check_datasource(character varying, character varying); Type: FUNCTION; Schema: products; Owner: postgres
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


ALTER FUNCTION products.check_datasource(datasourceid character varying, type character varying) OWNER TO postgres;

--
-- TOC entry 1357 (class 1255 OID 21000)
-- Name: check_mapset(character varying); Type: FUNCTION; Schema: products; Owner: postgres
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


ALTER FUNCTION products.check_mapset(mapsetid character varying) OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 195 (class 1259 OID 20710)
-- Name: data_type; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE data_type (
    data_type_id character varying NOT NULL,
    description character varying NOT NULL
);


ALTER TABLE products.data_type OWNER TO estation;

--
-- TOC entry 199 (class 1259 OID 20742)
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
    compose_area_type character varying,
    product_release character varying,
    release_position character varying,
    release_length integer,
    native_mapset character varying,
    CONSTRAINT check_mapset_chk CHECK (check_mapset(native_mapset))
);


ALTER TABLE products.datasource_description OWNER TO estation;

--
-- TOC entry 3415 (class 0 OID 0)
-- Dependencies: 199
-- Name: COLUMN datasource_description.format_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.format_type IS 'Values:
- DELIMITED
- FIXED';


--
-- TOC entry 3416 (class 0 OID 0)
-- Dependencies: 199
-- Name: COLUMN datasource_description.date_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.date_type IS 'A string, case insensitive, in YYYYMMDD, YYYYMMDDHHMM,YYYY,MMDD,HHMM. HHMM (may be used for MSG 15 minutes synthesis). This list may change with the project life. It is maintained by JRC';


--
-- TOC entry 3417 (class 0 OID 0)
-- Dependencies: 199
-- Name: COLUMN datasource_description.product_identifier; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.product_identifier IS 'Comma-separated list of strings present in the filename that form the Product Identifier';


--
-- TOC entry 3418 (class 0 OID 0)
-- Dependencies: 199
-- Name: COLUMN datasource_description.prod_id_position; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.prod_id_position IS 'In case of:
FIXED - integer value of the start position of the Product Identifier

DELIMITED - comma-separated integers indicating the delimiter positions of the Product Identifier to concatinate.';


--
-- TOC entry 3419 (class 0 OID 0)
-- Dependencies: 199
-- Name: COLUMN datasource_description.prod_id_length; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.prod_id_length IS 'In case of FIXED format this field indicates the string length to take starting from the prod_id_position.';


--
-- TOC entry 3420 (class 0 OID 0)
-- Dependencies: 199
-- Name: COLUMN datasource_description.area_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.area_type IS 'Values:
- REGION
- SEGMENT
- TILE
- GLOBAL';


--
-- TOC entry 3421 (class 0 OID 0)
-- Dependencies: 199
-- Name: COLUMN datasource_description.area_position; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.area_position IS 'In case of:
FIXED - integer value of the start position of the Area

DELIMITED - comma-separated integers indicating the delimiter positions of the Area to concatinate.';


--
-- TOC entry 3422 (class 0 OID 0)
-- Dependencies: 199
-- Name: COLUMN datasource_description.area_length; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.area_length IS 'In case of FIXED format this field indicates the string length to take starting from the area_position.';


--
-- TOC entry 3423 (class 0 OID 0)
-- Dependencies: 199
-- Name: COLUMN datasource_description.product_release; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.product_release IS 'String indicating the Product Release present in the filename.';


--
-- TOC entry 3424 (class 0 OID 0)
-- Dependencies: 199
-- Name: COLUMN datasource_description.release_position; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.release_position IS 'In case of:
FIXED - integer value of the start position of the Release

DELIMITED - comma-separated integers indicating the delimiter positions of the Release to concatinate.';


--
-- TOC entry 3425 (class 0 OID 0)
-- Dependencies: 199
-- Name: COLUMN datasource_description.release_length; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN datasource_description.release_length IS 'In case of FIXED format this field indicates the string length to take starting from the release_position.';


--
-- TOC entry 197 (class 1259 OID 20726)
-- Name: date_format; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE date_format (
    date_format character varying NOT NULL,
    definition character varying
);


ALTER TABLE products.date_format OWNER TO estation;

--
-- TOC entry 3426 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN date_format.date_format; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN date_format.date_format IS 'A string, case insensitive, in YYYYMMDD, YYYYMMDDHHMM,YYYY,MMDD,HHMM. HHMM (may be used for MSG 15 minutes synthesis). This list may change with the project life. It is maintained by JRC';


--
-- TOC entry 3427 (class 0 OID 0)
-- Dependencies: 197
-- Name: COLUMN date_format.definition; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN date_format.definition IS 'A text defining the date type.';


--
-- TOC entry 200 (class 1259 OID 20750)
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
-- TOC entry 3428 (class 0 OID 0)
-- Dependencies: 200
-- Name: COLUMN eumetcast_source.status; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN eumetcast_source.status IS 'On/Off
Active/Non active';


--
-- TOC entry 196 (class 1259 OID 20718)
-- Name: frequency; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE frequency (
    frequency character varying NOT NULL,
    definition character varying
);


ALTER TABLE products.frequency OWNER TO estation;

--
-- TOC entry 3429 (class 0 OID 0)
-- Dependencies: 196
-- Name: COLUMN frequency.frequency; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN frequency.frequency IS 'A string, case insensitive, indicating the time-span that the product represents (is distributed): 
undefined
INSTANTANEOUS
DEKAD!=10-days
8days
1month
1week
24hours (for MSG products)
1year';


--
-- TOC entry 206 (class 1259 OID 20804)
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
    input_to_process_re character varying
);


ALTER TABLE products.ingestion OWNER TO estation;

--
-- TOC entry 3430 (class 0 OID 0)
-- Dependencies: 206
-- Name: COLUMN ingestion.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN ingestion.defined_by IS 'values: JRC or USER';


--
-- TOC entry 3431 (class 0 OID 0)
-- Dependencies: 206
-- Name: COLUMN ingestion.wait_for_all_files; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN ingestion.wait_for_all_files IS 'When incomming files need to be mosaicked 
this boolean when TRUE, will indicate to ingestion to wait for all the needed files to come in before mosaicking. When FALSE mosaicking will be done even if not all files arrived.';


--
-- TOC entry 201 (class 1259 OID 20759)
-- Name: internet_source; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE internet_source (
    internet_id character varying NOT NULL,
    defined_by character varying DEFAULT 'JRC'::character varying NOT NULL,
    descriptive_name character varying,
    description character varying,
    modified_by character varying,
    update_datetime timestamp without time zone,
    url character varying,
    user_name character varying,
    password character varying,
    list character varying,
    period character varying,
    scope character varying,
    include_files_expression character varying,
    exclude_files_expression character varying,
    status boolean DEFAULT false NOT NULL,
    pull_frequency integer,
    datasource_descr_id character varying
);


ALTER TABLE products.internet_source OWNER TO estation;

--
-- TOC entry 3432 (class 0 OID 0)
-- Dependencies: 201
-- Name: COLUMN internet_source.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN internet_source.defined_by IS 'values: JRC or USER';


--
-- TOC entry 3433 (class 0 OID 0)
-- Dependencies: 201
-- Name: COLUMN internet_source.modified_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN internet_source.modified_by IS 'Username as value';


--
-- TOC entry 3434 (class 0 OID 0)
-- Dependencies: 201
-- Name: COLUMN internet_source.status; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN internet_source.status IS 'On/Off
Active/Non active';


--
-- TOC entry 3435 (class 0 OID 0)
-- Dependencies: 201
-- Name: COLUMN internet_source.pull_frequency; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN internet_source.pull_frequency IS 'In seconds';


--
-- TOC entry 198 (class 1259 OID 20734)
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
-- TOC entry 3436 (class 0 OID 0)
-- Dependencies: 198
-- Name: COLUMN mapset.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN mapset.defined_by IS 'values: JRC or USER';


--
-- TOC entry 204 (class 1259 OID 20787)
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
    frequency character varying NOT NULL,
    date_format character varying NOT NULL,
    scale_factor double precision,
    scale_offset double precision,
    nodata bigint,
    mask_min double precision,
    mask_max double precision,
    unit character varying,
    data_type_id character varying NOT NULL,
    masked boolean NOT NULL
);


ALTER TABLE products.product OWNER TO estation;

--
-- TOC entry 3437 (class 0 OID 0)
-- Dependencies: 204
-- Name: COLUMN product.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.defined_by IS 'values: JRC or USER';


--
-- TOC entry 3438 (class 0 OID 0)
-- Dependencies: 204
-- Name: COLUMN product.product_type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.product_type IS 'A product can be of type Native, Ingest or Derived.';


--
-- TOC entry 3439 (class 0 OID 0)
-- Dependencies: 204
-- Name: COLUMN product.descriptive_name; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.descriptive_name IS 'A clear and descriptive name of the product.';


--
-- TOC entry 3440 (class 0 OID 0)
-- Dependencies: 204
-- Name: COLUMN product.frequency; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.frequency IS 'A string, case insensitive, indicating the time-span that the product represents (is distributed): 
undefined
INSTANTANEOUS
DEKAD!=10-days
8days
1month
1week
24hours (for MSG products)
1year';


--
-- TOC entry 3441 (class 0 OID 0)
-- Dependencies: 204
-- Name: COLUMN product.date_format; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product.date_format IS 'A string, case insensitive, in YYYYMMDD, YYYYMMDDHHMM,YYYY,MMDD,HHMM. HHMM (may be used for MSG 15 minutes synthesis). This list may change with the project life. It is maintained by JRC';


--
-- TOC entry 207 (class 1259 OID 20813)
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
-- TOC entry 3442 (class 0 OID 0)
-- Dependencies: 207
-- Name: COLUMN product_acquisition_data_source.defined_by; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product_acquisition_data_source.defined_by IS 'values: JRC or USER';


--
-- TOC entry 3443 (class 0 OID 0)
-- Dependencies: 207
-- Name: COLUMN product_acquisition_data_source.type; Type: COMMENT; Schema: products; Owner: estation
--

COMMENT ON COLUMN product_acquisition_data_source.type IS 'Values: EUMETCAST, INTERNET, OTHER';


--
-- TOC entry 203 (class 1259 OID 20777)
-- Name: product_category; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE product_category (
    category_id character varying NOT NULL,
    descriptive_name character varying,
    order_index integer
);


ALTER TABLE products.product_category OWNER TO estation;

--
-- TOC entry 202 (class 1259 OID 20769)
-- Name: products_data; Type: TABLE; Schema: products; Owner: estation; Tablespace: 
--

CREATE TABLE products_data (
    productcode character varying NOT NULL,
    subproductcode character varying NOT NULL,
    version character varying NOT NULL,
    mapsetcode character varying NOT NULL,
    product_datetime character varying NOT NULL,
    directory character varying,
    filename character varying,
    year integer,
    month integer,
    day integer,
    hour integer,
    file_role character varying,
    file_type character varying,
    creation_datetime timestamp without time zone DEFAULT now()
);


ALTER TABLE products.products_data OWNER TO estation;

--
-- TOC entry 205 (class 1259 OID 20796)
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
-- TOC entry 3254 (class 2606 OID 20996)
-- Name: check_datasource_chk; Type: CHECK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE product_acquisition_data_source
    ADD CONSTRAINT check_datasource_chk CHECK (check_datasource(data_source_id, type)) NOT VALID;


--
-- TOC entry 3256 (class 2606 OID 20717)
-- Name: data_type_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY data_type
    ADD CONSTRAINT data_type_pk PRIMARY KEY (data_type_id);


--
-- TOC entry 3264 (class 2606 OID 20749)
-- Name: datasource_description_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY datasource_description
    ADD CONSTRAINT datasource_description_pk PRIMARY KEY (datasource_descr_id);


--
-- TOC entry 3260 (class 2606 OID 20733)
-- Name: date_format_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY date_format
    ADD CONSTRAINT date_format_pk PRIMARY KEY (date_format);


--
-- TOC entry 3266 (class 2606 OID 20758)
-- Name: eumetcast_source_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY eumetcast_source
    ADD CONSTRAINT eumetcast_source_pk PRIMARY KEY (eumetcast_id);


--
-- TOC entry 3258 (class 2606 OID 20725)
-- Name: frequency_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY frequency
    ADD CONSTRAINT frequency_pk PRIMARY KEY (frequency);


--
-- TOC entry 3280 (class 2606 OID 20812)
-- Name: ingestion_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY ingestion
    ADD CONSTRAINT ingestion_pk PRIMARY KEY (productcode, subproductcode, version, mapsetcode);


--
-- TOC entry 3268 (class 2606 OID 20768)
-- Name: internet_source_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY internet_source
    ADD CONSTRAINT internet_source_pk PRIMARY KEY (internet_id);


--
-- TOC entry 3262 (class 2606 OID 20741)
-- Name: mapset_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY mapset
    ADD CONSTRAINT mapset_pk PRIMARY KEY (mapsetcode);


--
-- TOC entry 3282 (class 2606 OID 20822)
-- Name: product_acquisition_data_source_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY product_acquisition_data_source
    ADD CONSTRAINT product_acquisition_data_source_pk PRIMARY KEY (productcode, subproductcode, version, data_source_id);


--
-- TOC entry 3273 (class 2606 OID 20784)
-- Name: product_category_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY product_category
    ADD CONSTRAINT product_category_pk PRIMARY KEY (category_id);


--
-- TOC entry 3276 (class 2606 OID 20795)
-- Name: product_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY product
    ADD CONSTRAINT product_pk PRIMARY KEY (productcode, subproductcode, version);


--
-- TOC entry 3270 (class 2606 OID 29086)
-- Name: products_data_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY products_data
    ADD CONSTRAINT products_data_pk PRIMARY KEY (productcode, subproductcode, version, mapsetcode, product_datetime);


--
-- TOC entry 3278 (class 2606 OID 20803)
-- Name: sub_datasource_description_pk; Type: CONSTRAINT; Schema: products; Owner: estation; Tablespace: 
--

ALTER TABLE ONLY sub_datasource_description
    ADD CONSTRAINT sub_datasource_description_pk PRIMARY KEY (productcode, subproductcode, version, datasource_descr_id);


--
-- TOC entry 3271 (class 1259 OID 20785)
-- Name: product_categories_order_index_key; Type: INDEX; Schema: products; Owner: estation; Tablespace: 
--

CREATE UNIQUE INDEX product_categories_order_index_key ON product_category USING btree (order_index);


--
-- TOC entry 3274 (class 1259 OID 20786)
-- Name: unique_product_category_name; Type: INDEX; Schema: products; Owner: estation; Tablespace: 
--

CREATE UNIQUE INDEX unique_product_category_name ON product_category USING btree (descriptive_name);


--
-- TOC entry 3287 (class 2606 OID 20828)
-- Name: data_type_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product
    ADD CONSTRAINT data_type_product_fk FOREIGN KEY (data_type_id) REFERENCES data_type(data_type_id);


--
-- TOC entry 3291 (class 2606 OID 20823)
-- Name: data_type_sub_datasource_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY sub_datasource_description
    ADD CONSTRAINT data_type_sub_datasource_description_fk FOREIGN KEY (data_type_id) REFERENCES data_type(data_type_id);


--
-- TOC entry 3285 (class 2606 OID 20863)
-- Name: datasource_description_eumetcast_source_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY eumetcast_source
    ADD CONSTRAINT datasource_description_eumetcast_source_fk FOREIGN KEY (datasource_descr_id) REFERENCES datasource_description(datasource_descr_id);


--
-- TOC entry 3286 (class 2606 OID 20858)
-- Name: datasource_description_internet_source_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY internet_source
    ADD CONSTRAINT datasource_description_internet_source_fk FOREIGN KEY (datasource_descr_id) REFERENCES datasource_description(datasource_descr_id);


--
-- TOC entry 3292 (class 2606 OID 20868)
-- Name: datasource_description_sub_datasource_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY sub_datasource_description
    ADD CONSTRAINT datasource_description_sub_datasource_description_fk FOREIGN KEY (datasource_descr_id) REFERENCES datasource_description(datasource_descr_id);


--
-- TOC entry 3283 (class 2606 OID 20843)
-- Name: datetype_filename_format_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY datasource_description
    ADD CONSTRAINT datetype_filename_format_fk FOREIGN KEY (date_type) REFERENCES date_format(date_format);


--
-- TOC entry 3289 (class 2606 OID 20838)
-- Name: datetype_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product
    ADD CONSTRAINT datetype_product_fk FOREIGN KEY (date_format) REFERENCES date_format(date_format);


--
-- TOC entry 3288 (class 2606 OID 20833)
-- Name: distribution_frequency_product_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product
    ADD CONSTRAINT distribution_frequency_product_fk FOREIGN KEY (frequency) REFERENCES frequency(frequency);


--
-- TOC entry 3284 (class 2606 OID 20853)
-- Name: mapset_filename_format_config_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY datasource_description
    ADD CONSTRAINT mapset_filename_format_config_fk FOREIGN KEY (native_mapset) REFERENCES mapset(mapsetcode);


--
-- TOC entry 3295 (class 2606 OID 20848)
-- Name: mapset_ingestion_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY ingestion
    ADD CONSTRAINT mapset_ingestion_fk FOREIGN KEY (mapsetcode) REFERENCES mapset(mapsetcode);


--
-- TOC entry 3290 (class 2606 OID 20883)
-- Name: product_categories_products_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product
    ADD CONSTRAINT product_categories_products_description_fk FOREIGN KEY (category_id) REFERENCES product_category(category_id);


--
-- TOC entry 3294 (class 2606 OID 21002)
-- Name: product_ingestion_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY ingestion
    ADD CONSTRAINT product_ingestion_fk FOREIGN KEY (productcode, subproductcode, version) REFERENCES product(productcode, subproductcode, version) ON UPDATE CASCADE;


--
-- TOC entry 3293 (class 2606 OID 20898)
-- Name: product_sub_datasource_description_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY sub_datasource_description
    ADD CONSTRAINT product_sub_datasource_description_fk FOREIGN KEY (productcode, subproductcode, version) REFERENCES product(productcode, subproductcode, version);


--
-- TOC entry 3296 (class 2606 OID 21007)
-- Name: products_description_product_acquisition_data_sources_fk; Type: FK CONSTRAINT; Schema: products; Owner: estation
--

ALTER TABLE ONLY product_acquisition_data_source
    ADD CONSTRAINT products_description_product_acquisition_data_sources_fk FOREIGN KEY (subproductcode, productcode, version) REFERENCES product(subproductcode, productcode, version) ON UPDATE CASCADE;


-- Completed on 2014-05-08 17:16:07 CEST

--
-- PostgreSQL database dump complete
--

