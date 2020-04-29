SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = products, analysis, pg_catalog;


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
                                ('slstr-sst', '1.0', 'SPOTV-UoG2-1km')
                              )
                          );

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

