
Ext.define("esapp.view.analysis.workspace",{
    extend: "Ext.panel.Panel",
 
    requires: [
        "esapp.view.analysis.workspaceController",
        "esapp.view.analysis.workspaceModel"

        // 'esapp.view.analysis.timeseriesChartSelection'
    ],
    
    controller: "analysis-workspace",
    viewModel: {
        type: "analysis-workspace"
    },
    xtype: 'analysisworkspace',

    // id: 'analysisworkspace',
    name: 'analysisworkspace',
    // reference: 'analysisworkspace',

    layout: {
        type: 'fit',
        padding: 0
    },
    frame: false,
    border: false,
    bodyPadding: '1 0 0 0',
    autoScroll: true,
    scrollable: 'vertical',
    closable: false,
    closeAction: 'destroy', // 'hide'
    plugins: ['tabtitleedit'],

    config:{
        workspaceid: null,
        workspacename: '',
        isNewWorkspace: true,
        isrefworkspace: false,
        title: '',
        titleEditable: false,
        closable: false,
        pinable: false,
        pinned: false,
        maps: [],
        graphs: [],
        tabConfig: {
            style: {
                color: 'black'
            }
        }
    },

    initComponent: function () {
        var me = this;

        //Ext.util.Observable.capture(me, function(e){console.log('AnalysisMain - ' + e);});
        // console.info(me.isrefworkspace);

        if (me.isrefworkspace){
            me.pinable = false;
            me.titleEditable = false;
        }
        else{
            me.tooltip = me.workspaceid != 'defaultworkspace' ? esapp.Utils.getTranslation('edit_workspace_name') : '';     // 'Doubleclick to edit workspace name';
        }

        if (!me.pinned && me.pinable) {
            me.setIconCls('fa fa-thumb-tack pin_red');

        }
        else if (me.pinned && me.pinable){
            me.setIconCls('fa fa-thumb-tack pin_green');
        }

        // if (me.workspaceid == 'defaultworkspace'){
        //     me.tabConfig.tabIndex = 2;
        // }


        if (me.pinable) {
            me.tabConfig = {
                // cls: me.isNewWorkspace ? 'newworkspacetab' : '',
                listeners: {
                    render: {
                        fn: function(e) {
                            if (!me.isrefworkspace) {
                                Ext.tip.QuickTipManager.register({
                                    target: e.btnIconEl.id,
                                    trackMouse: true,
                                    title: esapp.Utils.getTranslation('pin_unpin'),     // Pin/unpin
                                    text: esapp.Utils.getTranslation('pin_unpin_workspace')     // Click to pin or unpin workspace
                                });
                            }
                            e.btnIconEl.on('click', function(e) {
                                // alert('click');
                                if (!me.pinned && me.pinable) {
                                    me.setIconCls('fa fa-thumb-tack pin_green');
                                    me.pinned = true;
                                    if (!me.isNewWorkspace){
                                        me.getController().savePin();
                                    }
                                }
                                else if (me.pinned && me.pinable){
                                    me.setIconCls('fa fa-thumb-tack pin_red');
                                    me.pinned = false;
                                    if (!me.isNewWorkspace){
                                        me.getController().savePin();
                                    }
                                }
                            });
                            // e.btnIconEl.on('mouseover', function(e) {
                            //     console.info('mouseover');
                            //
                            // });
                            e.ownerCt.doLayout();
                        }
                    }
                }
            };
        }

        me.reorderable = true;
        if (me.isrefworkspace){
            me.tabConfig.cls = 'refworkspacetab';
        }
        else if (me.isNewWorkspace){
            me.tabConfig.cls = 'newworkspacetab';
        }
        else if (me.workspaceid == 'defaultworkspace'){
             me.tabConfig.cls = 'defaultworkspacetab';
             me.reorderable = false;
        }

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            padding: 1,
            // border: '0px 0px 1px 0px',
            style: {
                backgroundColor:'#fff',      // '#ADD2ED'
                borderColor: 'lightgray',
                borderStyle: 'solid',
                "border-bottom-width": '1px !important'
            },
            items: [' ', {
                xtype: 'button',
                name: 'newmapbtn',
                text: esapp.Utils.getTranslation('newmap'),  // 'MAPS',
                iconCls: 'map_add',
                style: { color: 'gray' },
                scale: 'small',
                handler: 'newMapView'
            }, {
                xtype: 'button',
                // id: 'analysismain_maptemplatebtn',
                name: 'maptemplateadminbtn_'+me.id.replace(/-/g,'_'),
                reference: 'maptemplateadminbtn_'+me.id.replace(/-/g,'_'),
                text: esapp.Utils.getTranslation('map_template'), // 'MY MAPS'
                iconCls: 'map_tpl',
                style: {color: 'gray'},
                scale: 'small',
                hidden: (esapp.getUser() == 'undefined' || esapp.getUser() == null ? true : false),
                // floating: false,  // usually you want this set to True (default)
                handler: 'showUserMaptemplates',
                listeners: {
                    afterrender: function (btn) {
                        btn.mapTemplateAdminPanel = new esapp.view.analysis.mapTemplateAdmin({owner:btn});
                    }
                }
                // enableToggle: false,
                // arrowVisible: false,
                // arrowAlign: 'right',
                // collapseDirection: 'bottom',
                // menuAlign: 'tl-bc',
                // menu: {
                //     // hideOnClick: true,
                //     defaults: {
                //         cls: "x-menu-no-icon",
                //         padding: 0
                //     },
                //     listeners: {
                //        // afterrender: function(menu , y , x ){
                //        //     Ext.util.Observable.capture(menu, function(e){console.log('mapTemplateMenu - ' + menu.id + ': ' + e);});
                //        // },
                //        activate: function(menu , y , x ){
                //             // menu.down().fireEvent('loadstore');
                //             // menu.down().show();
                //        }
                //     },
                //     items: [{
                //         xtype: 'usermaptpl'
                //         // ,hidden: false
                //     }]
                // }
            },{ xtype: 'tbseparator'
            },{
                xtype: 'button',
                name: 'analysismain_timeseriesbtn',
                reference: 'analysismain_timeseriesbtn',
                text: esapp.Utils.getTranslation('graphs'),  // 'GRAPHS',
                iconCls: 'chart-curve_medium',
                scale: 'small',
                handler: 'showTimeseriesChartSelection'
            },{
                xtype: 'button',
                // id: 'analysismain_graph_templatebtn',
                name: 'graphtemplateadminbtn_'+me.id.replace(/-/g,'_'),
                reference: 'graphtemplateadminbtn_'+me.id.replace(/-/g,'_'),
                text: esapp.Utils.getTranslation('my_graphs'), // 'MY GRAPHS'
                iconCls: 'graph_tpl',
                style: { color: 'gray' },
                scale: 'small',
                hidden:  (esapp.getUser() == 'undefined' || esapp.getUser() == null ? true : false),
                // floating: false,  // usually you want this set to True (default)
                handler: 'showUserGraphTemplates',
                listeners: {
                    afterrender: function (btn) {
                        btn.graphTemplateAdminPanel = new esapp.view.analysis.graphTemplateAdmin({owner:btn});
                    }
                }
            },{ xtype: 'tbspacer'
            },{ xtype: 'tbspacer'
            },{ xtype: 'tbspacer'
            },{ xtype: 'tbspacer'
            },{
                xtype: 'button',
                name: 'analysismain_legendsbtn_'+me.id.replace(/-/g,'_'),
                reference: 'analysismain_legendsbtn_'+me.id.replace(/-/g,'_'),
                text: esapp.Utils.getTranslation('legends'),  // 'LEGENDS',
                iconCls: 'legends',
                style: { color: 'gray' },
                scale: 'small',
                hidden:  (esapp.getUser() == 'undefined' || esapp.getUser() == null || esapp.globals['typeinstallation'] == 'jrc_online' ? true : false),
                handler: 'legendAdmin'
            },{
                xtype: 'button',
                name: 'analysismain_layersbtn_'+me.id.replace(/-/g,'_'),
                reference: 'analysismain_layersbtn_'+me.id.replace(/-/g,'_'),
                text: esapp.Utils.getTranslation('layers'),  // 'LAYERS',
                iconCls: 'layers',
                style: { color: 'gray' },
                scale: 'small',
                // hidden:  (esapp.getUser() == 'undefined' || esapp.getUser() == null ? true : false),
                hidden:  (esapp.getUser() == 'undefined' || esapp.getUser() == null || esapp.globals['typeinstallation'] == 'jrc_online' ? true : false),
                handler: 'layerAdmin'
            },{
                xtype: 'button',
                name: 'analysismain_logosbtn_'+me.id.replace(/-/g,'_'),
                reference: 'analysismain_logosbtn_'+me.id.replace(/-/g,'_'),
                text: esapp.Utils.getTranslation('logos'),  // 'LOGOS',
                iconCls: 'logos',
                style: { color: 'gray' },
                scale: 'small',
                hidden:  (esapp.getUser() == 'undefined' || esapp.getUser() == null || esapp.globals['typeinstallation'] == 'jrc_online' ? true : false),
                handler: 'logosAdmin'
            },
                { xtype: 'tbspacer'
            },
                { xtype: 'tbspacer'
            },
                { xtype: 'tbspacer'
            },{
                xtype: 'button',
                name: 'saveDefaultWorkspaceAsBtn',
                reference: 'saveDefaultWorkspaceAsBtn',
                text: esapp.Utils.getTranslation('save_as'),  // 'Save as',
                iconCls: 'fa fa-save fa-2x',
                style: {color: 'lightblue'},
                scale: 'medium',
                hidden: (!me.isrefworkspace && me.workspaceid != 'defaultworkspace') || esapp.getUser() == 'undefined' || esapp.getUser() == null ? true : false,
                listeners: {
                    afterrender: function (me) {
                        // Register the new tip with an element's ID
                        Ext.tip.QuickTipManager.register({
                            target: me.getId(), // Target button's ID
                            title: '',
                            text: esapp.Utils.getTranslation('save_workspace_as')
                        });
                    }
                },
                handler: 'setWorkspaceName'
            },{
                xtype: 'splitbutton',
                name: 'saveWorkspaceBtn',
                reference: 'saveWorkspaceBtn',
                iconCls: 'fa fa-save fa-2x',
                style: {color: 'lightblue'},
                cls: 'nopadding-splitbtn',
                scale: 'medium',
                hidden:  me.isrefworkspace || (me.workspaceid == 'defaultworkspace' || esapp.getUser() == 'undefined' || esapp.getUser() == null ? true : false),
                arrowVisible: (!me.isNewWorkspace ? true : false),
                listeners: {
                    afterrender: function (me) {
                        // Register the new tip with an element's ID
                        Ext.tip.QuickTipManager.register({
                            target: me.getId(), // Target button's ID
                            title: '',
                            text: esapp.Utils.getTranslation('save_workspace')
                        });
                    }
                },
                handler: 'saveWorkspace',
                menu: {
                    hideOnClick: false,
                    // hidden: (!me.isNewWorkspace ? true : false),
                    alwaysOnTop: true,
                    width: 165,
                    defaults: {
                        hideOnClick: true
                        // hidden: (!me.isNewWorkspace ? true : false)
                    },
                    items: [{
                            //xtype: 'button',
                            text: esapp.Utils.getTranslation('save_as'),    // 'Save as...',
                            glyph: 'xf0c7@FontAwesome',
                            cls:'lightblue',
                            // iconCls: 'fa fa-save fa-lg lightblue',
                            style: { color: 'lightblue' },
                            width: 165,
                            handler: 'setWorkspaceName'
                    }]
                }
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

        me.defaults = {
            titleAlign: 'center',
            frame: false,
            border: false,
            bodyPadding: 0
        };
        me.items = [{
            // region: 'center',
            xtype: 'container',
            id: 'backgroundmap_'+me.id,
            reference: 'backgroundmap_'+me.id,
            autoScroll: true,
            scrollable: 'vertical',
            closable: false,
            autoWidth: true,
            height: 700
            // flex: 1,
            // layout: {
            //     type: 'fit'
            // }
            // style: { "background-color": 'white' },
            // html : '<div id="backgroundmap_' + me.id + '" style="width: 100%; height: 100%;"></div>'
        }, {
            xtype: 'timeserieschartselection',
            // id: 'timeserieschartselection'+me.id,
            reference: 'timeserieschartselection'+me.id,
            workspace: me
        }];

        me.commonMapView = new ol.View({
            projection:"EPSG:4326",
            center: [16.4, -0.5],   // [15, 2]   [20, -4.7],   // ol.proj.transform([20, 4.5], 'EPSG:3857', 'EPSG:4326'),
            resolution: 0.1,
            minResolution: 0.0001,
            maxResolution: 0.25,
            zoomFactor: 1.1+0.1*5   // (cioe' nel range 1.1 -> 2.1)
            // ,zoom: 3
            // minZoom: 4,
            // maxZoom: 100,
            // zoomFactor: 1.5 // 1.0+(0.075*1)
        });
        me.commonMapView.setZoom(1.5);
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

                // var timeseriesChartSelectionWindow = me.lookupReference('timeserieschartselection'+me.id);
                // timeseriesChartSelectionWindow.hide();

                // var taskOpenMapsAndGraphs = new Ext.util.DelayedTask(function() {
                if (me.maps.length > 0) {
                    me.getController().openWorkspaceMaps(me.maps);
                }
                if (me.graphs.length > 0) {
                    me.getController().openWorkspaceGraphs(me.graphs);
                }
                // });
                // taskOpenMapsAndGraphs.delay(50);

                // Wait 5 seconds so that the workspace maps and graphs are openend and loaded and then make the
                // workspace tab closable.
                var taskMakeTabCloseable = new Ext.util.DelayedTask(function() {
                    if (me.workspaceid != "defaultworkspace"){
                        // console.info(me.allMapsLoaded);
                        // console.info(me.allGraphsLoaded);
                        me.tab.setClosable(true);
                        // me.ownerCt.getActiveTab().tab.setClosable(true);
                        me.updateLayout();
                    }
                });
                taskMakeTabCloseable.delay(5000);

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
            // resize: function () {
            //     //var size = [document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight];
            //     var size = [document.getElementById('backgroundmap_'+ me.id).offsetWidth, document.getElementById('backgroundmap_'+ me.id).offsetHeight];
            //     if (esapp.Utils.objectExists(me.map)) {
            //         me.map.setSize(size);
            //     }
            //     // console.info('analysis tab resized!');
            //     // var timeseriesChartSelectionWindow = this.lookupReference('timeserieschartselection'+me.id);
            //     // timeseriesChartSelectionWindow.fireEvent('align');
            // },
            close: function(){
                // console.info('closing and destroying workspace');
                this.lookupReference('timeserieschartselection'+me.id).destroy();
                this.destroy();
            }
        };

        me.callParent();
    }
});
