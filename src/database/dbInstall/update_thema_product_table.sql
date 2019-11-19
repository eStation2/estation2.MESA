--
-- Create/update thema_product table in order to match the table in Product Report
--
-- NOTE: for testing/development look at script in E:\clerima\Desktop\Sql\select_product.sqp
-- NOTE: for the current definition of the products/thema/mapsets look at:
--        \\ies-arch01\qt_vol21\eStation\Documents\eStation 2.0\Products\Mapsets\mapset_mc.xlsx

-- To be moved to DB
-- Function: products.update_insert_thema_products(character varying, character varying, character varying, boolean, boolean)

-- DROP FUNCTION products.update_insert_thema_products(character varying, character varying, character varying, boolean, boolean);

CREATE OR REPLACE FUNCTION products.update_insert_thema_products(
    themas character varying,
    products_versions character varying,
    mapsets character varying,
    activated boolean,
    dryrun boolean DEFAULT true)
  RETURNS SETOF text AS
$BODY$
	DECLARE
		_themas   ALIAS FOR  $1;
		_products_versions  ALIAS FOR  $2;
		_mapsets   ALIAS FOR  $3;
		_activated  ALIAS FOR  $4;
		_dryrun ALIAS FOR $5;
		_thema varchar(100) ARRAY;
		_product_version varchar(100) ARRAY;
		_mapset varchar(100) ARRAY;
		_prod_vers varchar(100) ARRAY;
		_query_cursor REFCURSOR;
		_rec character varying;
	BEGIN

	_thema := regexp_split_to_array(_themas, E'\\s+');
	_product_version := regexp_split_to_array(_products_versions, E'\\s+');
  _mapset := regexp_split_to_array(_mapsets, E'\\s+');
	IF _dryrun THEN
		FOR i IN 1..array_length(_thema, 1) LOOP
		    FOR j IN 1..array_length(_product_version, 1) LOOP
		        FOR z IN 1.. array_length(_mapset, 1) LOOP
        			_prod_vers = regexp_split_to_array(_product_version[j], E':');
              --raise notice 'Value: %', _prod_vers[1];
              RETURN QUERY SELECT DISTINCT 'SELECT products.update_insert_thema_product('|| 'thema_id := '''|| t.thema_id ||''', productcode := '''|| p.productcode ||''', version := '''||p.version||''', mapsetcode := '''||_mapset[z]||''', activated := '||_activated||');' as inserts
              FROM products.product p, (SELECT thema_id FROM products.thema) t
              WHERE p.product_type='Native'
              AND p.productcode = _prod_vers[1]
              AND p.version = _prod_vers[2]
              AND p.defined_by='JRC'
              AND p.activated=True
              --AND p.category_id='vegetation'
              AND thema_id=_thema[i];
            END LOOP;
		    END LOOP;
		END LOOP;
	ELSE
		FOR i IN 1..array_length(_thema, 1) LOOP
		    FOR j IN 1..array_length(_product_version, 1) LOOP
		        FOR z IN 1.. array_length(_mapset, 1) LOOP
			_prod_vers = regexp_split_to_array(_product_version[j], E':');

			OPEN _query_cursor FOR
				SELECT DISTINCT 'SELECT products.update_insert_thema_product('|| 'thema_id := '''|| t.thema_id ||''', productcode := '''|| p.productcode ||''', version := '''||p.version||''', mapsetcode := '''||_mapset[z]||''', activated := '||_activated||');' as inserts
				FROM products.product p, (SELECT thema_id FROM products.thema) t
				WHERE p.product_type='Native'
				AND p.productcode = _prod_vers[1]
				AND p.version = _prod_vers[2]
				AND p.defined_by='JRC'
				AND p.activated=True
				AND thema_id=_thema[i];


			LOOP
				FETCH _query_cursor INTO _rec;
				raise notice '%', _rec;

				IF _rec IS NOT NULL THEN
					EXECUTE _rec;
				END IF;

				-- exit when no more row to fetch
				EXIT WHEN NOT FOUND;
			END LOOP;

			CLOSE _query_cursor;

      		END LOOP;
		    END LOOP;
		END LOOP;
	END IF;
   END
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION products.update_insert_thema_products(character varying, character varying, character varying, boolean, boolean)
  OWNER TO estation;

--------------------------------------------------------------------------------------------------------
-- Vegetation Products: all CGL-1km 'Regional' and activated, but Continental for JRC+Training
--------------------------------------------------------------------------------------------------------
DO $$
DECLARE
  _dry_run boolean default TRUE;
BEGIN
  _dry_run := FALSE;

-- DMP/FAPAR/FCOVER/LAI/NDVI 1km
PERFORM products.update_insert_thema_products('AGEOS CICOS', 'vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 vgt-ndvi:proba-v2.2 wsi-hp:V1.0','SPOTV-CEMAC-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('AGRHYMET CSE CSSTE','vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 vgt-ndvi:proba-v2.2 wsi-hp:V1.0','SPOTV-ECOWAS-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ICPAC RCMRD','vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 vgt-ndvi:proba-v2.2 wsi-hp:V1.0','SPOTV-IGAD-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('OSS','vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 vgt-ndvi:proba-v2.2 wsi-hp:V1.0','SPOTV-NAfrica-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 vgt-ndvi:proba-v2.2 wsi-hp:V1.0','SPOTV-SADC-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD JRC Training', 'vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 vgt-ndvi:proba-v2.2 wsi-hp:V1.0','SPOTV-Africa-1km', TRUE, _dry_run);

-- Make available the VGT products for UoG and IOC (not activated by default)
PERFORM products.update_insert_thema_products('MOI', 'vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 vgt-ndvi:proba-v2.2 wsi-hp:V1.0','SPOTV-IOC-1km', FALSE, _dry_run);
PERFORM products.update_insert_thema_products('UOG', 'vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 vgt-ndvi:proba-v2.2 wsi-hp:V1.0','SPOTV-UoG-1km', FALSE, _dry_run);


-- NDVI 300m
PERFORM products.update_insert_thema_products('AGEOS CICOS','vgt-ndvi:proba300-v1.0','SPOTV-CEMAC-300m', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('AGRHYMET CSE CSSTE','vgt-ndvi:proba300-v1.0','SPOTV-ECOWAS-300m', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ICPAC RCMRD','vgt-ndvi:proba300-v1.0','SPOTV-IGAD-300m', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('OSS','vgt-ndvi:proba300-v1.0','SPOTV-NAfrica-300m', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'vgt-ndvi:proba300-v1.0','SPOTV-SADC-300m', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD JRC Training', 'vgt-ndvi:proba300-v1.0','SPOTV-Africa-300m', TRUE, _dry_run);

--------------------------------------------------------------------------------------------------------
-- Rainfall Products: all listed products Continental, activated for Land and de-activate for Marine
--------------------------------------------------------------------------------------------------------
-- Loop over products and set foreach Land THEMA

PERFORM products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL', 'arc2-rain:2.0','ARC2-Africa-11km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL', 'chirps-dekad:2.0' ,'CHIRP-Africa-5km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL', 'fewsnet-rfe:2.0','FEWSNET-Africa-8km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL', 'tamsat-rfe:3.0 tamsat-rfe:3.0','TAMSAT-Africa-4km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL', 'rain-spi:V1.0','CHIRP-Africa-5km', TRUE, _dry_run);

PERFORM products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'arc2-rain:2.0','ARC2-Africa-11km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'chirps-dekad:2.0' ,'CHIRP-Africa-5km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'fewsnet-rfe:2.0','FEWSNET-Africa-8km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'tamsat-rfe:3.0 tamsat-rfe:3.0','TAMSAT-Africa-4km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'rain-spi:V1.0','CHIRP-Africa-5km', TRUE, _dry_run);

--------------------------------------------------------------------------------------------------------
-- Fire Products: both active fires and ba available for land - activated for some only
--------------------------------------------------------------------------------------------------------
PERFORM products.update_insert_thema_products('AGEOS CICOS', 'modis-firms:v6.0','SPOTV-CEMAC-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('CSE CSSTE',   'modis-firms:v6.0','SPOTV-ECOWAS-1km', FALSE, _dry_run);
PERFORM products.update_insert_thema_products('AGRHYMET',   'modis-firms:v6.0','SPOTV-ECOWAS-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ICPAC RCMRD',  'modis-firms:v6.0','SPOTV-IGAD-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('OSS', 'modis-firms:v6.0'  ,'SPOTV-NAfrica-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'modis-firms:v6.0','SPOTV-SADC-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD JRC Training', 'modis-firms:v6.0','SPOTV-Africa-1km', TRUE, _dry_run);

PERFORM products.update_insert_thema_products('AGEOS CICOS', 'vgt-ba:V1.1','SPOTV-CEMAC-300m', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('CSE CSSTE',   'vgt-ba:V1.1','SPOTV-ECOWAS-300m', FALSE, _dry_run);
PERFORM products.update_insert_thema_products('AGRHYMET',   'vgt-ba:V1.1','SPOTV-ECOWAS-300m', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ICPAC RCMRD',  'vgt-ba:V1.1','SPOTV-IGAD-300m', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('OSS', 'vgt-ba:V1.1'  ,'SPOTV-NAfrica-300m', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'vgt-ba:V1.1','SPOTV-SADC-300m', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD JRC Training', 'vgt-ba:V1.1','SPOTV-Africa-300m', TRUE, _dry_run);

--------------------------------------------------------------------------------------------------------
-- Water Body detection
--------------------------------------------------------------------------------------------------------

PERFORM products.update_insert_thema_products('AGEOS CICOS', 'wd-gee:1.0','WD-GEE-CENTRALAFRICA-AVG', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('AGRHYMET CSE CSSTE',   'wd-gee:1.0','WD-GEE-WESTAFRICA-AVG', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ICPAC RCMRD',  'wd-gee:1.0','WD-GEE-IGAD-AVG', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('OSS', 'wd-gee:1.0'  ,'WD-GEE-NORTHAFRICA-AVG', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'wd-gee:1.0','WD-GEE-SOUTHAFRICA-AVG', TRUE, _dry_run);

PERFORM products.update_insert_thema_products('JRC', 'wd-gee:1.0','WD-GEE-CENTRALAFRICA-AVG WD-GEE-WESTAFRICA-AVG WD-GEE-IGAD-AVG WD-GEE-NORTHAFRICA-AVG WD-GEE-SOUTHAFRICA-AVG', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('Training',   'wd-gee:1.0','WD-GEE-WESTAFRICA-AVG', TRUE, _dry_run);

--------------------------------------------------------------------------------------------------------
-- Miscellaneous
--------------------------------------------------------------------------------------------------------
PERFORM products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL','ascat-swi:V3.1' ,'ASCAT-Africa-12-5km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'ascat-swi:V3.1' ,'ASCAT-Africa-12-5km', TRUE, _dry_run);

PERFORM products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL','cpc-sm:1.0' ,'CPC-Africa-50km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'cpc-sm:1.0' ,'CPC-Africa-50km', TRUE, _dry_run);

PERFORM products.update_insert_thema_products('AGEOS CICOS', 'lsasaf-et:undefined','SPOTV-CEMAC-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('AGRHYMET CSE CSSTE',   'lsasaf-et:undefined','SPOTV-ECOWAS-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ICPAC RCMRD',  'lsasaf-et:undefined','SPOTV-IGAD-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('OSS', 'lsasaf-et:undefined'  ,'SPOTV-NAfrica-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'lsasaf-et:undefined','SPOTV-SADC-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD JRC Training', 'cpc-sm:1.0' ,'CPC-Africa-50km', TRUE, _dry_run);

PERFORM products.update_insert_thema_products('AGEOS CICOS', 'lsasaf-et:undefined','SPOTV-CEMAC-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('AGRHYMET CSE CSSTE',   'lsasaf-et:undefined','SPOTV-ECOWAS-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ICPAC RCMRD',  'lsasaf-et:undefined','SPOTV-IGAD-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('OSS', 'lsasaf-et:undefined'  ,'SPOTV-NAfrica-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'lsasaf-et:undefined','SPOTV-SADC-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD JRC Training', 'lsasaf-et:undefined','SPOTV-Africa-1km', TRUE, _dry_run);

PERFORM products.update_insert_thema_products('AGEOS', 'lsasaf-lst:undefined','SPOTV-CEMAC-1km', FALSE, _dry_run);
PERFORM products.update_insert_thema_products('CICOS', 'lsasaf-lst:undefined','SPOTV-CEMAC-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('CSE CSSTE',   'lsasaf-lst:undefined','SPOTV-ECOWAS-1km', FALSE, _dry_run);
PERFORM products.update_insert_thema_products('AGRHYMET',   'lsasaf-lst:undefined','SPOTV-ECOWAS-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ICPAC',  'lsasaf-lst:undefined','SPOTV-IGAD-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('RCMRD',  'lsasaf-lst:undefined','SPOTV-IGAD-1km', FALSE, _dry_run);
PERFORM products.update_insert_thema_products('OSS', 'lsasaf-lst:undefined'  ,'SPOTV-NAfrica-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('BDMS SADC-CSC', 'lsasaf-lst:undefined','SPOTV-SADC-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('ACMAD JRC Training', 'lsasaf-lst:undefined','SPOTV-Africa-1km', TRUE, _dry_run);

--------------------------------------------------------------------------------------------------------
-- Oceanographic products; keep both IOC/UoG and IOC2/UoG2 (?)
--------------------------------------------------------------------------------------------------------
-- CMES-BIO
PERFORM products.update_insert_thema_products('CSIR MOI NARSS UOG JRC Training', 'cmes-bio:1.0','CPC-Africa-50km', TRUE, _dry_run);

-- MODIS 4km
PERFORM products.update_insert_thema_products('CSIR', 'modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-CSIR-4km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('MOI',  'modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-IOC2-4km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('MOI',  'modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-IOC-4km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('NARSS','modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-NAfrica-4km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('UOG',  'modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-UoG2-4km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('UOG',  'modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-UoG-4km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('JRC Training',  'modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-Africa-4km', TRUE, _dry_run);

-- PML MODIS 3day
PERFORM products.update_insert_thema_products('MOI',  'pml-modis-chl:3.0 pml-modis-sst:3.0','SPOTV-IOC-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('UOG',  'pml-modis-chl:3.0 pml-modis-sst:3.0','SPOTV-UoG-1km', TRUE, _dry_run);

PERFORM products.update_insert_thema_products('JRC',  'pml-modis-chl:3.0 pml-modis-sst:3.0','SPOTV-UoG-1km SPOTV-IOC-1km', TRUE, _dry_run);
PERFORM products.update_insert_thema_products('Training',  'pml-modis-chl:3.0 pml-modis-sst:3.0','SPOTV-UoG-1km SPOTV-IOC-1km', TRUE, _dry_run);

-- Sentinel OLCI/SLSTR
PERFORM products.update_insert_thema_products('CSIR', 'olci-wrr:V02.0 slstr-sst:1.0','SPOTV-CSIR-1km', TRUE, dry_run);
PERFORM products.update_insert_thema_products('MOI',  'olci-wrr:V02.0 slstr-sst:1.0','SPOTV-IOC2-1km', TRUE, dry_run);
PERFORM products.update_insert_thema_products('NARSS','olci-wrr:V02.0 slstr-sst:1.0','SPOTV-NAfrica-1km', TRUE, dry_run);
PERFORM products.update_insert_thema_products('UOG',  'olci-wrr:V02.0 slstr-sst:1.0','SPOTV-UoG2-1km', TRUE, dry_run);
PERFORM products.update_insert_thema_products('JRC Training',  'olci-wrr:V02.0 slstr-sst:1.0','SENTINEL-Africa-1km', TRUE, dry_run);

-- To be de-activated for ALL thema:
-- ECMWF-RFE: 'ecmwf-rain', 'OPE', 'ECMWF-Africa-25km'
-- MSG-MPE RFE: 'msg-mpe', 'undefined', 'MSG-satellite-3km'
-- FEWSNET: 'fewsnet-rfe', '2.0', 'FEWSNET-Africa-8km'

END $$;