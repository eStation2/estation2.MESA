ALTER TABLE products.thema
  ADD COLUMN activated boolean;

UPDATE products.thema set activated = FALSE;
UPDATE products.thema set activated = TRUE WHERE thema_id = themaid;
-- READ themaid from /eStation2/settings/system_settings.ini
-- systemsettings = functions.getSystemSettings()
-- themaid = systemsettings['thema']

CREATE OR REPLACE FUNCTION products.activate_deactivate_ingestion_pads_processing() RETURNS TRIGGER
    LANGUAGE plpgsql STRICT
    AS $$
BEGIN
	IF TG_OP='UPDATE' THEN
		IF (OLD.activated IS DISTINCT FROM NEW.activated AND NEW.product_type = 'Native') THEN
			UPDATE products.ingestion i
			SET activated = NEW.activated,
				  enabled = NEW.activated
			WHERE i.productcode = NEW.productcode
			AND i.version = NEW.version
			AND i.mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product
                           WHERE thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                             AND activated = TRUE
                             AND productcode = NEW.productcode
                             AND version = NEW.version);

			UPDATE products.process_product pp
			SET activated = NEW.activated
			WHERE pp.productcode = NEW.productcode
			AND pp.version = NEW.version
			AND pp.mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product
                            WHERE thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                              AND activated = TRUE
                              AND productcode = NEW.productcode
                              AND version = NEW.version);

			UPDATE products.processing p
			SET activated = NEW.activated,
				  enabled = NEW.activated
			WHERE (p.process_id) in (SELECT process_id
                               FROM products.process_product pp
                               WHERE pp.type = 'INPUT'
                                 AND pp.productcode = NEW.productcode
                                 AND pp.version = NEW.version
                                 AND pp.mapsetcode in (SELECT DISTINCT mapsetcode FROM products.thema_product
                                                       WHERE thema_id = (SELECT thema_id FROM products.thema WHERE activated = TRUE)
                                                         AND activated = TRUE
                                                         AND productcode = NEW.productcode
                                                         AND version = NEW.version));

			UPDATE products.product_acquisition_data_source pads
			SET activated = NEW.activated
			WHERE pads.productcode = NEW.productcode AND pads.version = NEW.version;
		END IF;
	END IF;

	RETURN NEW;
END;
$$;

CREATE TRIGGER update_product
	BEFORE UPDATE ON products.product
	FOR EACH ROW
	WHEN (OLD.activated IS DISTINCT FROM NEW.activated AND NEW.product_type = 'Native')
	EXECUTE PROCEDURE products.activate_deactivate_ingestion_pads_processing();



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

      UPDATE products.product_acquisition_data_source
      SET activated = FALSE
      WHERE defined_by = 'JRC';


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

          UPDATE products.product_acquisition_data_source pads
          SET activated = TRUE
          WHERE (pads.productcode, pads.version) in (SELECT productcode, version FROM products.thema_product WHERE thema_id = themaid AND activated = TRUE);

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

          UPDATE products.product_acquisition_data_source pads
          SET activated = TRUE
          WHERE (pads.productcode, pads.version) in (SELECT productcode, version FROM products.thema_product WHERE thema_id != themaid AND activated = TRUE);
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

