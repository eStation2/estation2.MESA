Ext.define("esapp.view.analysis.timeseriesChartSelection",{
    extend: "Ext.panel.Panel",      // "Ext.window.Window",
 
    requires: [
        "esapp.view.analysis.timeseriesChartSelectionController",
        "esapp.view.analysis.timeseriesChartSelectionModel",

        "esapp.view.analysis.timeseriesProductSelection"
    ],
    
    controller: "analysis-timeserieschartselection",
    viewModel: {
        type: "analysis-timeserieschartselection"
    },

    xtype  : 'timeserieschartselection',

    title: esapp.Utils.getTranslation('TIME SERIES GRAPHS'),  // 'Time series',

    header: {
        titlePosition: 1,
        titleAlign: 'center'
    },
    constrainHeader: true,
    constrain: true,
    autoShow : false,
    hidden: true,
    closable: true,
    closeAction: 'hide', // 'hide',
    maximizable: false,
    collapsible: true,
    collapsed: false,
    resizable: false,
    autoScroll: false,
    floating: true,
    floatable: true,
    alwaysOnTop: false,

    width:500,
    minWidth:500,
    //autoHeight: true,
    height: Ext.getBody().getViewSize().height-65,

    alignTarget: Ext.getCmp('backgroundmap'),
    defaultAlign: 'tr-tr',
    // glyph : 'xf080@FontAwesome',
    margin: '0 0 0 0',
    frame: true,
    border: true,
    layout: {
        type: 'fit'
    },


    initComponent: function () {
        var me = this;

        //Ext.util.Observable.capture(me, function (e) { console.log('timeserieschartselection - ' + e);});

        me.listeners = {
            align: function(){
                if (!me.hidden){
                    var task = new Ext.util.DelayedTask(function() {
                        //console.info('align');
                        //console.info(Ext.getCmp('analysismain').lookupReference('backgroundmap'));
                        me.expand();
                        me.alignTo(Ext.getCmp('analysismain').lookupReference('backgroundmap'), 'tr-tr');
                        me.updateLayout();
                    });
                    task.delay(200);
                }
            }
            ,activate: function() {
                //console.info('activate tsselectionwin');
                me.fireEvent('align');
            }
        };

        me.title = esapp.Utils.getTranslation('TIME SERIES GRAPHS');  // 'Time series',

        me.items = [{
            xtype: 'tabpanel',
            id: 'graphs_tabpanel_'+me.id,
            //width: 440,
            //minWidth: 440,
            //maxWidth : 500,
            minTabWidth: 210,
            hideCollapseTool: true,
            header: false,
            autoScroll:false,
            frame: false,
            border: false,
            layout: {
                type: 'fit'
            },
            items: [{
                title: esapp.Utils.getTranslation('DEFAULT X/Y GRAPH'),  // 'DEFAULT X/Y GRAPH',
                id: 'ts_default_xy_graph_tab_' + me.id,
                margin: 3,
                //minHeight: 800,
                autoHeight: true,
                autoScroll: true,
                layout: {
                    type: 'vbox'
                    , align: 'stretch'
                },
                defaults: {
                    margin: '0 0 5 0'
                },
                tbar: [{
                    xtype: 'button',
                    text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
                    id: 'gettimeseries_btn',
                    reference: 'gettimeseries_bnt1',
                    iconCls: 'chart-curve_medium',
                    scale: 'medium',
                    disabled: true,
                    width: 150,
                    margin: '5 0 0 0',
                    handler: 'generateTimeseriesChart'
                }],
                items: [{
                    //    xtype: 'container',
                    //    margin: '0 0 0 0',
                    //    items: [{
                    //        xtype: 'button',
                    //        text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
                    //        id: 'gettimeseries_btn',
                    //        reference: 'gettimeseries_bnt1',
                    //        iconCls: 'chart-curve_medium',
                    //        scale: 'medium',
                    //        disabled: true,
                    //        width: 200,
                    //        handler: 'generateTimeseriesChart'
                    //    }]
                    //},{
                    xtype: 'fieldset',
                    id: 'fieldset_selectedregion',
                    title: '<b style="font-size:16px; color:#0065A2; line-height: 18px;">' + esapp.Utils.getTranslation('selectedregion') + '</b>',
                    hidden: true,
                    autoHeight: true,   // 65,
                    border: 3,
                    padding: 5,
                    style: {
                        borderColor: '#157FCC',
                        borderStyle: 'solid'
                    },
                    items: [{
                        xtype: 'displayfield',
                        id: 'selectedregionname',
                        reference: 'selectedregionname',
                        fieldLabel: '',
                        labelAlign: 'left',
                        fieldCls: 'ts_selectedfeature_name_font',
                        style: {
                            color: 'green'
                            //"font-weight": 'bold',
                            //"font-size": 24
                        },
                        value: ''
                    }]
                }, {
                    xtype: 'timeseriesproductselection'

                    //title: esapp.Utils.getTranslation('products'),  // 'Products',
                    //xtype: 'grid',
                    //reference: 'TimeSeriesProductsGrid',
                    ////region: 'center',
                    ////width: 395,
                    //height: 300,
                    //bind: '{products}',
                    //session: true,
                    //viewConfig: {
                    //    stripeRows: false,
                    //    enableTextSelection: true,
                    //    draggable: false,
                    //    markDirty: false,
                    //    resizable: true,
                    //    disableSelection: false,
                    //    trackOver: true
                    //},
                    //layout: 'fit',
                    //hideHeaders: true,
                    //
                    //selModel: {
                    //    allowDeselect: true,
                    //    mode: 'SIMPLE'
                    //},
                    //
                    //collapsible: false,
                    //enableColumnMove: false,
                    //enableColumnResize: true,
                    //multiColumnSort: false,
                    //columnLines: false,
                    //rowLines: true,
                    //frame: false,
                    //border: true,
                    //bodyBorder: false,
                    //forceFit: true,
                    //
                    //tools: [{
                    //    type: 'refresh',
                    //    tooltip: esapp.Utils.getTranslation('refreshproductlist'),  // 'Refresh product list',
                    //    callback: function (grid) {
                    //        var timeseriesProductsStore = grid.getStore('products');
                    //
                    //        if (timeseriesProductsStore.isStore) {
                    //            timeseriesProductsStore.load();
                    //        }
                    //    }
                    //}],
                    //
                    //features: [{
                    //    reference: 'timeseriesproductcategories',
                    //    ftype: 'grouping',
                    //    groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
                    //    hideGroupedHeader: true,
                    //    enableGroupingMenu: false,
                    //    startCollapsed: true,
                    //    groupByText: esapp.Utils.getTranslation('productcategories')  // 'Product category'
                    //}],
                    //
                    //plugins: [{
                    //    ptype: 'rowexpander',
                    //    //cellWrap:true,
                    //    //layout:'fit',
                    //    rowBodyTpl: new Ext.XTemplate(
                    //        '<span class="smalltext">' +
                    //        '<p>{description}</p>' +
                    //        '</span>'
                    //    )
                    //}],
                    //
                    //listeners: {
                    //    //afterrender: 'loadTimeseriesProductsGrid',
                    //    rowclick: 'TimeseriesProductsGridRowClick'
                    //},
                    //
                    //columns: [{
                    //    text: '<div class="grid-header-style">' + esapp.Utils.getTranslation('productcategories') + '</div>',   // '<div class="grid-header-style">Product categories</div>',
                    //    menuDisabled: true,
                    //    defaults: {
                    //        sortable: false,
                    //        hideable: false,
                    //        variableRowHeight: true,
                    //        menuDisabled: true,
                    //        autoSize: true
                    //    },
                    //    columns: [
                    //        {
                    //            xtype: 'templatecolumn',
                    //            //width: "100%",
                    //            minWidth: 380,
                    //            cellWrap: true,
                    //            tpl: new Ext.XTemplate(
                    //                '<b>{prod_descriptive_name}</b>',
                    //                '<tpl if="version != \'undefined\'">',
                    //                '<b class="smalltext"> - {version}</b>',
                    //                '</tpl>',
                    //                '</br>',
                    //                '<b class="smalltext" style="color:darkgrey">{productcode} - {subproductcode}</b>',
                    //                '<tpl for="productmapsets">',
                    //                '<b class="smalltext"> - {descriptive_name}</b>',
                    //                '</tpl>'
                    //            )
                    //        }
                    //    ]
                    //}]
                //}, {
                    //xtype: 'grid',
                    //id: 'timeseries-mapset-dataset-grid',
                    //reference: 'timeseries-mapset-dataset-grid',
                    ////autoWidth: true,
                    ////width: 395,
                    //maxHeight: 250,
                    ////margin:'10 0 10 0',
                    //autoScroll: false,
                    //hidden: true,
                    //bind: '{timeseriesmapsetdatasets}',
                    //layout: 'fit',
                    //
                    //viewConfig: {
                    //    stripeRows: false,
                    //    enableTextSelection: true,
                    //    draggable: false,
                    //    markDirty: false,
                    //    resizable: false,
                    //    disableSelection: false,
                    //    trackOver: true
                    //},
                    //
                    //selType: 'checkboxmodel',
                    //selModel: {
                    //    allowDeselect: true,
                    //    checkOnly: false,
                    //    mode: 'SIMPLE'
                    //    //,listeners: {}
                    //},
                    //collapsible: false,
                    //enableColumnMove: false,
                    //enableColumnResize: true,
                    //multiColumnSort: false,
                    //columnLines: false,
                    //rowLines: true,
                    //frame: false,
                    //border: true,
                    //bodyBorder: false,
                    //forceFit: false,
                    //
                    ////listeners: {
                    ////    //rowclick: 'mapsetDataSetGridRowClick'
                    ////},
                    //defaults: {
                    //    sortable: false,
                    //    hideable: false,
                    //    variableRowHeight: false
                    //},
                    //columns: [{
                    //    text: '<div class="grid-header-style">' + esapp.Utils.getTranslation('timeseries') + '</div>',   //'<div class="grid-header-style">Time series</div>',
                    //    xtype: 'templatecolumn',
                    //    tpl: new Ext.XTemplate(
                    //        '<b>{prod_descriptive_name}</b>' +
                    //        '<tpl if="version != \'undefined\'">',
                    //        '<b class="smalltext"> - {version} </b>',
                    //        '</tpl>',
                    //        '</br>' +
                    //        '<span class="smalltext"><b style="color:darkgrey">{productcode} - {subproductcode}</b> - <b>{mapsetcode}</b>' +
                    //        '</span>'
                    //    ),
                    //    minWidth: 345,
                    //    sortable: false,
                    //    menuDisabled: true,
                    //    cellWrap: true
                    //}, {
                    //    xtype: 'actioncolumn',
                    //    //header: esapp.Utils.getTranslation('actions'),   // 'Edit draw properties',
                    //    menuDisabled: true,
                    //    sortable: true,
                    //    variableRowHeight: true,
                    //    draggable: false,
                    //    groupable: false,
                    //    hideable: false,
                    //    width: 35,
                    //    align: 'center',
                    //    stopSelection: false,
                    //
                    //    items: [{
                    //        // scope: me,
                    //        width: '35',
                    //        disabled: false,
                    //        getClass: function (v, meta, rec) {
                    //            return 'chart-curve_edit';
                    //        },
                    //        getTip: function (v, meta, rec) {
                    //            return esapp.Utils.getTranslation('edittimeseriesdrawproperties') + ' ' + rec.get('productcode') + ' - ' + rec.get('subproductcode');
                    //        },
                    //        handler: 'editTSDrawProperties'
                    //    }]
                    //}]
                }, {
                    xtype: 'fieldset',
                    id: 'ts_timeframe',
                    title: '<b style="font-size:16px; color:#0065A2; line-height: 18px;">' + esapp.Utils.getTranslation('timeframe') + '</b>',
                    hidden: false,
                    //autoWidth: true,
                    //width: 395,
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
                        }, {
                            xtype: 'datefield',
                            id: 'ts_from_period',
                            fieldLabel: esapp.Utils.getTranslation('from'),    // 'From',
                            labelAlign: 'top',
                            style: {"margin-right": "10px"},
                            width: 150,
                            format: "d/m/Y",
                            emptyText: 'dd/mm/yyyy ',
                            allowBlank: true,
                            maxValue: new Date(),
                            listeners: {
                                change: function () {
                                    Ext.getCmp("radio-fromto").setValue(true);
                                }
                            }
                        }, {
                            xtype: 'datefield',
                            id: 'ts_to_period',
                            fieldLabel: esapp.Utils.getTranslation('to'),    // 'To',
                            labelAlign: 'top',
                            style: {"margin-right": "10px"},
                            width: 150,
                            format: "d/m/Y",
                            emptyText: 'dd/mm/yyyy ',
                            allowBlank: true,
                            //maxValue: new Date(),
                            //,value: new Date()
                            listeners: {
                                change: function () {
                                    Ext.getCmp("radio-fromto").setValue(true);
                                }
                            }
                        }]
                    }, {
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
                                select: function () {
                                    Ext.getCmp("radio-year").setValue(true);
                                }
                            }
                        }]
                    }]
                    //},{
                    //    xtype: 'container',
                    //    margin: '0 0 0 0',
                    //    items: [{
                    //        xtype: 'button',
                    //        text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
                    //        id: 'gettimeseries_btn2',
                    //        reference: 'gettimeseries_bnt2',
                    //        iconCls: 'chart-curve_medium',
                    //        scale: 'medium',
                    //        disabled: true,
                    //        width: 200,
                    //        handler: 'generateTimeseriesChart'
                    //    }]
                }]
            },{
                title: esapp.Utils.getTranslation('MATRIX GRAPH'),  // 'MATRIX GRAPH',
                id: 'ts_matrix_graph_tab_'+me.id,
                margin:3,
                //minHeight: 800,
                autoHeight: true,
                autoScroll:true,
                layout: {
                    type: 'vbox'
                    ,align: 'stretch'
                },
                defaults: {
                    margin: '5 0 15 0'
                }
            },{
                title: 'Debug info',
                id: 'debug_info_tab_'+me.id,
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
        }];

        me.callParent();
    }
});
