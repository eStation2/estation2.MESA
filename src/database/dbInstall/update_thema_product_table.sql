--
-- Create/update thema_product table in order to match the table in Product Report
--
-- NOTE: for testing/development look at script in E:\clerima\Desktop\Sql\select_product.sqp
-- NOTE: for the current definition of the products/thema/mapsets look at:
--        \\ies-arch01\qt_vol21\eStation\Documents\eStation 2.0\Products\Mapsets\mapset_mc.xlsx

-- To be moved to DB
CREATE OR REPLACE FUNCTION products.update_insert_thema_products(
themas character varying,
products_versions character varying,
mapset character varying,
activated boolean)
RETURNS SETOF text AS
$BODY$
	DECLARE
		_themas   ALIAS FOR  $1;
		_products_versions  ALIAS FOR  $2;
		_mapset   ALIAS FOR  $3;
		_activated  ALIAS FOR  $4;
		_thema varchar(100) ARRAY;
		_product_version varchar(100) ARRAY;
		_prod_vers varchar(100) ARRAY;
	BEGIN

	_thema := regexp_split_to_array(_themas, E'\\s+');
	_product_version := regexp_split_to_array(_products_versions, E'\\s+');

	FOR i IN 1..array_length(_thema, 1) LOOP
	    FOR j IN 1..array_length(_product_version, 1) LOOP
	        _prod_vers = regexp_split_to_array(_product_version[j], E':');
	        --raise notice 'Value: %', _prod_vers[1];
		RETURN QUERY SELECT DISTINCT 'SELECT products.update_insert_thema_product('|| 'thema_id := '|| t.thema_id ||', productcode := '|| p.productcode ||', version := '||p.version||', mapsetcode := '||_mapset||', activated := '||_activated||');' as inserts
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
   END
$BODY$
 LANGUAGE plpgsql VOLATILE;
 ALTER FUNCTION products.update_insert_thema_products(character varying,character varying,character varying,boolean)
   OWNER TO estation;
--------------------------------------------------------------------------------------------------------
-- Vegetation Products: all CGL-1km 'Regional' and activated, but Continental for JRC+Training
--------------------------------------------------------------------------------------------------------
-- DMP/FAPAR/FCOVER/LAI/NDVI 1km
SELECT products.update_insert_thema_products('AGEOS CICOS', 'vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 wsi-hp:V1.0','SPOTV-CEMAC-1km', TRUE)
SELECT products.update_insert_thema_products('AGRHYMET CSE CSSTE',   'vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 wsi-hp:V1.0','SPOTV-ECOWAS-1km', TRUE)
SELECT products.update_insert_thema_products('ICPAC RCMRD',   'vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 wsi-hp:V1.0','SPOTV-IGAD-1km', TRUE)
SELECT products.update_insert_thema_products('OSS',   'vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 wsi-hp:V1.0','SPOTV-NAfrica-1km', TRUE)
SELECT products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 wsi-hp:V1.0','SPOTV-SADC-1km', TRUE)
SELECT products.update_insert_thema_products('ACMAD JRC Training', 'vgt-dmp:V2.0 vgt-lai:V2.0 vgt-fapar:V2.0 vgt-fcover:V2.0 vgt-ndvi:sv2-pv2.2 wsi-hp:V1.0','SPOTV-Africa-1km', TRUE)

-- NDVI 300m
SELECT products.update_insert_thema_products('AGEOS CICOS', 'vgt-ndvi:sv2-pv2.2','SPOTV-CEMAC-1km', TRUE)
SELECT products.update_insert_thema_products('AGRHYMET CSE CSSTE',   'vgt-ndvi:sv2-pv2.2','SPOTV-ECOWAS-1km', TRUE)
SELECT products.update_insert_thema_products('ICPAC RCMRD',  'vgt-ndvi:sv2-pv2.2','SPOTV-IGAD-1km', TRUE)
SELECT products.update_insert_thema_products('OSS',   'vgt-ndvi:sv2-pv2.2','SPOTV-NAfrica-1km', TRUE)
SELECT products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'vgt-ndvi:sv2-pv2.2','SPOTV-SADC-1km', TRUE)
SELECT products.update_insert_thema_products('ACMAD JRC Training', 'vgt-ndvi:sv2-pv2.2','SPOTV-Africa-1km', TRUE)

--------------------------------------------------------------------------------------------------------
-- Rainfall Products: all listed products Continental, activated for Land and de-activate for Marine
--------------------------------------------------------------------------------------------------------
-- Loop over products and set foreach Land THEMA

SELECT products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL', 'arc2-rain:2.0','ARC2-Africa-11km', TRUE)
SELECT products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL', 'chirps-dekad' ,'CHIRP-Africa-5km', TRUE)
SELECT products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL', 'fewsnet-rfe:2.0','FEWSNET-Africa-8km', TRUE)
SELECT products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL', 'tamsat-rfe:3.0 tamsat-rfe:3.0','TAMSAT-Africa-4km', TRUE)
SELECT products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL', 'rain-spi:V1.0','CHIRP-Africa-5km', TRUE)

SELECT products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'arc2-rain:2.0','ARC2-Africa-11km', TRUE)
SELECT products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'chirps-dekad' ,'CHIRP-Africa-5km', TRUE)
SELECT products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'fewsnet-rfe:2.0','FEWSNET-Africa-8km', TRUE)
SELECT products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'tamsat-rfe:3.0 tamsat-rfe:3.0','TAMSAT-Africa-4km', TRUE)
SELECT products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'rain-spi:V1.0','CHIRP-Africa-5km', TRUE)

--------------------------------------------------------------------------------------------------------
-- Fire Products: both active fires and ba available for land - activated for some only
--------------------------------------------------------------------------------------------------------
SELECT products.update_insert_thema_products('AGEOS CICOS', 'modis-firms:v6.0','SPOTV-CEMAC-1km', TRUE)
SELECT products.update_insert_thema_products('CSE CSSTE',   'modis-firms:v6.0','SPOTV-ECOWAS-1km', FALSE)
SELECT products.update_insert_thema_products('AGRHYMET',   'modis-firms:v6.0','SPOTV-ECOWAS-1km', TRUE)
SELECT products.update_insert_thema_products('ICPAC RCMRD',  'modis-firms:v6.0','SPOTV-IGAD-1km', TRUE)
SELECT products.update_insert_thema_products('OSS', 'modis-firms:v6.0'  ,'SPOTV-NAfrica-1km', TRUE)
SELECT products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'modis-firms:v6.0','SPOTV-SADC-1km', TRUE)
SELECT products.update_insert_thema_products('ACMAD JRC Training', 'modis-firms:v6.0','SPOTV-Africa-1km', TRUE)

SELECT products.update_insert_thema_products('AGEOS CICOS', 'vgt-ba:V1.1','SPOTV-CEMAC-300m', TRUE)
SELECT products.update_insert_thema_products('CSE CSSTE',   'vgt-ba:V1.1','SPOTV-ECOWAS-300m', FALSE)
SELECT products.update_insert_thema_products('AGRHYMET',   'vgt-ba:V1.1','SPOTV-ECOWAS-300m', TRUE)
SELECT products.update_insert_thema_products('ICPAC RCMRD',  'vgt-ba:V1.1','SPOTV-IGAD-300m', TRUE)
SELECT products.update_insert_thema_products('OSS', 'vgt-ba:V1.1'  ,'SPOTV-NAfrica-300m', TRUE)
SELECT products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'vgt-ba:V1.1','SPOTV-SADC-300m', TRUE)
SELECT products.update_insert_thema_products('ACMAD JRC Training', 'vgt-ba:V1.1','SPOTV-Africa-300m', TRUE)

--------------------------------------------------------------------------------------------------------
-- Water Body detection
--------------------------------------------------------------------------------------------------------

SELECT products.update_insert_thema_products('AGEOS CICOS', 'wd-gee:1.0','WD-GEE-CENTRALAFRICA-AVG', TRUE)
SELECT products.update_insert_thema_products('AGRHYMET CSE CSSTE',   'wd-gee:1.0','WD-GEE-WESTAFRICA-AVG', FALSE)
SELECT products.update_insert_thema_products('ICPAC RCMRD',  'wd-gee:1.0','WD-GEE-IGAD-AVG', TRUE)
SELECT products.update_insert_thema_products('OSS', 'wd-gee:1.0'  ,'WD-GEE-NORTHAFRICA-AVG', TRUE)
SELECT products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'wd-gee:1.0','WD-GEE-SOUTHAFRICA-AVG', TRUE)

SELECT products.update_insert_thema_products('JRC', 'wd-gee:1.0','WD-GEE-CENTRALAFRICA-AVG WD-GEE-WESTAFRICA-AVG WD-GEE-IGAD-AVG WD-GEE-NORTHAFRICA-AVG WD-GEE-SOUTHAFRICA-AVG', TRUE)
SELECT products.update_insert_thema_products('Training',   'wd-gee:1.0','WD-GEE-WESTAFRICA-AVG', FALSE)

--------------------------------------------------------------------------------------------------------
-- Miscellaneous
--------------------------------------------------------------------------------------------------------
SELECT products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL','ascat-swi:V3.1' ,'ASCAT-Africa-12-5km', TRUE)
SELECT products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'ascat-swi:V3.1' ,'ASCAT-Africa-12-5km', TRUE)

SELECT products.update_insert_thema_products('AGEOS CICOS CSE CSSTE ICPAC OSS RCMRD SADC-CSC SASSCAL','cpc-sm:1.0' ,'CPC-Africa-50km', TRUE)
SELECT products.update_insert_thema_products('ACMAD AGRHYMET BDMS JRC Training', 'cpc-sm:1.0' ,'CPC-Africa-50km', TRUE)

SELECT products.update_insert_thema_products('AGEOS CICOS', 'lsasaf-et:undefined','SPOTV-CEMAC-1km', TRUE)
SELECT products.update_insert_thema_products('AGRHYMET CSE CSSTE',   'lsasaf-et:undefined','SPOTV-ECOWAS-1km', TRUE)
SELECT products.update_insert_thema_products('ICPAC RCMRD',  'lsasaf-et:undefined','SPOTV-IGAD-1km', TRUE)
SELECT products.update_insert_thema_products('OSS', 'lsasaf-et:undefined'  ,'SPOTV-NAfrica-1km', TRUE)
SELECT products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'lsasaf-et:undefined','SPOTV-SADC-1km', TRUE)
SELECT products.update_insert_thema_products('ACMAD JRC Training', 'cpc-sm:1.0' ,'CPC-Africa-50km', TRUE)

SELECT products.update_insert_thema_products('AGEOS CICOS', 'lsasaf-et:undefined','SPOTV-CEMAC-1km', TRUE)
SELECT products.update_insert_thema_products('AGRHYMET CSE CSSTE',   'lsasaf-et:undefined','SPOTV-ECOWAS-1km', TRUE)
SELECT products.update_insert_thema_products('ICPAC RCMRD',  'lsasaf-et:undefined','SPOTV-IGAD-1km', TRUE)
SELECT products.update_insert_thema_products('OSS', 'lsasaf-et:undefined'  ,'SPOTV-NAfrica-1km', TRUE)
SELECT products.update_insert_thema_products('BDMS SADC-CSC SASSCAL', 'lsasaf-et:undefined','SPOTV-SADC-1km', TRUE)
SELECT products.update_insert_thema_products('ACMAD JRC Training', 'lsasaf-et:undefined','SPOTV-Africa-1km', TRUE)

SELECT products.update_insert_thema_products('AGEOS', 'lsasaf-lst:undefined','SPOTV-CEMAC-1km', FALSE)
SELECT products.update_insert_thema_products('CICOS', 'lsasaf-lst:undefined','SPOTV-CEMAC-1km', TRUE)
SELECT products.update_insert_thema_products('AGRHYMET CSE CSSTE',   'lsasaf-lst:undefined','SPOTV-ECOWAS-1km', FALSE)
SELECT products.update_insert_thema_products('ICPAC',  'lsasaf-lst:undefined','SPOTV-IGAD-1km', TRUE)
SELECT products.update_insert_thema_products('RCMRD',  'lsasaf-lst:undefined','SPOTV-IGAD-1km', FALSE)
SELECT products.update_insert_thema_products('OSS', 'lsasaf-lst:undefined'  ,'SPOTV-NAfrica-1km', TRUE)
SELECT products.update_insert_thema_products('BDMS SADC-CSC', 'lsasaf-lst:undefined','SPOTV-SADC-1km', TRUE)
SELECT products.update_insert_thema_products('ACMAD JRC Training', 'lsasaf-lst:undefined','SPOTV-Africa-1km', TRUE)

--------------------------------------------------------------------------------------------------------
-- Oceanographic products; keep both IOC/UoG and IOC2/UoG2 (?)
--------------------------------------------------------------------------------------------------------
-- MODIS 4km
SELECT products.update_insert_thema_products('CISR', 'modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-CSIR-4km', TRUE)
SELECT products.update_insert_thema_products('MOI',  'modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-IOC2-4km', TRUE)
SELECT products.update_insert_thema_products('MOI',  'modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-IOC-4km', TRUE)
SELECT products.update_insert_thema_products('NARSS','modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-NAfrica-4km', TRUE)
SELECT products.update_insert_thema_products('UOG',  'modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-UoG2-4km', TRUE)
SELECT products.update_insert_thema_products('UOG',  'modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-UoG-4km', TRUE)
SELECT products.update_insert_thema_products('JRC Training',  'modis-chla:v2013.1 modis-kd490:v2012.0 modis-par:v2012.0 modis-sst:v2013.1 modis-pp:v2013.1','MODIS-Africa-4km', TRUE)

-- PML MODIS 3day
SELECT products.update_insert_thema_products('MOI',  'pml-modis-chla:3.0 pml-modis-sst:3.0','SPOTV-IOC2-1km', TRUE)
SELECT products.update_insert_thema_products('MOI',  'pml-modis-chla:3.0 pml-modis-sst:3.0','SPOTV-IOC-1km', TRUE)
SELECT products.update_insert_thema_products('UOG',  'pml-modis-chla:3.0 pml-modis-sst:3.0','SPOTV-UoG2-1km', TRUE)
SELECT products.update_insert_thema_products('UOG',  'pml-modis-chla:3.0 pml-modis-sst:3.0','SPOTV-UoG-1km', TRUE)

SELECT products.update_insert_thema_products('JRC',  'pml-modis-chla:3.0 pml-modis-sst:3.0','SPOTV-UoG-1km SPOTV-UoG2-1km SPOTV-IOC-1km SPOTV-IOC2-1km', TRUE)
SELECT products.update_insert_thema_products('Training',  'pml-modis-chla:3.0 pml-modis-sst:3.0','SPOTV-UoG2-1km SPOTV-IOC2-1km', TRUE)

-- Sentinel OLCI/SLSTR
SELECT products.update_insert_thema_products('CISR', 'olci-wrr:V02.0 slstr-ssr:1:0','SPOTV-CSIR-1km', TRUE)
SELECT products.update_insert_thema_products('MOI',  'olci-wrr:V02.0 slstr-ssr:1:0','SPOTV-IOC2-1km', TRUE)
SELECT products.update_insert_thema_products('NARSS','olci-wrr:V02.0 slstr-ssr:1:0','SPOTV-NAfrica-1km', TRUE)
SELECT products.update_insert_thema_products('UOG',  'olci-wrr:V02.0 slstr-ssr:1:0','SPOTV-UoG2-1km', TRUE)

SELECT products.update_insert_thema_products('JRC Training',  'olci-wrr:V02.0 slstr-ssr:1:0','SPOTV-Africa-1km', TRUE)

-- To be de-activated for ALL thema:
-- ECMWF-RFE: 'ecmwf-rain', 'OPE', 'ECMWF-Africa-25km'
-- MSG-MPE RFE: 'msg-mpe', 'undefined', 'MSG-satellite-3km'
-- FEWSNET: 'fewsnet-rfe', '2.0', 'FEWSNET-Africa-8km'

