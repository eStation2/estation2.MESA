
Ext.define("esapp.view.analysis.timeseriesChartView",{
    "extend": "Ext.window.Window",
    "controller": "analysis-timeserieschartview",
    "viewModel": {
        "type": "analysis-timeserieschartview"
    },

    xtype: 'timeserieschart-window',

    requires: [
        'esapp.view.analysis.timeseriesChartViewModel',
        'esapp.view.analysis.timeseriesChartViewController',
        // 'esapp.model.GraphProperties',

        'Ext.window.Window',
        'Ext.toolbar.Toolbar'
    ],

    title: '<span class="panel-title-style">'+esapp.Utils.getTranslation('timeseries')+'</span>',
    header: {
        titlePosition: 2,
        titleAlign: "left"
    },
    constrainHeader: true,
    //constrain: true,
    autoShow : false,
    closeable: true,
    closeAction: 'destroy', // 'hide',
    maximizable: true,
    collapsible: true,
    resizable: true,

    width:700,
    height: Ext.getBody().getViewSize().height < 700 ? Ext.getBody().getViewSize().height-80 : 700,
    minWidth:400,
    minHeight:350,
    x: 50,
    y: 5,

    // glyph : 'xf080@FontAwesome',

    margin: '0 0 0 0',
    layout: {
        type: 'fit'
    },

    config: {
        isNewTemplate: true,
        isTemplate: false,
        graph_tpl_name: '',

        tsgraph: null,
        selectedTimeseries: null,
        yearTS: null,
        tsFromPeriod: null,
        tsToPeriod: null,
        yearsToCompare: null,
        tsFromSeason: null,
        tsToSeason: null,
        selectedregionname: null,
        wkt_geom: null,
        graphtype: null,
        timeseriesChart: {},
        timeseriesGraph: {}
    },

    listeners: {

        afterrender: function () {
            var me = this;
            if (me.isTemplate){
                me.setSize(me.graphviewsize[0],me.graphviewsize[1]);
                me.setPosition(me.graphviewposition);
                me.updateLayout();
            }
            me.getController().generateChart();
        }
        // The resize handle is necessary to set the map!
        ,resize: function () {
            var me = this;
            if( me.tsgraph instanceof Highcharts.Chart){
                me.tsgraph.setSize(document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight);
                me.tsgraph.redraw();
            }
        }
        ,move: function () {
            var me = this;
            if( me.tsgraph instanceof Highcharts.Chart){
                me.tsgraph.setSize(document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight);
                me.tsgraph.redraw();
            }
        }
    },

    initComponent: function () {
        var me = this;

        // me.title = '<span class="panel-title-style">'+esapp.Utils.getTranslation('timeseries')+'</span>';
        me.title = '<span id="graphview_title_templatename_' + me.id + '" class="graph-templatename"></span>' +
                   '<span id="graphview_title_' + me.id + '">'+esapp.Utils.getTranslation('timeseries')+'</span>';
        //me.height = Ext.getBody().getViewSize().height-80;
        me.frame = false;
        me.border= true;
        me.bodyBorder = false;

        me.wkt_geom = this.wkt_geom;

        me.tools = [
        {
            type: 'gear',
            tooltip: esapp.Utils.getTranslation('graphshowhidetools'),  // 'Show/hide graph tools menu',
            callback: function (tswin) {
                // toggle hide/show toolbar and adjust map size.
                var winBodyWidth = tswin.getWidth()-5;
                var winBodyHeight = tswin.getHeight()-45;
                var tsToolbar = tswin.getDockedItems('toolbar[dock="top"]')[0];
                var widthToolbar = tsToolbar.getWidth();
                var heightToolbar = tsToolbar.getHeight();
                if (tsToolbar.hidden == false) {
                    tsToolbar.setHidden(true);
                    winBodyWidth = document.getElementById(tswin.id + "-body").offsetWidth;
                    winBodyHeight =  document.getElementById(tswin.id + "-body").offsetHeight; //+heightToolbar;
                }
                else {
                    tsToolbar.setHidden(false);
                    winBodyWidth = document.getElementById(tswin.id + "-body").offsetWidth;
                    winBodyHeight = document.getElementById(tswin.id + "-body").offsetHeight-heightToolbar;
                }
                tswin.tsgraph.setSize(winBodyWidth, winBodyHeight);
                tswin.tsgraph.redraw();
            }
        }];

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            id: 'tbar_'+me.id,
            dock: 'top',
            autoShow: true,
            alwaysOnTop: true,
            floating: false,
            hidden: false,
            border: false,
            shadow: false,
            padding:0,
            defaults: {
                margin: 2
            },
            items: [{
                // text: esapp.Utils.getTranslation('properties'),    // 'Graph properties',
                tooltip: esapp.Utils.getTranslation('graph_edit_properties'), //  'Edit graph properties',
                iconCls: 'chart-curve_edit',
                scale: 'medium'
                ,handler: 'openChartProperties'
            },
            {
                // text: esapp.Utils.getTranslation('values'),    // downloadtimeseries = 'Download timeseries',
                tooltip: esapp.Utils.getTranslation('graph_download_values'),   //  'Download time series values',
                iconCls: 'download-values_excel',   // 'fa fa-file-excel-o fa-2x',    // 'fa fa-download fa-2x',
                style: { color: 'green' },
                scale: 'medium'
                ,handler: 'tsDownload'
            },{
                // text: esapp.Utils.getTranslation('savechart'),    // 'Save graph',
                tooltip: esapp.Utils.getTranslation('graph_download_png'),   //  'Download graph as PNG',
                iconCls: 'download_png',    // 'fa fa-floppy-o fa-2x',
                scale: 'medium'
                ,handler: 'saveChart'
            },{
                xtype: 'splitbutton',
                reference: 'saveGraphTemplate_'+me.id.replace(/-/g,'_'),
                tooltip: esapp.Utils.getTranslation('graph_save_graph_tpl'),   //  'Save graph as template',
                iconCls: 'fa fa-save fa-2x',
                style: {color: 'lightblue'},
                cls: 'nopadding-splitbtn',
                scale: 'medium',
                hidden:  (esapp.getUser() == 'undefined' || esapp.getUser() == null ? true : false),
                handler: 'setGraphTemplateName',
                menu: {
                    hideOnClick: false,
                    alwaysOnTop: true,
                    //iconAlign: '',
                    width: 165,
                    defaults: {
                        hideOnClick: true,
                        //cls: "x-menu-no-icon",
                        padding: 2
                    },
                    items: [{
                        //xtype: 'button',
                        text: esapp.Utils.getTranslation('save_as'),    // 'Save as...',
                        tooltip: esapp.Utils.getTranslation('graph_tpl_save_as'),   //  'Save graph as template',
                        iconCls: 'fa fa-save fa-lg lightblue',
                        style: { color: 'lightblue' },
                        //cls: 'x-menu-no-icon button-gray',
                        width: 165,
                        handler: function(){
                            me.isNewTemplate = true;
                            me.getController().setGraphTemplateName();
                        }
                    }]
                }

            },
            '->',
            {
                xtype: 'button',
                tooltip: esapp.Utils.getTranslation('graph_refresh'),   //  'Refresh graph',
                iconCls: 'fa fa-refresh fa-2x',
                style: { color: 'gray' },
                enableToggle: false,
                scale: 'medium',
                handler: 'refreshChart'
            }]
        });


        me.name ='tsgraphwindow_' + me.id;

        me.items = [{
                xtype: 'container',
                layout:'fit',
                reference:'tsgraph_'+me.id,
                id: 'tsgraph_' + me.id
        }];

        me.callParent();
    }
});
