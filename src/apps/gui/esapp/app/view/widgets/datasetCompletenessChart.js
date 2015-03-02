
Ext.define("esapp.view.widgets.datasetCompletenessChart",{
    "extend": "Ext.container.Container",

    requires: [
        'esapp.view.widgets.datasetCompletenessChartModel',
        'esapp.view.widgets.datasetCompletenessChartController',

        'Ext.data.JsonStore',
        'Ext.chart.CartesianChart',
        'Ext.chart.axis.Numeric',
        'Ext.chart.axis.Category',
        'Ext.chart.series.Bar',
        'Ext.chart.interactions.ItemHighlight'
    ],

    "controller": "widgets-datasetcompletenesschart",
    "viewModel": {
        "type": "widgets-datasetcompletenesschart"
    },
    xtype: 'datasetchart',

    //configs with auto generated getter/setter methods
    config: {
        firstdate:'',
        lastdate:'',
        totfiles:0,
        missingfiles:0
    },

    margin:0,
    bodyPadding:0,

    initComponent: function() {
        var me = this,
            spriteY = 7,
            fontsize = 10;

        me.items = [{
            xtype: 'cartesian',
            width: '100%',
            height: 30,

            colors: [
                '#81AF34', // green
                '#FF0000', // red
                '#808080' // black or gray
            ],
            legend: {
                hidden:true
            },
            innerPadding: {top: 0, left: 0, right: 0, bottom: 0},
            insetPadding: {top: 10, left: 15, right: 15, bottom: 0},
            flipXY: true,

            //store: Ext.create('Ext.data.JsonStore', {
            //    fields: me.storefields,
            //    data: me.datasetdata
            //}),
            sprites:  [{
                type: 'text',
                text: 'Files: ' + me.totfiles,
                fontSize: fontsize,
                x: 120,
                y: spriteY
            },{
                type: 'text',
                text: 'Missing: ' + me.missingfiles,
                fontSize: fontsize,
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
                x: 286,
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
                },
                //highlight: {
                //    fillStyle: 'white' // 'transparent'
                //    ,strokeStyle: "black"
                //    ,opacity: 30
                //    ,segment: {
                //        margin: 5
                //    }
                //},
                tooltip: {
                    trackMouse: false,
                    dismissDelay:2000,
                    style: 'background: #fff',
                    renderer: function (storeItem, item) {
                        var allperiods = '';
                        var arrayLength = item.series.getTitle().length;
                        var thisperiodindex = Ext.Array.indexOf(item.series.getYField(), item.field);

                        for (var i = 0; i < arrayLength; i++) {
                            if (i == thisperiodindex) {
                                allperiods = allperiods + '<b>'+item.series.getTitle()[thisperiodindex] + '</b></br>';
                            }
                            else {
                                allperiods = allperiods + item.series.getTitle()[i] + '</br>';
                            }
                        }

                        this.setHtml(allperiods);
                    }
                }
            }]

        }];

        me.callParent();
    }
});
