Ext.define('esapp.view.analysis.mapViewController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-mapview'

    ,toggleLink: function(btn, event) {
        var mapviewwin = btn.up().up();

        if (btn.pressed) {
            mapviewwin.map.setView(mapviewwin.mapView);
            btn.setText('Link');
            btn.setIconCls('link');
        }
        else {
            mapviewwin.map.setView(mapviewwin.up().commonMapView);
            btn.setText('Unlink');
            btn.setIconCls('unlink');
        }
    }

    ,openProductNavigator: function(btn, event) {
        var productNavigatorWin = Ext.getCmp(btn.up().up().getId()+'-productnavigator');
        //var productNavigatorWin = btn.up().up().up('window[id='+btn.up().up().getId()+'-productnavigator]');
        //if (Ext.isObject(productNavigatorWin)) {}
        if (!productNavigatorWin){
            productNavigatorWin = new esapp.view.analysis.ProductNavigator({mapviewid:btn.up().up().getId()});
        }
        productNavigatorWin.show();
        //var productsgridstore = productNavigatorWin.lookupReference('productsGrid').getStore('products');
        //if (productsgridstore.isStore) {
        //    productsgridstore.load({loadMask:true});
        //}
    }

    ,addVectorLayer: function(btn){
        // ToDo: Open a new window from which the user can select an in the eStation2 existing or upload a vector layer.
        // ToDo: Have the user set vector layer setting before adding the layer to the map.
        // For now a predifined GeoJSNON  layer with fixed settings is added.

        var me = this;
        var styleCache = {};
        var vectorLayer = new ol.layer.Vector({
          source: new ol.source.GeoJSON({
            projection: 'EPSG:3857',
            url: 'resources/geojson/countries.geojson'
          }),
          style: function(feature, resolution) {
            var text = resolution < 5000 ? feature.get('name') : '';
            if (!styleCache[text]) {
              styleCache[text] = [new ol.style.Style({
                fill: new ol.style.Fill({
                  color: 'rgba(255, 255, 255, 0.6)'
                }),
                stroke: new ol.style.Stroke({
                  color: '#319FD3',
                  width: 1
                }),
                text: new ol.style.Text({
                  font: '12px Calibri,sans-serif',
                  text: text,
                  fill: new ol.style.Fill({
                    color: '#000'
                  }),
                  stroke: new ol.style.Stroke({
                    color: '#fff',
                    width: 3
                  })
                })
              })];
            }
            return styleCache[text];
          }
        });

        me.layers.push(vectorLayer);


        var featureTooltip = Ext.create('Ext.tip.ToolTip', {
            //target: feature,
            //anchor: 'right',
            trackMouse: true,
            html: 'Tracking while you move the mouse'
        });
        /**
         * Create an overlay to anchor the popup to the map.
         */
        var overlay = new ol.Overlay({
          element: featureTooltip.getEl()
        });

        me.map.overlays.push(overlay);

        var highlightStyleCache = {};

        var featureOverlay = new ol.FeatureOverlay({
          map: me.map,
          style: function(feature, resolution) {
            var text = resolution < 5000 ? feature.get('name') : '';
            if (!highlightStyleCache[text]) {
              highlightStyleCache[text] = [new ol.style.Style({
                stroke: new ol.style.Stroke({
                  color: '#f00',
                  width: 1
                }),
                fill: new ol.style.Fill({
                  color: 'rgba(255,0,0,0.1)'
                }),
                text: new ol.style.Text({
                  font: '12px Calibri,sans-serif',
                  text: text,
                  fill: new ol.style.Fill({
                    color: '#000'
                  }),
                  stroke: new ol.style.Stroke({
                    color: '#f00',
                    width: 3
                  })
                })
              })];
            }
            return highlightStyleCache[text];
          }
        });

        var highlight;
        var displayFeatureInfo = function(pixel) {

            var feature = me.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
                return feature;
            });

            //var info = document.getElementById('info');
            if (feature) {
                featureTooltip.html = feature.getId() + ': ' + feature.get('name');
            } else {
                featureTooltip.html = '&nbsp;';
            }

            if (feature !== highlight) {
                if (highlight) {
                    featureOverlay.removeFeature(highlight);
                }
                if (feature) {
                    featureOverlay.addFeature(feature);
                }
                highlight = feature;
            }
        };

        me.mon(Ext.select('ol-viewport'), 'mousemove', function(evt){
            var pixel = me.map.getEventPixel(evt.originalEvent);
            displayFeatureInfo(pixel);
        }, me);

        //(me.map.getViewport()).on('mousemove', function(evt) {
        //    var pixel = me.map.getEventPixel(evt.originalEvent);
        //    displayFeatureInfo(pixel);
        //});

        me.map.on('click', function(evt) {
            var coordinate = evt.coordinate;
            overlay.setPosition(coordinate);
            displayFeatureInfo(evt.pixel);
        });
    }
});
