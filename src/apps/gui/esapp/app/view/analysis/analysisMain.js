
Ext.define("esapp.view.analysis.analysisMain",{
    "extend": "Ext.panel.Panel",
    "controller": "analysis-analysismain",
    "viewModel": {
        "type": "analysis-analysismain"
    },

    xtype  : 'analysis-main',

    requires: [
        'esapp.view.analysis.analysisMainModel',
        'esapp.view.analysis.analysisMainController',
        'esapp.view.analysis.mapView',
        'esapp.view.analysis.ProductNavigator'

        //,'Ext.window.Window'
    ],

    name: 'analysismain',
    reference: 'analysismain',

    layout: {
        type: 'fit'
    },
    frame: false,
    border: false,
    bodyPadding: '0 0 0 0',
    //suspendLayout : true,

    initComponent: function () {
        var me = this;

        me.defaults = {
            titleAlign: 'center',
            frame: true,
            border: false,
            bodyPadding: 0
        };
        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            style: {backgroundColor:'#ADD2ED'},
            items: [{
                xtype: 'button',
                name: 'newmapbtn',
                text: 'New map',
                iconCls: 'map_add',
                style: { color: 'gray' },
                scale: 'small',
                handler: 'newMapView'
            },
            '->',
            {
                xtype: 'button',
                name: 'togglebackgroundlayer',
                text: 'Hide Background layer',
                enableToggle: true,
                // iconCls: 'fa fa-cog', // fa-2x fa-spin 'icon-play', // icomoon fonts
                // style: { color: 'gray' },
                // glyph: 'xf0c7@FontAwesome',
                scale: 'small',
                handler: 'toggleBackgroundlayer'
            }]
        });

        me.html = '<div id="backgroundmap_' + me.id + '"></div>';

        me.commonMapView = new ol.View({
//            projection:"EPSG:4326",
            displayProjection:"EPSG:4326",
            center: ol.proj.transform([20, 4.5], 'EPSG:4326', 'EPSG:3857'),
            zoom: 4
        });

        me.listeners = {
            show: function(){
                // Open a new MapView with latest NDVI product.
                //me.controller.newMapView();
            },
            afterrender: function() {
                if (window.navigator.onLine){

                    me.bingStyles = [
                      'Road',
                      'Aerial',
                      'AerialWithLabels'
                    ];
                    me.backgroundLayers = [];

                    var i, ii;
                    for (i = 0, ii = me.bingStyles.length; i < ii; ++i) {
                        me.backgroundLayers.push(new ol.layer.Tile({
                            visible: false,
                            preload: Infinity,
                            projection: 'EPSG:4326',
                            source: new ol.source.BingMaps({
                                // My personal key jurvtk@gmail.com for http://h05-dev-vm19.ies.jrc.it/esapp/ created on www.bingmapsportal.com
                                key: 'Alp8PmGAclkgN_QJQTjgrkPlyRdkFfTnayMuMobAxMha_QF1ikefhdMlUQPdxNS3',
                                imagerySet: me.bingStyles[i]
                            })
                        }));
                    }
                    for (i = 0, ii = me.backgroundLayers.length; i < ii; ++i) {
                       me.backgroundLayers[i].setVisible(me.bingStyles[i] == 'Road');
                    }

                    var _getRendererFromQueryString = function() {
                      var obj = {}, queryString = location.search.slice(1),
                          re = /([^&=]+)=([^&]*)/g, m;

                      while (m = re.exec(queryString)) {
                        obj[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
                      }
                      if ('renderers' in obj) {
                        return obj['renderers'].split(',');
                      } else if ('renderer' in obj) {
                        return [obj['renderer']];
                      } else {
                        return undefined;
                      }
                    };

                    me.mousePositionControl = new ol.control.MousePosition({
                      coordinateFormat: ol.coordinate.createStringXY(4),
                      projection: 'EPSG:4326',
                      undefinedHTML: '&nbsp;'
                    });

                    me.map = new ol.Map({
                        layers: me.backgroundLayers,
                        // renderer: _getRendererFromQueryString(),
                        projection:"EPSG:3857",
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
                        }).extend([me.mousePositionControl])
                    });
                }
            }
            // The resize handle is necessary to set the map!
            ,resize: function () {
                var size = [document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight];
                this.map.setSize(size);
            }
        };

//        me.items = [{
//            xtype: 'mapview-window',
//            title: '<span class="panel-title-style">MAP 1</span>',
//            x:30,
//            y:50,
//            autoShow : true,
//            layers: [
//                new ol.layer.Tile({
//                    source: new ol.source.MapQuest({layer: 'sat'})
////                    ,projection: 'EPSG:4326'
//                })
//            ],
//            projection: 'EPSG:3857' //'EPSG:3857'
//        },{
//            xtype: 'mapview-window',
//            title: '<span class="panel-title-style">MAP 2</span>',
//            x:1000,
//            y:50,
//            autoShow : true,
//            layers: [
//                new ol.layer.Tile({
//                    source: new ol.source.OSM()
////                    ,projection: 'EPSG:4326'
//                })
//            ],
//            projection: 'EPSG:3857' // 'EPSG:3857'
//        }];

        me.callParent();
    }
});
