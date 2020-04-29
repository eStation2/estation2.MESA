SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;


CREATE TABLE IF NOT EXISTS products.db_version
(
    db_version integer NOT NULL,
    CONSTRAINT db_version_pk PRIMARY KEY (db_version)
)
TABLESPACE pg_default;

ALTER TABLE products.db_version
    OWNER to estation;

INSERT INTO products.db_version(db_version) VALUES (2200);