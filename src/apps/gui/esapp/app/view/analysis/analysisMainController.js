Ext.define('esapp.view.analysis.analysisMainController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-analysismain'

    ,showUserMapTemplates: function(btn){
        //console.info(btn.down().down());
        //Ext.getCmp('userMapTemplates').show();
        btn.down().down().fireEvent('loadstore');
        btn.down().down().show();
    }

    ,newMapView: function() {
        var newMapViewWin = new esapp.view.analysis.mapView({
            epsg: 'EPSG:4326'
        });
        this.getView().add(newMapViewWin);
        newMapViewWin.show();
    }

    ,layerAdmin: function(){
        var newLayerAdminWin = new esapp.view.analysis.layerAdmin();
        this.getView().add(newLayerAdminWin);
        newLayerAdminWin.show();
        this.getView().lookupReference('analysismain_layersbtn').disable();
    }

    ,showTimeseriesChartSelection: function(){
        var timeseriesChartSelectionWindow = this.getView().lookupReference('timeserieschartselection');
        // timeseriesChartSelectionWindow.setHeight(Ext.getBody().getViewSize().height-65);
        // timeseriesChartSelectionWindow.fireEvent('align');
        timeseriesChartSelectionWindow.show();
    }

    ,toggleBackgroundlayer: function(btn, event) {
        var analysismain = btn.up().up();
        var i, ii;
        var me = this.getView();

        if (!esapp.Utils.objectExists(analysismain.map)){
            me.map = new ol.Map({
                layers: me.backgroundLayers,
                // renderer: _getRendererFromQueryString(),
                projection:"EPSG:4326",
                displayProjection:"EPSG:4326",
                target: 'backgroundmap_'+ me.id,
                //overlays: [overlay],
                view: me.commonMapView,
                controls: ol.control.defaults({
                    zoom: false,
                    attribution:false,
                    attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                      collapsible: true // false to show always without the icon.
                    })
                }).extend([me.scaleline])   // me.mousePositionControl,
            });
            me.map.addInteraction(new ol.interaction.MouseWheelZoom({
              duration: 50
            }));
        }

        if (btn.pressed){
            btn.setText(esapp.Utils.getTranslation('hidebackgroundlayer'));
            analysismain.map.addControl(analysismain.mousePositionControl);
            for (i = 0, ii = analysismain.backgroundLayers.length; i < ii; ++i) {
                //analysismain.backgroundLayers[i].setVisible(analysismain.bingStyles[i] == 'Road');
                analysismain.backgroundLayers[i].setVisible(true);
            }
        }
        else {
            btn.setText(esapp.Utils.getTranslation('showbackgroundlayer'));
            analysismain.map.removeControl(analysismain.mousePositionControl);
            for (i = 0, ii = analysismain.backgroundLayers.length; i < ii; ++i) {
                analysismain.backgroundLayers[i].setVisible(false);
            }
        }
    }
});
