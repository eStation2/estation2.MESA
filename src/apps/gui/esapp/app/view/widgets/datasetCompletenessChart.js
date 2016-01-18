
Ext.define("esapp.view.widgets.datasetCompletenessChart",{
    "extend": "Ext.container.Container",

    requires: [
        'esapp.view.widgets.datasetCompletenessChartModel',
        'esapp.view.widgets.datasetCompletenessChartController',

        'Ext.data.JsonStore',
        'Ext.draw.engine.Svg',
        'Ext.chart.CartesianChart',
        'Ext.chart.axis.Numeric',
        'Ext.chart.axis.Category',
        'Ext.chart.series.Bar'
        //,'Ext.chart.interactions.ItemHighlight'
    ],

    "controller": "widgets-datasetcompletenesschart",
    "viewModel": {
        "type": "widgets-datasetcompletenesschart"
    },
    xtype: 'datasetchart',

    //configs with auto generated getter/setter methods
    //config: {
    //    firstdate:'',
    //    lastdate:'',
    //    totfiles:0,
    //    missingfiles:0,
    //    tooltipintervals: ''
    //},

    firstdate:'',
    lastdate:'',
    totfiles:0,
    missingfiles:0,
    tooltipintervals: '',

    margin:0,
    bodyPadding:0,
    //bufferedRenderer: true,

    initComponent: function() {
        var me = this,
            spriteY = 10,
            fontsize = 10;

        var missingFilesText = '';
        if(me.missingfiles>0)
           missingFilesText = esapp.Utils.getTranslation('Missing') + ': ' + me.missingfiles;

        me.listeners = {
            //element: 'el',
            //click: function() {
            //    var me = this;
            //    console.info(me.tooltipintervals);
            //    var widgettooltip = Ext.getCmp(me.getId() + '_tooltip');
            //    widgettooltip.enable();
            //    widgettooltip.show();
            //},
            afterrender: function () {
                Ext.create('Ext.tip.ToolTip', {
                    id: me.getId() + '_tooltip',
                    target: me.getId(),
                    disabled: true,
                    trackMouse: false,
                    autoHide: false,
                    dismissDelay: 5000, // auto hide after 5 seconds
                    closable: true,
                    anchorToTarget: true,
                    anchor: 'left',
                    padding: 10,
                    html: me.tooltipintervals, // Tip content
                    listeners: {
                        close: function() {
                            this.disable();
                        }
                    }
                });

                this.getEl().on('click', function() {
                    var widgettooltip = Ext.getCmp(me.getId() + '_tooltip');
                    widgettooltip.html = me.tooltipintervals;
                    widgettooltip.enable();
                    widgettooltip.show();
                });

            }
        };

        me.items = [{
            xtype: 'cartesian',
            width: '100%',
            height: 38,
            minWidth : 340,

            //engine: Ext.draw.engine.Canvas,
            engine: Ext.draw.engine.Svg,

            colors: [
                '#81AF34', // green
                '#FF0000', // red
                '#808080' // black or gray
            ],
            legend: {
                hidden:true
            },
            innerPadding: {top: 0, left: 0, right: 0, bottom: 0},
            insetPadding: {top: 12, left: 15, right: 15, bottom: 5},
            flipXY: true,

            //store: Ext.create('Ext.data.JsonStore', {
            //    fields: me.storefields,
            //    data: me.datasetdata
            //}),
            sprites:  [{
                type: 'text',
                text: esapp.Utils.getTranslation('files') + ': ' + me.totfiles,
                fontSize: fontsize,
                x: 120,
                y: spriteY
            },{
                type: 'text',
                text: missingFilesText,
                fontSize: fontsize+1,
                fontWeight: 'bold',
                fillStyle: '#FF0000',
                x: 190,
                y: spriteY
            },{
                type: 'text',
                text: me.firstdate,
                fontSize: fontsize,
                x: 0,
                y: spriteY
            },{
                type: 'text',
                text: me.lastdate,
                fontSize: fontsize,
                textAlign: 'middle',
                x: 286+25,
                y: spriteY
            }],

            axes: [{
                type: 'numeric',
                // fields: ['data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7'],
                grid: false,
                hidden:true
            }, {
                type: 'category',
                // fields: 'dataset',
                position: 'left',
                grid: false
            }],

            series: [{
                type: 'bar',
                // title: ['data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7'],
                // title: me.seriestitles,
                xField: 'dataset',
                // yField: me.seriesyField,
                axis: 'bottom',
                // colors: me.seriescolors,
                stacked: true,
                style: {
                    opacity: 0.80
                }
                //,highlight: {
                //    fillStyle: 'white' // 'transparent'
                //    ,strokeStyle: "black"
                //    ,opacity: 30
                //    ,segment: {
                //        margin: 5
                //    }
                //},
                //,tooltip: {
                //    trackMouse: false,
                //    dismissDelay:60000,
                //    style: 'background: #fff',
                //    renderer: function (storeItem, item) {
                //        var allperiods = '';
                //        var arrayLength = item.series.getTitle().length;
                //        var thisperiodindex = Ext.Array.indexOf(item.series.getYField(), item.field);
                //
                //        for (var i = 0; i < arrayLength; i++) {
                //            if (i == thisperiodindex) {
                //                allperiods = allperiods + '<b>'+item.series.getTitle()[thisperiodindex] + '</b></br>';
                //            }
                //            else {
                //                allperiods = allperiods + item.series.getTitle()[i] + '</br>';
                //            }
                //        }
                //
                //        this.setHtml(allperiods);
                //    }
                //}
            }]

        }];

        me.callParent();
    }
});
