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
    floatable: true,
    alwaysOnTop: false,
    autoScroll: true,
    scrollable: 'vertical',
    shrinkWrap: 3, // both width and height depend on content (shrink wrap).
    width:470,
    // maxWidth:470,
    // autoWidth: true,
    // autoHeight: true,
    // layout: {
    //     type: 'fit'
    // },
    alignTarget: Ext.getCmp('backgroundmap'),
    defaultAlign: 'tr-tr',
    frame: false,
    border: false,
    shadow: false,
    componentCls: 'rounded-box',

    initComponent: function () {
        var me = this;
        // me.height = Ext.getCmp('analysismain').getBody().height;

        me.viewConfig = {
            defaultAlign: 'tr-tr',
            alignTarget: Ext.getCmp('backgroundmap')
        };

        me.listeners = {
            // afterrender: function(){
            //     Ext.util.Observable.capture(me, function (e) { console.log('timeserieschartselection - ' + e);});
            //     // me.fireEvent('align');
            // },
            show: function(){
                // console.info('show tschartselection');
                me.hidden = false;
                me.fireEvent('align');
                me.expand();
            },
            align: function() {
                // console.info('align tschartselection');
                var task = new Ext.util.DelayedTask(function() {
                    // me.show();
                    // me.expand();
                    me.alignTo(Ext.getCmp('analysismain').lookupReference('backgroundmap'), 'tr-tr');
                    // me.alignTo(Ext.getCmp('analysismain'), 'tr-tr');
                    // me.height = Ext.getBody().getViewSize().height-65;
                    me.height = Ext.getCmp('analysismain').body.getHeight();
                    me.updateLayout();
                });
                if (!me.hidden) {
                    task.delay(50);
                }
            }
        };

        me.title = esapp.Utils.getTranslation('TIME_SERIES_GRAPHS');  // 'TIME SERIES GRAPHS',

        me.defaults = {
            margin: '8 3 8 3'
        };

        me.items = [{
            xtype: 'fieldset',
            id: 'fieldset_selectedregion',
            title: '<b style="font-size:16px; color:#0065A2; line-height: 18px;">' + esapp.Utils.getTranslation('selectedregion') + '</b>',
            hidden: false,
            autoHeight: false,   // 65,
            height: 60,
            maxHeight: 60,
            border: 2,
            padding: '5 5 5 15',
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
            xtype: 'tabpanel',
            id: 'graphs_tabpanel_'+me.id,
            hideCollapseTool: true,
            header: false,
            autoScroll:false,
            reserveScrollbar: false,
            frame: false,
            border: false,
            // bodyPadding: '3 3 3 3',
            componentCls: 'rounded-box',
            layout: {
                type: 'fit'
            },
            items: [{
                title: esapp.Utils.getTranslation('PROFILE'),  // 'DEFAULT X/Y GRAPH',
                id: 'ts_xy_graph_tab_' + me.id,
                autoHeight: true,
                autoScroll: true,
                layout: {
                    type: 'vbox'
                    ,align: 'stretch'
                },
                tbar: {
                    padding: '0 0 0 0',
                    items: [{
                        xtype: 'button',
                        text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
                        id: 'gettimeseries_btn_xy',
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
            },{

                title: esapp.Utils.getTranslation('CUMULATIVE'),  // 'CUMULATIVE',
                id: 'ts_cumulative_graph_tab_' + me.id,
                autoHeight: true,
                autoScroll: true,
                layout: {
                    type: 'vbox'
                    , align: 'stretch'
                },
                tbar: {
                    padding: '0 0 0 0',
                    items: [{
                        xtype: 'button',
                        text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
                        id: 'gettimeseries_btn_cum',
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
            },{
                title: esapp.Utils.getTranslation('RANKING_ZSCORE'),  // 'RANKING / Z-SCORE',
                id: 'ts_ranking_graph_tab_'+me.id,
                autoHeight: true,
                autoScroll:true,
                layout: {
                    type: 'vbox'
                    ,align: 'stretch'
                },
                tbar: {
                    padding: '0 0 0 0',
                    items: [{
                        xtype: 'button',
                        text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
                        id: 'gettimeseries_btn_ranking',
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
            },{
                title: esapp.Utils.getTranslation('MATRIX'),  // 'MATRIX',
                id: 'ts_matrix_graph_tab_'+me.id,
                autoHeight: true,
                autoScroll:true,
                layout: {
                    type: 'vbox'
                    ,align: 'stretch'
                },
                tbar: {
                    padding: '0 0 0 0',
                    items: [{
                        xtype: 'button',
                        text: esapp.Utils.getTranslation('gettimeseries'),    // 'Get timeseries',
                        id: 'gettimeseries_btn_matrix',
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
