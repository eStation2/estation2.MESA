CREATE TABLE products.geoserver
(
  geoserver_id integer NOT NULL,
  productcode character varying NOT NULL,
  subproductcode character varying NOT NULL,
  version character varying NOT NULL,
  defined_by character varying NOT NULL, -- values: JRC or USER
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

INSERT INTO products.geoserver VALUES (1, 'tamsat-rfe', '10d', '2.0', 'JRC', true, 20160101, NULL);
INSERT INTO products.geoserver VALUES (2, 'fewsnet-rfe', '10d', '2.0', 'JRC', true, 20160101, NULL);
INSERT INTO products.geoserver VALUES (3, 'vgt-ndvi', 'ndvi-linearx2', 'sv2-pv2.1', 'JRC', true, 20160101, NULL);
INSERT INTO products.geoserver VALUES (4, 'vgt-dmp', 'dmp', 'V1.0', 'JRC', true, 20160101, NULL);

