
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
        'esapp.view.analysis.ProductNavigator',
        'esapp.view.analysis.timeseriesChartView',

        'Ext.selection.CheckboxModel',
        'Ext.form.field.ComboBox',
        'Ext.form.field.Date',
        'Ext.toolbar.Toolbar'
    ],

    name: 'analysismain',
    reference: 'analysismain',

    frame: false,
    border: false,
    bodyPadding: '5 0 0 0',
    //suspendLayout : true,

    layout: {
        type: 'border',
        padding: 0
    },

    initComponent: function () {
        var me = this;

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            padding: 3,
            style: {backgroundColor:'#ADD2ED'},
            items: [{
                xtype: 'button',
                name: 'newmapbtn',
                text: esapp.Utils.getTranslation('newmap'),  // 'New map',
                iconCls: 'map_add',
                style: { color: 'gray' },
                scale: 'small',
                handler: 'newMapView'
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
            region: 'east',
            //title: esapp.Utils.getTranslation('timeseries'),  // 'Time series',
            width: 420,
            minWidth: 402,
            maxWidth : 475,
            split: true,
            hideCollapseTool: true,
            header: false,
            collapsible: true,
            collapsed: false,
            autoScroll:false,
            floatable: false,
            xtype: 'tabpanel',
            frame: false,
            border: false,
            items: [{
                title: esapp.Utils.getTranslation('timeseries'),  // 'Timeseries',
                margin:3,
                //minHeight: 800,
                autoHeight: true,
                autoScroll:true,
                layout:'vbox',
                defaults: {
                    margin: '5 0 15 0'
                },
                items: [{
                    xtype: 'fieldset',
                    id: 'fieldset_selectedregion',
                    title: '<b style="font-size:16px; color:#0065A2; line-height: 18px;">' + esapp.Utils.getTranslation('selectedregion') + '</b>',
                    hidden: true,
                    width: 395,
                    height: 65,
                    border: 3,
                    //padding: 5,
                    style: {
                        borderColor: '#157FCC',
                        borderStyle: 'solid'
                    },
                    //layout: 'vbox',
                    items: [{
                        xtype: 'displayfield',
                        id: 'selectedregionname',
                        reference: 'selectedregionname',
                        fieldLabel: '',
                        labelAlign : 'left',
                        fieldStyle: {
                            color:'darkgreen',
                            fontWeight:'bold'
                        },
                        value: ''
                    }]
                },{
                    title: esapp.Utils.getTranslation('products'),  // 'Products',
                    xtype : 'grid',
                    reference: 'TimeSeriesProductsGrid',
                    region: 'center',
                    width: 395,
                    height: 250,
                    bind: '{products}',
                    session:true,
                    viewConfig: {
                        stripeRows: false,
                        enableTextSelection: true,
                        draggable:false,
                        markDirty: false,
                        resizable:false,
                        disableSelection: false,
                        trackOver:true
                    },
                    hideHeaders: true,

                    selModel : {
                        allowDeselect : true,
                        mode:'SIMPLE'
                    },

                    collapsible: false,
                    enableColumnMove:false,
                    enableColumnResize:false,
                    multiColumnSort: false,
                    columnLines: false,
                    rowLines: true,
                    frame: false,
                    border: true,
                    bodyBorder: false,

                    tools:[{
                        type: 'refresh',
                        tooltip: esapp.Utils.getTranslation('refreshproductlist'),  // 'Refresh product list',
                        callback: function (grid) {
                            var timeseriesProductsStore  = grid.getStore('products');

                            if (timeseriesProductsStore.isStore) {
                                timeseriesProductsStore.load();
                            }
                        }
                    }],

                    features: [{
                        reference: 'timeseriesproductcategories',
                        ftype: 'grouping',
                        groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
                        hideGroupedHeader: true,
                        enableGroupingMenu: false,
                        startCollapsed : false,
                        groupByText: esapp.Utils.getTranslation('productcategories')  // 'Product category'
                    }],

                    plugins: [{
                        ptype: 'rowexpander',
                        cellWrap:true,
                        layout:'fit',
                        rowBodyTpl : new Ext.XTemplate(
                            '<span class="smalltext">' +
                            '<p>{description}</p>' +
                            '</span>'
                        )
                    }],

                    listeners: {
                        afterrender: 'loadTimeseriesProductsGrid',
                        rowclick: 'TimeseriesProductsGridRowClick'
                    },

                    columns : [{
                        text: '<div class="grid-header-style">' + esapp.Utils.getTranslation('productcategories') + '</div>',   // '<div class="grid-header-style">Product categories</div>',
                        menuDisabled: true,
                        defaults: {
                            sortable: false,
                            hideable: false,
                            variableRowHeight : true,
                            menuDisabled:true
                        },
                        columns: [
                            {
                                //text: "Product",
                                xtype: 'templatecolumn',
                                width: 345,
                                tpl:  new Ext.XTemplate(
                                    '<b>{prod_descriptive_name}</b>',
                                    '<tpl if="version != \'undefined\'">',
                                        '<b class="smalltext"> - {version}</b>',
                                    '</tpl>',
                                    '</br>',
                                    '<b class="smalltext" style="color:darkgrey">{productcode} - {subproductcode}</b>',
                                    '<tpl for="productmapsets">',
                                        '<b class="smalltext"> - {descriptive_name}</b>',
                                    '</tpl>'
                                )
                                //tpl:  new Ext.XTemplate(
                                //    '<b>{prod_descriptive_name}</b>',
                                //    '<tpl if="version != \'undefined\'">',
                                //        '<b class="smalltext"> - {version}</b>',
                                //    '</tpl>',
                                //    '</br>',
                                //    '<b class="smalltext" style="color:darkgrey">{productcode} - {subproductcode}</b>',
                                //    '<tpl if="productmapsets.length === 1">',
                                //        '<tpl for="productmapsets">',
                                //            '<b class="smalltext" style="color:darkgrey"> - {descriptive_name}</b>',
                                //        '</tpl>',
                                //    '<tpl else>',
                                //        '<b class="smalltext" style="color:darkgrey"> - ' + esapp.Utils.getTranslation('mapsets') + ' {productmapsets.length}, ' + esapp.Utils.getTranslation('clicktochoose') + '</b>',
                                //    '</tpl>'
                                //)
                            }
                        ]
                    }]
                }, {
                    xtype: 'grid',
                    id: 'timeseries-mapset-dataset-grid',
                    reference: 'timeseries-mapset-dataset-grid',
                    autoWidth: true,
                    width: 395,
                    maxHeight: 250,
                    //margin:'10 0 10 0',
                    autoScroll: true,
                    hidden: true,
                    bind: '{timeseriesmapsetdatasets}',
                    layout: 'fit',

                    viewConfig: {
                        stripeRows: false,
                        enableTextSelection: true,
                        draggable: false,
                        markDirty: false,
                        resizable: false,
                        disableSelection: false,
                        trackOver: true
                    },

                    selType: 'checkboxmodel',
                    selModel : {
                        allowDeselect : true,
                        mode:'SIMPLE'
                    },
                    collapsible: false,
                    enableColumnMove: false,
                    enableColumnResize: false,
                    multiColumnSort: false,
                    columnLines: true,
                    rowLines: true,
                    frame: false,
                    border: true,
                    bodyBorder: false,

                    listeners: {
                        //rowclick: 'mapsetDataSetGridRowClick'
                    },
                    defaults: {
                        sortable: false,
                        hideable: false,
                        variableRowHeight: false
                    },
                    columns: [{
                        text: '<div class="grid-header-style">' + esapp.Utils.getTranslation('timeseries') + '</div>',   //'<div class="grid-header-style">Time series</div>',
                        xtype: 'templatecolumn',
                        tpl: new Ext.XTemplate(
                            '<b>{prod_descriptive_name}</b>' +
                            '<tpl if="version != \'undefined\'">',
                            '<b class="smalltext"> - {version} </b>',
                            '</tpl>',
                            '</br>' +
                            '<span class="smalltext"><b style="color:darkgrey">{productcode} - {subproductcode}</b> - <b>{mapsetcode}</b>' +
                            '</span>'
                        ),
                        width: 345,
                        sortable: false,
                        menuDisabled: true
                    }]
                }, {
                    xtype: 'fieldset',
                    id: 'ts_timeframe',
                    title: '<b style="font-size:16px; color:#0065A2; line-height: 18px;">' + esapp.Utils.getTranslation('timeframe') + '</b>',
                    hidden: true,
                    width: 395,
                    height: 175,
                    border: 3,
                    padding: 15,
                    style: {
                        borderColor: '#157FCC',
                        borderStyle: 'solid'
                    },
                    layout: 'vbox',
                    items: [{
                        layout: 'hbox',
                        layoutConfig: {columns: 3, rows: 1},
                        items: [{
                            xtype: 'radio',
                            id: 'radio-fromto',
                            checked: false,
                            name: 'ts-period',
                            inputValue: 'year',
                            style: {"margin-right": "5px"},
                            disabled: false
                        },{
                            xtype: 'datefield',
                            id: 'ts_from_period',
                            fieldLabel: esapp.Utils.getTranslation('from'),    // 'From',
                            labelAlign: 'top',
                            style: {"margin-right": "10px"},
                            width: 150,
                            format: "d/m/Y",
                            emptyText : 'dd/mm/yyyy ',
                            allowBlank: true,
                            maxValue: new Date(),
                            listeners: {
                                change: function() {
                                    Ext.getCmp("radio-fromto").setValue(true);
                                }
                            }
                        },{
                            xtype: 'datefield',
                            id: 'ts_to_period',
                            fieldLabel: esapp.Utils.getTranslation('to'),    // 'To',
                            labelAlign: 'top',
                            style: {"margin-right": "10px"},
                            width: 150,
                            format: "d/m/Y",
                            emptyText : 'dd/mm/yyyy ',
                            allowBlank: true,
                            maxValue: new Date(),
                            //,value: new Date()
                            listeners: {
                                change: function() {
                                    Ext.getCmp("radio-fromto").setValue(true);
                                }
                            }
                        }]
                    },{
                        layout: 'hbox',
                        layoutConfig: {columns: 2, rows: 1},
                        items: [{
                            xtype: 'radio',
                            id: 'radio-year',
                            checked: false,
                            align: 'middle',
                            name: 'ts-period',
                            inputValue: 'year',
                            style: {"margin-right": "5px"},
                            disabled: false
                        }, {
                            xtype: 'combobox',
                            id: 'YearTimeseries',
                            name: 'YearTimeseries',
                            bind: {
                                store: '{years}'
                            },
                            fieldLabel: esapp.Utils.getTranslation('year'),    // 'Year',
                            labelWidth: 50,
                            labelAlign: 'top',
                            width: 150,
                            //colspan: 2,
                            valueField: 'year',
                            displayField: 'year',
                            publishes: ['year'],
                            typeAhead: true,
                            queryMode: 'local',
                            emptyText: esapp.Utils.getTranslation('select'),    // 'Select...',
                            listeners: {
                                select: function() {
                                    Ext.getCmp("radio-year").setValue(true);
                                }
                            }
                        }]
                    }]
                },{
                    xtype: 'button',
                    text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
                    id: 'gettimeseries_btn',
                    reference: 'gettimeseries',
                    iconCls: 'chart-curve_medium',
                    scale: 'medium',
                    disabled: true,
                    handler: 'getTimeseries'
                }]
            },{
                title: 'Debug info',
                hidden: true,
                items: [{
                    xtype: 'displayfield',
                    id: 'regionname',
                    reference: 'regionname',
                    fieldLabel: 'Region name',
                    labelAlign : 'top',
                    value: '<span style="color:green;">value</span>'
                }, {
                    xtype: 'displayfield',
                    id: 'admin0name',
                    reference: 'admin0name',
                    fieldLabel: 'Admin level 0 country name',
                    labelAlign : 'top',
                    value: '<span style="color:green;">value</span>'
                }, {
                    xtype: 'displayfield',
                    id: 'admin1name',
                    reference: 'admin1name',
                    fieldLabel: 'Admin level 1 region name',
                    labelAlign : 'top',
                    value: '<span style="color:green;">value</span>'
                }, {
                    xtype: 'displayfield',
                    id: 'admin2name',
                    reference: 'admin2name',
                    fieldLabel: 'Admin level 2 region name',
                    labelAlign : 'top',
                    value: '<span style="color:green;">value</span>'
                }, {
                    title: 'WKT of Polygon',
                    xtype: 'displayfield',
                    id: 'wkt_polygon',
                    reference: 'wkt_polygon',
                    fieldLabel: 'WKT of Polygon',
                    labelAlign : 'top',
                    value: ''
                }]
            }]
            ,listeners: {
                // The resize handle is necessary to set the map!
                expand: function () {
                    //var size = [document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight];
                    var size = [document.getElementById('backgroundmap_'+ me.id).offsetWidth, document.getElementById('backgroundmap_'+ me.id).offsetHeight];
                    me.map.setSize(size);
                    this.header =  false;
                    this.setTitle('');
                },
                collapse: function () {
                    //var size = [document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight];
                    var size = [document.getElementById('backgroundmap_'+ me.id).offsetWidth, document.getElementById('backgroundmap_'+ me.id).offsetHeight];
                    me.map.setSize(size);
                    this.header =  true;
                    this.setTitle('<span class="panel-title-style">'+esapp.Utils.getTranslation('timeseries')+'</span>');
                }
            }
        }, {
            region: 'center',
            autoScroll:true,
            layout: {
                type: 'fit'
            },
            html : '<div id="backgroundmap_' + me.id + '" style="width: 100%; height: 100%;"></div>'
        }];

        me.commonMapView = new ol.View({
            projection:"EPSG:4326",
            displayProjection:"EPSG:4326",
            center: [20, 4.5],   // ol.proj.transform([20, 4.5], 'EPSG:3857', 'EPSG:4326'),
            zoom: 4
        });

        me.listeners = {
            afterrender: function() {
                if (window.navigator.onLine){
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
                              }
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
                }
            }
            // The resize handle is necessary to set the map!
            ,resize: function () {
                //var size = [document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight];
                var size = [document.getElementById('backgroundmap_'+ me.id).offsetWidth, document.getElementById('backgroundmap_'+ me.id).offsetHeight];
                me.map.setSize(size);
            }

            //show: function(){
            //    // Open a new MapView with latest NDVI product.
            //    //me.controller.newMapView();
            //},
        };

        me.callParent();
    }
});
