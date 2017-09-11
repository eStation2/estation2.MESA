ALTER TABLE analysis.chart_drawproperties
  ADD COLUMN yaxe4_font_size integer;

UPDATE analysis.chart_drawproperties
SET yaxe4_font_size = 26;