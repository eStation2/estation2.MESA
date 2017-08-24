
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
        'esapp.view.analysis.timeseriesChartSelection',
        //'esapp.view.analysis.mapView',
        //'esapp.view.analysis.ProductNavigator',
        //'esapp.view.analysis.timeseriesChartView',
        //'esapp.view.analysis.layerAdmin',
        //'esapp.model.TSDrawProperties',

        'Ext.selection.CheckboxModel',
        'Ext.form.field.ComboBox',
        'Ext.form.field.Date',
        'Ext.toolbar.Toolbar'
    ],

    id: 'analysismain',
    name: 'analysismain',
    reference: 'analysismain',

    frame: false,
    border: false,
    bodyPadding: '1 0 0 0',
    // suspendLayout : true,

    layout: {
        type: 'fit',
        padding: 0
    },

    initComponent: function () {
        var me = this;

        //Ext.util.Observable.capture(me, function(e){console.log('AnalysisMain - ' + e);});

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            padding: 1,
            style: {backgroundColor:'#ADD2ED'},
            items: [{
                xtype: 'button',
                name: 'newmapbtn',
                text: esapp.Utils.getTranslation('newmap'),  // 'New map',
                iconCls: 'map_add',
                style: { color: 'gray' },
                scale: 'small',
                handler: 'newMapView'
            },{
                xtype: 'button',
                name: 'analysismain_maptemplatebtn',
                reference: 'analysismain_maptemplatebtn',
                text: esapp.Utils.getTranslation('map_template'), // 'MAP TEMPLATE'
                iconCls: 'map_tpl',
                style: { color: 'gray' },
                scale: 'small',
                hidden:  (esapp.getUser() == 'undefined' || esapp.getUser() == null ? true : false),
                floating: false,  // usually you want this set to True (default)
                enableToggle: false,
                arrowVisible: false,
                arrowAlign: 'right',
                collapseDirection: 'bottom',
                menuAlign: 'tl-bc',
                menu: {
                    hideOnClick: true,
                    defaults: {
                        cls: "x-menu-no-icon",
                        padding: 0
                    },
                    listeners: {
                       // afterrender: function(menu , y , x ){
                       //     Ext.util.Observable.capture(menu, function(e){console.log('mapTemplateMenu - ' + menu.id + ': ' + e);});
                       // },
                       activate: function(menu , y , x ){
                            menu.down().fireEvent('loadstore');
                       }
                    },
                    items: [{
                        xtype: 'usermaptpl',
                        hidden: false
                    }]
                }
            },{
                xtype: 'button',
                name: 'analysismain_layersbtn',
                reference: 'analysismain_layersbtn',
                text: esapp.Utils.getTranslation('layers'),  // 'Layers',
                iconCls: 'layers',
                style: { color: 'gray' },
                scale: 'small',
                handler: 'layerAdmin'
            },{
                xtype: 'button',
                name: 'analysismain_timeseriesbtn',
                reference: 'analysismain_timeseriesbtn',
                text: esapp.Utils.getTranslation('timeseries'),  // 'TIME SERIES',
                iconCls: 'chart-curve_medium',
                scale: 'small',
                handler: 'showTimeseriesChartSelection'

            },
            '->',
            {
                xtype: 'button',
                name: 'togglebackgroundlayer',
                //text: esapp.Utils.getTranslation('hidebackgroundlayer'),  // 'Hide Background layer',
                text: esapp.Utils.getTranslation('showbackgroundlayer'),  // 'Show Background layer',
                enableToggle: true,
                // iconCls: 'fa fa-cog', // fa-2x fa-spin 'icon-play', // icomoon fonts
                // style: { color: 'gray' },
                // glyph: 'xf0c7@FontAwesome',
                scale: 'small',
                handler: 'toggleBackgroundlayer'
            }]
        });

        //me.html = '<div id="backgroundmap_' + me.id + '"></div>';

        me.defaults = {
            titleAlign: 'center',
            frame: false,
            border: false,
            bodyPadding: 0
        };
        me.items = [{
            xtype: 'timeserieschartselection',
            id: 'timeserieschartselection',
            reference: 'timeserieschartselection'
        }, {
            region: 'center',
            xtype: 'container',
            id: 'backgroundmap',
            reference: 'backgroundmap',
            autoScroll:true,
            layout: {
                type: 'fit'
            },
            style: { "background-color": 'white' },
            html : '<div id="backgroundmap_' + me.id + '" style="width: 100%; height: 100%;"></div>'
        }];

        me.commonMapView = new ol.View({
            projection:"EPSG:4326",
            center: [14, -7],   // [15, 2]   [20, -4.7],   // ol.proj.transform([20, 4.5], 'EPSG:3857', 'EPSG:4326'),
            resolution: 0.1,
            minResolution: 0.0001,
            maxResolution: 0.25,
            zoomFactor: 1.1+0.1*5   // (cioe' nel range 1.1 -> 2.1)
            // zoom: 6,
            // minZoom: 4,
            // maxZoom: 100,
            // zoomFactor: 1.5 // 1.0+(0.075*1)
        });
        me.zoomFactorSliderValue = 5;

        me.listeners = {
            afterrender: function() {
                // Ext.util.Observable.capture(me, function (e) { console.log('analysismain - ' + e);});
                //if (window.navigator.onLine){
                    me.backgroundLayers = [];
                    me.backgroundLayers.push(
                      new ol.layer.Tile({
                          visible: false,
                          projection: 'EPSG:4326',
                          source: new ol.source.TileWMS({
                              url: 'analysis/getbackgroundlayer',   // 'http://demo.boundlessgeo.com/geoserver/wms',
                              params: {
                                  layername:'naturalearth',
                                  'LAYERS': 'HYP_HR_SR_OB_DR'       // 'ne:NE1_HR_LC_SR_W_DR'
                              },
                              wrapX: false,
                              noWrap: true
                        })
                      })
                    );

                    me.mousePositionControl = new ol.control.MousePosition({
                      coordinateFormat: ol.coordinate.createStringXY(4),
                      projection: 'EPSG:4326',
                      undefinedHTML: '&nbsp;'
                    });

                    me.scaleline = new ol.control.ScaleLine({
                      units: 'metric'       // 'degrees'  'nautical mile'
                    });

                    var taskOpenTimeseriesChartSelection = new Ext.util.DelayedTask(function() {
                        //me.lookupReference('analysismain_timeseriesbtn').fireEvent('click');
                        var timeseriesChartSelectionWindow = me.lookupReference('timeserieschartselection');
                        timeseriesChartSelectionWindow.show();
                        //timeseriesChartSelectionWindow.fireEvent('align');
                    });
                    taskOpenTimeseriesChartSelection.delay(0);



                    //me.map = new ol.Map({
                    //    layers: me.backgroundLayers,
                    //    // renderer: _getRendererFromQueryString(),
                    //    projection:"EPSG:4326",
                    //    displayProjection:"EPSG:4326",
                    //    target: 'backgroundmap_'+ me.id,
                    //    //overlays: [overlay],
                    //    view: me.commonMapView,
                    //    controls: ol.control.defaults({
                    //        zoom: false,
                    //        attribution:false,
                    //        attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                    //          collapsible: true // false to show always without the icon.
                    //        })
                    //    }).extend([me.scaleline])   // me.mousePositionControl,
                    //});
                    //
                    // http://services.arcgisonline.com/arcgis/rest/services/ESRI_StreetMap_World_2D/MapServer
                    // http://services.arcgisonline.com/arcgis/rest/services/ESRI_Imagery_World_2D/MapServer
                    //
                    //me.bingStyles = [
                    //  'Road',
                    //  'Aerial',
                    //  'AerialWithLabels'
                    //];
                    //
                    //var i, ii;
                    //for (i = 0, ii = me.bingStyles.length; i < ii; ++i) {
                    //    me.backgroundLayers.push(new ol.layer.Tile({
                    //        visible: false,
                    //        preload: Infinity,
                    //        projection: 'EPSG:4326',
                    //        source: new ol.source.BingMaps({
                    //            // My personal key jurvtk@gmail.com for http://h05-dev-vm19.ies.jrc.it/esapp/ created on www.bingmapsportal.com
                    //            key: 'Alp8PmGAclkgN_QJQTjgrkPlyRdkFfTnayMuMobAxMha_QF1ikefhdMlUQPdxNS3',
                    //            imagerySet: me.bingStyles[i]
                    //        })
                    //    }));
                    //}
                    //for (i = 0, ii = me.backgroundLayers.length; i < ii; ++i) {
                    //   me.backgroundLayers[i].setVisible(me.bingStyles[i] == 'Road');
                    //}
                    //
                    //var _getRendererFromQueryString = function() {
                    //  var obj = {}, queryString = location.search.slice(1),
                    //      re = /([^&=]+)=([^&]*)/g, m;
                    //
                    //  while (m = re.exec(queryString)) {
                    //    obj[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
                    //  }
                    //  if ('renderers' in obj) {
                    //    return obj['renderers'].split(',');
                    //  } else if ('renderer' in obj) {
                    //    return [obj['renderer']];
                    //  } else {
                    //    return undefined;
                    //  }
                    //};
                    //
                    //me.backgroundLayers.push(
                    //    new ol.layer.Image({
                    //        title: esapp.Utils.getTranslation('backgroundlayer'),  // 'Background layer',
                    //        layer_id: 'backgroundlayer',
                    //        layerorderidx: 0,
                    //        type: 'base',
                    //        visible: false,
                    //        source: new ol.source.ImageWMS({
                    //            url: 'analysis/getbackgroundlayer',
                    //            crossOrigin: 'anonymous',
                    //            params: {
                    //                layername:'naturalearth',
                    //                'FORMAT': 'image/png'
                    //            },
                    //            serverType: 'mapserver' /** @type {ol.source.wms.ServerType}  ('mapserver') */
                    //        })
                    //    })
                    //);
                    //
                    //layer = new ol.layer.XYZ(
                    //    "ESRI",
                    //    "http://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer",
                    //    {sphericalMercator: true}
                    //);
                    //
                    //me.backgroundLayers.push(
                    //  new ol.layer.Tile({
                    //      visible: true,
                    //      projection: 'EPSG:4326',
                    //      source: new ol.source.TileWMS({
                    //          url: 'http://services.arcgisonline.com/arcgis/rest/services/ESRI_StreetMap_World_2D/MapServer',
                    //          params: {
                    //            LAYERS: '0,1,2',
                    //            FORMAT:"image/png"
                    //          }
                    //    })
                    //  })
                    //);
                //}
            },

            // The resize handle is necessary to set the map!
            resize: function () {
                //var size = [document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight];
                var size = [document.getElementById('backgroundmap_'+ me.id).offsetWidth, document.getElementById('backgroundmap_'+ me.id).offsetHeight];
                if (esapp.Utils.objectExists(me.map)) {
                    me.map.setSize(size);
                }
                // console.info('analysis tab resized!');
                var timeseriesChartSelectionWindow = this.lookupReference('timeserieschartselection');
                timeseriesChartSelectionWindow.fireEvent('align');
            }
        };

        me.callParent();
    }
});
