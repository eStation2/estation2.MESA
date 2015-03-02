Ext.define('esapp.view.analysis.analysisMainController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-analysismain'

    ,newMapView: function() {

        var newMapViewWin = new esapp.view.analysis.mapView({
            layers: [
                new ol.layer.Image({
                    source: new ol.source.ImageWMS({
                        url: 'analysis/getproductlayer',
                        crossOrigin: 'anonymous',
                        attributions: [new ol.Attribution({
                            html: '&copy; ' +
                                '<a href="https://ec.europa.eu/jrc/' +
                                'eStation 2 </a>'
                        })],
                        params: {
                            // 'LAYERS': 'ch.swisstopo.pixelkarte-farbe-pk1000.noscale',
                            'FORMAT': 'image/png'
                        },
                        serverType: 'mapserver' /** @type {ol.source.wms.ServerType}  ('mapserver') */
                    })
                })
            ],
            epsg: 'EPSG:4326'
        });
        //console.info(this.getView());
        this.getView().add(newMapViewWin);
        newMapViewWin.show();
    }

    ,toggleBackgroundlayer: function(btn, event) {
        var analysismain = btn.up().up();
        var i, ii;
        if (btn.pressed){
            btn.setText('Show Background layer');
            analysismain.map.removeControl(analysismain.mousePositionControl);
            for (i = 0, ii = analysismain.backgroundLayers.length; i < ii; ++i) {
                analysismain.backgroundLayers[i].setVisible(!btn.pressed);
            }
        }
        else {
            btn.setText('Hide Background layer');
            analysismain.map.addControl(analysismain.mousePositionControl);
            for (i = 0, ii = analysismain.backgroundLayers.length; i < ii; ++i) {
                analysismain.backgroundLayers[i].setVisible(analysismain.bingStyles[i] == 'Road');
            }
        }
    }

});
