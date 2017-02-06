
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
        'esapp.model.ChartProperties',

        'Ext.window.Window',
        'Ext.toolbar.Toolbar'
    ],

    title: '<span class="panel-title-style">'+esapp.Utils.getTranslation('timeseries')+'</span>',
    header: {
        titlePosition: 2,
        titleAlign: "center"
    },
    constrainHeader: true,
    //constrain: true,
    autoShow : false,
    closeable: true,
    closeAction: 'destroy', // 'hide',
    maximizable: true,
    collapsible: true,
    resizable: true,

    width:900,
    //height: Ext.getBody().getViewSize().height < 750 ? Ext.getBody().getViewSize().height-80 : 800,  // 600,
    minWidth:400,
    minHeight:350,
    x: 50,
    y: 5,

    // glyph : 'xf080@FontAwesome',

    margin: '0 0 0 0',
    layout: {
        type: 'fit'
    },

    tschart: null,
    selectedTimeseries: null,
    yearTS: null,
    tsFromPeriod: null,
    tsToPeriod: null,
    yearsToCompare: null,
    tsFromSeason: null,
    tsToSeason: null,
    //tsYear1Season: null,
    //tsYear2Season: null,
    wkt: null,
    charttype: null,
    timeseriesChart: {},
    timeseriesGraph: {},

    listeners: {
        afterrender: function () {
            var me = this;
            me.getController().generateChart();
        }
        // The resize handle is necessary to set the map!
        ,resize: function () {
            var me = this;
            if( me.tschart instanceof Highcharts.Chart){
                me.tschart.setSize(document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight);
                me.tschart.redraw();
            }
        }
        ,move: function () {
            var me = this;
            if( me.tschart instanceof Highcharts.Chart){
                me.tschart.setSize(document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight);
                me.tschart.redraw();
            }
        }
    },

    initComponent: function () {
        var me = this;

        me.title = '<span class="panel-title-style">'+esapp.Utils.getTranslation('timeseries')+'</span>';
        //me.height = Ext.getBody().getViewSize().height-80;
        me.frame = false;
        me.border= true;
        me.bodyBorder = false;

        me.wkt = this.wkt;

        me.tools = [
        {
            type: 'gear',
            tooltip: esapp.Utils.getTranslation('tiptimeserieschartshowhidetools'),  // 'Show/hide time series chart tools menu',
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
                tswin.tschart.setSize(winBodyWidth, winBodyHeight);
                tswin.tschart.redraw();
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
            items: [
                {
                text: esapp.Utils.getTranslation('chartproperties'),    // 'Chart properties',
                iconCls: 'chart-curve_edit',
                scale: 'medium'
                ,handler: 'openChartProperties'
            },{
                xtype: 'button',
                iconCls: 'fa fa-refresh fa-2x',
                style: { color: 'gray' },
                enableToggle: false,
                scale: 'medium',
                handler: 'refreshChart'
            },
            '->',{
                text: esapp.Utils.getTranslation('downloadtimeseries'),    // 'Download timeseries',
                iconCls: 'fa fa-download fa-2x',
                scale: 'medium'
                ,handler: 'tsDownload'
            },{
                text: esapp.Utils.getTranslation('savechart'),    // 'Save chart',
                iconCls: 'fa fa-floppy-o fa-2x',
                scale: 'medium'
                ,handler: 'saveChart'
            }]
        });


        me.name ='tschartwindow_' + me.id;

        me.items = [{
            //xtype: 'container',
            //id: 'tschartcontainer_' + me.id,
            //items: [{
                xtype: 'container',
                layout:'fit',
                reference:'tschart_'+me.id,
                id: 'tschart_' + me.id
            //}]
        }];

        me.callParent();
    }
});
