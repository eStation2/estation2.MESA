Ext.define("esapp.view.analysis.timeseriesChartSelection",{
    extend: "Ext.panel.Panel",
 
    requires: [
        "esapp.view.analysis.timeseriesChartSelectionController",
        "esapp.view.analysis.timeseriesChartSelectionModel",

        "esapp.view.analysis.timeseriesProductSelection"
    ],
    
    controller: "analysis-timeserieschartselection",
    viewModel: {
        type: "analysis-timeserieschartselection"
    },

    xtype: 'timeserieschartselection',

    title: esapp.Utils.getTranslation('TIME_SERIES_GRAPHS'),  // 'TIME SERIES GRAPHS',

    header: {
        titlePosition: 1,
        titleAlign: 'center'
    },
    constrainHeader: true,
    constrain: false,
    autoShow : false,
    hidden: true,
    closable: true,
    closeAction: 'hide', // 'hide',
    maximizable: false,
    collapsible: true,
    collapsed: false,
    resizable: false,
    floating: true,
    alwaysOnTop: false,
    shrinkWrap: 3, // both width and height depend on content (shrink wrap).
    width:420,
    // maxWidth:500,
    // autoWidth: true,
    // autoHeight: true,
    layout: {
        type: 'vbox',
        pack: 'start',
        align: 'stretch'
    },
    margin: '0 3 0 0',
    // alignTarget: Ext.getCmp('backgroundmap'),
    defaultAlign: 'tr-tr',
    frame: false,
    border: false,
    shadow: false,
    componentCls: 'rounded-box',

    config: {
        workspace: null
    },


    initComponent: function () {
        var me = this;
        // me.height = Ext.getCmp('analysismain').getBody().height;

        me.viewConfig = {
            defaultAlign: 'tr-tr'
            // alignTarget: Ext.getCmp(me.workspace.id).body      // Ext.getCmp('backgroundmap')
        };

        me.listeners = {
            afterrender: function(){
                // Ext.util.Observable.capture(me, function (e) { console.log('timeserieschartselection - ' + e);});
                // console.info(Ext.getCmp(me.workspace.id));
                me.alignTarget = Ext.getCmp(me.workspace.id).body;
                // me.fireEvent('align');
            },
            show: function(){
                me.hidden = false;
                me.fireEvent('align');
                me.height = Ext.getCmp(me.workspace.id).body.getHeight()-3;
                me.updateLayout();
                me.expand();
            },
            align: function() {
                var task = new Ext.util.DelayedTask(function() {
                    me.alignTo(Ext.getCmp(me.workspace.id).body, 'tr-tr');
                    me.height = Ext.getCmp(me.workspace.id).body.getHeight()-3;
                    me.updateLayout();
                });
                if (!me.hidden) {
                    task.delay(50);
                }
            }
        };

        me.title = esapp.Utils.getTranslation('TIME_SERIES_GRAPHS');  // 'TIME SERIES GRAPHS',

        me.defaults = {
            margin: '5 3 2 3'
        };

        me.items = [{
            xtype: 'fieldset',
            // id: 'fieldset_selectedregion',
            title: '<b style="font-size:16px; color:#0065A2; line-height: 18px;">' + esapp.Utils.getTranslation('selectedregion') + '</b>',
            hidden: false,
            autoHeight: true,   // 65,
            height: 65,
            flex: 1,
            maxHeight: 80,
            border: 2,
            padding: '3 5 3 10',
            style: {
                borderColor: '#157FCC',
                borderStyle: 'solid'
            },
            items: [{
                xtype: 'displayfield',
                // id: 'selectedregionname_'+me.workspace.id,
                reference: 'selectedregionname',
                height: 40,
                fieldLabel: '',
                labelAlign: 'left',
                fieldCls: 'ts_selectedfeature_name_font',
                style: {
                    color: 'green'
                    //"font-weight": 'bold',
                    //"font-size": 24
                },
                value: '',
                listeners: {
                    change: function(field,newValue, oldValue){
                        var new_wkt_polygon = me.lookupReference('wkt_polygon').getValue();
                        var new_selectedregionname = me.lookupReference('selectedregionname').getValue();

                        if (new_wkt_polygon.trim() != '' && new_selectedregionname.trim() != '') {
                            var graphViewWindows = Ext.ComponentQuery.query('timeserieschart-window');

                            Ext.Object.each(graphViewWindows, function(id, graphview_window, thisObj) {
                                if (graphview_window.link_region_change){
                                    graphview_window.getController().changeSelectedRegion();
                                }
                            });
                        }
                    }
                }
            }]
        }, {
            xtype: 'tabpanel',
            // id: 'graphs_tabpanel_' + me.id,
            hideCollapseTool: true,
            header: false,
            frame: false,
            border: false,
            flex: 5,
            // bodyPadding: '3 3 3 3',
            componentCls: 'rounded-box',
            resizable: false,
            defaults: {
                layout: {
                    type: 'fit'
                }
            },
            items: [{
                title: esapp.Utils.getTranslation('PROFILE'),  // 'DEFAULT X/Y GRAPH',
                // id: 'ts_xy_graph_tab_' + me.id,
                tbar: {
                    padding: '0 0 0 0',
                    items: [{
                        xtype: 'button',
                        text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
                        // id: 'gettimeseries_btn_xy',
                        reference: 'gettimeseries_btn_xy',
                        iconCls: 'chart-curve_medium',
                        scale: 'medium',
                        disabled: false,
                        //width: 150,
                        autoWidth: true,
                        margin: '0 0 5 0',
                        graphtype: 'xy',
                        handler: 'generateTimeseriesChart'
                    }]
                },
                items: [{
                    xtype: 'timeseriesproductselection',
                    graphtype: 'xy',
                    cumulative: false,
                    multiplevariables: true,
                    fromto: true,
                    year: false,
                    // compareyears: false,
                    multipleyears: true
                }]
            }, {
                title: esapp.Utils.getTranslation('CUMULATIVE'),  // 'CUMULATIVE',
                // id: 'ts_cumulative_graph_tab_' + me.id,
                tbar: {
                    padding: '0 0 0 0',
                    items: [{
                        xtype: 'button',
                        text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
                        // id: 'gettimeseries_btn_cum',
                        reference: 'gettimeseries_btn_cum',
                        iconCls: 'chart-curve_medium',
                        scale: 'medium',
                        disabled: false,
                        //width: 150,
                        autoWidth: true,
                        margin: '0 0 5 0',
                        graphtype: 'cumulative',
                        handler: 'generateTimeseriesChart'
                    }]
                },
                items: [{
                    xtype: 'timeseriesproductselection',
                    graphtype: 'cumulative',
                    cumulative: true,
                    multiplevariables: true,
                    fromto: true,
                    year: true,
                    // compareyears: false,
                    multipleyears: false
                }]
            }, {
                title: esapp.Utils.getTranslation('RANKING_ZSCORE'),  // 'RANKING / Z-SCORE',
                // id: 'ts_ranking_graph_tab_' + me.id,
                tbar: {
                    padding: '0 0 0 0',
                    items: [{
                        xtype: 'button',
                        text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
                        // id: 'gettimeseries_btn_ranking',
                        reference: 'gettimeseries_btn_ranking',
                        iconCls: 'chart-curve_medium',
                        scale: 'medium',
                        disabled: false,
                        autoWidth: true,
                        margin: '0 0 5 0',
                        graphtype: 'ranking',
                        handler: 'generateTimeseriesChart'
                    }]
                },
                items: [{
                    xtype: 'timeseriesproductselection',
                    graphtype: 'ranking',
                    cumulative: false,
                    ranking: true,
                    multiplevariables: false,
                    fromto: false,
                    year: false,
                    // compareyears: false,
                    multipleyears: true
                }]
            }, {
                title: esapp.Utils.getTranslation('MATRIX'),  // 'MATRIX',
                // id: 'ts_matrix_graph_tab_' + me.id,
                tbar: {
                    padding: '0 0 0 0',
                    items: [{
                        xtype: 'button',
                        text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
                        // id: 'gettimeseries_btn_matrix',
                        reference: 'gettimeseries_btn_matrix',
                        iconCls: 'chart-curve_medium',
                        scale: 'medium',
                        disabled: false,
                        autoWidth: true,
                        margin: '0 0 5 0',
                        graphtype: 'matrix',
                        handler: 'generateTimeseriesChart'
                    }]
                },
                items: [{
                    xtype: 'timeseriesproductselection',
                    graphtype: 'matrix',
                    cumulative: false,
                    matrix: true,
                    multiplevariables: false,
                    fromto: false,
                    year: false,
                    // compareyears: false,
                    multipleyears: true
                }]
            // }, {
            //     title: esapp.Utils.getTranslation('SCATTER'),  // 'CUMULATIVE',
            //     // id: 'ts_cumulative_graph_tab_' + me.id,
            //     tbar: {
            //         padding: '0 0 0 0',
            //         items: [{
            //             xtype: 'button',
            //             text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
            //             reference: 'gettimeseries_btn_scatter',
            //             iconCls: 'chart-curve_medium',
            //             scale: 'medium',
            //             disabled: false,
            //             autoWidth: true,
            //             margin: '0 0 5 0',
            //             graphtype: 'scatter',
            //             handler: 'generateTimeseriesChart'
            //         }]
            //     },
            //     items: [{
            //         xtype: 'timeseriesproductselection',
            //         graphtype: 'scatter',
            //         cumulative: false,
            //         multiplevariables: true,
            //         fromto: true,
            //         year: false,
            //         // compareyears: false,
            //         multipleyears: false
            //     }]
            }, {
                title: 'Debug info',
                // id: 'debug_info_tab_' + me.id,
                hidden: true,
                items: [{
                    xtype: 'displayfield',
                    // id: 'regionname',
                    reference: 'regionname',
                    fieldLabel: 'Region name',
                    labelAlign: 'top',
                    value: '<span style="color:green;">value</span>'
                }, {
                    title: 'WKT of Polygon',
                    xtype: 'displayfield',
                    // id: 'wkt_polygon_'+ me.workspace.id,
                    reference: 'wkt_polygon',
                    fieldLabel: 'WKT of Polygon',
                    labelAlign: 'top',
                    value: ''
                }]
            }]
        }];

        me.callParent();
    }
});
