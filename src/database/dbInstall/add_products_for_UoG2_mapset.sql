SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = products, analysis, pg_catalog;

SELECT products.update_insert_ingestion(  productcode := 'modis-kd490', subproductcode := 'kd490-day', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', defined_by := 'JRC', activated := false, wait_for_all_files := false, input_to_process_re := NULL, enabled := false, full_copy := false );
SELECT products.update_insert_ingestion(  productcode := 'modis-par', subproductcode := 'par-day', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', defined_by := 'JRC', activated := false, wait_for_all_files := false, input_to_process_re := NULL, enabled := false, full_copy := false );
SELECT products.update_insert_ingestion(  productcode := 'modis-sst', subproductcode := 'sst-day', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', defined_by := 'JRC', activated := false, wait_for_all_files := false, input_to_process_re := NULL, enabled := false, full_copy := false );
SELECT products.update_insert_ingestion(  productcode := 'modis-chla', subproductcode := 'chla-day', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', defined_by := 'JRC', activated := false, wait_for_all_files := false, input_to_process_re := NULL, enabled := false, full_copy := false );
SELECT products.update_insert_ingestion(  productcode := 'olci-wrr', subproductcode := 'chl-oc4me', version := 'V02.0', mapsetcode := 'SPOTV-UoG2-1km', defined_by := 'JRC', activated := false, wait_for_all_files := false, input_to_process_re := NULL, enabled := false, full_copy := false );
SELECT products.update_insert_ingestion(  productcode := 'pml-modis-chl', subproductcode := 'chl-3day', version := '3.0', mapsetcode := 'SPOTV-UoG2-1km', defined_by := 'JRC', activated := false, wait_for_all_files := false, input_to_process_re := NULL, enabled := false, full_copy := false );
SELECT products.update_insert_ingestion(  productcode := 'slstr-sst', subproductcode := 'wst', version := '1.0', mapsetcode := 'SPOTV-UoG2-1km', defined_by := 'JRC', activated := false, wait_for_all_files := false, input_to_process_re := NULL, enabled := false, full_copy := false );
SELECT products.update_insert_ingestion(  productcode := 'pml-modis-sst', subproductcode := 'sst-3day', version := '3.0', mapsetcode := 'SPOTV-UoG2-1km', defined_by := 'JRC', activated := false, wait_for_all_files := false, input_to_process_re := NULL, enabled := false, full_copy := false );

SELECT products.update_insert_processing( process_id := 85, defined_by := 'JRC', output_mapsetcode := 'MODIS-UoG2-4km', activated := false, derivation_method := 'std_modis_monavg', algorithm := 'std_modis_monavg', priority := '1', enabled := false, full_copy := false );
SELECT products.update_insert_processing( process_id := 86, defined_by := 'JRC', output_mapsetcode := 'MODIS-UoG2-4km', activated := false, derivation_method := 'std_modis_monavg', algorithm := 'std_modis_monavg', priority := '1', enabled := false, full_copy := false );
SELECT products.update_insert_processing( process_id := 87, defined_by := 'JRC', output_mapsetcode := 'MODIS-UoG2-4km', activated := false, derivation_method := 'std_modis_monavg', algorithm := 'std_modis_monavg', priority := '1', enabled := false, full_copy := false );
SELECT products.update_insert_processing( process_id := 88, defined_by := 'JRC', output_mapsetcode := 'MODIS-UoG2-4km', activated := false, derivation_method := 'std_modis_monavg', algorithm := 'std_modis_monavg', priority := '1', enabled := false, full_copy := false );
SELECT products.update_insert_processing( process_id := 89, defined_by := 'JRC', output_mapsetcode := 'MODIS-UoG2-4km', activated := false, derivation_method := 'modis_pp', algorithm := 'modis_pp', priority := '1', enabled := false, full_copy := false );
SELECT products.update_insert_processing( process_id := 90, defined_by := 'JRC', output_mapsetcode := 'MODIS-UoG2-4km', activated := false, derivation_method := 'modis_pp', algorithm := 'modis_pp', priority := '1', enabled := false, full_copy := false );
SELECT products.update_insert_processing( process_id := 91, defined_by := 'JRC', output_mapsetcode := 'SPOTV-UoG2-1km', activated := true, derivation_method := 'std_fronts', algorithm := 'std_fronts', priority := '1', enabled := true, full_copy := false );
SELECT products.update_insert_processing( process_id := 92, defined_by := 'JRC', output_mapsetcode := 'SPOTV-UoG2-1km', activated := false, derivation_method := 'std_fronts', algorithm := 'std_fronts', priority := '1', enabled := false, full_copy := false );
SELECT products.update_insert_processing( process_id := 93, defined_by := 'JRC', output_mapsetcode := 'MODIS-UoG2-4km', activated := true, derivation_method := 'std_gradient', algorithm := 'std_gradient', priority := '1', enabled := true, full_copy := false );
SELECT products.update_insert_processing( process_id := 94, defined_by := 'JRC', output_mapsetcode := 'SPOTV-UoG2-1km', activated := true, derivation_method := 'std_olci_wrr', algorithm := 'std_olci_wrr', priority := '1', enabled := true, full_copy := false );
SELECT products.update_insert_processing( process_id := 95, defined_by := 'JRC', output_mapsetcode := 'SPOTV-UoG2-1km', activated := true, derivation_method := 'std_fronts', algorithm := 'std_fronts', priority := '1', enabled := true, full_copy := false );
SELECT products.update_insert_processing( process_id := 96, defined_by := 'JRC', output_mapsetcode := 'SPOTV-UoG2-1km', activated := true, derivation_method := 'std_gradient', algorithm := 'std_gradient', priority := '1', enabled := true, full_copy := false );
SELECT products.update_insert_processing( process_id := 97, defined_by := 'JRC', output_mapsetcode := 'SPOTV-UoG2-1km', activated := true, derivation_method := 'std_monavg', algorithm := 'std_monavg', priority := '1', enabled := true, full_copy := false );
SELECT products.update_insert_processing( process_id := 98, defined_by := 'JRC', output_mapsetcode := 'SPOTV-UoG2-1km', activated := true, derivation_method := 'std_3dayavg', algorithm := 'std_3dayavg', priority := '1', enabled := true, full_copy := false );
SELECT products.update_insert_processing( process_id := 99, defined_by := 'JRC', output_mapsetcode := 'SPOTV-UoG2-1km', activated := true, derivation_method := 'std_gradient', algorithm := 'std_gradient', priority := '1', enabled := true, full_copy := false );


SELECT products.update_insert_process_product( process_id := 85, productcode := 'modis-chla', subproductcode := 'chla-day', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := false, final := false, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 85, productcode := 'modis-chla', subproductcode := 'monanom', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := false, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 85, productcode := 'modis-chla', subproductcode := 'monavg', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := false, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 85, productcode := 'modis-chla', subproductcode := 'monclim', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := false, final := false, date_format := 'MMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 86, productcode := 'modis-sst', subproductcode := 'monanom', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 86, productcode := 'modis-sst', subproductcode := 'monavg', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 86, productcode := 'modis-sst', subproductcode := 'monclim', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := true, final := false, date_format := 'MMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 86, productcode := 'modis-sst', subproductcode := 'sst-day', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := true, final := false, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 87, productcode := 'modis-par', subproductcode := 'monanom', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 87, productcode := 'modis-par', subproductcode := 'monavg', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 87, productcode := 'modis-par', subproductcode := 'monclim', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := true, final := false, date_format := 'MMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 87, productcode := 'modis-par', subproductcode := 'par-day', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := true, final := false, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 88, productcode := 'modis-kd490', subproductcode := 'kd490-day', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := true, final := false, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 88, productcode := 'modis-kd490', subproductcode := 'monanom', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 88, productcode := 'modis-kd490', subproductcode := 'monavg', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 88, productcode := 'modis-kd490', subproductcode := 'monclim', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := true, final := false, date_format := 'MMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 89, productcode := 'modis-chla', subproductcode := '8daysavg', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 89, productcode := 'modis-kd490', subproductcode := '8daysavg', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 89, productcode := 'modis-par', subproductcode := '8daysavg', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 89, productcode := 'modis-pp', subproductcode := '8daysavg', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 89, productcode := 'modis-sst', subproductcode := '8daysavg', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 90, productcode := 'modis-chla', subproductcode := 'monavg', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 90, productcode := 'modis-kd490', subproductcode := 'monavg', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 90, productcode := 'modis-par', subproductcode := 'monavg', version := 'v2012.0', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 90, productcode := 'modis-pp', subproductcode := 'monavg', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 90, productcode := 'modis-sst', subproductcode := 'monavg', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 91, productcode := 'pml-modis-sst', subproductcode := 'sst-3day', version := '3.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'INPUT', activated := true, final := false, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 91, productcode := 'pml-modis-sst', subproductcode := 'sst-fronts', version := '3.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 91, productcode := 'pml-modis-sst', subproductcode := 'sst-fronts-shp', version := '3.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 92, productcode := 'modis-sst', subproductcode := 'sst-day', version := 'v2013.1', mapsetcode := 'SPOTV-UoG2-1km', type := 'INPUT', activated := false, final := false, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 92, productcode := 'modis-sst', subproductcode := 'sst-fronts', version := 'v2013.1', mapsetcode := 'SPOTV-UoG2-1km', type := 'OUTPUT', activated := false, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 92, productcode := 'modis-sst', subproductcode := 'sst-fronts-shp', version := 'v2013.1', mapsetcode := 'SPOTV-UoG2-1km', type := 'OUTPUT', activated := false, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 93, productcode := 'modis-chla', subproductcode := 'chla-day', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 93, productcode := 'modis-chla', subproductcode := 'gradient', version := 'v2013.1', mapsetcode := 'MODIS-UoG2-4km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 94, productcode := 'olci-wrr', subproductcode := '3daysavg', version := 'V02.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 94, productcode := 'olci-wrr', subproductcode := 'chl-oc4me', version := 'V02.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 94, productcode := 'olci-wrr', subproductcode := 'monchla', version := 'V02.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 95, productcode := 'slstr-sst', subproductcode := 'sst-fronts', version := '1.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 95, productcode := 'slstr-sst', subproductcode := 'sst-fronts-shp', version := '1.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 95, productcode := 'slstr-sst', subproductcode := 'wst', version := '1.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 96, productcode := 'olci-wrr', subproductcode := 'chl-oc4me', version := 'V02.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 96, productcode := 'olci-wrr', subproductcode := 'gradient', version := 'V02.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 97, productcode := 'slstr-sst', subproductcode := 'monavg', version := '1.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 97, productcode := 'slstr-sst', subproductcode := 'wst', version := '1.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 98, productcode := 'slstr-sst', subproductcode := '3dayavg', version := '1.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 98, productcode := 'slstr-sst', subproductcode := 'wst', version := '1.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 99, productcode := 'slstr-sst', subproductcode := 'gradient', version := '1.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'OUTPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );
SELECT products.update_insert_process_product( process_id := 99, productcode := 'slstr-sst', subproductcode := 'wst', version := '1.0', mapsetcode := 'SPOTV-UoG2-1km', type := 'INPUT', activated := true, final := true, date_format := 'YYYYMMDD', start_date:=   NULL, end_date:= NULL, full_copy := false );



UPDATE products.product p
SET activated = TRUE
WHERE p.product_type = 'Native'
AND (p.productcode, p.version) in (
	('modis-pp', 'v2013.1'),
	('modis-par', 'v2012.0'),
	('modis-kd490', 'v2012.0'),
	('pml-modis-chl', '3.0'),
	('modis-sst', 'v2013.1'),
	('modis-chla', 'v2013.1'),
	('pml-modis-sst', '3.0'),
	('olci-wrr', 'V02.0'),
	('slstr-sst', '1.0'));

UPDATE products.ingestion i
SET activated = TRUE,
enabled = TRUE
WHERE (i.productcode, i.version, i.mapsetcode) in (
	('modis-par', 'v2012.0', 'MODIS-UoG2-4km'),
	('modis-kd490', 'v2012.0', 'MODIS-UoG2-4km'),
	('pml-modis-chl', '3.0', 'SPOTV-UoG2-1km'),
	('modis-sst', 'v2013.1', 'MODIS-UoG2-4km'),
	('modis-chla', 'v2013.1', 'MODIS-UoG2-4km'),
	('pml-modis-sst', '3.0', 'SPOTV-UoG2-1km'),
	('olci-wrr', 'V02.0', 'SPOTV-UoG2-1km'),
	('slstr-sst', '1.0', 'SPOTV-UoG2-1km'));

UPDATE products.process_product pp
SET activated = TRUE
WHERE (pp.productcode, pp.version, pp.mapsetcode) in (
	('modis-par', 'v2012.0', 'MODIS-UoG2-4km'),
	('modis-kd490', 'v2012.0', 'MODIS-UoG2-4km'),
	('pml-modis-chl', '3.0', 'SPOTV-UoG2-1km'),
	('modis-sst', 'v2013.1', 'MODIS-UoG2-4km'),
	('modis-chla', 'v2013.1', 'MODIS-UoG2-4km'),
	('pml-modis-sst', '3.0', 'SPOTV-UoG2-1km'),
	('olci-wrr', 'V02.0', 'SPOTV-UoG2-1km'),
	('slstr-sst', '1.0', 'SPOTV-UoG2-1km'));

UPDATE products.processing p
SET activated = TRUE,
    enabled = TRUE
WHERE (p.process_id) in (SELECT process_id
			 FROM products.process_product pp
			 WHERE pp.type = 'INPUT'
			 AND (pp.productcode, pp.version, pp.mapsetcode) in (
				('modis-par', 'v2012.0', 'MODIS-UoG2-4km'),
				('modis-kd490', 'v2012.0', 'MODIS-UoG2-4km'),
				('pml-modis-chl', '3.0', 'SPOTV-UoG2-1km'),
				('modis-sst', 'v2013.1', 'MODIS-UoG2-4km'),
				('modis-chla', 'v2013.1', 'MODIS-UoG2-4km'),
				('pml-modis-sst', '3.0', 'SPOTV-UoG2-1km'),
				('olci-wrr', 'V02.0', 'SPOTV-UoG2-1km'),
				('slstr-sst', '1.0', 'SPOTV-UoG2-1km'));

UPDATE products.product_acquisition_data_source pads
SET activated = TRUE
WHERE (pads.productcode, pads.version) in (
	('modis-par', 'v2012.0'),
	('modis-kd490', 'v2012.0'),
	('pml-modis-chl', '3.0'),
	('modis-sst', 'v2013.1'),
	('modis-chla', 'v2013.1'),
	('pml-modis-sst', '3.0'),
	('olci-wrr', 'V02.0'),
	('slstr-sst', '1.0'));

