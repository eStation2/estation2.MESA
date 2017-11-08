ALTER TABLE analysis.chart_drawproperties
  ADD COLUMN yaxe4_font_size integer;

UPDATE analysis.chart_drawproperties
SET yaxe4_font_size = 26;

ALTER TABLE analysis.map_templates
   ALTER COLUMN vectorlayers TYPE character varying;
ALTER TABLE analysis.map_templates
  ADD COLUMN zoomextent character varying;

ALTER TABLE analysis.map_templates
  ADD COLUMN mapsize character varying;

ALTER TABLE analysis.map_templates
  ADD COLUMN mapcenter character varying;

ALTER TABLE analysis.legend
   ALTER COLUMN step_type SET DEFAULT 'irregular';




CREATE OR REPLACE FUNCTION analysis.copylegend(
    tocopylegendid bigint,
    newlegendname text)
  RETURNS integer AS
$BODY$
DECLARE
    newlegendid INT8;
BEGIN

  PERFORM nextval('analysis.legend_legend_id_seq');
  SELECT INTO newlegendid currval('analysis.legend_legend_id_seq');

  INSERT INTO analysis.legend (legend_id, legend_name, step_type, min_value, max_value, min_real_value, max_real_value, colorbar, step, step_range_from, step_range_to, unit )
  (SELECT newlegendid, legend_name, step_type, min_value, max_value, min_real_value, max_real_value, newlegendname || '  - ID: ' || CAST(newlegendid AS text), step, step_range_from, step_range_to, unit
   FROM analysis.legend
   WHERE legend_id = tocopylegendid );

  INSERT INTO analysis.legend_step ( legend_id, from_step, to_step, color_rgb, color_label, group_label )
  (SELECT newlegendid, from_step, to_step, color_rgb, color_label, group_label
   FROM analysis.legend_step
   WHERE legend_id = tocopylegendid);

  RETURN newlegendid;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION analysis.copylegend(bigint, text)
  OWNER TO estation;